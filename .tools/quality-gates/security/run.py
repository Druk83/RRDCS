#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
QUALITY_GATES_DIR = SCRIPT_PATH.parents[1]
if str(QUALITY_GATES_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_GATES_DIR))

from common import (  # noqa: E402
    CheckOutcome,
    command_exists,
    find_files,
    print_report,
    run_command,
    summarize_exit_code,
    tool_missing_outcome,
)


DOCKER_SECURITY_SPECS: dict[str, dict] = {
    "gitleaks": {
        "image": "zricethezav/gitleaks:latest",
        "command": [],
    }
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запустить пакет security quality-gates (gitleaks + baseline SAST профиля).",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Путь к корню репозитория (по умолчанию автоопределение).",
    )
    parser.add_argument(
        "--policy",
        default=None,
        help="Путь к файлу check-packages policy (JSON-совместимый YAML).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Формат вывода.",
    )
    parser.add_argument(
        "--tool-runtime",
        choices=("auto", "local", "docker"),
        default="auto",
        help="Режим запуска инструментов: auto/local/docker.",
    )
    parser.add_argument(
        "--allow-missing-tools",
        action="store_true",
        help="Возвращать предупреждение (exit 2), если внешний инструмент не установлен.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать план проверок без запуска внешних инструментов.",
    )
    return parser.parse_args()


def detect_repo_root(arg_value: str | None) -> Path:
    if arg_value:
        return Path(arg_value).resolve()
    return SCRIPT_PATH.parents[3]


def default_policy_path(repo_root: Path) -> Path:
    candidates = [
        repo_root / ".manifest" / "policies" / "check-packages.yaml",
        repo_root / ".github" / "policies" / "check-packages.yaml",
        repo_root / ".sources" / ".manifest" / "policies" / "check-packages.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def load_policy(repo_root: Path, raw_policy_path: str | None) -> dict:
    policy_path = Path(raw_policy_path).resolve() if raw_policy_path else default_policy_path(repo_root)
    if not policy_path.exists():
        raise FileNotFoundError(f"Файл policy не найден: {policy_path}")
    text = policy_path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def resolve_runtime(mode: str) -> str:
    if mode == "auto":
        return "docker" if command_exists("docker") else "local"
    return mode


def select_tool(candidates: list[str]) -> str | None:
    for item in candidates:
        if command_exists(item):
            return item
    return None


def docker_base_command(repo_root: Path, image: str) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo_root}:/work",
        "-w",
        "/work",
        image,
    ]


def run_command_check_local(
    check_name: str,
    tool_candidates: list[str],
    args: list[str],
    repo_root: Path,
    allow_missing_tools: bool,
    dry_run: bool,
) -> tuple[CheckOutcome, bool]:
    selected_tool = select_tool(tool_candidates)
    if selected_tool is None:
        return (
            tool_missing_outcome(
                check_name=check_name,
                tool_name="/".join(tool_candidates) if tool_candidates else "unknown",
                allow_missing_tools=allow_missing_tools,
            ),
            True,
        )

    command = [selected_tool, *args]
    if dry_run:
        return (
            CheckOutcome(
                check=check_name,
                status="pass",
                message=f"dry-run(local): {' '.join(command)}",
                command=command,
                return_code=0,
            ),
            False,
        )

    rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=900)
    if rc == 0:
        return (
            CheckOutcome(check=check_name, status="pass", message="ok", command=command, return_code=0),
            False,
        )

    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()
    details = stderr_text if stderr_text else stdout_text
    message = details.splitlines()[0] if details else "команда завершилась с ошибкой"
    return (
        CheckOutcome(
            check=check_name,
            status="fail",
            message=message,
            command=command,
            return_code=rc,
        ),
        False,
    )


def run_command_check_docker(
    check_name: str,
    args: list[str],
    repo_root: Path,
    allow_missing_tools: bool,
    dry_run: bool,
) -> tuple[CheckOutcome, bool]:
    if not command_exists("docker"):
        return (
            tool_missing_outcome(check_name=check_name, tool_name="docker", allow_missing_tools=allow_missing_tools),
            True,
        )

    spec = DOCKER_SECURITY_SPECS.get(check_name)
    if not spec:
        return (
            CheckOutcome(
                check=check_name,
                status="fail",
                message=f"для docker-режима не настроен check '{check_name}'",
            ),
            False,
        )

    command = docker_base_command(repo_root=repo_root, image=str(spec["image"])) + [*spec.get("command", []), *args]
    if dry_run:
        return (
            CheckOutcome(
                check=check_name,
                status="pass",
                message=f"dry-run(docker): {' '.join(command)}",
                command=command,
                return_code=0,
            ),
            False,
        )

    rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=1800)
    if rc == 0:
        return (
            CheckOutcome(check=check_name, status="pass", message="ok (docker)", command=command, return_code=0),
            False,
        )

    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()
    details = stderr_text if stderr_text else stdout_text
    message = details.splitlines()[0] if details else "docker-команда завершилась с ошибкой"
    return (
        CheckOutcome(
            check=check_name,
            status="fail",
            message=message,
            command=command,
            return_code=rc,
        ),
        False,
    )


