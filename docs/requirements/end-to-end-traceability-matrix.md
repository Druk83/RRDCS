# Сквозная матрица трассировки (FR/NFR -> Домены -> Сценарии -> BL/AL/TL -> Тесты)

## 1. Назначение
Документ фиксирует единую цепочку трассировки требований от бизнес-уровня до проверки в тестах:
- требования: `FR-*`, `NFR-*`;
- домены: `docs/requirements/домены/реестр.md`;
- сценарии: `docs/requirements/сценарии/*`;
- архитектура: `docs/requirements/архитектура/*` (BL/AL/TL);
- тестирование: `docs/requirements/тестирование/*`.

## 2. Трассировка функциональных требований (FR)

| REQ | Домены | Сценарии (UC) | BL/AL/TL трассировка | Тесты |
|---|---|---|---|---|
| FR-001 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AP-001, AP-002; TL: TS-004, AR-001, TIF-001 | T-001, T-002 |
| FR-002 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AP-004; TL: TS-001 | T-001 |
| FR-003 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AP-004; TL: TS-001 | T-002 |
| FR-004 | quality-gate-orchestration, verification-packages | UC-QGO-01, UC-VP-01 | BL: BP-002, BP-003; AL: AC-006, AP-003; TL: TN-003, SW-002, SW-003, SW-004, AR-002 | T-003 |
| FR-005 | policy-and-toolchain-governance | UC-PG-01 | BL: BP-001; AL: AC-002, AP-002; TL: TS-004, SW-005, AR-003 | T-009 |
| FR-006 | verification-packages | UC-VP-01 | BL: BP-003; AL: AC-003, AP-003; TL: AR-002, SW-004, TS-003 | T-001 |
| FR-007 | verification-packages | UC-VP-01 | BL: BP-003; AL: AC-003, AP-003; TL: AR-002, SW-002, TS-003 | T-004 |
| FR-008 | reporting-and-evidence | UC-RE-01 | BL: BP-004; AL: AC-005, AP-005; TL: TS-002, AR-004 | T-005 |
| FR-009 | verification-packages | UC-VP-01 | BL: BP-003; AL: AP-003; TL: TN-001, TN-002, SW-003, SW-004 | T-006 |
| FR-010 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AC-001, AS-001; TL: TS-005, AR-001, AR-002 | T-007 |
| FR-011 | policy-and-toolchain-governance | UC-PG-02 | BL: BP-005; AL: AC-007, AP-006; TL: TS-005, TS-004, AR-005 | T-011 |
| FR-012 | policy-and-toolchain-governance | UC-PG-02 | BL: BP-005, BO-007; AL: AP-006, DO-008; TL: TS-005, AR-005 | T-011 |
| FR-013 | quality-gate-orchestration, policy-and-toolchain-governance | UC-QGO-01, UC-PG-02 | BL: BP-002, BP-005; AL: AP-004, AP-006; TL: TS-001, TS-005 | T-011 |

## 3. Трассировка нефункциональных требований (NFR)

| REQ | Домены | Сценарии (UC) | BL/AL/TL трассировка | Тесты |
|---|---|---|---|---|
| NFR-001 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AP-004; TL: TS-001, SW-001 | T-001, T-002 |
| NFR-002 | reporting-and-evidence | UC-RE-01 | BL: BP-004; AL: AP-005; TL: TS-003, SW-001 | T-008 |
| NFR-003 | verification-packages | UC-VP-01 | BL: BP-003; AL: AP-003; TL: AR-002, TS-003 | T-004 |
| NFR-004 | policy-and-toolchain-governance | UC-PG-01 | BL: BP-001; AL: AP-002; TL: SW-005, TS-004, AR-003 | T-009 |
| NFR-005 | quality-gate-orchestration, policy-and-toolchain-governance | UC-QGO-01, UC-PG-01 | BL: BP-002, BP-001; AL: AC-001, AC-006; TL: TS-005, AR-001, AR-002 | T-003, T-011 |
| NFR-006 | reporting-and-evidence | UC-RE-01 | BL: BP-004; AL: AP-005; TL: TS-002, AR-004 | T-005 |
| NFR-007 | policy-and-toolchain-governance | UC-PG-01 | BL: BP-001; AL: AS-001, AP-002; TL: TS-005, AR-001 | T-007 |
| NFR-008 | quality-gate-orchestration | UC-QGO-01 | BL: BP-002; AL: AC-006; TL: AR-002, TS-003 | T-010 |
| NFR-009 | policy-and-toolchain-governance | UC-PG-02 | BL: BP-005; AL: AP-006; TL: TS-005, AR-005 | T-011 |

## 4. Контроль целостности
- Каждое `FR-*` имеет домен-владелец, минимум один `UC`, архитектурную трассировку и тест.
- Каждое `NFR-*` имеет проверяемый тестовый сценарий.
- Для multi-repo onboarding цепочка `FR-011/FR-012/FR-013 -> UC-PG-02 -> BP-005/AP-006 -> T-011` замкнута.
