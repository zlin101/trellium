# Runtime Context

## Current Phase

Self-hosting pilot: the collaboration layer now maintains the Trellium repository itself.

## Focus

- TASK-0003

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | Run the self-hosting pilot and collect K1-K4 shadow evidence. | active | Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`. |
| TASK-0002 | Publish the existing 2026.09.3 tag as a GitHub Release. | blocked | User creates the Release in GitHub UI; then verify latest resolution. |
| TASK-0003 | Execute the 2026-09-08 next-cycle plan: calibrate K1-K4 and add the self-hosting CI check. | ready_for_review | Owner reviews the K1-K4 mapping and CI scope; first GitHub-side CI run lands with the next push. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

## Current Progress

- TASK-0001: adopted the repo in tracked mode, created the shadow-run ledger, ran the first lifecycle transition (draft -> active), first handoff recorded. Reconciled coverage as of 2026-09-08: 3 real TASKs, 3 observed transitions (TASK-0002 was created directly as active), 2 recorded handoffs, 0 blocked -> active.
- TASK-0002: K4 policy corrected and local gates passed; blocked because this environment has no GitHub release client or connector.
- TASK-0003: M0 preflight verified the plan baseline; M1 reconciled the K1-K4 contract (append-only, canonical K3/K4 observation tables opened); M2 re-verified the release blocker (latest still 2026.09.2); M3 wired the read-only self-hosting check into CI for PR and `develop` push. Ready for owner review.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- Accepted the 2026-09-08 GLM plan via the owner's start instruction; created TASK-0003 (Level C, M1+M3 in scope, M4 stays with TASK-0001).
- Reconciled the K1-K4 experiment contract in the shadow ledger (canonical mapping, history preserved); updated TASK-0001 acceptance criteria.
- Added the read-only self-hosting vault check to CI and extended push triggers to `develop`; recorded durable decisions in `vault/decisions.md`.
- Drafted `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` for owner handoff; no checker, CI, release, or governance implementation was performed.
- Adopted Trellium into its own repository (tracked mode, protocol 2026.09.3).
- Created TASK-0001 (self-hosting pilot) and `vault/details/shadow-run-2026-09.md`.
- Unignored `AGENTS.md` and `vault/` in `.gitignore` (user-approved).
- Started TASK-0002 to publish the existing 2026.09.3 tag; corrected K4 setup to measurement-only.

## Known Risks

- TASK-0001's K1-K4 labels currently diverge from the canonical hypotheses in the linked 2026-09-04 plan; reconcile them without rewriting historical observations before drawing pilot conclusions.
- Single-developer pace may produce fewer than 5 real TASKs quickly; coverage grows only with real work, never manufactured.

## Required Checks

```bash
python3 scripts/trellium.py check . --format json
```

## Next Steps

- Owner: review TASK-0003 (K1-K4 mapping + CI scope); after acceptance it moves to `accepted` and TASK-0001 continues M4 long-term observation.
- Push the local commits so the CI gate's first GitHub-side run executes on `develop`.
- Unblock TASK-0002 after the user creates the GitHub Release for 2026.09.3; verify latest resolution and accept the task.
