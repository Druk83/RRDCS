#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


STDLIB_MODULES = set(getattr(sys, "stdlib_module_names", set()))
STDLIB_MODULES.update({"__future__"})

LAYER_ALLOWED_INTERNAL_IMPORTS: dict[str, set[str]] = {
    "check-all": set(),
    "check-encoding": set(),
    "quality-gates": {"common"},
    "onboarding": {"profile_lib"},
    "reporting": set(),
    "pdd": set(),
    "plantuml-render": set(),
}


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    imported: str
    rule: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверить границы модулей .tools через анализ внутренних импортов.",
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Путь к корню репозитория (по умолчанию автоопределение).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Формат вывода.",
    )
    return parser.parse_args()


def detect_repo_root(raw_value: str) -> Path:
    if raw_value.strip():
        return Path(raw_value).resolve()
    return Path(__file__).resolve().parents[3]


def iter_python_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.py")
        if path.is_file() and "__pycache__" not in path.parts
    )


def parse_import_roots(path: Path) -> tuple[list[tuple[str, int]], list[str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return [], [f"{path}: не удалось разобрать Python: {exc}"]

    imports: list[tuple[str, int]] = []
    errors: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0].strip()
                if root:
                    imports.append((root, getattr(node, "lineno", 1)))
            continue

        if isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                errors.append(
                    f"{path}:{getattr(node, 'lineno', 1)}: relative import is not allowed"
                )
                continue
            if not node.module:
                continue
            root = node.module.split(".", 1)[0].strip()
            if root:
                imports.append((root, getattr(node, "lineno", 1)))

    return imports, errors


def detect_internal_modules(files: list[Path]) -> set[str]:
    discovered: set[str] = set()
    for path in files:
        imports, _ = parse_import_roots(path)
        for root, _ in imports:
            if root not in STDLIB_MODULES:
                discovered.add(root)
    return discovered


def classify_area(path: Path, repo_root: Path) -> str:
    rel = path.relative_to(repo_root / ".tools")
    if not rel.parts:
        return "unknown"
    return rel.parts[0]


def build_violations(files: list[Path], repo_root: Path) -> tuple[list[Violation], list[str]]:
    internal_modules = detect_internal_modules(files)
    violations: list[Violation] = []
    parse_errors: list[str] = []

    for path in files:
        area = classify_area(path, repo_root)
        allowed = LAYER_ALLOWED_INTERNAL_IMPORTS.get(area, set())
        imports, errors = parse_import_roots(path)
        parse_errors.extend(errors)

        for imported, line in imports:
            if imported in STDLIB_MODULES:
                continue
            if imported not in internal_modules:
                continue
            if imported in allowed:
                continue
            violations.append(
                Violation(
                    path=path,
                    line=line,
                    imported=imported,
                    rule=f"area:{area}",
                    message=(
                        f"internal import '{imported}' is not allowed for area '{area}'"
                    ),
                )
            )

    return violations, parse_errors


def format_violations_text(violations: list[Violation], parse_errors: list[str]) -> None:
    if parse_errors:
        print("[FAIL] architecture guard: parse errors detected")
        for item in parse_errors:
            print(f"  - {item}")
    if violations:
        print("[FAIL] architecture guard: module boundary violations detected")
        for item in violations:
            rel = item.path.as_posix()
            print(f"  - {rel}:{item.line}: {item.message}")
    if not violations and not parse_errors:
        print("[PASS] architecture guard: internal imports follow module boundaries")


def build_payload(violations: list[Violation], parse_errors: list[str], repo_root: Path) -> dict:
    return {
        "report_version": "1.0",
        "repo_root": str(repo_root),
        "status": "fail" if violations or parse_errors else "pass",
        "parse_errors": parse_errors,
        "violations": [
            {
                "path": str(item.path),
                "line": item.line,
                "imported": item.imported,
                "rule": item.rule,
                "message": item.message,
            }
            for item in violations
        ],
    }


def main() -> int:
    args = parse_args()
    repo_root = detect_repo_root(args.repo_root)
    tools_root = repo_root / ".tools"

    if not tools_root.exists():
        print(f"[FAIL] architecture guard: .tools not found at {tools_root}")
        return 1

    files = iter_python_files(tools_root)
    violations, parse_errors = build_violations(files=files, repo_root=repo_root)

    if args.format == "json":
        print(
            json.dumps(
                build_payload(violations=violations, parse_errors=parse_errors, repo_root=repo_root),
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        format_violations_text(violations=violations, parse_errors=parse_errors)

    if violations or parse_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
