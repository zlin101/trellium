# Runtime Context

## Current Phase

Replace with the current phase.

## Focus

- TASK-0001

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | Replace with a one-line objective. | active | Replace with the next action. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

## Current Progress

- Replace with short current state for the focused task.

## Constraints

- Keep this file short.
- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not store secrets.

## Recent Changes

- Replace with recent relevant changes.

Keep at most 10 entries; earlier ones merge into task-file execution history
during compaction.

## Known Risks

- Replace with known risks.

## Required Checks

```bash
replace-with-project-check
```

## Next Steps

- Replace with next useful action.
