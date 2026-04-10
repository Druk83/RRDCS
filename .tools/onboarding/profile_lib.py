#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def default_policy_path(repo_root: Path) -> Path:
    candidates = [
        repo_root / ".manifest" / "policies" / "repository-onboarding-policy.yaml",
        repo_root / ".github" / "policies" / "repository-onboarding-policy.yaml",
        repo_root / ".sources" / ".manifest" / "policies" / "repository-onboarding-policy.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[1]


def resolve_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def load_json_like_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"файл не найден: {path}")
    text = path.read_text(encoding="utf-8-sig")
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"документ должен быть JSON-объектом: {path}")
    return data


def semver_like(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 3:
        return False
    for item in parts:
        if not item.isdigit():
            return False
    return True


def validate_profile_data(
    profile: dict[str, Any],
    policy: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []

    required_fields = policy.get("required_profile_fields", [])
    if not isinstance(required_fields, list):
        errors.append("policy.required_profile_fields должен быть массивом")
        required_fields = []

    for field in required_fields:
        if field not in profile:
            errors.append(f"отсутствует обязательное поле: {field}")

    profile_version = str(profile.get("profile_version", "")).strip()
    if profile_version and not semver_like(profile_version):
        errors.append("profile_version должен быть в формате MAJOR.MINOR.PATCH")

    policy_version = str(profile.get("policy_version", "")).strip()
    if policy_version and not semver_like(policy_version):
        errors.append("policy_version должен быть в формате MAJOR.MINOR.PATCH")

    repository_slug = str(profile.get("repository_slug", "")).strip()
    if repository_slug and "/" not in repository_slug:
        errors.append("repository_slug должен быть в формате 'owner/repository'")

    rollout_channel = str(profile.get("rollout_channel", "")).strip()
    allowed_rollout = policy.get("rollout_channels", [])
    if rollout_channel and rollout_channel not in allowed_rollout:
        errors.append(
            f"rollout_channel должен быть одним из: {', '.join(str(v) for v in allowed_rollout)}"
        )

    enforcement_mode = str(profile.get("enforcement_mode", "")).strip()
    allowed_modes = policy.get("enforcement_modes", [])
    if enforcement_mode and enforcement_mode not in allowed_modes:
        errors.append(
            f"enforcement_mode должен быть одним из: {', '.join(str(v) for v in allowed_modes)}"
        )

    required_checks = profile.get("required_checks", [])
    if not isinstance(required_checks, list) or not required_checks:
        errors.append("required_checks должен быть непустым массивом")

    check_plan_path = str(profile.get("check_plan_path", "")).strip()
    if check_plan_path:
        check_plan_abs = resolve_path(repo_root=repo_root, raw_path=check_plan_path)
        if not check_plan_abs.exists():
            errors.append(f"check_plan_path не существует: {check_plan_path}")

    return errors
