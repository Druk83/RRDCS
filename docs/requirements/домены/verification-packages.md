# Домен: Пакеты проверок (Verification Packages)

## Назначение домена

Домен реализует фактические проверки качества и безопасности:
- запускает и исполняет check-пакеты;
- нормализует результаты выполнения;
- передает результаты в слой оркестрации и отчетности.

Цель домена — обеспечить техническое выполнение quality/security контроля по согласованному baseline.

- **slug:** verification-packages
- **title:** Пакеты проверок (Verification Packages)
- **type:** core
- **status:** active
- **scope_in:**
  - Выполнение style/quality checks для shell, dockerfile, markdown и workflow.
  - Выполнение baseline security checks для PR.
  - Выполнение кросс-платформенных проверок в CI matrix (Windows/Linux).
  - Формирование единообразных результатов выполнения каждого check.
  - Выполнение набора проверок согласно профилю интеграции конкретного репозитория.
- **scope_out:**
  - Принятие финального merge-решения (домен `quality-gate-orchestration`).
  - Версионирование политик качества (quality policy) и выбор обязательности проверок (checks) (домен `policy-and-toolchain-governance`).
  - Долговременное хранение артефактов отчетности (домен `reporting-and-evidence`).
- **actors:**
  - Система непрерывной интеграции (Continuous Integration System) — запускает и исполняет check-пакеты.
  - Разработчик (Developer) — исправляет нарушения, выявленные check-пакетами.
  - Технический лидер и архитектор (Tech Lead and Architect) — утверждает состав обязательного baseline.
- **owned_data:**
  - `CheckResult`: `check_name`, `status`, `duration_sec`, `error_count`.
  - `SecurityFinding`: `tool`, `severity`, `location`, `fingerprint`.
  - `PlatformRun`: `platform`, `runner`, `status`, `log_ref`.
- **requirements_refs:**
  - FR-006, FR-007, FR-009
  - NFR-003, NFR-004
- **interfaces:**
  - `<- quality-gate-orchestration` (sync): получение плана запуска checks.
  - `-> reporting-and-evidence` (sync): передача результатов, логов и findings.

## Что делает домен

1. Выполняет style/quality checks (`ShellCheck`, `Hadolint`, `markdownlint`, `actionlint` и др.).
2. Выполняет baseline security checks (`gitleaks`, `CodeQL`, профильные security jobs).
3. Выполняет проверки в кросс-платформенном CI matrix.
4. Формирует стандартизированные `CheckResult`/`SecurityFinding` для дальнейшей обработки.
5. Прокидывает идентификатор репозитория в результаты для multi-repo трассировки.

## Что домен не делает

1. Не принимает итоговое решение о merge (это `quality-gate-orchestration`).
2. Не определяет обязательность проверок (`checks`) и правила политик качества (quality policy) (это `policy-and-toolchain-governance`).
3. Не ведет долгосрочную отчетность и аудитные отчеты (это `reporting-and-evidence`).

