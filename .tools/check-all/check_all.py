#!/usr/bin/env python3
"""
check_all.py

Кросс-платформенный локальный агрегатор проверок.
Запускает набор checks из JSON-плана и завершает работу:
- 0: все проверки пройдены
- 1: есть падения или ошибка выполнения
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_PLAN = Path(".tools/check-all/check-plan.json")
MIN_PYTHON = (3, 10)


@dataclass
class CheckSpec:
    check_id: str
    title: str
    group: str
    tags: tuple[str, ...]
    required: bool
    success_codes: set[int]
    command: list[str]


@dataclass
class CheckResult:
    spec: CheckSpec
    return_code: int
    duration_sec: float
    ok: bool
    stdout: str
    stderr: str
    error: str | None = None


ERROR_CODES_BY_GROUP = {
    "style": "RRDCS-STYLE-CHECK-FAILED",
    "security": "RRDCS-SECURITY-CHECK-FAILED",
    "platform": "RRDCS-PLATFORM-CHECK-FAILED",
    "governance": "RRDCS-GOVERNANCE-CHECK-FAILED",
    "architecture": "RRDCS-ARCHITECTURE-CHECK-FAILED",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запустить локальные проверки RRDCS из JSON-плана.",
    )
    parser.add_argument(
        "--plan",
        default=str(DEFAULT_PLAN),
        help=f"Путь к JSON-плану проверок (по умолчанию: {DEFAULT_PLAN})",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help=(
            "Селекторы для выборочного запуска (можно повторять). Поддерживаются id, group, tag. "
            "Примеры: --only style ; --only security ; --only style,security"
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать проверки из плана и завершить",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать команды без выполнения",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Остановиться на первом упавшем обязательном check",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Записать машинный JSON-отчет по пути",
    )
    parser.add_argument(
        "--report-md",
        default="",
        help="Записать человекочитаемый markdown-отчет по пути",
    )
    return parser.parse_args()


def load_plan(plan_path: Path) -> list[CheckSpec]:
    if not plan_path.exists():
        raise FileNotFoundError(f"Файл плана не найден: {plan_path}")

    try:
        raw = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Некорректный JSON в плане: {plan_path}: {exc}") from exc

    checks = raw.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("План должен содержать непустой массив 'checks'")

    parsed: list[CheckSpec] = []
    for index, item in enumerate(checks, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Check #{index} должен быть объектом")

        check_id = str(item.get("id", "")).strip()
        title = str(item.get("title", "")).strip()
        group = str(item.get("group", "default")).strip() or "default"
        tags_raw = item.get("tags", [])
        required = bool(item.get("required", True))
        success_codes_raw = item.get("success_codes", [0])
        command_raw = item.get("command", [])

        if not check_id:
            raise ValueError(f"Check #{index}: отсутствует 'id'")
        if not title:
            raise ValueError(f"Check {check_id}: отсутствует 'title'")
        if not isinstance(success_codes_raw, list) or not success_codes_raw:
            raise ValueError(f"Check {check_id}: 'success_codes' должен быть непустым списком")
        if not isinstance(command_raw, list) or not command_raw:
            raise ValueError(f"Check {check_id}: 'command' должен быть непустым списком")
        if not isinstance(tags_raw, list):
            raise ValueError(f"Check {check_id}: 'tags' должен быть массивом")

        success_codes: set[int] = set()
        for code in success_codes_raw:
            if not isinstance(code, int):
                raise ValueError(f"Check {check_id}: код успеха должен быть целым числом")
            success_codes.add(code)

        command = [str(arg) for arg in command_raw]
        tags = tuple(
            sorted({str(tag).strip() for tag in tags_raw if str(tag).strip()})
        )
        parsed.append(
            CheckSpec(
                check_id=check_id,
                title=title,
                group=group,
                tags=tags,
                required=required,
                success_codes=success_codes,
                command=command,
            )
        )
    return parsed


def resolve_command(command: Iterable[str]) -> list[str]:
    resolved: list[str] = []
    for idx, arg in enumerate(command):
        value = os.path.expandvars(arg)
        if idx == 0 and value.lower() in {"python", "python3"}:
            resolved.append(sys.executable)
        else:
            resolved.append(value)
    return resolved


def validate_environment(checks: list[CheckSpec], repo_root: Path) -> list[str]:
    errors: list[str] = []

    if sys.version_info < MIN_PYTHON:
        errors.append(
            f"Требуется Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+; обнаружен {sys.version_info.major}.{sys.version_info.minor}"
        )

    for spec in checks:
        cmd = resolve_command(spec.command)
        executable = cmd[0]

        if os.path.isabs(executable) or executable.startswith("."):
            abs_exec = (repo_root / executable).resolve() if not os.path.isabs(executable) else Path(executable)
            if not abs_exec.exists():
                errors.append(f"[{spec.check_id}] исполняемый файл не найден: {executable}")
        else:
            if shutil.which(executable) is None:
                errors.append(f"[{spec.check_id}] исполняемый файл недоступен в PATH: {executable}")

        if len(cmd) >= 2 and cmd[1].endswith(".py"):
            script = Path(cmd[1])
            script_abs = script if script.is_absolute() else (repo_root / script)
            if not script_abs.exists():
                errors.append(f"[{spec.check_id}] скрипт не найден: {cmd[1]}")

    return errors


def parse_selectors(raw: list[str]) -> set[str]:
    tokens: set[str] = set()
    for part in raw:
        for token in part.split(","):
            normalized = token.strip()
            if normalized:
                tokens.add(normalized)
    return tokens


def filter_checks(checks: list[CheckSpec], selectors: set[str]) -> tuple[list[CheckSpec], set[str]]:
    if not selectors:
        return checks, set()

    selected: list[CheckSpec] = []
    matched: set[str] = set()

    for spec in checks:
        spec_selectors = {spec.check_id, spec.group, *spec.tags}
        if selectors.intersection(spec_selectors):
            selected.append(spec)
            matched.update(selectors.intersection(spec_selectors))

    unknown = selectors - matched
    return selected, unknown


def available_selectors(checks: list[CheckSpec]) -> tuple[list[str], list[str], list[str]]:
    ids = sorted({spec.check_id for spec in checks})
    groups = sorted({spec.group for spec in checks})
    tags = sorted({tag for spec in checks for tag in spec.tags})
    return ids, groups, tags


def run_check(spec: CheckSpec, repo_root: Path, dry_run: bool) -> CheckResult:
    command = resolve_command(spec.command)
    started = time.monotonic()

    if dry_run:
        print(f"[DRY-RUN] {spec.check_id}: {' '.join(command)}")
        return CheckResult(
            spec=spec,
            return_code=0,
            duration_sec=0.0,
            ok=True,
            stdout="",
            stderr="",
        )

    try:
        proc = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        duration = time.monotonic() - started
        ok = proc.returncode in spec.success_codes
        return CheckResult(
            spec=spec,
            return_code=proc.returncode,
            duration_sec=duration,
            ok=ok,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except OSError as exc:
        duration = time.monotonic() - started
        return CheckResult(
            spec=spec,
            return_code=1,
            duration_sec=duration,
            ok=False,
            stdout="",
            stderr="",
            error=str(exc),
        )


def print_result(result: CheckResult) -> None:
    status = "PASS" if result.ok else "FAIL"
    req_flag = "required" if result.spec.required else "optional"
    print(
        f"[{status}] {result.spec.check_id} ({req_flag}) "
        f"rc={result.return_code} time={result.duration_sec:.2f}s"
    )
    if result.error:
        print(f"  ошибка: {result.error}")
    if result.stdout.strip():
        print("  stdout:")
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
    if result.stderr.strip():
        print("  stderr:")
        for line in result.stderr.strip().splitlines():
            print(f"    {line}")


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        candidate = line.strip()
        if candidate:
            return candidate
    return ""


def get_diagnostic_message(result: CheckResult) -> str:
    if result.error:
        return result.error
    stderr_line = first_nonempty_line(result.stderr)
    if stderr_line:
        return stderr_line
    stdout_line = first_nonempty_line(result.stdout)
    if stdout_line:
        return stdout_line
    return "нет диагностического сообщения"


def get_error_code(result: CheckResult) -> str:
    by_group = ERROR_CODES_BY_GROUP.get(result.spec.group)
    if by_group:
        return by_group
    return "RRDCS-CHECK-FAILED"


def build_report_payload(
    results: list[CheckResult],
    plan_path: Path,
    repo_root: Path,
) -> dict[str, Any]:
    total = len(results)
    passed = sum(1 for item in results if item.ok)
    failed_required = [item for item in results if (not item.ok and item.spec.required)]
    failed_optional = [item for item in results if (not item.ok and not item.spec.required)]
    failed_all = [item for item in results if not item.ok]

    checks: list[dict[str, Any]] = []
    for item in results:
        checks.append(
            {
                "id": item.spec.check_id,
                "title": item.spec.title,
                "group": item.spec.group,
                "tags": list(item.spec.tags),
                "required": item.spec.required,
                "status": "pass" if item.ok else "fail",
                "return_code": item.return_code,
                "duration_sec": round(item.duration_sec, 3),
                "error_code": "" if item.ok else get_error_code(item),
                "diagnostic_message": "" if item.ok else get_diagnostic_message(item),
                "source_step": item.spec.check_id,
                "source_command": resolve_command(item.spec.command),
            }
        )

    payload: dict[str, Any] = {
        "report_version": "1.0",
        "plan_path": str(plan_path),
        "repo_root": str(repo_root),
        "summary": {
            "total": total,
            "passed": passed,
            "failed_required": len(failed_required),
            "failed_optional": len(failed_optional),
            "overall_status": "fail" if failed_required else "pass",
        },
        "failed_checks": [item.spec.check_id for item in failed_all],
        "checks": checks,
    }
    return payload


def build_markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines: list[str] = []
    lines.append("## Отчет RRDCS Check")
    lines.append("")
    lines.append(f"- общий статус: `{summary['overall_status']}`")
    lines.append(f"- всего: `{summary['total']}`")
    lines.append(f"- успешно: `{summary['passed']}`")
    lines.append(f"- обязательных ошибок: `{summary['failed_required']}`")
    lines.append(f"- необязательных ошибок: `{summary['failed_optional']}`")
    lines.append("")
    lines.append("| check_id | group | required | status | rc | error_code | diagnostic |")
    lines.append("|---|---|---:|---|---:|---|---|")
    for item in payload["checks"]:
        status_icon = "PASS" if item["status"] == "pass" else "FAIL"
        required = "да" if item["required"] else "нет"
        error_code = item["error_code"] if item["error_code"] else "-"
        diagnostic = item["diagnostic_message"] if item["diagnostic_message"] else "-"
        lines.append(
            f"| `{item['id']}` | `{item['group']}` | {required} | `{status_icon}` | {item['return_code']} | `{error_code}` | {diagnostic} |"
        )
    return "\n".join(lines) + "\n"


def write_report_file(path_value: str, content: str, repo_root: Path) -> None:
    target = Path(path_value)
    if not target.is_absolute():
        target = (repo_root / target).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def summarize(results: list[CheckResult], plan_path: Path, repo_root: Path, report_json: str, report_md: str) -> int:
    payload = build_report_payload(results=results, plan_path=plan_path, repo_root=repo_root)
    summary = payload["summary"]
    failed_required = [item for item in results if (not item.ok and item.spec.required)]
    failed_optional = [item for item in results if (not item.ok and not item.spec.required)]

    print("")
    print("=== Сводка check-all ===")
    print(f"всего: {summary['total']}")
    print(f"успешно: {summary['passed']}")
    print(f"обязательных ошибок: {summary['failed_required']}")
    print(f"необязательных ошибок: {summary['failed_optional']}")

    if failed_required:
        print("упавшие обязательные проверки:")
        for item in failed_required:
            print(f"  - {item.spec.check_id} (rc={item.return_code})")

    if failed_optional:
        print("упавшие необязательные проверки:")
        for item in failed_optional:
            print(f"  - {item.spec.check_id} (rc={item.return_code})")

    if report_json:
        json_content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        write_report_file(path_value=report_json, content=json_content, repo_root=repo_root)
        print(f"отчет_json: {report_json}")

    if report_md:
        md_content = build_markdown_report(payload)
        write_report_file(path_value=report_md, content=md_content, repo_root=repo_root)
        print(f"отчет_md: {report_md}")

    return 1 if failed_required else 0


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = (repo_root / plan_path).resolve()

    try:
        checks = load_plan(plan_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    selectors = parse_selectors(args.only)
    selected, unknown = filter_checks(checks, selectors)
    if not selected:
        print("[ERROR] Не выбраны проверки.")
        ids, groups, tags = available_selectors(checks)
        print(f"  доступные ids: {', '.join(ids)}")
        print(f"  доступные группы: {', '.join(groups)}")
        if tags:
            print(f"  доступные теги: {', '.join(tags)}")
        print("  подсказка: используйте --list для просмотра")
        return 1

    if unknown:
        print("[ERROR] Неизвестные селекторы: " + ", ".join(sorted(unknown)))
        ids, groups, tags = available_selectors(checks)
        print(f"  доступные ids: {', '.join(ids)}")
        print(f"  доступные группы: {', '.join(groups)}")
        if tags:
            print(f"  доступные теги: {', '.join(tags)}")
        return 1

    if args.list:
        print(f"план: {plan_path}")
        for spec in selected:
            req = "обязательный" if spec.required else "необязательный"
            tags = f" tags={','.join(spec.tags)}" if spec.tags else ""
            print(f"- {spec.check_id} [{spec.group}] ({req}){tags} :: {spec.title}")
        return 0

    env_errors = validate_environment(selected, repo_root)
    if env_errors:
        print("[ERROR] Проверка окружения завершилась ошибкой:")
        for err in env_errors:
            print(f"  - {err}")
        return 1

    print(f"Запуск {len(selected)} проверок из {plan_path}")
    print(f"Корень репозитория: {repo_root}")

    results: list[CheckResult] = []
    for spec in selected:
        print("")
        print(f"--- {spec.check_id}: {spec.title} ---")
        result = run_check(spec, repo_root=repo_root, dry_run=args.dry_run)
        print_result(result)
        results.append(result)

        if args.fail_fast and (not result.ok) and spec.required:
            print("Fail-fast: остановка после упавшего обязательного check.")
            break

    return summarize(
        results=results,
        plan_path=plan_path,
        repo_root=repo_root,
        report_json=args.report_json,
        report_md=args.report_md,
    )


if __name__ == "__main__":
    sys.exit(main())
