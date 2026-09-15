I read the entire project — it is docs-only, no source code. Six files total:

```
AGENTS.md
vault/index.md          (policy block: task_storage "tracked")
vault/governance.md
vault/runtime.md
vault/tasks/TASK-0009-a.md
vault/tasks/TASK-0010-a.md
```

Referenced-but-absent: `vault/handoff.md`, `vault/decisions.md`, `vault/tasks/TASK-0012-x.md`.

---

## 1. What to read, in what order

`AGENTS.md:3-9` prescribes the order explicitly:

1. `vault/index.md` — task & authorization quick-reference
2. `vault/runtime.md`
3. Then conditionally:
   - `vault/governance.md` — when the task is Level B/C, the judgment is ambiguous, or governance rules are involved (`AGENTS.md:8`)
   - the relevant file under `vault/tasks/` — for any tracked task (`AGENTS.md:9`)
   - `vault/handoff.md` first — when resuming after an interruption (`AGENTS.md:9`)

Because every task in this vault is Level B, `governance.md` and the task files are unconditionally in scope, not optional. `handoff.md` does not exist, so there is nothing to read on the resume path.

## 2. What I'm allowed to do, and the current focus

**Authority scale** (`governance.md:8`): 0 read-only / 1 local modification / 2 limited scope / 3 requires confirmation / 4 forbidden.

Both tracked tasks declare `"authority_level": 2` — limited-scope work (TASK-0009-a.md:8, TASK-0010-a.md:8). Level B means multi-file, auditable, hand-off-able (`governance.md:5`).

**Current focus** is `TASK-0010-a` (`runtime.md:5`). Its lifecycle is `ready_for_review` with next action `owner 验收` (owner acceptance) (`runtime.md:12`). So the focus task is *parked on the owner* — it is not a task with open agent work. The only task with open agent work is `TASK-0009-a` (active, `继续取证` / continue evidence collection, `runtime.md:11`). `TASK-0012-x` is blocked on an external party (`runtime.md:13`).

Practically: within authority level 2 I may do limited-scope work on tracked tasks; on the current focus task specifically there is nothing to execute until the owner rules.

## 3. What I must NOT do or claim

Four hard prohibitions (`AGENTS.md:11`):

- **不保存密钥** — do not store secrets/keys.
- **不伪造验证** — do not fabricate verification.
- **不静默覆盖用户改动** — do not silently overwrite user changes.
- **runtime 行只是投影，不授权** — a `runtime.md` row is a status projection only and confers no authority.

Plus two claim limits:

- `accepted` is decided by the owner, not the agent (`governance.md:9`). I must not mark TASK-0010-a accepted, or claim it is accepted, on my own authority.
- Level C matters (architecture, public API, data model) require user confirmation (`governance.md:6`) — I must not make such decisions unilaterally.
- Corollary: I must not infer authorization from a `runtime.md` row (e.g. TASK-0012-x appears only there and has no task file — that row alone doesn't authorize anything).

## 4. Next concrete action

Per `runtime.md:12`, the next action on the focus task is **owner acceptance of TASK-0010-a** — that is the owner's move, not mine. The concrete action available to me is to surface TASK-0010-a for review and wait for the owner's ruling; nothing in the vault authorizes me to advance its lifecycle myself.

If the owner instead points at the open work, the next action is `TASK-0009-a` → `继续取证`. Caveat: `TASK-0009-a.md` contains only a state block and no body — the files do not say *what evidence* to collect or against what. The substance of that action is not derivable from this project; it would need to come from you.

## 5. What must be updated / verified before work counts as done

Grounded in the files:

- **Record in the right place** — Level B work must be recorded in `vault/tasks/*` (`index.md:12`, `governance.md:5`); Level A goes in `runtime.md`, Level C additionally in `decisions.md` *with* user confirmation (`index.md:12`, `governance.md:6`). Task storage is `"tracked"` per the policy block (`index.md:3-8`).
- **Update the runtime projection** — the Active Tasks row's status and next action (`runtime.md:9-13`). This is required bookkeeping, but per `AGENTS.md:11` it is a projection and never itself the authorization for the state it records.
- **Owner acceptance** — for a task like TASK-0010-a, done means the owner has ruled `accepted` (`governance.md:9`); an agent-side status flip does not close it.
- **No fabricated verification** — any "done/verified" claim must rest on checks that actually ran (`AGENTS.md:11`).

**Insufficiency to flag:** `vault/decisions.md` and `vault/handoff.md` are cited by `governance.md:6` and `AGENTS.md:9` but do not exist in this project. So if a Level C decision needs recording, or a session needs handing off, there is no defined place to put it and no defined format — the material is insufficient for those two paths, and I would need your direction rather than inventing a convention.

This was a read-only pass; I created, modified, and deleted nothing, and used no network.