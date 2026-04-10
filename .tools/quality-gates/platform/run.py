#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
QUALITY_GATES_DIR = SCRIPT_PATH.parents[1]
if str(QUALITY_GATES_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_GATES_DIR))

from common import CheckOutcome, find_files, print_report, summarize_exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запустить пакет platform quality-gates (runtime + CI кроссплатформенный baseline).",
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


def parse_version(raw: str) -> tuple[int, int]:
    normalized = raw.strip().replace("python", "").strip()
    parts = normalized.split(".")
    if len(parts) < 2:
        raise ValueError(f"Неверный формат версии: {raw}")
    return int(parts[0]), int(parts[1])


def run_python_version_check(check_name: str, min_version_raw: str) -> CheckOutcome:
    min_major, min_minor = parse_version(min_version_raw)
    current = sys.version_info
    if (current.major, current.minor) >= (min_major, min_minor):
        return CheckOutcome(
            check=check_name,
            status="pass",
            message=f"python {current.major}.{current.minor} >= {min_major}.{min_minor}",
        )
    return CheckOutcome(
        check=check_name,
        status="fail",
        message=f"python {current.major}.{current.minor} < {min_major}.{min_minor}",
    )


def run_ci_matrix_check(
    check_name: str,
    repo_root: Path,
    workflow_patterns: list[str],
    required_os_tokens: list[str],
) -> CheckOutcome:
    files = find_files(root=repo_root, patterns=workflow_patterns)
    if not files:
        return CheckOutcome(
            check=check_name,
            status="fail",
            message="не найдены workflow файлы для проверки matrix",
        )

    required = [token.lower() for token in required_os_tokens]
    for file_path in files:
        content = file_path.read_text(encoding="utf-8-sig", errors="replace").lower()
        if "runs-on" not in content and "matrix" not in content:
            continue
        if all(token in content for token in required):
            return CheckOutcome(
                check=check_name,
                status="pass",
                message=f"cross-platform config found in {file_path.relative_to(repo_root)}",
            )

    return CheckOutcome(
        check=check_name,
        status="fail",
        message=f"workflow не покрывает требуемые платформы: {', '.join(required)}",
    )


def run_host_platform_info() -> CheckOutcome:
    system_name = platform.system() or "unknown"
    release = platform.release() or "unknown"
    return CheckOutcome(
        check="host-platform-info",
        status="pass",
        message=f"платформа хоста: {system_name} {release}",
    )


def run_platform_package(policy: dict, repo_root: Path) -> list[CheckOutcome]:
    checks = (
        policy.get("packages", {})
        .get("platform", {})
        .get("checks", [])
    )
    outcomes: list[CheckOutcome] = [run_host_platform_info()]

    for item in checks:
        check_type = str(item.get("type", "")).strip()
        check_name = str(item.get("id", "")).strip() or "platform-check"

        if check_type == "python-version":
            min_version = str(item.get("min", "3.10"))
            outcomes.append(run_python_version_check(check_name, min_version))
            continue

        if check_type == "ci-matrix":
            workflow_patterns = [str(v) for v in item.get("workflow_patterns", [])]
            required_os_tokens = [str(v) for v in item.get("required_os_tokens", [])]
            outcomes.append(
                run_ci_matrix_check(
                    check_name=check_name,
                    repo_root=repo_root,
                    workflow_patterns=workflow_patterns,
                    required_os_tokens=required_os_tokens,
                )
            )
            continue

        outcomes.append(
            CheckOutcome(
                check=check_name,
                status="fail",
                message=f"неподдерживаемый тип platform-проверки: {check_type}",
            )
        )

    return outcomes


def main() -> int:
    args = parse_args()
    repo_root = detect_repo_root(args.repo_root)

    try:
        policy = load_policy(repo_root=repo_root, raw_policy_path=args.policy)
        outcomes = run_platform_package(policy=policy, repo_root=repo_root)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError) as exc:
        outcome = CheckOutcome(
            check="platform-package",
            status="fail",
            message=str(exc),
        )
        print_report([outcome], args.format)
        return 1

    print_report(outcomes, args.format)
    return summarize_exit_code(outcomes)


if __name__ == "__main__":
    sys.exit(main())
