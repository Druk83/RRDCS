#!/usr/bin/env python3
"""
Минимальная security-проверка для MVP.
Проверяет, что в .gitignore есть правило игнорирования .env-файлов.
"""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
GITIGNORE_PATH = REPO_ROOT / ".gitignore"
ALLOWED_ENV_PATTERNS = {
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "*/.env",
    "*/.env.*",
}


def normalize_rule(line: str) -> str:
    return line.strip().lstrip("/")


def active_rules(content: str) -> list[str]:
    rules: list[str] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            continue
        rules.append(normalize_rule(line))
    return rules


def has_env_ignore_rule(rules: list[str]) -> bool:
    for rule in rules:
        if rule in ALLOWED_ENV_PATTERNS:
            return True
        if rule.startswith(".env"):
            return True
    return False


def main() -> int:
    if not GITIGNORE_PATH.exists():
        print("[FAIL] файл .gitignore не найден")
        return 1

    content = GITIGNORE_PATH.read_text(encoding="utf-8-sig")
    rules = active_rules(content)

    if not has_env_ignore_rule(rules):
        print("[FAIL] для security baseline .gitignore должен игнорировать .env файлы")
        print("       добавьте одно из правил: .env, .env.*, **/.env")
        return 1

    print("[PASS] baseline security: политика игнорирования .env настроена")
    return 0


if __name__ == "__main__":
    sys.exit(main())
