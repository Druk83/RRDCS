# RRDCS — правила репозитория для безопасности кода

RRDCS — это набор правил, манифестов и инструментов для репозитория, который удерживает качество и безопасность изменений через воспроизводимые проверки, обязательные шлюзы pull request (PR gates) и профиль подключения репозитория.

## Первый шаг
Если нужно подготовить пакет интеграции RRDCS для другого репозитория, сначала собери `.out/`:

```bash
python .tools/onboarding/build_integration_bundle.py --output-dir .out --force
```

Это дает готовый набор файлов для переноса:
- `.github/workflows/` с готовыми рабочими процессами (workflows) для PR gates;
- `.github/policies/` и `.github/profiles/` с настройками подключения;
- `.tools/setup/` со скриптами для локальной проверки и подготовки Docker;
- `.out/.github/README.md` с инструкцией по запуску в целевом репозитории.

Если тебе не нужен пакет интеграции, а нужна работа с уже подключенным репозиторием, переходи сразу к `check-all` и документации ниже.

## Что здесь есть
- Локальная предварительная проверка и обязательные PR gates в GitHub Actions.
- Профиль подключения репозитория и режимы внедрения `audit -> required`.
- Пакеты проверок `style`, `security`, `platform` и `architecture`.
- Генерация доказательств (evidence) в `JSON` и `Markdown`, а также артефактов.
- Документация требований, архитектуры, сценариев, тестирования, релиза и операций.
- Манифесты правил и процессов в `.sources/.manifest/`.

## Как устроен проект
1. Изменение проходит локальный `check-all`.
2. Затем срабатывают PR gates в GitHub Actions.
3. Результаты публикуются как краткий отчет (summary) и артефакты (artifacts).
4. При подключении профиль репозитория переводится из `audit` в `required`.

## Быстрый старт
```bash
python .tools/check-all/check_all.py
python .tools/plantuml-render/plantuml_render.py --path docs/requirements/
python .tools/onboarding/build_integration_bundle.py --output-dir .out --force
```

Для локального рендеринга диаграмм с Docker см. [`.tools/plantuml-render/README.md`](.tools/plantuml-render/README.md).

## Ключевые разделы
- `docs/requirements/` — требования, сценарии, архитектура, тестирование и структура данных.
- `docs/operations/github-ops-baseline.md` — базовый операционный контур GitHub.
- `docs/release/mvp-release-plan.md` — план релиза MVP.
- `.tasks/` — текущие задачи и архив выполненных задач.
- `.issues/` — проблемы и инциденты.
- `.sources/.manifest/` — исходные манифесты, политики и шаблоны.
- `.tools/` — автоматизация, проверки, рендеринг диаграмм и onboarding.

## Ключевые инструменты
- [`check-all`](.tools/check-all/README.md) — локальный агрегатор проверок.
- [`onboarding`](.tools/onboarding/README.md) — валидация профиля, перевод режима и пакет интеграции.
- [`plantuml-render`](.tools/plantuml-render/README.md) — рендер PlantUML-диаграмм.
- [`quality-gates`](.tools/quality-gates/) — пакеты проверок качества.
- [`reporting`](.tools/reporting/) — генерация отчетов и доказательств (evidence).
- [`check-encoding`](.tools/check-encoding/) — проверка кодировок и искажений текста (mojibake).
- [`pdd`](.tools/pdd/) — сканирование `@todo` и реестр задач.

## Документация
- [Предметная область](docs/requirements/предметная%20область.md)
- [Обоснование выбора](docs/requirements/обоснование%20выбора.md)
- [Внутренний стандарт требований](docs/requirements/требования/требования_внутренний_стандарт.md)
- [Реестр разрывов](docs/requirements/gap-tracking.md)
- [Архитектура](docs/requirements/архитектура/)
- [Сценарии](docs/requirements/сценарии/)
- [Тестирование](docs/requirements/тестирование/)

## Коротко о правилах
- Основной язык документации — русский, английские термины допускаются в скобках как уточнение.
- Подробные правила оформления README находятся в [`.sources/.manifest/readmemanifest.md`](.sources/.manifest/readmemanifest.md).
- Правила иерархии документов находятся в [`.sources/.manifest/hierarchymanifest.md`](.sources/.manifest/hierarchymanifest.md).
- Правила для задач находятся в [`.sources/.manifest/taskmanifest.md`](.sources/.manifest/taskmanifest.md).

## Статус
- Этапы трека `[1]-[9]` завершены.
- Текущее состояние gap-tracking см. в [docs/requirements/gap-tracking.md](docs/requirements/gap-tracking.md).

## Проверка
Если нужно быстро проверить состояние репозитория, запусти:

```bash
python .tools/check-all/check_all.py
```
