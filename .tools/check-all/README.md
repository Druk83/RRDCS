# check-all — локальный агрегатор проверок

Кросс-платформенный инструмент для запуска локального pre-check набора RRDCS.
Использует JSON-план проверок и единый контракт завершения:
- `0` — все required проверки пройдены
- `1` — есть ошибка выполнения или упавшая required проверка

Default check-plan ориентирован на smoke-проверку самого tooling-репозитория RRDCS.
Для целевых репозиториев используйте отдельный `--plan` (шаблоны в `templates/`).

## Быстрый старт

```bash
# Unix
.tools/check-all/check-all

# Windows
.tools/check-all/check-all.bat

# Универсально через Python
python .tools/check-all/check_all.py
```

## Основные опции

* `--plan` — путь к JSON-плану (по умолчанию `.tools/check-all/check-plan.json`)
* `--only` — запуск по селекторам (check id, group, tag); флаг можно повторять
* `--list` — показать checks и выйти
* `--dry-run` — показать команды без выполнения
* `--fail-fast` — остановка на первом падении required check
* `--report-json` — записать агрегированный отчет в JSON
* `--report-md` — записать агрегированный отчет в Markdown

## Примеры

```bash
# Показать набор проверок
python .tools/check-all/check_all.py --list

# Запустить только style-набор
python .tools/check-all/check_all.py --only style

# Запустить несколько селекторов
python .tools/check-all/check_all.py --only style,security --only governance

# Запустить профиль целевого репозитория (пример)
python .tools/check-all/check_all.py --plan .tools/check-all/templates/check-plan-repository-profile.json

# Dry-run полного набора
python .tools/check-all/check_all.py --dry-run

# Сформировать диагностический отчет (локально и для CI)
python .tools/check-all/check_all.py \
  --report-json .artifacts/local/check-all-report.json \
  --report-md .artifacts/local/check-all-summary.md
```

## Диагностика и evidence

Единый формат диагностики формируется самим `check-all`:
- `report JSON` — машинно-читаемый отчет (`overall_status`, `failed_checks`, `error_code`, `source_step`).
- `report Markdown` — читаемый summary для PR/человека.

В CI этот же формат публикуется в artifacts:
- `rrdcs-check-all-linux-evidence`
- `rrdcs-check-all-windows-evidence`
- `rrdcs-gate-decision-evidence`

## План проверок

Файл: `.tools/check-all/check-plan.json`

Текущий default-набор (tooling smoke):
- `tooling-core-files` (`governance`, теги: `governance`, `baseline`, `tooling`)
- `style-python-syntax-baseline` (`style`, теги: `style`, `baseline`, `tooling`)
- `security-env-ignore-policy` (`security`, теги: `security`, `baseline`)
- `onboarding-profile-baseline` (`governance`, теги: `governance`, `onboarding`, `baseline`, `tooling`)
- `encoding-mojibake-check` (`style`, теги: `style`, `encoding`, `baseline`, `tooling`)
- `style-package-smoke` (`style`, теги: `style`, `smoke`, `quality-gates`)
- `security-package-smoke` (`security`, теги: `security`, `smoke`, `quality-gates`)
- `platform-package-smoke` (`platform`, теги: `platform`, `smoke`, `quality-gates`)

Шаблоны для целевых репозиториев:
- `.tools/check-all/templates/check-plan-repository-profile.json` — профиль через `encoding-gate` + пакеты `.tools/quality-gates/*`.
- `.tools/check-all/templates/check-plan-polyglot-example.json` — пример для прямых tool-команд.

Поддерживаемые поля check-объекта:
- `id` — уникальный идентификатор
- `title` — читаемое имя
- `group` — логическая группа
- `tags` — массив селекторов для выборочного запуска (например: `style`, `security`)
- `required` — блокирующий check (`true`/`false`)
- `success_codes` — массив допустимых exit-code
- `command` — команда запуска (массив аргументов)

## Проверка окружения

Перед запуском выполняется валидация:
- Python версии `3.10+`
- наличие исполняемых файлов в `PATH`
- наличие локальных скриптов, указанных в check-плане

Если передан селектор, который не найден в плане, инструмент завершится с ошибкой и покажет доступные `id/group/tag`.

## Связанные файлы

* `.tools/check-all/check_all.py`
* `.tools/check-all/check-plan.json`
* `.tools/check-all/templates/check-plan-repository-profile.json`
* `.tools/check-all/templates/check-plan-polyglot-example.json`
* `.tools/registry.json`
