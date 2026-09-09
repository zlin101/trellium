# Runtime Context

## Current Phase

Self-hosting pilot: the collaboration layer now maintains the Trellium repository itself.

## Focus

- TASK-0001

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | Run the self-hosting pilot and collect K1-K4 shadow evidence. | active | Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`. |
| TASK-0002 | Publish the existing 2026.09.3 tag as a GitHub Release. | accepted | Closed 2026-09-08: release is live and latest resolves; title/notes demoted to optional by owner decision (D-0003). |
| TASK-0003 | Execute the 2026-09-08 next-cycle plan: calibrate K1-K4 and add the self-hosting CI check. | accepted | Closed 2026-09-08 after review round 2 and a green first CI run (34181086563). |
| TASK-0004 | Post-release validation: cold-start baseline, second-project pilot, Context Go/No-Go. | blocked | M3 No-Go adopted as D-0004; resumes (blocked -> active) when the owner provides a second real project in local mode. |
| TASK-0007 | Local TASK lifecycle close-out and clone-safe projection (2026.09.4). | ready_for_review | Implementation and independent review complete; awaiting owner acceptance and 2026.09.4 release. |
| TASK-0005 | Vault evidence quality: converge coverage counts to a single source and fix cold-start methodology. | accepted | Closed 2026-09-09 after owner review round 2 (final gate closed, six findings fixed). |
| TASK-0006 | Non-Context optimization: ablation experiments and per-candidate Go/No-Go; Evidence Receipt v0 only if M2 experiments pass. | accepted | Closed 2026-09-09 with strictly scoped conclusions: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle (direction not falsified). |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

## Current Progress

- TASK-0001: self-hosting pilot continues on real work. Coverage facts live solely in `vault/details/shadow-run-2026-09.md` (append-only event rows; dated derived snapshot — D-0005). Unmet gates: 5th real TASK, M2 second project, canonical cross-project evidence, five-question review.
- TASK-0002: 2026.09.3 Release published (tag `97d5506`, non-draft, non-prerelease) and `releases/latest` resolves to it. Accepted after the owner demoted the empty title/notes to an optional, non-gating improvement (D-0003).
- TASK-0003: M1 reconciled the K1-K4 contract (append-only, canonical K3/K4 observation tables opened); M2 re-verified the release blocker (latest still 2026.09.2); M3 wired the read-only self-hosting check into CI (write permission confined to the PR self-heal job). Accepted 2026-09-08 after review round 2 and a green first CI run.
- TASK-0004: M1 complete — S1-S7 in 7 independent cold sessions, 7/7 correct, 0 overreach, 0 stale-evidence misuse. Owner adopted the No-Go as D-0004 (no M4, no context implementation; reopen only via its three conditions). Task blocked pending a second real project for M2.
- TASK-0005: coverage counts single-sourced into the shadow ledger (D-0005); cold-start Protocol v2 isolated under `docs/evals/cold-start-v2/`. Accepted 2026-09-09 after owner review round 2 (final gate closed, six findings fixed).
- TASK-0006: M0-M2 complete — preregistration frozen before results; E0/E1/E2 ablation run (E0 4/4, E1 4/4, E2 3/4 with the designed false-positive causing the only error). Accepted 2026-09-09 with strictly scoped conclusions: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle (direction not falsified); M3 Blocked, M4 rules draft (no numeric threshold), M5 Blocked + D0-sufficient, M6 deferred.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- 2026.09.4 implemented per the local-task-lifecycle plan (TASK-0007): W-group ablation picked the single-line disposition gate; checker gained local-aware projection (`TASK_RUNTIME_LOCAL_UNRESOLVED` warning, `TASK_RUNTIME_CLOSED_LOCAL` error); 12 focused tests; version/migrations/README/snapshots synced; independent review passed with F1-F3 closed. ready_for_review.
- Owner approved the local TASK lifecycle direction; the GLM contract at `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md` passed final plan review after R1-R6 fixes (real test command, supersede safety, tracked N/A, full distribution surface, executable ablation, explicit dirty handoff). No 09.4 implementation has started.
- Owner formally accepted TASK-0005 and TASK-0006 (2026-09-09); TASK-0006 conclusions strictly scoped: E2 No-Go, E1 Inconclusive, v0 not implemented this cycle, direction not falsified; D-0004 unchanged, no Evidence Receipt decision added, M3-M6 not reopened. Focus back to TASK-0001.
- Owner review round 2 (REQUEST_CHANGES) on TASK-0005/0006: six findings fixed — TASK-0005 final gate closed; 12 raw first answers archived; M2 conclusions narrowed (E2 No-Go, E1 Inconclusive, v0 not implemented this cycle, direction not falsified); unsafe untracked golden split; 20 KB threshold removed; D-0004 reconsider_when draft rejected (D0 sufficient).

- TASK-0006 M2 ablation concluded (E1 Inconclusive — cost unmeasured; E2 No-Go — false-positive misled; 0 fresh-mislabels) — Evidence Receipt v0 not implemented this cycle, zero code changes, direction not falsified; M3-M6 conclusions delivered; task ready_for_review.

- Opened TASK-0006 (Level C) from the non-Context optimization plan; experiment preregistration frozen under `docs/evals/non-context-optimization-2026-09/` before any results were collected.
- Drafted the non-Context Vault optimization and ablation plan for GLM handoff; no candidate feature is authorized or implemented, and D-0004 remains unchanged.
- TASK-0005 (owner-mandated evidence-quality fix) ready for review: coverage counts single-sourced into the shadow ledger (D-0005), runtime no longer keeps numeric copies; cold-start Protocol v2 isolated under `docs/evals/cold-start-v2/`.
- Owner adopted the Context No-Go as D-0004 (M4 unauthorized; reopen only via its three conditions); TASK-0004 active → blocked pending the second real project for M2.
- M1 cold-start baseline complete (S1-S7, 7 independent sessions): 7/7 correct, 0 overreach, 0 stale-evidence misuse; M3 No-Go recommendation delivered to owner.

- Opened the post-release validation phase (TASK-0004, Level B): plan formalized at `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md`, M1 cold-start protocol drafted.
- TASK-0002 accepted: owner demoted Release title/notes to a non-gating optional improvement (D-0003); Codex had already verified the release live and moved it blocked -> active.
- Verified the published 2026.09.3 Release and latest resolution; TASK-0002 moved blocked → active, with title/notes completion still pending.
- Pushed the next-cycle work to `origin/develop`; first GitHub Actions run (34181086563) green: `gate` job executed the self-hosting check on push, `sync` job correctly skipped.
- TASK-0003 accepted after review round 2 (canonical K1-K4 mapping and CI scope approved; round 1 findings R1-R6 fixed).
- Accepted the 2026-09-08 GLM plan via the owner's start instruction; created TASK-0003 (Level C, M1+M3 in scope, M4 stays with TASK-0001).
- Reconciled the K1-K4 experiment contract in the shadow ledger (canonical mapping, history preserved); updated TASK-0001 acceptance criteria.
- Added the read-only self-hosting vault check to CI and extended push triggers to `develop`; recorded durable decisions in `vault/decisions.md` (D-0001/D-0002).
- Drafted `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` for owner handoff; no checker, CI, release, or governance implementation was performed.
- Adopted Trellium into its own repository (tracked mode, protocol 2026.09.3).
- Created TASK-0001 (self-hosting pilot) and `vault/details/shadow-run-2026-09.md`.
- Unignored `AGENTS.md` and `vault/` in `.gitignore` (user-approved).
- Started TASK-0002 to publish the existing 2026.09.3 tag; corrected K4 setup to measurement-only.

## Known Risks

- The PR-only snapshot self-heal push path has not yet been observed in a real GitHub PR run; develop push event routing and the read-only gate have been verified.
- The checker validates the Active Tasks table and structure but cannot see natural-language counts elsewhere; stale prose numbers need manual reconciliation (observed 2026-09-08: "3 TASKs" vs `current_task_files: 4`).
- The 2026.09.3 Release title and body remain empty; per D-0003 this is an optional improvement, not a risk to machine paths.
- Single-developer pace may produce fewer than 5 real TASKs quickly; coverage grows only with real work, never manufactured.

## Required Checks

```bash
python3 scripts/trellium.py check . --format json
```

## Next Steps

- Continue TASK-0001 (the only active task): real work accumulates canonical K1-K4 shadow evidence; reopen triggers for Context (D-0004) are observed here — register any real misjudgment or cost event in the ledger.
- Provide a second real project (local mode) to resume TASK-0004 M2; its blocked -> active transition will also complete TASK-0001's missing coverage sample.
- Context implementation stays closed per D-0004; any reopen requires the owner-approved Level C task first.
