# Маппинг ПМИ на наборы тестов

## Контекст
- Источник проверок `T-###`: `docs/requirements/требования/требования_внутренний_стандарт.md` (раздел `8.3`).
- ПМИ: `docs/requirements/тестирование/испытание системы.md`.
- Стек тестов: `docs/requirements/тестирование/стек тестов.md`.

## Таблица маппинга

| ID проверки (ПМИ) | Уровень | Набор тестов (suite) | Тип выполнения | Где описано выполнение | Ожидаемые артефакты |
|---|---|---|---|---|---|
| T-001 | Lint and Static | suite-lint-required | auto | `испытание системы.md#7` | lint logs, checks status |
| T-002 | Integration / Gate Flow | suite-required-pass | auto | `испытание системы.md#7` | checks summary |
| T-003 | Integration / Gate Flow | suite-parity-local-ci | mixed | `испытание системы.md#7` | local + CI logs |
| T-004 | Security Baseline | suite-security-required | auto | `испытание системы.md#7` | findings/logs |
| T-005 | Observability and Evidence | suite-evidence-completeness | auto | `испытание системы.md#7` | PR summary + links |
| T-006 | Platform Matrix | suite-platform-windows-linux | auto | `испытание системы.md#7` | matrix logs |
| T-007 | Governance and Pin Audit | suite-extensibility-check | mixed | `испытание системы.md#7` | diff + execution logs |
| T-008 | Performance of Core Pipeline | suite-pipeline-performance | auto | `испытание системы.md#7` | duration report |
| T-009 | Governance and Pin Audit | suite-toolchain-pin-audit | auto | `испытание системы.md#7` | pin-audit report |
| T-010 | Coverage Metrics | suite-coverage-mvp | auto | `испытание системы.md#7` | coverage report |

## Правила синхронизации
- Любая новая проверка в ПМИ обязана получить `T-###` и строку маппинга.
- Маппинг должен быть синхронизирован с `маппинг.json`.
- Тип выполнения:
  - `auto`: выполняется в CI job.
  - `manual`: выполняется вручную.
  - `mixed`: содержит автоматическую и ручную часть.
