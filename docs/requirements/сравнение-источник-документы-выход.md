# Сопоставление `sources -> docs -> .out`

Документ показывает, как одна и та же идея проходит три этапа:
1. постановка задачи в `.sources/README.md` и `.sources/SpeechToText.md`;
2. формализация в `docs/requirements/` и связанных операционных документах;
3. генерация и исполнение в `.out/`.

## Итоговая оценка

Проект реализован в полном объеме на уровне текущего `docs/` и `.out/`.

От исходной постановки `.sources/` остались не пробелы, а сознательные MVP-адаптации:
- `coverage` сделан аудиторским на MVP, а не блокирующим;
- архитектурные правила реализованы как исполнимый guard, а не буквальный ArcUnit;
- `small PR policy` оформлен как warning-only;
- набор style checks адаптирован под фактический стек проекта;
- README и манифесты приведены к `русский-first` стилю без потери технических терминов.

## Как читать документ

- `sources` - что было заявлено в исходных материалах.
- `docs` - как это было зафиксировано в технической документации.
- `.out` - что реально собрано в generated bundle для применения в целевом репозитории.

## Сводная таблица

| Тема | `sources` | `docs` | `.out` | Статус |
|---|---|---|---|---|
| PR gates | Обязательные quality gates для PR | Описаны `quality-gate-orchestration`, `policy-and-toolchain-governance`, required checks | Есть `rrdcs-repo-gates.yml`, `rrdcs-reusable-gates.yml` | Реализовано |
| Coverage | Coverage должен блокировать PR при падении ниже порога | В `тестирование/стек тестов.md` coverage трактуется как non-blocking на MVP | Coverage job есть, отдельного blocking gate нет | Сознательно адаптировано под MVP |
| Style checks | Примеры: `ClangTidy`, `ShellCheck`, `Hadalint` | В docs зафиксирован пакет style checks и policy-driven orchestration | В `.out` есть `style/run.py` с `ShellCheck`, `Hadolint`, `markdownlint`, `actionlint` | Адаптировано под фактический стек |
| Security / SAST | Базовый security gate с `gitleaks` и SAST | В docs security baseline закреплен как обязательный элемент PR проверки | В `.out` есть `rrdcs-sast-baseline.yml` с `CodeQL` и security package с `gitleaks` | Реализовано по направлению исходника |
| Architecture / ArcUnit | ArcUnit как unit-test для архитектурных правил | В docs зафиксирован executable architecture guard для границ модулей | В `.out` появляется `quality-gate-architecture` как package-level check | Сознательно заменено на executable guard |
| Agent Coding Manifest | Отдельный манифест стандартов кодирования | В docs есть standalone `agentcodingmanifest.md` с русским-first стилем и English в скобках | В `.out` манифест экспортируется в `.manifest/agentcodingmanifest.md` | Реализовано |
| Small PR policy | Желательны PR меньше 100 строк | В docs оформлена warning-only policy с порогом 100 строк | В `.out` есть PR size report job и generated summary | Сознательно адаптировано под MVP |
| Repository onboarding | Rollout `audit -> required`, reusable profile | В docs есть профиль интеграции и runbook onboarding | В `.out` есть generated profile и bundle для переноса | Реализовано |
| README as context | README может помогать LLM понимать архитектуру | Корневой README приведен к L0 и используется как входная точка | В `.out/.github/README.md` есть инструкция переноса и запуска | Реализовано |

## Что реализовано

### 1. PR gates и reusable workflow

- `sources`: идея обязательных PR gates и evidence artifacts.
- `docs`: описаны orchestration, quality gate decision, required checks, traceability.
- `.out`: собраны `rrdcs-repo-gates.yml` и `rrdcs-reusable-gates.yml`, которые запускают профиль и required checks в целевом репозитории.

### 2. Repository profile и onboarding

- `sources`: описан профиль подключения репозитория и переход `audit -> required`.
- `docs`: это оформлено как домен `policy-and-toolchain-governance`, включая runbook.
- `.out`: сгенерирован `repository-integration-profile.generated.yaml` и базовые workflow/policy файлы для переноса.

### 3. Security baseline

- `sources`: есть требование к `gitleaks` и SAST.
- `docs`: security baseline закреплен как обязательная часть PR-контроля.
- `.out`: присутствует `rrdcs-sast-baseline.yml` с `CodeQL`, а security package включает `gitleaks`.

### 4. Agent Coding Manifest

- `sources`: ожидался отдельный manifest правил кодирования.
- `docs`: добавлен standalone `agentcodingmanifest.md` с русским-first стилем и English в скобках.
- `.out`: manifest экспортируется в `.manifest/agentcodingmanifest.md`.

### 5. README как точка входа

- `sources`: README должен помогать ориентироваться в проекте.
- `docs`: корневой README приведен к L0-формату входной страницы.
- `.out`: в `.out/.github/README.md` есть инструкция переноса и запуска для целевого репозитория.

## Что сознательно адаптировано

### 1. Coverage

- `sources`: coverage должен блокировать PR.
- `docs`: coverage описан как MVP non-blocking.
- `.out`: нет blocking coverage gate, только контур для базовых проверок.

### 2. ArcUnit

- `sources`: архитектурные правила должны выражаться в unit-test через ArcUnit.
- `docs`: вместо буквального ArcUnit закреплен executable guard для module boundaries.
- `.out`: guard сгенерирован и включен в bundle.

### 3. Small PRs

- `sources`: желательно держать PR меньше 100 строк.
- `docs`: это оформлено как warning-only policy с threshold 100 строк и отдельной обработкой docs-only PR.
- `.out`: job публикует отчет по размеру PR и summary, но не блокирует merge на MVP.

### 4. Style tools

- `sources`: примеры инструментов включают `ClangTidy`.
- `docs`: style-пакет зафиксирован на уровне policy and test stack.
- `.out`: реализация выбрала другой набор проверок, адаптированный под текущее окружение.

## Что важно понимать

`docs/requirements/` переводит исходную идею в формальные домены, сценарии, архитектуру и тестовый стек. На этом этапе часть требований была адаптирована под MVP, но без потери общей цели.

`.out/` показывает, что именно реально генерируется как переносимый пакет для целевого репозитория:
- workflows;
- policies;
- profiles;
- локальные wrappers и setup scripts.

Итог: проект уже не находится в состоянии "что-то еще надо придумать", а находится в состоянии "MVP собран и согласован". Оставшиеся различия с `.sources` являются осознанными решениями, а не незакрытыми пробелами.

## Связанные файлы

- `.sources/README.md`
- `.sources/SpeechToText.md`
- `docs/requirements/gap-tracking.md`
- `docs/requirements/тестирование/стек тестов.md`
- `docs/requirements/архитектура/описание AL.md`
- `docs/requirements/архитектура/описание BL.md`
- `docs/requirements/архитектура/описание TL.md`
- `docs/requirements/сценарии/quality-gate-orchestration/карта процесса.md`
- `.out/.github/README.md`
- `.out/.github/workflows/rrdcs-repo-gates.yml`
- `.out/.github/workflows/rrdcs-reusable-gates.yml`
- `.out/.github/workflows/rrdcs-sast-baseline.yml`
- `.out/.github/profiles/repository-integration-profile.generated.yaml`
- `.out/.manifest/agentcodingmanifest.md`
- `.out/.tools/check-all/README.md`
- `.out/.tools/check-all/check-plan.json`
- `.out/.tools/reporting/build_pr_size_report.py`
- `.out/.tools/quality-gates/architecture/run.py`
- `.out/.tools/quality-gates/style/run.py`
- `.out/.tools/quality-gates/security/run.py`
