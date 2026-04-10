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
    chunked,
    command_exists,
    find_files,
    print_report,
    run_command,
    summarize_exit_code,
    tool_missing_outcome,
)


DOCKER_STYLE_SPECS: dict[str, dict] = {
    "shellcheck": {
        "image": "koalaman/shellcheck-alpine:stable",
        "command": ["shellcheck"],
    },
    "hadolint": {
        "image": "hadolint/hadolint:latest",
        "command": ["hadolint"],
    },
    "markdownlint": {
        "image": "node:20-alpine",
        "command": ["sh", "-lc", "npx -y markdownlint-cli2@0.22.0 \"$@\"", "--"],
    },
    "actionlint": {
        "image": "rhysd/actionlint:latest",
        "command": [],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запустить пакет style quality-gates (ShellCheck, Hadolint, markdownlint, actionlint).",
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


def select_tool(candidates: list[str]) -> str | None:
    for item in candidates:
        if command_exists(item):
            return item
    return None


def resolve_runtime(mode: str) -> str:
    if mode == "auto":
        return "docker" if command_exists("docker") else "local"
    return mode


def to_rel_files(files: list[Path], repo_root: Path) -> list[str]:
    return [str(path.relative_to(repo_root)).replace("\\", "/") for path in files]


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


def check_with_files_local(
    check_name: str,
    tool_name: str,
    args: list[str],
    files: list[Path],
    repo_root: Path,
    chunk_size: int,
    dry_run: bool,
) -> CheckOutcome:
    if dry_run:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message=f"dry-run(local): {tool_name} на {len(files)} файлах",
            command=[tool_name, *args],
            return_code=0,
        )

    for batch in chunked(files, chunk_size):
        command = [tool_name, *args, *[str(path) for path in batch]]
        rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=600)
        if rc != 0:
            stderr_text = (stderr or "").strip()
            stdout_text = (stdout or "").strip()
            details = stderr_text if stderr_text else stdout_text
            message = details.splitlines()[0] if details else "команда завершилась с ошибкой"
            return CheckOutcome(
                check=check_name,
                status="fail",
                message=message,
                command=command,
                return_code=rc,
            )

    return CheckOutcome(
        check=check_name,
        status="pass",
        message=f"ok ({len(files)} файлов)",
        command=[tool_name, *args],
        return_code=0,
    )


def check_with_files_docker(
    check_name: str,
    image: str,
    tool_cmd: list[str],
    args: list[str],
    files: list[Path],
    repo_root: Path,
    chunk_size: int,
    dry_run: bool,
) -> CheckOutcome:
    rel_files = to_rel_files(files=files, repo_root=repo_root)
    if dry_run:
        command = docker_base_command(repo_root=repo_root, image=image) + tool_cmd + args + rel_files[:1]
        return CheckOutcome(
            check=check_name,
            status="pass",
            message=f"dry-run(docker): {image} на {len(files)} файлах",
            command=command,
            return_code=0,
        )

    for batch in chunked(rel_files, chunk_size):
        command = docker_base_command(repo_root=repo_root, image=image) + tool_cmd + args + batch
        rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=1200)
        if rc != 0:
            stderr_text = (stderr or "").strip()
            stdout_text = (stdout or "").strip()
            details = stderr_text if stderr_text else stdout_text
            message = details.splitlines()[0] if details else "docker-команда завершилась с ошибкой"
            return CheckOutcome(
                check=check_name,
                status="fail",
                message=message,
                command=command,
                return_code=rc,
            )

    return CheckOutcome(
        check=check_name,
        status="pass",
        message=f"ok ({len(files)} файлов, docker)",
        command=docker_base_command(repo_root=repo_root, image=image) + tool_cmd + args,
        return_code=0,
    )


def check_without_files_local(
    check_name: str,
    tool_name: str,
    args: list[str],
    repo_root: Path,
    dry_run: bool,
) -> CheckOutcome:
    command = [tool_name, *args]
    if dry_run:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message=f"dry-run(local): {' '.join(command)}",
            command=command,
            return_code=0,
        )
    rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=600)
    if rc == 0:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message="ok",
            command=command,
            return_code=0,
        )
    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()
    details = stderr_text if stderr_text else stdout_text
    message = details.splitlines()[0] if details else "команда завершилась с ошибкой"
    return CheckOutcome(
        check=check_name,
        status="fail",
        message=message,
        command=command,
        return_code=rc,
    )


