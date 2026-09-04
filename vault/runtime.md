# Runtime Context

## Current Phase

Self-hosting pilot: the collaboration layer now maintains the Trellium repository itself.

## Focus

- TASK-0002

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | Run the self-hosting pilot and collect K1-K4 shadow evidence. | active | Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`. |
| TASK-0002 | Publish the existing 2026.09.3 tag as a GitHub Release. | active | Run pre-release checks, create the Release, and verify latest resolution. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

## Current Progress

- TASK-0001: adopted the repo in tracked mode, created the shadow-run ledger, ran the first lifecycle transition (draft -> active), first handoff recorded.
- TASK-0002: user approved the K4 policy correction and GitHub Release creation; release verification is in progress.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- Adopted Trellium into its own repository (tracked mode, protocol 2026.09.3).
- Created TASK-0001 (self-hosting pilot) and `vault/details/shadow-run-2026-09.md`.
- Unignored `AGENTS.md` and `vault/` in `.gitignore` (user-approved).
- Started TASK-0002 to publish the existing 2026.09.3 tag; corrected K4 setup to measurement-only.

## Known Risks

- Single-developer pace may produce fewer than 5 real TASKs quickly; coverage grows only with real work, never manufactured.

## Required Checks

```bash
python3 scripts/trellium.py check . --format json
```

## Next Steps

- Continue TASK-0001: real work creates the remaining TASKs, transitions, and the second handoff.
- Complete TASK-0002: create and verify the GitHub Release for 2026.09.3.
