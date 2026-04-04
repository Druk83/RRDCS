# RRDCS — Repository Rules for Code Safety

**RRDCS** — это методология и набор репозиторных инструментов, которые защищают кодовую базу от деградации (в том числе при активном использовании ИИ) за счет воспроизводимых правил и обязательных автоматических quality gates.

## Ключевые возможности
- Операционная модель: `локальный pre-check + обязательные PR gates в GitHub Actions`.
- Единый инженерный контракт через `AGENTS.md` и манифесты `.manifest/*`.
- Управление политиками и версиями toolchain (pinning, governance decisions).
- Оркестрация required checks с блокировкой merge при любом fail.
- Пакеты проверок (style/security/platform) и доказательная отчетность (summary + artifacts).
- Кросс-платформенная модель разработки и исполнения (Windows/Linux, локально и в CI).
- Простое подключение нового репозитория через профиль интеграции репозитория (Repository Integration Profile) и reusable workflow.

## High-Level архитектура
1. Изменение попадает в `Pull Request`.
2. Оркестратор quality gates получает required check-plan из policy-слоя.
3. Исполняются пакеты проверок и формируется merge decision.
4. Результаты публикуются в PR как summary и доказательная база (logs/artifacts).

## Ближайшие анонсы проекта
- Внедрение обязательных `PR gates` в `GitHub Actions` как единого механизма допуска изменений в основную ветку.
- Запуск baseline-проверок безопасности (`secret scanning`, `SAST`) в обязательном контуре PR.
- Закрепление matrix-исполнения проверок минимум для `Windows` и `Linux`.
- Сохранение режима `coverage` как метрики на MVP с последующим переходом к блокирующим порогам.
- Развитие модели хранения: на MVP используется гибрид `Git + Checks + Artifacts + Cache`, при росте аналитических задач возможен переход к выделенному хранилищу.

## Интеграция в разные репозитории
1. В целевом репозитории подключается `RRDCS`-профиль: состав required checks, версии runtime/toolchain и режим внедрения (`audit` или `required`).
2. В `GitHub Actions` подключается reusable workflow с вызовом `.tools/*` и публикацией summary/artifacts.
3. На старте можно включить `audit`, затем перевести репозиторий в `required` после стабилизации.
4. Управление выполняется через versioned policy/manifests: rollout по версиям и быстрый rollback на предыдущий профиль.

## Статус документации
- Этапы трека `[1]-[9]` завершены (`CLOSED`).
- Текущее состояние см. в `docs/requirements/gap-tracking.md`.

## Ключевые ссылки
- Предметная область: `docs/requirements/предметная область.md`
- Обоснование выбора: `docs/requirements/обоснование выбора.md`
- Требования: `docs/requirements/требования/требования_внутренний_стандарт.md`
- Домены: `docs/requirements/домены/реестр.md`
- Сценарии: `docs/requirements/сценарии/`
- Структура данных: `docs/requirements/структура Данных/описание Данных.md`
- Архитектура (BL/AL/TL): `docs/requirements/архитектура/`
- Структура ПО: `docs/requirements/структура ПО/`
- Тестирование: `docs/requirements/тестирование/`
- Манифесты процесса: `.manifest/`
