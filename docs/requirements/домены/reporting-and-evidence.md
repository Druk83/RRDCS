# Домен: Отчетность и доказательная база (Reporting and Evidence)

## Назначение домена

Домен обеспечивает прозрачность и доказуемость результатов проверок:
- формирует понятный статус в PR;
- собирает логи и артефакты;
- готовит данные для приемки и аудита.

Цель домена — сделать результаты quality/security проверок наблюдаемыми и проверяемыми.

- **slug:** reporting-and-evidence
- **title:** Отчетность и доказательная база (Reporting and Evidence)
- **type:** supporting
- **status:** active
- **scope_in:**
  - Формирование PR summary по результатам проверок.
  - Сохранение ссылок на логи и артефакты каждого check-run.
  - Подготовка доказательной отчетности для приемки и аудита.
  - Представление причин падения checks в читаемом виде.
- **scope_out:**
  - Запуск и выполнение проверок (домен `verification-packages`).
  - Управление политиками качества (quality policy) и версиями цепочки инструментов (toolchain) (домен `policy-and-toolchain-governance`).
  - Решение о merge-допуске (домен `quality-gate-orchestration`).
- **actors:**
  - Разработчик (Developer) — анализирует причины fail в PR summary/logs.
  - Технический лидер и архитектор (Tech Lead and Architect) — использует отчетность для контроля качества и решений.
  - Система непрерывной интеграции (Continuous Integration System) — публикует и обновляет summary/artifacts.
- **owned_data:**
  - `RunSummary`: `pr_id`, `run_id`, `overall_status`, `failed_checks`.
  - `EvidenceLink`: `artifact_id`, `artifact_type`, `url`, `retention_days`.
  - `VerificationReport`: `report_id`, `period`, `tests_passed`, `deviations`.
- **requirements_refs:**
  - FR-008
  - NFR-002, NFR-006
- **interfaces:**
  - `<- quality-gate-orchestration` (sync): получение итогового статуса run.
  - `<- verification-packages` (sync): получение детальных результатов и логов.

## Что делает домен

1. Публикует PR summary со статусом проверок и причинами падений.
2. Связывает результаты checks с логами и артефактами исполнения.
3. Формирует верификационные отчеты для приемки и ретроспектив качества.
4. Поддерживает единый формат evidence для командной и аудиторской проверки.

## Что домен не делает

1. Не запускает и не исполняет проверки (это `verification-packages`).
2. Не определяет политики качества (quality policy), пороги и состав обязательных проверок (`required checks`) (это `policy-and-toolchain-governance`).
3. Не решает, можно ли merge (это `quality-gate-orchestration`).

