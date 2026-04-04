# Домен: Оркестрация проверок качества (Quality Gate Orchestration)

## Назначение домена

Домен отвечает за центральный процесс допуска изменений в `main`:
- запускает обязательный поток проверок;
- собирает их статус;
- принимает итоговое решение о возможности merge.

Цель домена — обеспечить единое и воспроизводимое enforcement-правило для всех PR.

- **slug:** quality-gate-orchestration
- **title:** Оркестрация проверок качества (Quality Gate Orchestration)
- **type:** core
- **status:** active
- **scope_in:**
  - Запуск обязательных PR checks при событиях `pull_request`.
  - Принятие решения о допуске/блокировке merge по результатам обязательных проверок (`required checks`).
  - Локальный запуск `check-all` как эквивалент core-проверок.
  - Подключение новых проверок через конфигурацию без изменения базового потока.
  - Применение режима внедрения репозитория (`audit`/`required`) из профиля интеграции.
- **scope_out:**
  - Детальная реализация конкретных линтеров и security-сканеров (домен `verification-packages`).
  - Хранение и утверждение политик качества (quality policy) и версий цепочки инструментов (toolchain) (домен `policy-and-toolchain-governance`).
  - Хранение и представление доказательной отчетности (домен `reporting-and-evidence`).
- **actors:**
  - Разработчик (Developer) — запускает pre-check и инициирует PR.
  - Система непрерывной интеграции (Continuous Integration System) — исполняет orchestration logic и выставляет итоговый статус.
  - Технический лидер и архитектор (Tech Lead and Architect) — определяет обязательность checks и правила допуска.
- **owned_data:**
  - `GateExecution`: `execution_id`, `trigger_type`, `started_at`, `completed_at`, `final_status`.
  - `MergeDecision`: `pr_id`, `required_checks_passed`, `decision`, `reason`.
  - `CheckPlan`: `plan_id`, `required_checks`, `optional_checks`, `matrix_profile`.
- **requirements_refs:**
  - FR-001, FR-002, FR-003, FR-004, FR-010, FR-013
  - NFR-001, NFR-005
- **interfaces:**
  - `-> verification-packages` (sync): вызов пакетов проверок по плану.
  - `-> policy-and-toolchain-governance` (sync): чтение политик качества (quality policy) и закрепленных версий (`pinned versions`).
  - `-> reporting-and-evidence` (sync): отправка итоговых статусов и событий.

## Что делает домен

1. Запускает обязательные проверки (`required checks`) по событиям `pull_request`.
2. Агрегирует статусы всех обязательных проверок.
3. Формирует итоговое решение: merge разрешен или заблокирован.
4. Поддерживает единый orchestration-поток для локального `check-all` и CI.
5. Позволяет подключать новые проверки через конфигурацию и адаптеры.
6. Поддерживает переход репозитория из `audit` в `required` без изменения core scripts.

## Что домен не делает

1. Не реализует внутреннюю логику линтеров/сканеров (это `verification-packages`).
2. Не определяет политики качества (quality policy) и закрепленные версии (`pinned versions`) (это `policy-and-toolchain-governance`).
3. Не хранит и не публикует доказательную отчетность как отдельный контур (это `reporting-and-evidence`).

