# Описание AL (Application Layer) — RRDCS

## 0. Контекст
- **Проект:** RRDCS
- **Версия:** 1.0
- **Дата:** 2026-04-03
- **Стандарт:** ArchiMate 3.2 — Application Layer
- **Зависимости:**
  - `docs/requirements/архитектура/сущности.md`
  - `docs/requirements/архитектура/описание BL.md`
  - `docs/requirements/структура Данных/описание Данных.md`

## 1. Назначение прикладного слоя
Application Layer фиксирует, **как** реализуется бизнес-поток quality gate:
- получение PR-событий;
- разрешение плана обязательных проверок;
- выполнение пакетов проверок;
- расчет решения о слиянии;
- публикация сводки и доказательств.

## 2. Компоненты и интерфейсы

### 2.1 Application Components
| ID | Component | Назначение |
|---|---|---|
| AC-001 | Оркестратор workflow (Workflow Orchestrator) | Управляет последовательностью AP-001..AP-006 |
| AC-002 | Разрешатель политик (Policy Resolver) | Читает policy/toolchain pins и формирует check-plan |
| AC-003 | Исполнитель пакетов проверок (Verification Runner) | Запускает style/security/platform checks |
| AC-004 | Движок решения о слиянии (Merge Decision Engine) | Применяет правила допуска к результатам checks |
| AC-005 | Публикатор доказательств (Evidence Publisher) | Формирует summary и публикует ссылки на artifacts/logs |
| AC-006 | Локальный CLI предварительной проверки (Local Pre-check CLI `check-all`) | Запускает core checks вне CI с паритетом к PR gates |
| AC-007 | Менеджер профилей интеграции репозитория (Repository Integration Profile Manager) | Управляет onboarding/rollout режимами `audit|required` по репозиториям |

### 2.2 Application Interfaces
| ID | Interface | Используется компонентами | Назначение |
|---|---|---|---|
| AI-001 | Интерфейс событий PR (PR Event Interface) | AC-001 | Вход событий `pull_request` |
| AI-002 | Интерфейс манифестов политик (Policy Manifest Interface) | AC-002 | Доступ к policy/config из репозитория |
| AI-003 | Интерфейс пакетов проверок (Verification Package Interface) | AC-003, AC-006 | Запуск и получение результатов check-пакетов |
| AI-004 | Интерфейс отчетности (Reporting Interface) | AC-005 | Публикация summary/evidence |
| AI-005 | Интерфейс локального CLI (Local CLI Interface) | AC-006 | Локальный запуск pre-check |
| AI-006 | Интерфейс профиля интеграции репозитория (Repository Integration Profile Interface) | AC-007, AC-001 | Чтение/применение `Repository Integration Profile` |

## 3. Прикладные процессы и события

### 3.1 Application Processes
| ID | Application Process | Реализует BL-процесс | Участники |
|---|---|---|---|
| AP-001 | Обработка события PR (Process PR Event) | BP-002 | AC-001, AI-001 |
| AP-002 | Разрешение обязательных проверок (Resolve Required Checks) | BP-001, BP-002 | AC-001, AC-002, AI-002 |
| AP-003 | Запуск набора проверок (Run Verification Set) | BP-003 | AC-001, AC-003, AC-006, AI-003, AI-005 |
| AP-004 | Расчет решения о слиянии (Calculate Merge Decision) | BP-002 | AC-004 |
| AP-005 | Публикация доказательств (Publish Evidence) | BP-004 | AC-005, AI-004 |
| AP-006 | Применение профиля интеграции репозитория (Apply Repository Integration Profile) | BP-005 | AC-007, AC-001, AI-006 |

### 3.2 Application Events
| ID | Application Event | Генерируется в | Назначение |
|---|---|---|---|
| AE-001 | Событие PR получено (PR Event Received) | вход в AP-001 | Начало orchestration-run |
| AE-002 | План обязательных проверок разрешен (Required Plan Resolved) | AP-002 | Передача check-plan в runner |
| AE-003 | Набор проверок завершен (Verification Set Completed) | AP-003 | Триггер расчета merge-решения |
| AE-004 | Решение о слиянии рассчитано (Merge Decision Calculated) | AP-004 | Триггер публикации итогов |
| AE-005 | Доказательства опубликованы (Evidence Published) | AP-005 | Завершение run-потока |
| AE-006 | Профиль интеграции применен (Repository Profile Applied) | AP-006 | Актуализирован режим `audit|required` для репозитория |