def check_without_files_docker(
    check_name: str,
    image: str,
    tool_cmd: list[str],
    args: list[str],
    repo_root: Path,
    dry_run: bool,
) -> CheckOutcome:
    command = docker_base_command(repo_root=repo_root, image=image) + tool_cmd + args
    if dry_run:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message=f"dry-run(docker): {' '.join(command)}",
            command=command,
            return_code=0,
        )
    rc, stdout, stderr = run_command(command=command, cwd=repo_root, timeout_sec=1200)
    if rc == 0:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message="ok (docker)",
            command=command,
            return_code=0,
        )
    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()
    details = stderr_text if stderr_text else stdout_text
    message = details.splitlines()[0] if details else "docker-команда завершилась с ошибкой"
    return CheckOutcome(
        check=check_name,
        status="fail",
        message=message,
        command=command,
        return_code=rc,
    )


def run_style_package(
    policy: dict,
    repo_root: Path,
    allow_missing_tools: bool,
    dry_run: bool,
    tool_runtime: str,
) -> tuple[list[CheckOutcome], bool]:
    checks = policy.get("packages", {}).get("style", {}).get("checks", [])
    outcomes: list[CheckOutcome] = []
    had_missing_tools = False

    runtime = resolve_runtime(tool_runtime)

    for item in checks:
        check_name = str(item.get("id", "")).strip() or "style-check"
        tool_candidates = [str(v) for v in item.get("tool", [])]
        args = [str(v) for v in item.get("args", [])]
        file_patterns = [str(v) for v in item.get("file_patterns", [])]
        chunk_size = int(item.get("chunk_size", 50))
        pass_files = bool(item.get("pass_files", True))

        if runtime == "docker":
            if not command_exists("docker"):
                outcomes.append(
                    tool_missing_outcome(
                        check_name=check_name,
                        tool_name="docker",
                        allow_missing_tools=allow_missing_tools,
                    )
                )
                had_missing_tools = True
                continue

            docker_spec = DOCKER_STYLE_SPECS.get(check_name)
            if not docker_spec:
                outcomes.append(
                    CheckOutcome(
                        check=check_name,
                        status="fail",
                        message=f"для docker-режима не настроен check '{check_name}'",
                    )
                )
                continue

            if not pass_files:
                if file_patterns:
                    files = find_files(root=repo_root, patterns=file_patterns)
                    if not files:
                        outcomes.append(
                            CheckOutcome(check=check_name, status="skipped", message="нет файлов по шаблону")
                        )
                        continue

                outcomes.append(
                    check_without_files_docker(
                        check_name=check_name,
                        image=str(docker_spec["image"]),
                        tool_cmd=[str(v) for v in docker_spec.get("command", [])],
                        args=args,
                        repo_root=repo_root,
                        dry_run=dry_run,
                    )
                )
                continue

            files = find_files(root=repo_root, patterns=file_patterns)
            if not files:
                outcomes.append(CheckOutcome(check=check_name, status="skipped", message="нет файлов по шаблону"))
                continue

            outcomes.append(
                check_with_files_docker(
                    check_name=check_name,
                    image=str(docker_spec["image"]),
                    tool_cmd=[str(v) for v in docker_spec.get("command", [])],
                    args=args,
                    files=files,
                    repo_root=repo_root,
                    chunk_size=chunk_size,
                    dry_run=dry_run,
                )
            )
            continue

        selected_tool = select_tool(tool_candidates)
        if selected_tool is None:
            outcomes.append(
                tool_missing_outcome(
                    check_name=check_name,
                    tool_name="/".join(tool_candidates) if tool_candidates else "unknown",
                    allow_missing_tools=allow_missing_tools,
                )
            )
            had_missing_tools = True
            continue

        if not pass_files:
            if file_patterns:
                files = find_files(root=repo_root, patterns=file_patterns)
                if not files:
                    outcomes.append(CheckOutcome(check=check_name, status="skipped", message="нет файлов по шаблону"))
                    continue
            outcomes.append(
                check_without_files_local(
                    check_name=check_name,
                    tool_name=selected_tool,
                    args=args,
                    repo_root=repo_root,
                    dry_run=dry_run,
                )
            )
            continue

        files = find_files(root=repo_root, patterns=file_patterns)
        if not files:
            outcomes.append(CheckOutcome(check=check_name, status="skipped", message="нет файлов по шаблону"))
            continue

        outcomes.append(
            check_with_files_local(
                check_name=check_name,
                tool_name=selected_tool,
                args=args,
                files=files,
                repo_root=repo_root,
                chunk_size=chunk_size,
                dry_run=dry_run,
            )
        )

    return outcomes, had_missing_tools


def main() -> int:
    args = parse_args()
    repo_root = detect_repo_root(args.repo_root)

    try:
        policy = load_policy(repo_root=repo_root, raw_policy_path=args.policy)
        outcomes, had_missing_tools = run_style_package(
            policy=policy,
            repo_root=repo_root,
            allow_missing_tools=args.allow_missing_tools,
            dry_run=args.dry_run,
            tool_runtime=args.tool_runtime,
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        outcome = CheckOutcome(check="style-package", status="fail", message=str(exc))
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
