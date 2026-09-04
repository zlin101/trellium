# Vault Index

This file routes Agents to the right project context and carries the project
policy block. Do not use it as a long project history or a second status
surface.

<!-- trellium-policy
{
  "schema_version": 1,
  "task_storage": "tracked",
  "budgets": {
    "runtime": {"max_lines": 120, "max_recent_entries": 10},
    "handoff": {"max_lines": 100, "max_entries": 3},
    "decisions": {"max_lines": 150, "max_records": 8},
    "parked": {"max_lines": 60, "max_entries": 20},
    "tasks": {"max_active_tasks": 40}
  }
}
-->

The block above is the single source for project budgets and TASK storage.
`task_storage: tracked` keeps task files in version control; `local` keeps
task files, review ledgers, and archive out of Git (Accepted conclusions must
then be distilled into `decisions.md` or other published truth). Budget
numbers elsewhere in the protocol are initialization defaults, not project
policy. A missing policy block means a legacy project: report it, and do not
substitute hidden defaults.

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

- `index.md` (this file): routing + the `trellium-policy` project policy block; no runtime state.
- `project.md`: stable project purpose, scope, boundaries, and phase.
- `runtime.md`: current state, active task pointer table (Focus + Active Tasks), checks, risks, and next steps. TASK rows are projections of each task's `trellium-task-state` block.
- `governance.md`: task levels, authority, task contracts, acceptance gates, escalation, and handoff.
- `decisions.md`: durable decision index and, before the split, full records; bodies move to `vault/decisions/D-xxxx-*.md` after indexing.
- `handoff.md`: recent transfer state for interrupted work, each entry named after its task id; live Git facts are read at resume time, not stored as authoritative.
- `parked.md`: cold index of user-parked items; read only when mentioned, never on the default path.
- `collaboration.md`: soft collaboration preferences that cannot override hard rules.
- `tasks/README.md`: task file lifecycle flow, state block, and template.
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
- Update `tasks/*` for Level B or Level C work: change the `trellium-task-state` block first, then the matching `runtime.md` row (a projection).
- Update `decisions.md` for durable decisions.
- Update `handoff.md` when interrupted or handing off.
- Record parked items in `parked.md` when the user suspends them; promote back to a task file or `runtime.md` when mentioned again.
- Move long details out of `runtime.md`.
- Check hot-file budgets when updating them; current limits live in the `trellium-policy` block above.
- When a budget is exceeded, compact: measure → classify → restructure → verify → record. Semantic judgments (Superseded / Merged / Expired) are proposals only; keep Active until the user confirms.
