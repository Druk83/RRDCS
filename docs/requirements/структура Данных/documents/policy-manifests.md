# `Манифесты политик (policy-manifests)`

* тип: `документ (document)`
* назначение: Набор versioned policy/manifest файлов, определяющих обязательные проверки и правила качества.
* владелец: `BC Управление политиками и цепочкой инструментов (Policy and Toolchain Governance BC)`
* источники `docs/**`: `docs/requirements/домены/policy-and-toolchain-governance.md`, `docs/requirements/требования/требования_внутренний_стандарт.md`
* источники проверки: `.manifest/*`, `AGENTS.md`, `.github/workflows/*`
* статус: `draft`, ревью: `не выполнено`

## Структура

| Поле | Тип | Обяз. | Индекс | Валидация | Примечание |
|---|---|---:|---:|---|---|
| policy_id | string | yes | no | not empty | Идентификатор policy |
| version | integer | yes | no | > 0 | Версия policy |
| required_checks | array[string] | yes | no | min length 1 | Обязательные проверки |
| thresholds | object | yes | no | schema | Пороги quality/security |
| repository_profiles | array[object] | yes | no | min length 1 | Профили интеграции репозиториев |
| effective_from | datetime | yes | no | ISO-8601 | Дата вступления |

## Правила
* валидация/схема: policy-contract в markdown/json-schema (будет формализован в этапе [8]).
* индексы: не применяются (versioned files в Git).
* примеры документов: policy YAML/JSON в репозитории.

## Использование
* сценарии: UC-PG-01, UC-PG-02, UC-QGO-01.
* критичные операции: чтение актуальной policy версий для orchestration.
* требования: FR-005, FR-011, FR-012, NFR-004, NFR-007, NFR-009.

## Примечания
* Источник истины (source of truth) — Git.
* Изменения только через PR workflow.
