# Описание связей TL-AL-BL — RRDCS

## 0. Контекст
- **Проект:** RRDCS
- **Версия:** 1.0
- **Дата:** 2026-04-03
- **Стандарт:** ArchiMate 3.2 (межслойные и внутрислойные связи)
- **Зависимости:**
  - `docs/requirements/архитектура/сущности.md`
  - `docs/requirements/архитектура/описание BL.md`
  - `docs/requirements/архитектура/описание AL.md`
  - `docs/requirements/архитектура/описание TL.md`

## 1. Внутрислойные связи (минимальный набор)

### 1.1 Бизнес-слой (BL)
| Source | Relation | Target | Назначение |
|---|---|---|---|
| BA-001 | Assignment | BR-001 | Разработчик исполняет роль инициатора изменений |
| BA-002 | Assignment | BR-002 | Технический лидер и архитектор исполняет роль владельца политик |
| BA-003 | Assignment | BR-003 | CI-система исполняет роль исполнителя проверок |
| BR-001 | Assignment | BP-002 | Инициатор запускает оркестрацию обязательных проверок PR |
| BR-002 | Assignment | BP-001 | Владелец политик управляет baseline policy |
| BR-003 | Assignment | BP-003 | Исполнитель проверок выполняет базовый набор проверок |
| BR-004 | Assignment | BP-004 | Аналитик доказательств ведет публикацию сводки |
| BE-001 | Triggering | BP-002 | Событие обновления PR запускает оркестрацию |
| BP-002 | Triggering | BE-002 | Оркестрация формирует событие готовности check-plan |
| BE-002 | Triggering | BP-003 | Полученный check-plan запускает выполнение проверок |
| BP-003 | Triggering | BE-003 | Завершение набора проверок формирует событие completion |
| BP-003 | Triggering | BE-005 | Fail обязательной проверки формирует негативное событие |
| BE-003 | Triggering | BP-004 | Completion проверки инициирует публикацию сводки |
| BE-005 | Triggering | BP-004 | Fail проверки инициирует публикацию доказательств |
| BP-004 | Triggering | BE-004 | Публикация фиксирует итоговое merge-решение |
| BP-003 | Access | BO-004 | Формируются события запусков проверок |
| BP-003 | Access | BO-005 | Формируются артефакты верификации |
| BP-004 | Access | BO-006 | Формируются сводки запусков |

### 1.2 Прикладной слой (AL)
| Source | Relation | Target | Назначение |
|---|---|---|---|
| AC-001 | Realization | AS-001 | Оркестратор workflow реализует сервис разрешения плана |
| AC-002 | Realization | AS-001 | Разрешатель политик реализует сервис разрешения плана |
| AC-003 | Realization | AS-002 | Verification Runner реализует сервис выполнения проверок |
| AC-006 | Realization | AS-002 | Локальный CLI реализует сервис выполнения проверок |
| AC-004 | Realization | AS-003 | Движок решения о слиянии реализует merge decision service |
| AC-005 | Realization | AS-004 | Публикатор доказательств реализует evidence publication service |
| AC-001 | Realization | AI-001 | Оркестратор реализует интерфейс событий PR |
| AC-002 | Realization | AI-002 | Разрешатель политик реализует интерфейс манифестов |
| AC-003 | Realization | AI-003 | Runner реализует интерфейс пакетов проверок |
| AC-005 | Realization | AI-004 | Publisher реализует интерфейс отчетности |
| AC-006 | Realization | AI-005 | Локальный CLI реализует локальный интерфейс |
| AI-001 | Serving | AP-001 | Интерфейс событий PR обслуживает обработку PR |
| AI-002 | Serving | AP-002 | Интерфейс манифестов обслуживает разрешение проверок |
| AI-003 | Serving | AP-003 | Интерфейс пакетов обслуживает запуск проверок |
| AI-004 | Serving | AP-005 | Интерфейс отчетности обслуживает публикацию доказательств |
| AI-005 | Serving | AP-003 | Локальный интерфейс обслуживает запуск pre-check |
| AE-001 | Triggering | AP-001 | Получение PR-события запускает обработку |
| AP-001 | Triggering | AP-002 | После обработки PR разрешается check-plan |
| AP-002 | Triggering | AE-002 | Разрешение check-plan публикует событие AE-002 |
| AE-002 | Triggering | AP-003 | AE-002 запускает выполнение набора проверок |
| AP-003 | Triggering | AE-003 | Выполнение набора публикует событие completion |
| AE-003 | Triggering | AP-004 | Completion запускает расчет merge-решения |
| AP-004 | Triggering | AE-004 | Расчет решения публикует событие AE-004 |
| AE-004 | Triggering | AP-005 | AE-004 запускает публикацию доказательств |
| AP-005 | Triggering | AE-005 | Завершение публикации формирует AE-005 |
| AP-002 | Access | DO-001 | Чтение манифестов политик |
| AP-003 | Access | DO-005 | Запись артефактов верификации |
| AP-005 | Access | DO-006 | Запись сводок запусков |

