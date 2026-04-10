# Дорожная карта покрытия (Coverage Roadmap) для RRDCS

## 1. Цель
Зафиксировать переход от MVP-режима non-blocking к управляемым blocking-порогам покрытия для скриптов и тестового контура RRDCS.

## 2. Текущее состояние (MVP, 2026-04-06)
- Coverage собирается отдельным job `rrdcs-coverage` в workflow `.github/workflows/rrdcs-test-harness.yml`.
- Job помечен как `continue-on-error: true`.
- Результаты публикуются как evidence (`coverage.txt`, `coverage.xml`, `coverage.json`).
- Coverage на MVP не блокирует merge (соответствие NFR-008).

## 3. Этапы повышения требований

### Этап M0 (MVP, активен)
- Режим: non-blocking.
- Минимум: публикация coverage-артефактов на каждом запуске test-harness.
- Критерий готовности: доступен тренд по данным минимум за 2 недели.

### Этап M1 (после стабилизации MVP)
- Режим: soft-gate (warning в PR summary).
- Целевой порог: `line coverage >= 40%` для `tests/acceptance` и `tests`.
- Действие при нарушении: предупреждение без блокировки merge.

### Этап M2 (после подключения pilot-репозитория)
- Режим: blocking для core test-harness.
- Целевой порог: `line coverage >= 55%`.
- Действие при нарушении: fail required check `rrdcs-coverage`.

### Этап M3 (production baseline)
- Режим: blocking + дельта-контроль.
- Целевые пороги:
- `line coverage >= 65%` для тестового контура;
- отсутствие деградации покрытия относительно предыдущего релиза.

## 4. Источники метрик
- `.artifacts/coverage/coverage.txt`
- `.artifacts/coverage/coverage.json`
- GitHub artifact `rrdcs-coverage-evidence`

## 5. Условия перехода между этапами
- M0 -> M1: не менее 10 последовательных запусков с корректной публикацией coverage-артефактов.
- M1 -> M2: не менее 2 недель без критических инцидентов ложных блокировок.
- M2 -> M3: подтвержденная стабильность rollout `audit -> required` для pilot-репозитория и готовность расширять policy на wave/global.
