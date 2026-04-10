# Раздел .tools

В каталоге `.tools/` хранятся утилиты и скрипты, поддерживающие разработку и автоматизацию проекта (маленькие инструменты, которые не являются частью core-сервиса).

## Структура
```text
.tools/
  README.md
  registry.json
  check-all/
    README.md
    check_all.py
    check-plan.json
    check-all         # bash wrapper
    check-all.bat     # Windows wrapper
  check-encoding/
    README.md
    check_encoding.py
    check-encoding
    check-encoding.ps1
    check-encoding.bat
  quality-gates/
    common.py
    style/
      run.py
    security/
      run.py
    platform/
      run.py
  reporting/
    build_gate_report.py
  onboarding/
    README.md
    profile_lib.py
    validate_profile.py
    export_profile_context.py
    promote_profile.py
  pdd/
    README.md
    pdd_scan.py
    pdd-scan         # bash wrapper
    pdd-scan.bat     # Windows wrapper
  plantuml-render/
    README.md
    plantuml_render.py
    plantuml-render      # bash wrapper
    plantuml-render.bat  # Windows wrapper
```

## Инструменты

* **check-all** — локальный агрегатор pre-check набора RRDCS (JSON-план, единый exit contract) → см. `.tools/check-all/README.md` (stable)
* **check-encoding** — проверка репозитория на артефакты поврежденной кодировки (mojibake) → `.tools/check-encoding/check_encoding.py`
* **quality-gate-style** — пакет style-проверок (`shellcheck`, `hadolint`, `markdownlint`, `actionlint`) → `.tools/quality-gates/style/run.py`
* **quality-gate-security** — пакет security-проверок (`gitleaks` + baseline SAST profile) → `.tools/quality-gates/security/run.py`
* **quality-gate-platform** — пакет platform-проверок (runtime + CI cross-platform baseline) → `.tools/quality-gates/platform/run.py`
* **reporting-build-gate-report** — агрегированный отчет gate-decision для PR summary/artifacts → `.tools/reporting/build_gate_report.py`
* **onboarding-validate-profile** — валидация `Repository Integration Profile` против onboarding policy → `.tools/onboarding/validate_profile.py`
* **onboarding-export-profile-context** — экспорт параметров профиля для reusable workflow → `.tools/onboarding/export_profile_context.py`
* **onboarding-promote-profile** — promotion профиля `audit -> required` с `--write` → `.tools/onboarding/promote_profile.py`
* **pdd** — сканирует `@todo` в исходниках и генерирует реестр задач → см. `.tools/pdd/README.md` (stable)
* **plantuml-render** — рендерит `.plantuml` файлы в PNG/SVG через Kroki-compatible API (облачный или локальный endpoint) → см. `.tools/plantuml-render/README.md` (stable)

## Кроссплатформенный запуск

Каждый инструмент имеет три точки входа:
- `entry` — универсальная команда через python (работает везде)
- `entry_unix` — bash wrapper для Linux/macOS
- `entry_win` — .bat wrapper для Windows

**Рекомендуемый способ:** использовать `entry` из `registry.json`:
```bash
# Универсально (Windows/Linux/macOS)
python .tools/pdd/pdd_scan.py --format md
python .tools/plantuml-render/plantuml_render.py --format png
python .tools/check-all/check_all.py
python .tools/check-encoding/check_encoding.py --paths .
python .tools/quality-gates/style/run.py
python .tools/quality-gates/security/run.py
python .tools/quality-gates/platform/run.py
python .tools/reporting/build_gate_report.py --help
python .tools/onboarding/validate_profile.py --help
python .tools/onboarding/export_profile_context.py --help
python .tools/onboarding/promote_profile.py --help
```

## Примечания об операционных файлах

* `registry.json` — машинно-удобный реестр утилит в `.tools/` (имя, путь, точка входа, теги). Поля `entry_win`/`entry_unix` — платформо-специфичные варианты запуска.

## Ссылки

* В корень проекта: `/README.md`
* Документация: `docs/` (если есть)
* Правила оформления README: `.manifest/readmemanifest.md`