### 1.3 Технологический слой (TL)
| Source | Relation | Target | Назначение |
|---|---|---|---|
| SW-001 | Assignment | TN-001 | Runtime GitHub Actions используется на Linux runner |
| SW-001 | Assignment | TN-002 | Runtime GitHub Actions используется на Windows runner |
| SW-002 | Assignment | TN-001 | Python runtime на Linux runner |
| SW-002 | Assignment | TN-002 | Python runtime на Windows runner |
| SW-002 | Assignment | TN-003 | Python runtime на рабочей станции разработчика |
| SW-003 | Assignment | TN-002 | PowerShell runtime на Windows runner |
| SW-003 | Assignment | TN-003 | PowerShell runtime на рабочей станции разработчика |
| SW-004 | Assignment | TN-001 | Bash runtime на Linux runner |
| SW-004 | Assignment | TN-003 | Bash runtime на рабочей станции разработчика |
| TS-001 | Serving | AC-001 | Checks API обслуживает оркестратор workflow |
| TS-001 | Serving | AC-004 | Checks API обслуживает движок merge-решения |
| TS-002 | Serving | AC-005 | Artifacts service обслуживает публикацию доказательств |
| TS-003 | Serving | AC-003 | Cache service обслуживает запуск проверок |
| TS-004 | Serving | AC-002 | Git repository service обслуживает разрешатель политик |
| TS-004 | Serving | AC-006 | Git repository service обслуживает локальный pre-check |
| AR-001 | Realization | AC-001 | Workflow YAML реализует оркестрацию |
| AR-002 | Realization | AC-003 | Скрипты реализуют запуск пакетов проверок |
| AR-003 | Realization | AC-002 | Манифесты политик реализуют policy-input |

## 2. Межслойные связи

### 2.1 TL -> AL
| Source | Relation | Target | Назначение |
|---|---|---|---|
| TS-001 | Serving | AC-001 | Checks API обеспечивает публикацию статусов orchestration |
| TS-001 | Serving | AC-004 | Checks API обеспечивает фиксацию merge-решения |
| TS-002 | Serving | AC-005 | Artifacts service обеспечивает публикацию evidence |
| TS-003 | Serving | AC-003 | Cache service ускоряет execution checks |
| TS-004 | Serving | AC-002 | Git repository service предоставляет policy manifests |
| AR-001 | Realization | AC-001 | Workflow YAML реализует оркестрацию |
| AR-002 | Realization | AC-003 | Скрипты реализуют запуск check-пакетов |
| AR-003 | Realization | AC-002 | Манифесты политик реализуют policy input |

### 2.2 AL -> BL
| Source | Relation | Target | Назначение |
|---|---|---|---|
| AS-001 | Realization | BS-001 | Application service реализует policy governance service |
| AS-002 | Realization | BS-003 | Application service реализует verification service |
| AS-003 | Realization | BS-002 | Application service реализует quality gate service |
| AS-004 | Realization | BS-004 | Application service реализует reporting and evidence service |
| AS-003 | Serving | BP-002 | Merge decision service обслуживает процесс оркестрации |
| AS-002 | Serving | BP-003 | Verification execution service обслуживает процесс проверок |
| AS-004 | Serving | BP-004 | Reporting service обслуживает публикацию evidence |
| AE-004 | Triggering | BE-004 | Прикладное событие фиксирует бизнес-решение merge |
| DO-001 | Realization | BO-001 | Data object реализует манифесты политик |
| DO-005 | Realization | BO-005 | Data object реализует артефакты верификации |
| DO-006 | Realization | BO-006 | Data object реализует сводки запусков |

## 3. Сквозные цепочки трассировки
| Цепочка | BL | AL | TL |
|---|---|---|---|
| C-001 Решение о merge для PR | BP-002 | AP-001 -> AP-002 -> AP-003 -> AP-004 | AR-001 + TS-001 + TN-001/TN-002 |
| C-002 Исполнение базового набора проверок | BP-003 | AP-003 | AR-002 + SW-002 + TS-003 + TN-001/TN-002 |
| C-003 Публикация доказательств | BP-004 | AP-005 | TS-002 + AR-004 + TN-001/TN-002 |
| C-004 Управление политиками | BP-001 | AP-002 | TS-004 + AR-003 + SW-005 |

## 4. Проверка связности
- [x] Определены внутрислойные связи BL/AL/TL.
- [x] Определены межслойные связи TL -> AL и AL -> BL.
- [x] Для критичных сценариев заданы сквозные цепочки BL -> AL -> TL.
- [x] На диаграммах BL/AL/TL нет висящих сущностей без связей.
