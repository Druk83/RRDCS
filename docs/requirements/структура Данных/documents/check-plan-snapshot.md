# `check-plan-snapshot`

* тип: `document`
* назначение: Снимок resolved check-плана для конкретного запуска проверки PR.
* владелец: `BC Оркестрация проверок качества (Quality Gate Orchestration BC)`
* источники `docs/**`: `docs/requirements/сценарии/quality-gate-orchestration/карта процесса.md`, `docs/requirements/сценарии/quality-gate-orchestration/каталог мероприятий.md`
* источники проверки: GitHub workflow run metadata / generated JSON summary
* статус: `draft`, ревью: `не выполнено`

## Структура

| Поле | Тип | Обяз. | Индекс | Валидация | Примечание |
|---|---|---:|---:|---|---|
| run_id | string | yes | no | not empty | Идентификатор запуска |
| pr_id | string | yes | no | not empty | Идентификатор PR |
| policy_version | integer | yes | no | > 0 | Версия policy |
| required_checks | array[string] | yes | no | min length 1 | Проверки для запуска |
| enforcement_mode | string | yes | no | enum | `audit` или `required` |
| trigger_type | string | yes | no | enum | open/synchronize/reopen |
| created_at | datetime | yes | no | ISO-8601 | Время генерации |

## Правила
* validation/schema: JSON contract для snapshot.
* индексы: не применяются.
* примеры документов: run snapshot JSON в artifacts.

## Использование
* сценарии: UC-QGO-01.
* критичные операции: сопоставление результата run с планом проверок.
* требования: FR-001, FR-004, FR-010, FR-013.

## Примечания
* Объект может храниться как artifact JSON и быть связан с run summary.
