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
        description="Экспортировать контекст профиля для CI workflow.",
    )
    parser.add_argument("--profile", required=True, help="Путь к профилю репозитория.")
    parser.add_argument("--policy", default="", help="Путь к onboarding policy.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Формат вывода.",
    )
    parser.add_argument(
        "--github-output",
        default="",
        help="Путь к файлу GitHub output (опционально).",
    )
    return parser.parse_args()


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
        print(f"[FAIL] ошибка: {exc}")
        return 1

    errors = validate_profile_data(profile=profile, policy=policy, repo_root=repo_root)
    if errors:
        print("[FAIL] профиль невалиден")
        for item in errors:
            print(f"  - {item}")
        return 1

    context = {
        "profile_version": str(profile.get("profile_version", "")),
        "policy_version": str(profile.get("policy_version", "")),
        "repository_slug": str(profile.get("repository_slug", "")),
        "check_plan_path": str(profile.get("check_plan_path", "")),
        "rollout_channel": str(profile.get("rollout_channel", "")),
        "enforcement_mode": str(profile.get("enforcement_mode", "")),
    }

    if args.github_output:
        out_path = resolve_path(repo_root=repo_root, raw_path=args.github_output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("a", encoding="utf-8") as handle:
            for key, value in context.items():
                handle.write(f"{key}={value}\n")

    if args.format == "json":
        print(json.dumps(context, ensure_ascii=False, indent=2))
    else:
        for key, value in context.items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
