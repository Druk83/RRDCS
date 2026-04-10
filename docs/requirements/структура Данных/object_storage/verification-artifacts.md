# `Артефакты проверок (verification-artifacts)`

* тип: `контейнер (bucket)`
* назначение: Логи и артефакты выполнения style/security/platform checks.
* владелец: `BC Пакеты проверок (Verification Packages BC)`
* источники `docs/**`: `docs/requirements/сценарии/verification-packages/каталог мероприятий.md`, `docs/requirements/сценарии/reporting-and-evidence/каталог мероприятий.md`
* источники проверки: GitHub Actions Artifacts
* статус: `draft`, ревью: `не выполнено`

## Схема
* bucket: `github-actions-artifacts/verification`
* объект/ключ: `<repo>/<workflow>/<run-id>/<check-code>/<file>`
* метаданные: `run_id`, `pr_id`, `repository_slug`, `profile_version`, `check_code`, `platform`, `created_at`, `retention_days`
* lifecycle/retention: по настроенной policy хранения артефактов (artifact retention policy)
* доступ: GitHub permissions / repository access

## Использование
* сценарии: UC-VP-01, UC-RE-01.
* критичные операции: публикация логов fail-check и ссылок evidence в PR summary.
* требования: FR-008, NFR-006.

## Примечания
* Артефакты не являются источником истины (source of truth) правил; это доказательная база выполнения.
