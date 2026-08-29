# Vault Index

This file routes Agents to the right project context. Do not use it as a long project history.

## Task And Authority Cheat Sheet

- Level A, simple: low risk, one session, 1-2 files; record in `runtime.md`.
- Level B, tracked: multi-file, auditable, may need handoff; record in `tasks/*`.
- Level C, governed: architecture, public API, data model, framework, external service, security, cost, deployment, or governance-rule changes; record in `tasks/*` and `decisions.md`; needs user confirmation.
- Authority: 0 read-only / 1 local edit / 2 scoped change / 3 approval required / 4 forbidden.
- Unclear classification or governance-rule work: read full `governance.md`.

## Default Reading

For non-trivial work, read:

1. `AGENTS.md`
2. `vault/index.md` (with the cheat sheet)
3. `vault/runtime.md`

For Level B or Level C work, unclear classification, or governance-rule changes, also read:

- `vault/governance.md`

First project entry:

- `vault/project.md`

Interrupted or resumed work:

- `vault/handoff.md`

Tracked or governed work:

- active file under `vault/tasks/`

When the user mentions a parked, shelved, or suspended item:

- `vault/parked.md`

## File Responsibilities

- `project.md`: stable project purpose, scope, boundaries, and phase.
- `runtime.md`: current state, active task pointer table (Focus + Active Tasks), checks, risks, and next steps.
- `governance.md`: task levels, authority, task contracts, acceptance gates, escalation, and handoff.
- `decisions.md`: durable decision index and, before the split, full records; bodies move to `vault/decisions/D-xxxx-*.md` after indexing.
- `handoff.md`: recent transfer state for interrupted work, each entry named after its task id.
- `parked.md`: cold index of user-parked items; read only when mentioned, never on the default path.
- `collaboration.md`: soft collaboration preferences that cannot override hard rules.
- `tasks/README.md`: task file status flow and template.
- `details/*`: optional long context, created only when repeated reads justify it.

## Detail Routing

- Architecture: `vault/details/architecture.md` and `vault/decisions.md`.
- Development tools, dependencies, tests, or environment: `vault/details/development.md`.
- API contracts: `vault/details/api.md` and `vault/decisions.md`.
- Agent, LLM, prompt, or tool behavior: `vault/details/agent.md` and `vault/decisions.md`.
- Domain knowledge: `vault/details/domain.md`.
- Collaboration preferences: `vault/collaboration.md`.

## Update Rules

- Hot-file update discipline: keep section order fixed, one item per line; replace the single matching line on a status or progress change instead of rewriting whole sections.
- Update `runtime.md` after non-trivial work (the status and next action of the matching row in Active Tasks).
- Update `tasks/*` for Level B or Level C work.
- Update `decisions.md` for durable decisions.
- Update `handoff.md` when interrupted or handing off.
- Record parked items in `parked.md` when the user suspends them; promote back to a task file or `runtime.md` when mentioned again.
- Move long details out of `runtime.md`.
- Check hot-file budgets when updating them: runtime ≤ 120 lines (Recent Changes ≤ 10 entries); handoff ≤ 3 entries or 100 lines; decisions ≤ 150 lines or 8 full records; parked ≤ 60 lines or 20 entries.
- When a budget is exceeded, compact: measure → classify → restructure → verify → record. Semantic judgments (Superseded / Merged / Expired) are proposals only; keep Active until the user confirms.