### 3.3 Application Services
| ID | Application Service | Предоставляется через |
|---|---|---|
| AS-001 | Сервис разрешения плана проверок (Check Plan Resolution Service) | AC-001 + AC-002 + AI-002 |
| AS-002 | Сервис выполнения проверок (Verification Execution Service) | AC-003 + AC-006 + AI-003 |
| AS-003 | Сервис решения о слиянии (Merge Decision Service) | AC-004 |
| AS-004 | Сервис публикации доказательств (Evidence Publication Service) | AC-005 + AI-004 |
| AS-005 | Сервис управления onboarding/rollout (Repository Onboarding and Rollout Service) | AC-007 + AI-006 |

## 4. Data Objects и доступ
| ID | Data Object | Производится/читается |
|---|---|---|
| DO-001 | Манифесты политик (Policy Manifests) | AC-002 читает |
| DO-002 | Снимок плана проверок (Check Plan Snapshot) | AC-002 формирует, AC-001/AC-003 читают |
| DO-003 | Журнал решений по governance (Governance Decisions Log) | AC-002 читает baseline-решения |
| DO-004 | События запусков проверок (Check Run Events) | AC-001/AC-003/AC-004 формируют |
| DO-005 | Артефакты верификации (Verification Artifacts) | AC-003/AC-005 формируют |
| DO-006 | Сводки запусков (Run Summaries) | AC-005 формирует |
| DO-007 | CI-кэш (CI Cache) | AC-003/AC-006 используют как ускоритель исполнения |
| DO-008 | Профили интеграции репозиториев (Repository Integration Profiles) | AC-007 читает/применяет |

## 5. Политики надежности и наблюдаемости
- `AL-C1 Idempotency`: дедупликация входных PR-событий по `eventId`/`correlationId`.
- `AL-C2 Observability`: единый `correlationId=pr_id`, публикация summary и ссылок на логи.
- `AL-C3 Decision Safety`: merge-решение валидно только при полном наборе required check-статусов.
- `AL-C4 Parity`: `check-all` сохраняет паритет core checks с PR gates.

## 6. Ограничения AL
- Логика orchestration находится в scripts/workflow и не зависит от конкретной CI-платформы на уровне доменных правил.
- AL не определяет policy и toolchain pins (это зона BL, BP-001).
- AL не описывает параметры инфраструктуры (это зона TL).

## 7. Трассировка AL к требованиям
| AL-сценарий | FR | NFR |
|---|---|---|
| AP-001 + AP-002 | FR-001, FR-005 | NFR-005 |
| AP-003 | FR-006, FR-007, FR-009 | NFR-003, NFR-004 |
| AP-004 | FR-002, FR-003 | NFR-001 |
| AP-005 | FR-008 | NFR-006 |
| AC-006 (`check-all`) | FR-004 | NFR-005 |
| AP-006 + AC-007 | FR-011, FR-012, FR-013 | NFR-009 |

## 8. Межслойные связи (зеркальная фиксация)
### 8.1 TL -> AL
- `TS-001 -> AC-001`, `TS-001 -> AC-004`
- `TS-002 -> AC-005`
- `TS-003 -> AC-003`
- `TS-004 -> AC-001`, `TS-004 -> AC-002`, `TS-004 -> AC-006`
- `TS-005 -> AC-001`, `TS-005 -> AC-007`
- `AR-001 -> AC-001`
- `AR-002 -> AC-003`, `AR-002 -> AC-006`
- `AR-003 -> AC-002`, `AR-003 -> AC-006`
- `AR-004 -> AC-005`
- `AR-005 -> AC-007`

### 8.2 AL -> BL
- `AS-001 -> BP-001`, `AS-001 -> BP-002`
- `AS-002 -> BP-003`
- `AS-003 -> BP-002`
- `AS-004 -> BP-004`
- `AS-005 -> BP-005`
- `AE-004 -> BE-004`
- `DO-001 -> BO-001`, `DO-005 -> BO-005`, `DO-006 -> BO-006`, `DO-008 -> BO-007`

## 9. Диаграмма AL
- исходник: `docs/requirements/архитектура/diagrams/AL.plantuml`
- рендер: `docs/requirements/архитектура/diagrams/AL.png`

## 10. Готовность
- [x] Состав AL-компонентов и интерфейсов определен.
- [x] Выполнено сопоставление AP-* к BL-процессам.
- [x] Зафиксированы Data Objects и инварианты надежности.
