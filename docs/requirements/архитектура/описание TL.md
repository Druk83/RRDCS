# Описание TL (Technology Layer) — RRDCS

## 0. Контекст
- **Проект:** RRDCS
- **Версия:** 1.0
- **Дата:** 2026-04-03
- **Стандарт:** ArchiMate 3.2 — Technology Layer
- **Зависимости:**
  - `docs/requirements/архитектура/сущности.md`
  - `docs/requirements/архитектура/описание AL.md`
  - `docs/requirements/обоснование выбора.md`

## 1. Назначение технологического слоя
Technology Layer фиксирует, **на чем** выполняются прикладные сценарии quality gate:
- hosted runners в GitHub Actions;
- runtime-инструменты (Python/PowerShell/Bash/Git);
- технологические сервисы (Checks API, Artifacts, Cache, Git Repository);
- артефакты workflow и scripts.

## 2. Узлы, ПО и технологические сервисы

### 2.1 Узлы (Nodes)
| ID | Node | Назначение |
|---|---|---|
| TN-001 | Linux-раннер GitHub (GitHub Linux Runner) | Выполнение Linux jobs для checks/orchestration |
| TN-002 | Windows-раннер GitHub (GitHub Windows Runner) | Выполнение Windows jobs для checks/orchestration |
| TN-003 | Рабочая станция разработчика (Developer Workstation) | Локальный запуск `check-all` |

### 2.2 Системное ПО (System Software)
| ID | System Software | Назначение |
|---|---|---|
| SW-001 | Среда выполнения GitHub Actions (GitHub Actions Runtime) | Исполнение workflow jobs |
| SW-002 | Среда выполнения Python 3.12 (Python 3.12 Runtime) | Исполнение orchestration scripts |
| SW-003 | Среда выполнения PowerShell (PowerShell Runtime) | Кросс-платформенные wrappers для Windows |
| SW-004 | Среда выполнения Bash (Bash Runtime) | Wrappers для Linux/macOS |
| SW-005 | Среда выполнения Git (Git Runtime) | Versioned storage и чтение policy/config |

### 2.3 Технологические сервисы (Technology Services)
| ID | Technology Service | Используется AL-компонентами |
|---|---|---|
| TS-001 | Сервис GitHub Checks API (GitHub Checks API Service) | AC-001, AC-004 |
| TS-002 | Сервис GitHub Artifacts (GitHub Artifacts Service) | AC-005 |
| TS-003 | Сервис GitHub Actions Cache (GitHub Actions Cache Service) | AC-003 |
| TS-004 | Сервис Git-репозитория (Git Repository Service) | AC-001, AC-002, AC-006 |

## 3. Интерфейсы, артефакты, сеть

### 3.1 Технологические интерфейсы (Technology Interfaces)
| ID | Technology Interface | Назначение |
|---|---|---|
| TIF-001 | Интерфейс webhook/событий PR (PR Webhook/Event Interface) | Доставка `pull_request` событий в workflow |
| TIF-002 | Интерфейс загрузки артефактов (Artifact Upload Interface) | Публикация logs/summaries |
| TIF-003 | Интерфейс доступа к кэшу (Cache Access Interface) | Чтение/запись CI-cache |

### 3.2 Артефакты (Artifacts)
| ID | Artifact | Расположение |
|---|---|---|
| AR-001 | Файлы workflow YAML (Workflow YAML Artifacts) | `.github/workflows/*` |
| AR-002 | Скрипты проверок (Verification Scripts) | `.tools/*` |
| AR-003 | Манифесты политик (Policy Manifests) | `.manifest/*`, policy/config files |
| AR-004 | Артефакты верификации (Verification Artifacts) | generated CI artifacts |

### 3.3 Сеть и пути (Communication Network and Paths)
| ID | Тип | Название | Назначение |
|---|---|---|---|
| CN-001 | Communication Network | Облачная сеть GitHub (GitHub Cloud Network) | Связность раннеров и GitHub services |
| CN-002 | Communication Network | Локальная сеть разработчика (Local Developer Network) | Локальное окружение разработчика |
| PT-001 | Path | Путь события PR (PR Event Path) | Путь `pull_request` -> workflow |
| PT-002 | Path | Путь загрузки артефактов (Artifact Upload Path) | Путь публикации artifacts |
| PT-003 | Path | Путь доступа к кэшу (Cache Access Path) | Путь доступа к cache |

## 4. Размещение AL-компонентов на TL
| AL Component | Основной Node | System Software |
|---|---|---|
| AC-001 Оркестратор workflow (Workflow Orchestrator) | TN-001/TN-002 | SW-001, SW-002 |
| AC-002 Разрешатель политик (Policy Resolver) | TN-001/TN-002 | SW-001, SW-002, SW-005 |
| AC-003 Исполнитель пакетов проверок (Verification Runner) | TN-001/TN-002 | SW-001, SW-002, SW-003, SW-004 |
| AC-004 Движок решения о слиянии (Merge Decision Engine) | TN-001/TN-002 | SW-001, SW-002 |
| AC-005 Публикатор доказательств (Evidence Publisher) | TN-001/TN-002 | SW-001, SW-002 |
| AC-006 Локальный CLI предварительной проверки (Local Pre-check CLI `check-all`) | TN-003 | SW-002, SW-003, SW-004, SW-005 |

## 5. Надежность, безопасность, наблюдаемость
- **Надежность:** merge-gate опирается на обязательные status checks и branch protection.
- **Производительность:** ускорение pipeline через TS-003 (`GitHub Actions Cache Service`).
- **Безопасность:** baseline security jobs выполняются в CI и блокируют merge при fail.
- **Наблюдаемость:** каждый failed check должен иметь log + summary + artifact link.

## 6. Ограничения TL
- На MVP не используется выделенная прикладная БД (используется гибрид: Git + Checks + Artifacts + Cache).
- TL ограничен hosted-моделью GitHub Actions на старте.
- Переход к self-hosted/отдельному хранилищу допускается как эволюционный этап.

## 7. Трассировка TL к требованиям
| TL-механизм | FR | NFR |
|---|---|---|
| TN-001/TN-002 + SW-001 | FR-001, FR-009 | NFR-001 |
| TS-001 (Checks API) | FR-002, FR-003 | NFR-001 |
| TS-002 + AR-004 | FR-008 | NFR-006 |
| TS-003 | FR-010 | NFR-002 |
| SW-002/SW-003/SW-004/SW-005 | FR-004, FR-005 | NFR-004, NFR-005 |

## 8. Диаграмма TL
- исходник: `docs/requirements/архитектура/diagrams/TL.plantuml`
- рендер: `docs/requirements/архитектура/diagrams/TL.png`

## 9. Готовность
- [x] Определены nodes, system software, technology services и artifacts.
- [x] Выполнено отображение AL-компонентов на инфраструктурные узлы.
- [x] Зафиксированы ограничения MVP без выделенной прикладной БД.
