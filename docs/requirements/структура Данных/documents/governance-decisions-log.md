# `governance-decisions-log`

* тип: `document`
* назначение: Журнал решений по изменениям policy/toolchain.
* владелец: `BC Управление политиками и цепочкой инструментов (Policy and Toolchain Governance BC)`
* источники `docs/**`: `docs/requirements/сценарии/policy-and-toolchain-governance/каталог мероприятий.md`
* источники проверки: PR history + release notes + governance logs
* статус: `draft`, ревью: `не выполнено`

## Структура

| Поле | Тип | Обяз. | Индекс | Валидация | Примечание |
|---|---|---:|---:|---|---|
| decision_id | string | yes | no | not empty | ID решения |
| policy_change_id | string | yes | no | not empty | ID изменения policy |
| decision | string | yes | no | enum | approved/rejected |
| approved_by | string | yes | no | not empty | Ответственный |
| reason | string | no | no |  | Причина |
| decided_at | datetime | yes | no | ISO-8601 | Время решения |

## Правила
* validation/schema: governance decision record.
* индексы: не применяются.
* примеры документов: release/governance notes.

## Использование
* сценарии: UC-PG-01.
* критичные операции: аудит изменений policy и версий toolchain.
* требования: FR-005, NFR-007.

## Примечания
* Журнал должен быть трассируем к PR и версии policy.
