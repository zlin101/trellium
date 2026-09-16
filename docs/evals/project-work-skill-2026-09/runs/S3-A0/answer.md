I've read all five files. Here are the answers, each grounded in the project's own text.

---

## 1. What to read, and in what order

`AGENTS.md:3-9` is the only reading-order instruction in the project:

1. `vault/index.md` — described as "含任务与授权速查表" (contains the task & authorization quick-reference)
2. `vault/runtime.md`
3. **Conditionally** — `vault/governance.md`, when the task is "Level B/C、判定模糊或涉及治理规则" (Level B/C, ambiguous judgment, or touching governance rules)
4. **Conditionally** — the task file under `vault/tasks/` for any tracked task
5. **Conditionally** — `vault/handoff.md` *first*, when resuming from an interruption

For this project the conditional branches are not optional: `vault/tasks/TASK-0098-local.md:6` declares `"level": "B"`, so `governance.md` is mandatory, and the task file itself is mandatory. Effective order: **AGENTS.md → index.md → runtime.md → governance.md → tasks/TASK-0098-local.md**.

Two discrepancies in the reading map itself:
- `AGENTS.md:5` says the quick-reference table is in `index.md`; it is actually in `governance.md:3-9`. `index.md` only holds a policy block (`vault/index.md:3-8`: `task_storage: "local"`).
- `vault/handoff.md` **does not exist** in the project, though `AGENTS.md:9` designates it as the interruption-recovery entry point.

## 2. What I'm allowed to do, and the current focus

**Allowed — the files grant nothing positive.** There is no permission model, no capability list, and no statement of "you may do X" anywhere in the project. The only operative constraints are negative: the Forbidden list (`AGENTS.md:11`) and the governance rules (`governance.md:5-9`). I should not infer a grant of authority that isn't written. The one affirmative signal is `vault/index.md:7` — `"task_storage": "local"` — meaning task state lives in local task files, which is why `governance.md`'s local-task rules apply.

**Focus — declared, but broken.** `vault/runtime.md:5` declares `Focus: TASK-0001`. No file for TASK-0001 exists anywhere in the project — the only file under `vault/tasks/` is `TASK-0098-local.md`. The single row in the Active Tasks table (`runtime.md:11`) is `TASK-0098-local | 私有调研 (private research) | accepted | 已完成 (completed)`. **The material is insufficient to state a real current focus**: the declared focus has no artifact behind it, and the only tracked task is marked already completed.

## 3. What I must NOT do or claim

From `AGENTS.md:11`:
- Do not save secrets (不保存密钥)
- Do not fabricate verification (不伪造验证)
- Do not silently overwrite user changes (不静默覆盖用户改动)
- **`runtime.md` lines are projections only, not authorization** (runtime 行只是投影，不授权) — I must not treat the `accepted` status in `runtime.md:11` as permission to do anything.

From `governance.md`:
- **`accepted` is decided by the owner; an Agent must not confer it on itself** (`governance.md:9`).
- A local task whose Memory Updates "Durable knowledge disposition" is unfilled counts as `pending` and **must not enter `ready_for_review` or `accepted`** (`governance.md:5-7`).

I also must not claim meaning the project never defines: `authority_level: 2` (`TASK-0098-local.md:7`) has no definition in any file here, so I can't assert what authority it confers. `"level": "B"` is defined only insofar as it triggers the `governance.md` read.

## 4. Next concrete action

The project's own rules put the tracked task in an illegal state, and that is what any next action has to resolve:

- `TASK-0098-local.md:15` reads `Durable knowledge disposition: pending` — i.e. unfilled.
- Yet `TASK-0098-local.md:9` declares `"lifecycle": "accepted"`, and `runtime.md:11` repeats `accepted`.
- `governance.md:5-7` says a pending disposition forbids `accepted`; `governance.md:9` says only the owner can confer `accepted`.

So the concrete actions the project demands, in order: **(a)** the owner decides whether `accepted` was legitimate, **(b)** the disposition gets filled with exactly one of `not_applicable` | `none — <理由>` | `distilled — <canonical 目标文件>`, **(c)** once the task closes, the `runtime.md:11` row is deleted (`governance.md:8`).

**In this session I cannot take any of them** — this is a read-only session and each would write to a file. The only concrete action available to me is to report the contradiction to the owner and wait. Two further items need owner input: the missing `vault/handoff.md`, and the dangling `Focus: TASK-0001` with no task file.

## 5. What must be updated or verified before work counts as done

Grounded in `governance.md` and `AGENTS.md`, for a local task in this project:

| # | Requirement | Source |
|---|---|---|
| 1 | Memory Updates → "Durable knowledge disposition" filled with exactly one of `not_applicable` / `none — <理由>` / `distilled — <canonical 目标文件>`. Pending or blank blocks `ready_for_review` and `accepted`. | `governance.md:5-7` |
| 2 | `accepted` conferred by the **owner**, never self-assigned. | `governance.md:9` |
| 3 | On closing the task, the corresponding `runtime.md` row is deleted. | `governance.md:8` |
| 4 | Any verification claimed is real, never fabricated. | `AGENTS.md:11` |
| 5 | No user changes silently overwritten. | `AGENTS.md:11` |

Point 5 of that list is what makes this task's current "accepted / 已完成" status untrustworthy: the disposition is still `pending`, so by the project's own checklist the work does **not** count as done, regardless of what `runtime.md` projects.

---

**Insufficiencies, stated explicitly:** the project contains no code, no build config, no tests, no VCS, no CLAUDE.md, and no definition of `authority_level` or of the `trellium-*` schema beyond `schema_version: 1`. Anything about *what the work actually is* — beyond the label 私有调研 — cannot be answered from these files. I invented nothing above; where the files are silent or contradictory, I've said so rather than filled the gap.