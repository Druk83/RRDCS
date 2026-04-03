# `check-run-events`

* тип: `topic`
* назначение: Поток событий выполнения проверок и статусов quality gates.
* владелец: `BC Оркестрация проверок качества (Quality Gate Orchestration BC)`
* источники `docs/**`: `docs/requirements/сценарии/*/каталог мероприятий.md`
* источники проверки: GitHub Checks API / workflow events
* статус: `draft`, ревью: `не выполнено`

## Схема
* topic: `check-run-events`
* схема сообщения: envelope + payload события (`eventId`, `eventType`, `eventVersion`, `correlationId`, `causationId`, `payload`)
* совместимость: backward-compatible additions
* партиции/ключ: `pr_id` / `run_id` (логический ключ)
* retention: определяется политикой GitHub и artifact retention

## Использование
* сценарии: UC-QGO-01, UC-VP-01, UC-RE-01.
* критичные события: `PullRequestUpdated`, `RequiredVerificationSetCompleted`, `MergeDecisionRecorded`, `PRSummaryPublished`.
* требования: FR-001, FR-008, NFR-006.

## Примечания
* Это логический stream поверх GitHub events/check statuses, без отдельного брокера на MVP.
