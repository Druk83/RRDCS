# Пошаговая инструкция (Runbook): Подключение нового репозитория (Repository Onboarding and Rollout)

## 1. Назначение
Runbook фиксирует операционный порядок подключения нового репозитория к RRDCS через `Repository Integration Profile` и управляемый переход режима `audit -> required`.
Первый rollout выполняется на одном pilot-репозитории; каналы `wave` и `global` подключаются после стабилизации pilot.

Связанные артефакты:
- `карта процесса.md` (UC-PG-02)
- `каталог мероприятий.md` (RepositoryOnboardingPlanned / RepositoryOnboardedInAuditMode / RepositoryPromotedToRequired)
- `docs/requirements/требования/требования_внутренний_стандарт.md` (FR-011, FR-012, FR-013, NFR-009)
- `docs/requirements/тестирование/испытание системы.md` (T-011)

## 2. Роли
- Технический лидер и архитектор (Tech Lead and Architect): принимает решения `audit|required`, утверждает rollout.
- Разработчик (Developer): выполняет технические действия в репозитории и подтверждает работоспособность PR-потока.

## 3. Входные условия
- Доступен reusable workflow и актуальная версия policy.
- Определен целевой репозиторий (`repository_slug`).
- Согласованы required checks для домена репозитория.

## 4. Выходные условия
- Репозиторий подключен через `Repository Integration Profile`.
- В `audit` режиме успешно пройден контрольный прогон PR.
- По решению владельца политик выполнен перевод в `required` (если метрики стабильны).
- Для первого rollout подтвержден один pilot-репозиторий и зафиксировано, что `wave/global` отложены до следующего этапа.

## 5. Пошаговая процедура

| Шаг | Действие | Результат/событие |
|---|---|---|
| 1 | Инициировать onboarding для целевого `repository_slug`. | Старт UC-PG-02. |
| 2 | Сформировать/обновить `Repository Integration Profile` (policy version, required checks, rollout channel, enforcement mode=`audit`). | `CMD: CreateRepositoryIntegrationProfile` |
| 3 | Провести governance-review профиля и связанной policy-конфигурации. | Профиль готов к публикации. |
| 4 | Опубликовать профиль в оркестрацию. | `CMD: PublishProfileToOrchestrator` |
| 5 | Подтвердить факт подключения репозитория в `audit`. | `EVT: RepositoryOnboardedInAuditMode` |
| 6 | Выполнить контрольный PR-прогон в `audit` и собрать evidence. | Проверка T-011 (часть `audit`). |
| 7 | Проанализировать стабильность quality-метрик (доля pass/fail, полнота evidence, повторяемость результатов). | Решение о готовности к promotion. |
| 8 | При стабильных метриках выполнить команду перевода в `required`. | `CMD: PromoteRepositoryToRequiredMode` |
| 9 | Подтвердить публикацию события promotion в оркестрацию и отчетность. | `EVT: RepositoryPromotedToRequired` |
| 10 | Выполнить повторный PR-прогон уже в `required` и подтвердить блокировку merge при fail required checks. | Проверка T-011 (часть `required`). |

## 5.1 Технические команды (MVP baseline)
```bash
# 1) Валидация профиля перед публикацией
python .tools/onboarding/validate_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml

# 2) Экспорт контекста профиля для CI
python .tools/onboarding/export_profile_context.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml

# 3) Preview promotion audit -> required
python .tools/onboarding/promote_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml \
  --approved-by "tech-lead"

# 4) Применение promotion
python .tools/onboarding/promote_profile.py \
  --profile .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml \
  --approved-by "tech-lead" \
  --write
```

## 5.2 Подключение reusable workflow
```yaml
name: rrdcs-repo-gates

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  rrdcs-gates:
    uses: ./.github/workflows/rrdcs-reusable-gates.yml
    with:
      profile_path: .sources/.manifest/profiles/repository-integration-profile.rrdcs-tooling.yaml
      enforcement_mode: audit
      upload_evidence: true
```

## 6. Критерии готовности (Definition of Done)
- Профиль интеграции сохранен в versioned артефактах.
- Для режима `audit` есть подтвержденный прогон с опубликованным summary и evidence.
- Для режима `required` подтверждена корректная работа merge gate.
- Результаты зафиксированы в артефактах тестирования (T-011).

## 7. Откат
- Если в `required` наблюдается нестабильность или неприемлемый рост блокирующих ложных срабатываний:
1. Вернуть профиль репозитория в `audit`.
2. Зафиксировать причину отката и обновить policy/profile.
3. Повторить шаги 6-10 после корректировок.

## 8. Многорепозиторная раскатка (Multi-repo rollout)
- После стабилизации пилотного репозитория новые репозитории подключаются волнами.
- Первая волна (`pilot set`) содержит ограниченное число репозиториев и используется для проверки воспроизводимости onboarding.
- Минимальный `pilot set` для stage-2 начинается с текущего пилотного репозитория; дополнительные репозитории добавляются только если:
  - у них совместимый стек и тот же базовый набор `policy/profile/workflow`;
  - не требуется ручная миграция core scripts;
  - есть понятный rollback и владелец;
  - PR-flow стабилен и не требует уникальных исключений вне runbook.
- Следующая волна (`wave`) подключается только после подтверждения стабильности `audit -> required` на pilot set.
- Глобальный канал (`global`) используется только после подтверждения, что политики, evidence и rollback одинаково работают на нескольких репозиториях.
- Для каждой волны должны быть зафиксированы:
  - список репозиториев;
  - версии policy/profile;
  - required checks;
  - критерии перехода в следующую волну;
  - план отката.

## 9. Критерии перехода между волнами
- Переход из `pilot` в `wave` разрешается только если:
  - контрольный PR-поток стабилен;
  - evidence публикуется без ручных обходов;
  - rollback выполним и проверен.
- Первый дополнительный репозиторий должен быть максимально близок к текущему пилоту по стеку, чтобы проверять именно воспроизводимость onboarding, а не адаптацию к новому типу проекта.
- Переход из `wave` в `global` разрешается только если:
  - нет устойчивых ложных блокировок;
  - метрики качества проверок стабильны;
  - версии профилей и workflow совместимы.
