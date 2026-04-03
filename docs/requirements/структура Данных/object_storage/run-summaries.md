# `run-summaries`

* тип: `bucket`
* назначение: Сводные результаты проверок PR (summary JSON/Markdown) для review и аудита.
* владелец: `BC Отчетность и доказательная база (Reporting and Evidence BC)`
* источники `docs/**`: `docs/requirements/сценарии/reporting-and-evidence/карта процесса.md`, `docs/requirements/сценарии/reporting-and-evidence/каталог мероприятий.md`
* источники проверки: PR summary + GitHub Artifacts
* статус: `draft`, ревью: `не выполнено`

## Схема
* bucket: `github-actions-artifacts/run-summaries`
* объект/ключ: `<repo>/<run-id>/summary.<json|md>`
* метаданные: `run_id`, `pr_id`, `overall_status`, `failed_checks_count`, `generated_at`
* lifecycle/retention: по artifact retention policy
* доступ: участники PR и роли с правами чтения артефактов

## Использование
* сценарии: UC-RE-01.
* критичные операции: публикация читаемого итогового статуса в PR.
* требования: FR-008, NFR-006.

## Примечания
* При необходимости long-term analytics данные могут экспортироваться в отдельное хранилище на следующем этапе эволюции.
