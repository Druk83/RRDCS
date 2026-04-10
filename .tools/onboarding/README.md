# onboarding — инструменты профиля интеграции репозитория

Набор утилит для сценария `audit -> required` без изменения ядра `.tools/*`.
Формат профиля и политики: JSON-совместимый YAML (`.yaml` с JSON-содержимым).

## Первый шаг: собрать `.out/`

Если нужен пакет для интеграции в другой репозиторий, сначала собери `out`-пакет:

```bash
# Windows (короткая команда)
.tools\onboarding\build-bundle.bat --repository-slug owner/repository --owner-team team-name

# Linux/macOS (короткая команда)
bash .tools/onboarding/build-bundle --repository-slug owner/repository --owner-team team-name
```

После выполнения в `.out/` будет готовый набор:
- `.tools/`
- `.github/workflows/`
- `.github/policies/`
- `.github/profiles/`
- `.out/.github/README.md` — инструкция переноса и запуска.
- `.out/.tools/setup/check-docker.bat` — проверка доступности Docker.
- `.out/.tools/setup/prepare-docker-images.bat` — загрузка Docker-образов для всех обязательных проверок.
- `.out/.tools/setup/run-local-checks-docker.bat` — запуск локальных проверок через Docker.
- `.out/.github/workflows/rrdcs-sast-baseline.yml` — базовый SAST workflow (CodeQL marker для security-gates).
- Служебный файл `bundle-manifest.json` не создается.

## Быстрый старт

Эта последовательность дает три вещи:
- проверяет, что профиль интеграции валиден и не содержит ошибок;
- подготавливает контекст профиля для GitHub Actions и reusable workflow;
- позволяет сначала посмотреть эффект перевода `audit -> required`, а затем применить его только с явным `--write`.

```bash
# Валидация профиля
python .tools/onboarding/validate_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml

# Экспорт контекста профиля для CI
python .tools/onboarding/export_profile_context.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml

# Preview promotion audit -> required
python .tools/onboarding/promote_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml \
  --approved-by "tech-lead" 

# Применение promotion
python .tools/onboarding/promote_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml \
  --approved-by "tech-lead" \
  --write
```

## Опции
* `validate_profile.py --format <text|json>` — формат вывода результата валидации.
* `export_profile_context.py --github-output <path>` — запись key=value в файл output GitHub Actions.
* `promote_profile.py --write` — обязательный флаг для изменения файла профиля.

## Входы / Выходы
* Input: профиль `.sources/.manifest/profiles/*.yaml`, policy `.sources/.manifest/policies/repository-onboarding-policy.yaml`.
* Output: валидация профиля (pass/fail).
* Output: экспорт контекста (`check_plan_path`, `enforcement_mode`, `rollout_channel`, `version`).
* Output: promotion preview/apply.

## Ссылки
* `.tools/README.md`
* `docs/requirements/сценарии/policy-and-toolchain-governance/repository-onboarding-runbook.md`

