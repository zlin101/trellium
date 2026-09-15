I read every file in the project — it's six files, no code:

```
AGENTS.md
vault/index.md
vault/runtime.md
vault/handoff.md
vault/governance.md
vault/tasks/TASK-0099-b.md
```

Here are the answers, each grounded in those files.

## 1. What to read, and in what order

`AGENTS.md:3-9` prescribes the order:

1. **`vault/index.md`** — described as “含任务与授权速查表” (task & authority quick-reference table)
2. **`vault/runtime.md`**
3. **`vault/governance.md`** — appended whenever the task is Level B/C, the judgment is ambiguous, or governance rules are involved
4. **`vault/tasks/`** task files — for tracked tasks
5. **`vault/handoff.md`** — read *first* when resuming after an interruption (`AGENTS.md:9`)

For the situation this project is actually in (a Level B tracked task, resuming from a handoff), all five apply, in the order: index → runtime → governance → handoff → `vault/tasks/TASK-0099-b.md` (the handoff explicitly names that file at `handoff.md:10`).

**One discrepancy worth flagging:** `index.md` does not contain the promised quick-reference table — it holds only a policy comment (`vault/index.md:3-8`, `task_storage: "tracked"`). The table actually lives in `governance.md:5-9`. The reading order still works, but the pointer in AGENTS.md is stale.

## 2. What I'm currently allowed to do, and the current focus

**Allowed:** `vault/tasks/TASK-0099-b.md:8` sets `"authority_level": 2`. `governance.md:8` defines the scale — `0 只读 / 1 局部修改 / 2 限定范围 / 3 需确认 / 4 禁止` — so level 2 means **limited-scope modification**. The governance file gives only the label for level 2, not its precise boundary (e.g. which paths count as "in scope"); that is not derivable from the material, so I won't guess at it.

**Current focus:** `runtime.md:3-5` names `TASK-0099-b` as the focus — objective 上游接口对接 (`vault/tasks/TASK-0099-b.md:1`), lifecycle `active`, current slice **`M2 - adapter 实现`** (`TASK-0099-b.md:10`).

**Overriding this session:** you specified a read-only session, which supersedes level 2. Nothing gets written.

## 3. What I must NOT do or claim

From `AGENTS.md:11` and `governance.md:9`:

- **不保存密钥** — don't store secrets.
- **不伪造验证** — don't fabricate verification; the two required checks (`TASK-0099-b.md:16-19`) must actually run, not be claimed.
- **不静默覆盖用户改动** — don't silently overwrite user changes.
- **Runtime rows are projections, not authorization.** `runtime.md`'s line saying TASK-0099-b is active with a next action (`runtime.md:9-11`) does *not* by itself authorize work — `governance.md:9` states this explicitly. I must not cite runtime.md as a grant of authority.
- **`accepted` is the owner's call.** I must not mark a decision accepted myself (`governance.md:9`).
- **No Level C work without user confirmation** — architecture, public API, data model changes require confirmation (`governance.md:7`); level 3 means "needs confirmation," level 4 means forbidden (`governance.md:8`).
- **Lifecycle limits:** M1 is the only completed milestone (`handoff.md:6`). M2 is blocked on the upstream contract freezing (`handoff.md:8`) — I must not start or claim progress on M2 before that, and must not report completion beyond what's recorded.

## 4. Next concrete action

`handoff.md:9` gives it directly:

> 上游契约冻结后继续 M2；先跑 `python3 -m unittest tests.test_adapter` 与兼容性冒烟脚本

So: **wait for the upstream contract freeze (the blocker at `handoff.md:8`), then resume M2, starting with `python3 -m unittest tests.test_adapter` followed by the adapter compatibility smoke script.**

**Honest gap:** this directory contains no code and no `tests/` directory — only the six files listed above. Neither verification command can currently be executed against anything here. Whether the implementation lives elsewhere (e.g. the sibling directories under `/tmp/pws-eval/`) is not stated in the project files, so I can't confirm it from the material.

## 5. What must be updated or verified before work here counts as done

**Verified** — per `vault/tasks/TASK-0099-b.md:16-19`, Required:
- `python3 -m unittest tests.test_adapter`
- the adapter 兼容性冒烟脚本 (compatibility smoke script)

**Updated** — because this is Level B ("多文件、需审计、可能交接；记 tasks/*" — `governance.md:6`):
- the task file `vault/tasks/TASK-0099-b.md`, including its `trellium-task-state` block (level, authority_level, lifecycle, current_slice) reflecting the new state — the files don't enumerate the allowed lifecycle values, so I won't name one
- `vault/handoff.md`, following the entry format already there (Objective / Completed / In progress / Blockers / Next best action / Files to read first, `handoff.md:3-10`)
- `vault/runtime.md`, both the Focus section and the Active Tasks row

`decisions.md` is only required for Level C (`governance.md:7`); it's not applicable to TASK-0099-b, and no such file exists. Across all of it, the AGENTS.md forbidden list from §3 applies — in particular verification must be genuinely run, and `accepted` status stays with the owner.

---

**Summary of where the material falls short** rather than my guessing: (a) `index.md` lacks the table AGENTS.md says it holds; (b) level 2's exact scope boundary is undefined beyond the label 限定范围; (c) the required verification commands reference a `tests/` module and smoke script that don't exist in this directory; (d) the freeze condition for the M2 blocker has no documented signal — nothing says how I'd detect that the upstream contract is frozen.