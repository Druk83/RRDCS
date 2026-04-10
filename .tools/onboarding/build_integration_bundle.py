#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from profile_lib import repo_root_from_script, resolve_path


DEFAULT_OUTPUT_DIR = ".out"
DEFAULT_PROFILE_TEMPLATE = ".sources/.manifest/profiles/repository-integration-profile.template.yaml"
DEFAULT_CHECK_PLAN_TEMPLATE = ".tools/check-all/templates/check-plan-repository-profile.json"
DEFAULT_PROFILE_NAME = "repository-integration-profile.generated.yaml"
DEFAULT_CALLER_WORKFLOW_NAME = "rrdcs-repo-gates.yml"
DEFAULT_SAST_WORKFLOW_NAME = "rrdcs-sast-baseline.yml"

DOCKER_REQUIRED_IMAGES: list[str] = [
    "koalaman/shellcheck-alpine:stable",
    "hadolint/hadolint:latest",
    "node:20-alpine",
    "rhysd/actionlint:latest",
    "zricethezav/gitleaks:latest",
]

COPY_ITEMS: list[tuple[str, str]] = [
    (".tools/check-all", ".tools/check-all"),
    (".tools/check-encoding", ".tools/check-encoding"),
    (".tools/quality-gates", ".tools/quality-gates"),
    (".tools/reporting", ".tools/reporting"),
    (".tools/onboarding", ".tools/onboarding"),
    (".tools/registry.json", ".tools/registry.json"),
    (".github/workflows/rrdcs-reusable-gates.yml", ".github/workflows/rrdcs-reusable-gates.yml"),
    (".sources/.manifest/agentcodingmanifest.md", ".manifest/agentcodingmanifest.md"),
    (".sources/.manifest/policies/check-packages.yaml", ".github/policies/check-packages.yaml"),
    (
        ".sources/.manifest/policies/repository-onboarding-policy.yaml",
        ".github/policies/repository-onboarding-policy.yaml",
    ),
    (
        ".sources/.manifest/profiles/repository-integration-profile.template.yaml",
        ".github/profiles/repository-integration-profile.template.yaml",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Собрать out-пакет файлов для внедрения RRDCS в другой репозиторий.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Каталог вывода (по умолчанию: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--profile-template",
        default=DEFAULT_PROFILE_TEMPLATE,
        help=f"Путь к шаблону профиля (по умолчанию: {DEFAULT_PROFILE_TEMPLATE}).",
    )
    parser.add_argument(
        "--check-plan-template",
        default=DEFAULT_CHECK_PLAN_TEMPLATE,
        help=f"Путь к шаблону check-plan (по умолчанию: {DEFAULT_CHECK_PLAN_TEMPLATE}).",
    )
    parser.add_argument(
        "--repository-slug",
        default="owner/repository",
        help="Slug целевого репозитория в формате owner/repository.",
    )
    parser.add_argument(
        "--owner-team",
        default="team-name",
        help="Имя команды-владельца профиля.",
    )
    parser.add_argument(
        "--profile-name",
        default=DEFAULT_PROFILE_NAME,
        help=f"Имя генерируемого профиля (по умолчанию: {DEFAULT_PROFILE_NAME}).",
    )
    parser.add_argument(
        "--caller-workflow-name",
        default=DEFAULT_CALLER_WORKFLOW_NAME,
        help=f"Имя workflow-вызова (по умолчанию: {DEFAULT_CALLER_WORKFLOW_NAME}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Перезаписать output-каталог, если он уже существует.",
    )
    return parser.parse_args()


def copy_item(src_root: Path, dst_root: Path, src_relative: str, dst_relative: str) -> None:
    src = src_root / src_relative
    dst = dst_root / dst_relative
    if not src.exists():
        raise FileNotFoundError(f"Не найден обязательный путь для bundle: {src_relative}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return
    shutil.copy2(src, dst)


def load_json_object(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Ожидался JSON-объект в файле: {path}")
    return data


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str, *, bom: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoding = "utf-8-sig" if bom else "utf-8"
    path.write_text(content, encoding=encoding)


def build_profile(
    profile_template_path: Path,
    target_profile_path: Path,
    repository_slug: str,
    owner_team: str,
) -> None:
    profile = load_json_object(profile_template_path)
    profile["repository_slug"] = repository_slug
    profile["owner_team"] = owner_team
    profile["check_plan_path"] = ".tools/check-all/check-plan.json"
    profile["rollout_channel"] = "pilot"
    profile["enforcement_mode"] = "audit"
    profile["updated_at"] = date.today().isoformat()
    write_json(target_profile_path, profile)


def write_caller_workflow(path: Path, profile_relative_path: str) -> None:
    content = (
        "name: rrdcs-repo-gates\n\n"
        "on:\n"
        "  pull_request:\n"
        "    types: [opened, synchronize, reopened, ready_for_review]\n\n"
        "permissions:\n"
        "  contents: read\n"
        "  pull-requests: read\n\n"
        "jobs:\n"
        "  rrdcs-pr-size:\n"
        "    name: rrdcs-pr-size\n"
        "    runs-on: ubuntu-22.04\n"
        "    timeout-minutes: 10\n"
        "    steps:\n"
        "      - name: Checkout repository\n"
        "        uses: actions/checkout@v4.2.2\n"
        "        with:\n"
        "          fetch-depth: 0\n\n"
        "      - name: Setup Python\n"
        "        uses: actions/setup-python@v5.4.0\n"
        "        with:\n"
        "          python-version: \"3.12.8\"\n\n"
        "      - name: Run PR size policy\n"
        "        shell: bash\n"
        "        run: |\n"
        "          set -euo pipefail\n"
        "          mkdir -p .artifacts/pr-size\n"
        "          python .tools/reporting/build_pr_size_report.py \\\n"
        "            --base \"${{ github.event.pull_request.base.sha || 'HEAD~1' }}\" \\\n"
        "            --head \"${{ github.event.pull_request.head.sha || github.sha }}\" \\\n"
        "            --threshold-lines 100 \\\n"
        "            --mode warning-only \\\n"
        "            --output-json .artifacts/pr-size/pr-size-report.json \\\n"
        "            --output-md .artifacts/pr-size/pr-size-summary.md \\\n"
        "            2>&1 | tee .artifacts/pr-size/pr-size.log\n\n"
        "      - name: Publish PR size summary\n"
        "        if: always()\n"
        "        shell: bash\n"
        "        run: |\n"
        "          {\n"
        "            echo \"## RRDCS PR Size Policy\"\n"
        "            echo \"\"\n"
        "            if [ -f .artifacts/pr-size/pr-size-summary.md ]; then\n"
        "              cat .artifacts/pr-size/pr-size-summary.md\n"
        "            else\n"
        "              echo \"No PR size report generated.\"\n"
        "            fi\n"
        "            echo \"\"\n"
        "            echo \"Policy mode: \\`warning-only\\`\"\n"
        "          } >> \"$GITHUB_STEP_SUMMARY\"\n\n"
        "      - name: Upload PR size evidence\n"
        "        if: always()\n"
        "        uses: actions/upload-artifact@v4.6.2\n"
        "        with:\n"
        "          name: rrdcs-pr-size-evidence\n"
        "          path: .artifacts/pr-size\n"
        "          if-no-files-found: warn\n"
        "          retention-days: 14\n\n"
        "  rrdcs-gates:\n"
        "    uses: ./.github/workflows/rrdcs-reusable-gates.yml\n"
        "    with:\n"
        f"      profile_path: {profile_relative_path}\n"
        "      enforcement_mode: audit\n"
        "      upload_evidence: true\n"
    )
    write_text(path, content)


def write_sast_baseline_workflow(path: Path) -> None:
    content = (
        "name: rrdcs-sast-baseline\n\n"
        "on:\n"
        "  workflow_dispatch:\n\n"
        "permissions:\n"
        "  actions: read\n"
        "  contents: read\n"
        "  security-events: write\n\n"
        "jobs:\n"
        "  codeql:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - name: Initialize CodeQL\n"
        "        uses: github/codeql-action/init@v3\n"
        "        with:\n"
        "          languages: javascript,python\n"
        "      - name: Autobuild\n"
        "        uses: github/codeql-action/autobuild@v3\n"
        "      - name: Analyze\n"
        "        uses: github/codeql-action/analyze@v3\n"
    )
    write_text(path, content)


def write_check_docker_bat(path: Path) -> None:
    content = """@echo off
docker version >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Docker not found. Install Docker Desktop and retry.
  exit /b 1
)
set "DOCKER_OS="
for /f %%i in ('docker info --format "{{.OSType}}" 2^>nul') do set "DOCKER_OS=%%i"
if /I not "%DOCKER_OS%"=="linux" (
  echo [FAIL] Docker is not running Linux engine ^(OSType=%DOCKER_OS%^).
  echo        Switch Docker Desktop to Linux containers.
  exit /b 1
)
echo [PASS] Docker is available and runs in Linux engine.
docker --version
"""
    write_text(path, content)


def write_prepare_docker_images_bat(path: Path) -> None:
    image_lines = "\n".join([f'call :pull "{image}" || exit /b 1' for image in DOCKER_REQUIRED_IMAGES])
    content = f"""@echo off
call "%~dp0check-docker.bat" || exit /b 1
{image_lines}
echo [PASS] RRDCS Docker images are ready.
exit /b 0

:pull
set "IMAGE=%~1"
echo [INFO] pull %IMAGE%
docker pull "%IMAGE%"
if errorlevel 1 (
  echo [FAIL] Failed to pull image: %IMAGE%
  exit /b 1
)
exit /b 0
"""
    write_text(path, content)


def write_run_local_checks_docker_bat(path: Path) -> None:
    content = """@echo off
setlocal
if /I not "%RRDCS_SKIP_DOCKER_PULL%"=="1" (
  call "%~dp0prepare-docker-images.bat" || exit /b 1
)
python .tools\\check-all\\check_all.py --plan .tools\\check-all\\check-plan.json
"""
    write_text(path, content)


def write_output_readme(path: Path, profile_name: str, caller_workflow_name: str) -> None:
    content = (
        "# RRDCS Integration Bundle\n\n"
        "Этот каталог содержит готовый набор файлов для переноса в целевой репозиторий.\n\n"
        "## Состав\n\n"

        "- `.tools/`\n"
        "- `.manifest/`\n"
        "- `.github/workflows/`\n"
        "- `.github/policies/`\n"
        "- `.github/profiles/`\n\n"
        "## Docker-first локальная проверка (Windows)\n\n"

        "1. Убедитесь, что Docker установлен и запущен в Linux engine:\n\n"
        "```bat\n"
        ".tools\\setup\\check-docker.bat\n"
        "```\n\n"
        "1. Подготовьте Docker-образы RRDCS:\n\n"
        "```bat\n"
        ".tools\\setup\\prepare-docker-images.bat\n"
        "```\n\n"
        "1. Запустите локальные проверки:\n\n"
        "```bat\n"
        ".tools\\setup\\run-local-checks-docker.bat\n"
        "```\n\n"
        "## Как применить в целевом репозитории\n\n"

        "1. Скопируйте содержимое этого каталога в корень целевого репозитория.\n"
        "1. Проверьте манифест агента: `.manifest/agentcodingmanifest.md`.\n"
        f"1. Проверьте профиль: `.github/profiles/{profile_name}`.\n"
        "1. Убедитесь, что workflow включен:\n"
        "   - `.github/workflows/rrdcs-repo-gates.yml` включает warning-only policy по размеру PR\n"
        f"   - `.github/workflows/{caller_workflow_name}`\n"
        "   - `.github/workflows/rrdcs-reusable-gates.yml`\n"
        "   - `.github/workflows/rrdcs-sast-baseline.yml`\n"
    )
    write_text(path, content, bom=True)


def cleanup_transient_files(bundle_root: Path) -> None:
    for cache_dir in bundle_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir, ignore_errors=True)
    for pyc_file in bundle_root.rglob("*.pyc"):
        if pyc_file.is_file():
            pyc_file.unlink(missing_ok=True)


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script(Path(__file__))
    output_dir = resolve_path(repo_root=repo_root, raw_path=args.output_dir)

    if output_dir.exists() and not args.force:
        print(f"[FAIL] Каталог уже существует: {output_dir}")
        print("       Используйте --force для перезаписи.")
        return 1

    if output_dir.exists() and args.force:
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        for src_relative, dst_relative in COPY_ITEMS:
            copy_item(
                src_root=repo_root,
                dst_root=output_dir,
                src_relative=src_relative,
                dst_relative=dst_relative,
            )

        check_plan_template = resolve_path(repo_root=repo_root, raw_path=args.check_plan_template)
        target_check_plan = output_dir / ".tools/check-all/check-plan.json"
        shutil.copy2(check_plan_template, target_check_plan)

        profile_template = resolve_path(repo_root=repo_root, raw_path=args.profile_template)
        target_profile = output_dir / f".github/profiles/{args.profile_name}"
        build_profile(
            profile_template_path=profile_template,
            target_profile_path=target_profile,
            repository_slug=args.repository_slug,
            owner_team=args.owner_team,
        )

        caller_workflow = output_dir / f".github/workflows/{args.caller_workflow_name}"
        write_caller_workflow(
            path=caller_workflow,
            profile_relative_path=f".github/profiles/{args.profile_name}",
        )
        write_sast_baseline_workflow(output_dir / f".github/workflows/{DEFAULT_SAST_WORKFLOW_NAME}")

        write_check_docker_bat(output_dir / ".tools/setup/check-docker.bat")
        write_prepare_docker_images_bat(output_dir / ".tools/setup/prepare-docker-images.bat")
        write_run_local_checks_docker_bat(output_dir / ".tools/setup/run-local-checks-docker.bat")
        write_output_readme(
            path=output_dir / ".github/README.md",
            profile_name=args.profile_name,
            caller_workflow_name=args.caller_workflow_name,
        )

        cleanup_transient_files(output_dir)
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[FAIL] Ошибка сборки bundle: {exc}")
        return 1

    print("[PASS] Bundle для интеграции сформирован")
    print(f"  каталог: {output_dir}")
    print("  ключевые файлы:")
    print(f"  - {output_dir / '.github/README.md'}")
    print(f"  - {output_dir / '.tools/setup/check-docker.bat'}")
    print(f"  - {output_dir / '.tools/setup/prepare-docker-images.bat'}")
    print(f"  - {output_dir / '.tools/setup/run-local-checks-docker.bat'}")
    print(f"  - {output_dir / '.tools/check-all/check-plan.json'}")
    print(f"  - {output_dir / f'.github/profiles/{args.profile_name}'}")
    print(f"  - {output_dir / f'.github/workflows/{args.caller_workflow_name}'}")
    print(f"  - {output_dir / f'.github/workflows/{DEFAULT_SAST_WORKFLOW_NAME}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
