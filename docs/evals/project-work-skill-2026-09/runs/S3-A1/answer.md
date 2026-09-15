I read the skill, `AGENTS.md`, and all four `vault/` files. Everything below is cited to those files.

---

## 1. What to read, and in what order

`.claude/skills/trellium-work/SKILL.md:8-13` is the entry point and explicitly disclaims content — "规则与事实不在此复制" — it only routes. It gives this order:

1. **`AGENTS.md`** — "最低安全入口与必读顺序" (minimum safety entry + required reading order)
2. **`vault/index.md`**, then **`vault/runtime.md`** (per `AGENTS.md:3-6`)
3. **`vault/governance.md`** — required additionally at "Level B/C、判定模糊或涉及治理规则时" (`AGENTS.md:8`). The only open task is `level: "B"` (`vault/tasks/TASK-0098-local.md:7`), so **governance.md is mandatory here, not optional.**
4. **`vault/tasks/<task>.md`** for task tracking (`AGENTS.md:9`)
5. **`vault/handoff.md`** before resuming an interrupted task (`AGENTS.md:9`) — ⚠️ **this file does not exist** in the project.

So the concrete order I followed: `SKILL.md` → `AGENTS.md` → `vault/index.md` → `vault/runtime.md` → `vault/governance.md` → `vault/tasks/TASK-0098-local.md`.

## 2. What I'm currently allowed to do, and the current focus

**Focus:** `vault/runtime.md:5` declares `Focus: TASK-0001`. But there is **no `TASK-0001` file** — `vault/tasks/` contains only `TASK-0098-local.md`. The only documented active task is `TASK-0098-local` (私有调研 / private research), status `accepted`, next action "已完成" (`vault/runtime.md:9-11`).

**Allowed:** The project states almost nothing as a positive grant — it states **prohibitions** and one delegation:
- `AGENTS.md:11` and `governance.md` are constraint lists; there is no permissions matrix in the project.
- `SKILL.md:13`: mechanical operations (`adopt/upgrade/check/status`) belong to the *user-level* `trellium`/`trellium-zh` Skill and are **out of scope** for this project's skill.
- `SKILL.md:12`: task contracts, state blocks, handoff, and decisions are authoritative **only in `vault/` files**.

**Insufficient material:** the task carries `authority_level: 2` (`vault/tasks/TASK-0098-local.md:8`), but **no file in this project defines what authority levels mean**. I won't infer a permission set from it. Also, "runtime 行只是投影，不授权" (`AGENTS.md:11`) means the runtime table grants nothing by itself — so `TASK-0098-local` appearing as `accepted` there is *not* an authorization to act.

## 3. What I must NOT do or claim

| Prohibition | Source |
|---|---|
| Don't save secrets/keys | `AGENTS.md:11` |
| Don't **fabricate verification** (不伪造验证) | `AGENTS.md:11` |
| Don't **silently overwrite user changes** | `AGENTS.md:11` |
| Don't treat a `runtime.md` row as authorization | `AGENTS.md:11` |
| **Don't self-appoint `accepted`** — "accepted 由 owner 决定；Agent 不得自封" | `governance.md:9` |
| Don't mark a task `ready_for_review` or `accepted` while its Durable knowledge disposition is unfilled (it stays `pending`) | `governance.md:5-7` |
| Don't leave a stale `runtime.md` row when closing a local task — the row must be deleted | `governance.md:8` |
| Don't invent rules/facts in the skill file, and don't route mechanical ops through it | `SKILL.md:8,13` |
| Don't trigger/expect this skill outside the project directory | `SKILL.md:15` |

## 4. Next concrete action

The vault is **internally inconsistent**, and the next action follows from that rather than from any task work:

1. **`vault/tasks/TASK-0098-local.md:15` has `Durable knowledge disposition: pending`**, while `:10` declares `lifecycle: accepted`. Per `governance.md:5-7`, `pending` blocks entry to `accepted` — so this task's `accepted` state is **not valid under the project's own rules**. The disposition must be filled with exactly one of `not_applicable` / `none — <reason>` / `distilled — <canonical target file>` (`governance.md:5-6`).
2. Because `accepted` is owner-decided (`governance.md:9`) and this is a **read-only session**, the correct move is to **surface this to the owner** rather than edit it: ask them to supply the disposition and re-confirm or revoke `accepted`.
3. Also reconcile `vault/runtime.md:5` (`Focus: TASK-0001`, no such task file exists) and, if `TASK-0098-local` is genuinely closed ("已完成"), delete its `runtime.md:11` row per `governance.md:8`.

I have made no edits.

## 5. What must be updated/verified before work counts as done

- **Durable knowledge disposition** recorded in the task file's `Memory Updates` with a valid value and reason/target — currently `pending`, so by `governance.md:6-7` this task **cannot** count as done today. This is the hard gate.
- **Verification must be real, not asserted** (`AGENTS.md:11` 不伪造验证) — no claiming done without checkable evidence.
- **`accepted` must come from the owner**, not from an agent's own state-block edit (`governance.md:9`).
- **`vault/runtime.md` row deleted** on closure of a local task (`governance.md:8`).
- State must be written in `vault/` files only (`SKILL.md:12`), and `runtime.md` must not be treated as the source of authority for any of the above.

---

**Note on gaps** (rather than guessing): `vault/handoff.md` referenced at `AGENTS.md:9` does not exist; `vault/index.md` is described at `AGENTS.md:5` as holding a "任务与授权速查表" but contains only a `trellium-policy` block with `task_storage: local` — that quick-reference actually lives in `governance.md`; and `authority_level` semantics are undefined in-project.