def run_sast_profile_check(
    check_name: str,
    workflow_patterns: list[str],
    required_markers: list[str],
    repo_root: Path,
) -> CheckOutcome:
    files = find_files(root=repo_root, patterns=workflow_patterns)
    if not files:
        return CheckOutcome(
            check=check_name,
            status="fail",
            message="не найдены CI workflow файлы для проверки SAST профиля",
        )

    lowered_markers = [item.lower() for item in required_markers]
    for file_path in files:
        content = file_path.read_text(encoding="utf-8-sig", errors="replace").lower()
        if any(marker in content for marker in lowered_markers):
            return CheckOutcome(
                check=check_name,
                status="pass",
                message=f"профиль найден в {file_path.relative_to(repo_root)}",
            )

    return CheckOutcome(
        check=check_name,
        status="fail",
        message="SAST профиль не настроен в workflows (маркеры CodeQL/Semgrep не найдены)",
    )


def run_security_package(
    policy: dict,
    repo_root: Path,
    allow_missing_tools: bool,
    dry_run: bool,
    tool_runtime: str,
) -> tuple[list[CheckOutcome], bool]:
    checks = policy.get("packages", {}).get("security", {}).get("checks", [])
    outcomes: list[CheckOutcome] = []
    had_missing_tools = False
    runtime = resolve_runtime(tool_runtime)

    for item in checks:
        check_type = str(item.get("type", "command")).strip()
        check_name = str(item.get("id", "")).strip() or "security-check"

        if check_type == "command":
            tool_candidates = [str(v) for v in item.get("tool", [])]
            args = [str(v) for v in item.get("args", [])]

            if runtime == "docker":
                outcome, missing = run_command_check_docker(
                    check_name=check_name,
                    args=args,
                    repo_root=repo_root,
                    allow_missing_tools=allow_missing_tools,
                    dry_run=dry_run,
                )
            else:
                outcome, missing = run_command_check_local(
                    check_name=check_name,
                    tool_candidates=tool_candidates,
                    args=args,
                    repo_root=repo_root,
                    allow_missing_tools=allow_missing_tools,
                    dry_run=dry_run,
                )

            outcomes.append(outcome)
            if missing:
                had_missing_tools = True
            continue

        if check_type == "sast-profile":
            if dry_run:
                outcomes.append(
                    CheckOutcome(
                        check=check_name,
                        status="pass",
                        message="dry-run: проверка SAST профиля",
                    )
                )
                continue
            workflow_patterns = [str(v) for v in item.get("workflow_patterns", [])]
            required_markers = [str(v) for v in item.get("required_markers", [])]
            outcomes.append(
                run_sast_profile_check(
                    check_name=check_name,
                    workflow_patterns=workflow_patterns,
                    required_markers=required_markers,
                    repo_root=repo_root,
                )
            )
            continue

        outcomes.append(
            CheckOutcome(
                check=check_name,
                status="fail",
                message=f"неподдерживаемый тип security-проверки: {check_type}",
            )
        )

    return outcomes, had_missing_tools


def main() -> int:
    args = parse_args()
    repo_root = detect_repo_root(args.repo_root)

    try:
        policy = load_policy(repo_root=repo_root, raw_policy_path=args.policy)
        outcomes, had_missing_tools = run_security_package(
            policy=policy,
            repo_root=repo_root,
            allow_missing_tools=args.allow_missing_tools,
            dry_run=args.dry_run,
            tool_runtime=args.tool_runtime,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        outcome = CheckOutcome(check="security-package", status="fail", message=str(exc))
        print_report([outcome], args.format)
        return 1

    print_report(outcomes, args.format)
    base_exit = summarize_exit_code(outcomes)
    if base_exit != 0:
        return base_exit
    if had_missing_tools and args.allow_missing_tools:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
