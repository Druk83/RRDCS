#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from profile_lib import (
    default_policy_path,
    load_json_like_yaml,
    repo_root_from_script,
    resolve_path,
    validate_profile_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Перевести режим профиля репозитория (audit -> required).",
    )
    parser.add_argument("--profile", required=True, help="Путь к профилю репозитория.")
    parser.add_argument("--policy", default="", help="Путь к onboarding policy.")
    parser.add_argument(
        "--to",
        choices=("required",),
        default="required",
        help="Целевой режим enforcement.",
    )
    parser.add_argument(
        "--approved-by",
        default="",
        help="Идентификатор согласующего в metadata promotion.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Применить изменения в файле профиля. Без флага только preview.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Формат вывода.",
    )
    return parser.parse_args()


def bump_patch(raw_version: str) -> str:
    parts = raw_version.split(".")
    if len(parts) != 3 or not all(item.isdigit() for item in parts):
        return raw_version
    major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    return f"{major}.{minor}.{patch + 1}"


def build_result_payload(status: str, message: str, preview: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": status,
        "message": message,
        "preview": preview,
    }


def write_profile(path: Path, profile: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    path.write_text(content, encoding="utf-8")


def print_payload(payload: dict[str, Any], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"[{payload['status'].upper()}] {payload['message']}")
    for key, value in payload["preview"].items():
        print(f"  {key}: {value}")


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

    current_mode = str(profile.get("enforcement_mode", "")).strip()
    if current_mode == args.to:
        payload = build_result_payload(
            status="warning",
            message=f"профиль уже в режиме '{args.to}'",
            preview={"enforcement_mode": current_mode},
        )
        print_payload(payload, args.format)
        return 2

    if current_mode != "audit" or args.to != "required":
        print("[FAIL] разрешен только переход 'audit -> required'")
        return 1

    updated = dict(profile)
    updated["enforcement_mode"] = args.to
    updated["profile_version"] = bump_patch(str(profile.get("profile_version", "1.0.0")))
    updated["updated_at"] = date.today().isoformat()
    updated["promotion_approved_by"] = args.approved_by if args.approved_by else "not-set"

    preview = {
        "profile_path": str(profile_path),
        "from_mode": current_mode,
        "to_mode": args.to,
        "profile_version_before": str(profile.get("profile_version", "")),
        "profile_version_after": str(updated.get("profile_version", "")),
        "rollout_channel": str(updated.get("rollout_channel", "")),
    }

    if not args.write:
        payload = build_result_payload(
            status="warning",
            message="dry-run preview; используйте --write для применения",
            preview=preview,
        )
        print_payload(payload, args.format)
        return 2

    write_profile(profile_path, updated)
    payload = build_result_payload(
        status="pass",
        message="профиль переведен в режим required",
        preview=preview,
    )
    print_payload(payload, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
