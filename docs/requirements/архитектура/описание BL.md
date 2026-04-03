# Описание BL (Business Layer) — RRDCS

## 0. Контекст
- **Проект:** RRDCS
- **Версия:** 1.0
- **Дата:** 2026-04-03
- **Стандарт:** ArchiMate 3.2 — Business Layer
- **Реестр сущностей:** `docs/requirements/архитектура/сущности.md`

## 1. Назначение бизнес-слоя
Business Layer фиксирует, **что** делает система RRDCS для контроля качества изменений в PR:
- управление политиками и фиксацией toolchain;
- оркестрация обязательных проверок;
- исполнение базового набора проверок;
- публикация сводки и доказательств.

## 2. Акторы и роли

### 2.1 Акторы
| ID | Actor | Роль в процессе |
|---|---|---|
| BA-001 | Разработчик (Developer) | Создает/обновляет PR, запускает локальный pre-check |
| BA-002 | Технический лидер и архитектор (Tech Lead and Architect) | Утверждает политики качества и фиксацию toolchain |
| BA-003 | Система непрерывной интеграции (Continuous Integration System) | Исполняет orchestration flow и check-пакеты |

### 2.2 Роли
| ID | Role | Исполняется актором | Назначение |
|---|---|---|---|
| BR-001 | Инициатор изменения (Change Initiator) | BA-001 | Инициирует PR-поток в quality gate |
| BR-002 | Владелец политик (Policy Owner) | BA-002 | Управляет required checks и pinned versions |
| BR-003 | Исполнитель проверок (Verification Executor) | BA-003 | Запускает и завершает пакеты проверок |
| BR-004 | Аналитик доказательств (Evidence Reviewer) | BA-001, BA-002 | Анализирует сводку и логи |

## 3. Бизнес-процессы
| ID | Business Process | Триггер | Результат |
|---|---|---|---|
| BP-001 | Управление политиками и фиксацией toolchain (Policy and Toolchain Pin Governance) | Запрос на изменение policy/toolchain | Актуальный baseline quality policy |
| BP-002 | Оркестрация обязательных проверок PR (Pull Request Required Checks Orchestration) | `Pull Request Updated` | Зафиксированное merge-решение |
| BP-003 | Выполнение базового набора проверок (Baseline Verification Set Execution) | Команда оркестрации `Run Required Verification Set` | Статусы и findings по checks |
| BP-004 | Публикация сводки и доказательств (Summary and Evidence Publication) | Готовность результатов run | PR summary + ссылки на logs/artifacts |

## 4. Бизнес-сервисы и объекты

### 4.1 Бизнес-сервисы
| ID | Business Service | Предоставляется для | Реализуется через процессы |
|---|---|---|---|
| BS-001 | Сервис управления политиками (Policy Governance Service) | BR-002 | BP-001 |
| BS-002 | Сервис качественных ворот (Quality Gate Service) | BR-001 | BP-002 |
| BS-003 | Сервис верификации (Verification Service) | BR-003 | BP-003 |
| BS-004 | Сервис отчетности и доказательств (Reporting and Evidence Service) | BR-004 | BP-004 |

### 4.2 Бизнес-объекты
| ID | Business Object | Назначение |
|---|---|---|
| BO-001 | Манифесты политик (Policy Manifests) | Source of truth для policy/config |
| BO-002 | Снимок плана проверок (Check Plan Snapshot) | Актуальный план required/optional checks |
| BO-003 | Журнал решений по governance (Governance Decisions Log) | История решений по policy/toolchain |
| BO-004 | События запусков проверок (Check Run Events) | Факты выполнения и статусы check-run |
| BO-005 | Артефакты верификации (Verification Artifacts) | Логи и результаты checks |
| BO-006 | Сводки запусков (Run Summaries) | Итоговый статус и сводка по run |

## 5. События и правила (инварианты)

### 5.1 Ключевые события
| ID | Business Event | Значение |
|---|---|---|
| BE-001 | PR обновлен (Pull Request Updated) | Запуск gate-потока для PR |
| BE-002 | План обязательных проверок определен (Required Check Plan Resolved) | Сформирован check-plan |
| BE-003 | Набор проверок завершен (Required Verification Set Completed) | Завершено выполнение check-пакетов |
| BE-004 | Решение по слиянию зафиксировано (Merge Decision Recorded) | Зафиксировано решение `allowed/blocked` |
| BE-005 | Обязательная проверка завершилась ошибкой (Required Check Failed) | Зафиксирован fail обязательной проверки |

### 5.2 Бизнес-инварианты
- `BR-BL-01`: merge запрещен, если хотя бы один required check завершился со статусом `failed`.
- `BR-BL-02`: для каждого PR-run фиксируется ровно одно итоговое merge-решение (`BE-004`).
- `BR-BL-03`: публикация evidence обязательна для каждого failed check (summary + log/artifact reference).
- `BR-BL-04`: изменения policy/toolchain проходят только через versioned артефакты и историю git.

## 6. Трассировка BL к требованиям
| Процесс | FR | NFR |
|---|---|---|
| BP-001 | FR-005 | NFR-004, NFR-007 |
| BP-002 | FR-001, FR-002, FR-003, FR-004, FR-010 | NFR-001, NFR-005 |
| BP-003 | FR-006, FR-007, FR-009 | NFR-003, NFR-004 |
| BP-004 | FR-008 | NFR-002, NFR-006 |

## 7. Внешние границы
- Внешняя система событий PR: GitHub Pull Request API.
- Вне BL: прикладная реализация компонентов (AL) и инфраструктурные механизмы исполнения (TL).

## 8. Диаграмма BL
- исходник: `docs/requirements/архитектура/diagrams/BL.plantuml`
- рендер: `docs/requirements/архитектура/diagrams/BL.png`

## 9. Готовность
- [x] Акторы, роли, процессы и сервисы BL определены.
- [x] События и инварианты BL зафиксированы.
- [x] Выполнена трассировка BL -> FR/NFR.

