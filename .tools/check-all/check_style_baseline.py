#!/usr/bin/env python3
"""
Минимальная style-проверка для tooling-репозитория.
Проверяет синтаксическую корректность Python-скриптов check-all.
"""

from __future__ import annotations

from pathlib import Path
import py_compile
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_FILES = [
    REPO_ROOT / ".tools" / "check-all" / "check_all.py",
    REPO_ROOT / ".tools" / "check-all" / "check_governance_baseline.py",
    REPO_ROOT / ".tools" / "check-all" / "check_security_baseline.py",
    REPO_ROOT / ".tools" / "check-all" / "check_style_baseline.py",
    REPO_ROOT / ".tools" / "check-encoding" / "check_encoding.py",
    REPO_ROOT / ".tools" / "onboarding" / "profile_lib.py",
    REPO_ROOT / ".tools" / "onboarding" / "validate_profile.py",
    REPO_ROOT / ".tools" / "onboarding" / "export_profile_context.py",
    REPO_ROOT / ".tools" / "onboarding" / "promote_profile.py",
    REPO_ROOT / ".tools" / "onboarding" / "build_integration_bundle.py",
    REPO_ROOT / ".tools" / "quality-gates" / "architecture" / "run.py",
    REPO_ROOT / ".tools" / "reporting" / "build_gate_report.py",
    REPO_ROOT / ".tools" / "reporting" / "build_pr_size_report.py",
]


def main() -> int:
    failed: list[str] = []

    for path in TARGET_FILES:
        if not path.exists():
            failed.append(f"{path}: файл не найден")
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failed.append(f"{path}: {exc.msg}")

    if failed:
        print("[FAIL] baseline style: обнаружены синтаксические ошибки Python")
        for item in failed:
            print(f"  - {item}")
        return 1

    print("[PASS] baseline style: синтаксис Python корректен")
    return 0


if __name__ == "__main__":
    sys.exit(main())
