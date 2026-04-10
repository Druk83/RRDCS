# Справочник портов (Ports Reference) — RRDCS

## 0. Контекст
- **Проект:** RRDCS
- **Среда:** локальная разработка (dev)
- **Дата обновления:** 2026-04-03
- **Источник конфигурации:**
  - `.tools/plantuml-render/docker-compose.base.yml`
  - `.tools/plantuml-render/docker-compose.dev.yml`
  - `.tools/plantuml-render/.env.example`

## 1. Сводная таблица портов

| Слой | Сервис | Привязка хоста | Соответствие (host:container) | Протокол | Публичный/внутренний | Назначение | Примечания |
|---|---|---|---|---|---|---|---|
| TL (Технологический слой) | Локальный сервис Kroki (Local Kroki Service) | по умолчанию `0.0.0.0` через Docker publish | `${KROKI_PORT:-8000}:8000` | tcp | internal (рекомендуемо) | Рендер PlantUML диаграмм | Для безопасного режима рекомендуется bind на localhost |

## 2. Детализация сервиса

### 2.1 Локальный сервис Kroki (Local Kroki Service)
- **Service ID:** `kroki`
- **Технология:** Docker image `yuzutech/kroki:0.30.1`
- **Порт контейнера:** `8000/tcp`
- **Порт хоста:** `${KROKI_PORT}` (по умолчанию `8000`)
- **Базовый URL:** `${KROKI_BASE_URL}` (по умолчанию `http://localhost:8000`)
- **Назначение:** endpoint для `.tools/plantuml-render/plantuml_render.py`

## 3. Порты прикладного слоя (Application Layer)
- На текущем этапе прикладные сервисы с сетевыми портами отсутствуют.
- Будущие порты AL/OBS/SEC добавляются после появления `.github/workflows/*` и/или runtime-сервисов.

## 4. Политика портов
- По умолчанию все локальные сервисы должны быть `internal`.
- Публикация порта наружу допустима только при явной необходимости.
- Для инструментов разработки предпочтителен `localhost` bind.
- Конфликты портов решаются через переменные окружения (`KROKI_PORT`).

## 5. Проверка актуальности
- Проверить конфигурацию:
  - `docker compose -f .tools/plantuml-render/docker-compose.base.yml -f .tools/plantuml-render/docker-compose.dev.yml config`
- Проверить запущенные сервисы:
  - `docker compose -f .tools/plantuml-render/docker-compose.base.yml -f .tools/plantuml-render/docker-compose.dev.yml ps`
- Проверить доступность endpoint:
  - `curl -fsS http://localhost:8000/health`

## 6. Типовые изменения в будущем
- Добавление CI self-hosted runners: порты фиксируются отдельным разделом.
- Добавление observability-сервисов (Prometheus/Grafana): порты и access-policy описываются в этом файле.
- Изменение порта Kroki: обновить `.env`/`.env.example` и таблицу раздела 1.
