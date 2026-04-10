#!/usr/bin/env python3
"""
Минимальная governance-проверка для MVP.
Проверяет наличие ключевых файлов самого инструмента check-all.
"""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = [
    ".tools/check-all/check_all.py",
    ".tools/check-all/check-plan.json",
    ".tools/check-all/check-all",
    ".tools/check-all/check-all.bat",
    ".tools/check-encoding/check_encoding.py",
    ".tools/check-encoding/check-encoding.ps1",
    ".tools/check-encoding/check-encoding.bat",
    ".tools/onboarding/validate_profile.py",
    ".tools/onboarding/export_profile_context.py",
    ".tools/onboarding/promote_profile.py",
    ".tools/onboarding/build_integration_bundle.py",
    ".tools/quality-gates/architecture/run.py",
    ".sources/.manifest/policies/repository-onboarding-policy.yaml",
    ".sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml",
    ".tools/reporting/build_gate_report.py",
    ".tools/reporting/build_pr_size_report.py",
    ".github/workflows/rrdcs-pr-gates.yml",
    ".github/workflows/rrdcs-reusable-gates.yml",
    ".tools/registry.json",
]


def main() -> int:
    missing: list[str] = []

    for rel_path in REQUIRED_FILES:
        abs_path = REPO_ROOT / rel_path
        if not abs_path.exists():
            missing.append(rel_path)

    if missing:
        print("[FAIL] baseline governance: отсутствуют обязательные файлы")
        for item in missing:
            print(f"  - {item}")
        return 1

    print("[PASS] baseline governance: обязательные файлы присутствуют")
    return 0


if __name__ == "__main__":
    sys.exit(main())
