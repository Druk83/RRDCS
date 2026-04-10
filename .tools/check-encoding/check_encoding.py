#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EXCLUDED_PARTS = {
    ".git",
    ".out",
    "out",
    "target",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
}

PATTERNS = [
    re.compile(r"\uFFFD"),
    re.compile(r"[\u0403\u0409\u040A\u040B\u040E\u040F\u0453\u0459\u045A\u045B\u045E\u045F]"),
    re.compile(r"(\u0420[\u0410-\u044F\u0401\u0451]){3,}"),
    re.compile(r"(\u0421[\u0410-\u044F\u0401\u0451]){3,}"),
    re.compile(r"(\u0420[\u0410-\u044F\u0401\u0451]\u0421[\u0410-\u044F\u0401\u0451]){2,}"),
    re.compile(r"([\u00D0\u00D1])[A-Za-z]{2,}"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверка файлов на подозрительные артефакты кодировки (mojibake).",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["."],
        help="Файлы или каталоги для сканирования (по умолчанию: .)",
    )
    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=1024,
        help="Пропускать файлы больше этого размера в КБ (по умолчанию: 1024).",
    )
    return parser.parse_args()


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def iter_files(paths: list[str], repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for raw in paths:
        target = Path(raw)
        if not target.is_absolute():
            target = (repo_root / target).resolve()
        if not target.exists():
            continue
        if target.is_file():
            if not is_excluded(target):
                result.append(target)
            continue
        for item in target.rglob("*"):
            if item.is_file() and not is_excluded(item):
                result.append(item)
    unique_sorted = sorted({item for item in result})
    return unique_sorted


def read_text_lines(path: Path, max_size_bytes: int) -> list[str] | None:
    try:
        if path.stat().st_size > max_size_bytes:
            return None
    except OSError:
        return None

    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None
    return text.splitlines()


def find_suspicious(lines: list[str]) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for idx, line in enumerate(lines, start=1):
        for pattern in PATTERNS:
            if pattern.search(line):
                findings.append((idx, line))
                break
    return findings


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    files = iter_files(paths=args.paths, repo_root=repo_root)
    max_size_bytes = args.max_file_size_kb * 1024

    issues: list[tuple[Path, int, str]] = []
    for file_path in files:
        lines = read_text_lines(path=file_path, max_size_bytes=max_size_bytes)
        if lines is None:
            continue
        findings = find_suspicious(lines)
        for lineno, line in findings:
            issues.append((file_path, lineno, line))

    if not issues:
        print("OK: подозрительных артефактов кодировки не найдено.")
        return 0

    print("Проверка кодировки завершилась с ошибкой. Найдены подозрительные строки:")
    for path, lineno, line in issues:
        rel = path.relative_to(repo_root) if path.is_absolute() else path
        print(f"{rel}:{lineno}: {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
