#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CheckOutcome:
    check: str
    status: str
    message: str
    command: list[str] | None = None
    return_code: int | None = None
    duration_sec: float = 0.0


def command_exists(binary: str) -> bool:
    return shutil.which(binary) is not None


def run_command(
    command: list[str],
    cwd: Path,
    timeout_sec: int = 300,
) -> tuple[int, str, str]:
    def decode_output(raw: bytes | None) -> str:
        if raw is None:
            return ""
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("cp1251", errors="replace")

    proc = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=False,
        check=False,
        timeout=timeout_sec,
    )
    stdout = decode_output(proc.stdout)
    stderr = decode_output(proc.stderr)
    return proc.returncode, stdout, stderr


def excluded_path(path: Path) -> bool:
    excluded = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".mypy_cache",
        "dist",
        "build",
    }
    return any(part in excluded for part in path.parts)


def find_files(root: Path, patterns: list[str]) -> list[Path]:
    result: list[Path] = []
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file() and not excluded_path(path):
                result.append(path)
    unique_sorted = sorted({item.resolve() for item in result})
    return unique_sorted


def chunked(items: list[Path], chunk_size: int) -> list[list[Path]]:
    if chunk_size <= 0:
        return [items]
    chunks: list[list[Path]] = []
    for idx in range(0, len(items), chunk_size):
        chunks.append(items[idx : idx + chunk_size])
    return chunks


def summarize_exit_code(outcomes: list[CheckOutcome]) -> int:
    has_fail = any(item.status == "fail" for item in outcomes)
    return 1 if has_fail else 0


def print_report(outcomes: list[CheckOutcome], fmt: str) -> None:
    summary = {
        "total": len(outcomes),
        "passed": sum(1 for item in outcomes if item.status == "pass"),
        "failed": sum(1 for item in outcomes if item.status == "fail"),
        "skipped": sum(1 for item in outcomes if item.status == "skipped"),
    }

    if fmt == "json":
        payload = {
            "summary": summary,
            "checks": [asdict(item) for item in outcomes],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("=== отчет quality-gate ===")
    print(f"всего: {summary['total']}")
    print(f"успешно: {summary['passed']}")
    print(f"ошибок: {summary['failed']}")
    print(f"пропущено: {summary['skipped']}")
    for item in outcomes:
        prefix = item.status.upper()
        print(f"[{prefix}] {item.check}: {item.message}")


def tool_missing_outcome(
    check_name: str,
    tool_name: str,
    allow_missing_tools: bool,
) -> CheckOutcome:
    if allow_missing_tools:
        return CheckOutcome(
            check=check_name,
            status="skipped",
            message=f"инструмент '{tool_name}' не установлен",
        )
    return CheckOutcome(
        check=check_name,
        status="fail",
        message=f"обязательный инструмент '{tool_name}' не установлен",
    )


def run_single_command_check(
    check_name: str,
    command: list[str],
    cwd: Path,
    timeout_sec: int = 300,
) -> CheckOutcome:
    started = time.monotonic()
    try:
        rc, stdout, stderr = run_command(command=command, cwd=cwd, timeout_sec=timeout_sec)
    except Exception as exc:
        return CheckOutcome(
            check=check_name,
            status="fail",
            message=str(exc),
            command=command,
            return_code=1,
            duration_sec=time.monotonic() - started,
        )

    if rc == 0:
        return CheckOutcome(
            check=check_name,
            status="pass",
            message="ok",
            command=command,
            return_code=0,
            duration_sec=time.monotonic() - started,
        )

    stderr_text = (stderr or "").strip()
    stdout_text = (stdout or "").strip()
    details = stderr_text if stderr_text else stdout_text
    short = details.splitlines()[0] if details else "команда завершилась с ошибкой"
    return CheckOutcome(
        check=check_name,
        status="fail",
        message=short,
        command=command,
        return_code=rc,
        duration_sec=time.monotonic() - started,
    )
