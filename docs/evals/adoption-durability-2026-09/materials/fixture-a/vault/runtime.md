# Runtime Context

## Current Phase

Trellium adoption recorded on 2026-09-18.

## Focus

- ADOPTION

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| ADOPTION | Maintain the Agent collaboration layer. | active | Update `vault/project.md` with durable facts. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

Acceptance: `AGENTS.md`, `vault/`, and `skills/agent-task/SKILL.md` exist and route future Agents to project memory.

Required Check: `python3 trellium.py adopt <target> --dry-run` from a Trellium checkout or Skill package, when available.

## Current Progress

- Agent collaboration layer has been initialized or refreshed.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- Added Trellium project memory files.

## Known Risks

- Replace template text with project facts as the project evolves.

## Required Checks

```bash
find vault -maxdepth 2 -type f | sort
```

## Next Steps

- Update `vault/project.md` with durable project facts.
- Update `vault/governance.md` only when project-specific governance differs from the default.
