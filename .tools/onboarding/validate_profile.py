#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from profile_lib import (
    default_policy_path,
    load_json_like_yaml,
    repo_root_from_script,
    resolve_path,
    validate_profile_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Проверить профиль интеграции репозитория по onboarding policy.",
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Путь к профилю репозитория (JSON-совместимый YAML).",
    )
    parser.add_argument(
        "--policy",
        default="",
        help="Путь к onboarding policy (по умолчанию автоопределение).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Формат вывода.",
    )
    return parser.parse_args()


def print_text_ok(profile_path: Path, policy_path: Path) -> None:
    print("[PASS] профиль интеграции репозитория валиден")
    print(f"  профиль: {profile_path}")
    print(f"  policy:  {policy_path}")


def print_text_fail(errors: list[str], profile_path: Path, policy_path: Path) -> None:
    print("[FAIL] профиль интеграции репозитория невалиден")
    print(f"  профиль: {profile_path}")
    print(f"  policy:  {policy_path}")
    for item in errors:
        print(f"  - {item}")


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script(Path(__file__))
    profile_path = resolve_path(repo_root=repo_root, raw_path=args.profile)
    policy_path = (
        resolve_path(repo_root=repo_root, raw_path=args.policy)
        if args.policy
        else default_policy_path(repo_root)
    )

    try:
        profile = load_json_like_yaml(profile_path)
        policy = load_json_like_yaml(policy_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        payload = {"status": "fail", "errors": [str(exc)]}
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"[FAIL] ошибка: {exc}")
        return 1

    errors = validate_profile_data(profile=profile, policy=policy, repo_root=repo_root)
    if errors:
        if args.format == "json":
            payload = {
                "status": "fail",
                "profile": str(profile_path),
                "policy": str(policy_path),
                "errors": errors,
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_text_fail(errors=errors, profile_path=profile_path, policy_path=policy_path)
        return 1

    if args.format == "json":
        payload = {
            "status": "pass",
            "profile": str(profile_path),
            "policy": str(policy_path),
            "errors": [],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_ok(profile_path=profile_path, policy_path=policy_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
