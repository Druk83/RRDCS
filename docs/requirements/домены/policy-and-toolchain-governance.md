# Домен: Управление политиками и цепочкой инструментов (Policy and Toolchain Governance)

## Назначение домена

Домен задает и поддерживает единый контракт качества для всей системы RRDCS:
- какие проверки (checks) обязательны для допуска в `main`;
- какие политики качества (quality policy), пороги и правила применяются;
- какие версии среды исполнения (runtime) и цепочки инструментов (toolchain) считаются допустимыми.

Цель домена — обеспечить воспроизводимость и управляемость правил качества во времени.

- **slug:** policy-and-toolchain-governance
- **title:** Управление политиками и цепочкой инструментов (Policy and Toolchain Governance)
- **type:** supporting
- **status:** active
- **scope_in:**
  - Управление обязательными правилами качества (манифесты и политики, `manifest/policy`) в репозитории.
  - Управление фиксированными версиями среды исполнения (runtime) и цепочки инструментов (toolchain) для воспроизводимости.
  - Определение состава обязательных и опциональных проверок (required/optional checks) и правил их эволюции.
  - Контроль изменений политик (`policy`) через PR-процесс и историю git.
  - Управление профилем интеграции репозитория (Repository Integration Profile): `enforcement_mode`, `required_checks`, `rollout_channel`.
  - Управляемое распространение и откат версий policy/profile по группам репозиториев.
- **scope_out:**
  - Исполнение проверок в runtime (домен `verification-packages`).
  - Оркестрация pipeline и merge-решение (домен `quality-gate-orchestration`).
  - Публикация и хранение результатов проверок (домен `reporting-and-evidence`).
- **actors:**
  - Технический лидер и архитектор (Tech Lead and Architect) — владелец политик (`policy`) и критериев качества.
  - Разработчик (Developer) — предлагает изменения правил через PR.
  - Система непрерывной интеграции (Continuous Integration System) — использует политики (`policy`) как источник конфигурации.
- **owned_data:**
  - `QualityPolicy`: `policy_id`, `required_checks`, `thresholds`, `effective_from`.
  - `ToolchainPin`: `tool_name`, `version`, `scope`, `update_policy`.
  - `GovernanceDecision`: `decision_id`, `change_reason`, `approved_by`, `approved_at`.
  - `RepositoryIntegrationProfile`: `repository_slug`, `profile_version`, `enforcement_mode`, `rollout_channel`.
- **requirements_refs:**
  - FR-005
  - FR-011, FR-012
  - NFR-004, NFR-005, NFR-007
  - NFR-009
- **interfaces:**
  - `-> quality-gate-orchestration` (sync): предоставление политик (`policy`) и закрепленных версий (`pinned versions`).
  - `-> verification-packages` (sync): предоставление baseline параметров проверок.

## Что делает домен

1. Определяет состав обязательных проверок (`required checks`) и критерии их успешного прохождения.
2. Управляет политиками качества (quality policy): пороги, baseline и правила эволюции.
3. Фиксирует версии среды исполнения (runtime) и инструментов (`pinned versions`) для стабильного результата.
4. Обеспечивает изменение правил через PR и историю git.
5. Управляет onboarding новых репозиториев через профиль интеграции и staged rollout.
   - Первый rollout выполняется на одном pilot-репозитории.
   - Каналы `wave` и `global` включаются только после стабилизации pilot.

## Политика малых PR (small PR)

На этапе MVP контроль размера PR работает как warning-only policy.

- Основная метрика: churn = additions + deletions.
- Порог для code PR: 100 changed lines.
- Docs-only PRs считаются отдельно и не блокируют merge на первом этапе.
- Результат проверки публикуется в PR summary и artifact log.

## Что домен не делает

1. Не запускает линтеры/сканеры/тесты (это `verification-packages`).
2. Не принимает финальное решение о merge (это `quality-gate-orchestration`).
3. Не формирует и не хранит отчетные артефакты (это `reporting-and-evidence`).

