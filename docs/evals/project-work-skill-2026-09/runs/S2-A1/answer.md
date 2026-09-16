I read the skill router and every file in the project (7 files total — the tree is `AGENTS.md`, `.claude/skills/trellium-work/SKILL.md`, and `vault/{index,runtime,governance,handoff}.md` + `vault/tasks/TASK-0099-b.md`). There is **no source code, no `tests/` directory, no `decisions.md`**, and it is not a git repo.

## 1. What to read, in what order

The work skill is a pure router — it contains no rules itself (`SKILL.md:8-13`). It directs you to `AGENTS.md`, which fixes the order (`AGENTS.md:3-9`):

1. `.claude/skills/trellium-work/SKILL.md` — entry point / router
2. `AGENTS.md` — "最低安全入口与必读顺序"
3. `vault/index.md` — first required read per `AGENTS.md:5`
4. `vault/runtime.md` — second required read per `AGENTS.md:6`
5. `vault/governance.md` — **mandatory here**, because `TASK-0099-b.md:6` declares `"level": "B"` and `AGENTS.md:8` says Level B/C requires it
6. `vault/handoff.md` — required for resuming after interruption (`AGENTS.md:9`); relevant since this session is a fresh look at an in-flight task
7. `vault/tasks/TASK-0099-b.md` — the task contract; `handoff.md:10` names it as "Files to read first"

## 2. What is allowed now, and the current focus

- **Focus** is unambiguous and stated in two places: `runtime.md:5` (`## Focus: TASK-0099-b`) and the active-tasks row at `runtime.md:9-11`. Only one task exists.
- **The task's own scope**: objective "上游接口对接" (`TASK-0099-b.md:1`), current slice **M2 — adapter 实现** (`TASK-0099-b.md:11`).
- **Authority**: `"authority_level": 2` (`TASK-0099-b.md:8`), which `governance.md:8` defines as **限定范围** — scoped, in-scope modification. So a work session on this task may modify within that task's scope; not unrestricted write access.
- **Record-keeping duty**: Level B means record in `tasks/*`, not just `runtime.md` (`governance.md:6`). `index.md:7` sets `"task_storage": "tracked"`, confirming task state lives in the task file.
- For **this specific session**, your instruction overrides the project: read-only, no file creation/modification/deletion, no network.

## 3. What must NOT be done or claimed

From the `Forbidden` line, `AGENTS.md:11`:
- 不保存密钥 — never store secrets.
- 不伪造验证 — never fabricate verification results.
- 不静默覆盖用户改动 — never silently overwrite user changes.
- **runtime 行只是投影，不授权** — a line in `runtime.md` is a status projection, not permission. Reinforced at `governance.md:9`: `runtime.md` 的行只是状态投影，不授权；**accepted 由 owner 决定**. So you must not claim the task is accepted/authorized because `runtime.md:11` says `active` — acceptance is the owner's call.

Lifecycle/scope limits:
- `lifecycle: "active"` with a blocker (`handoff.md:8`) — you must not claim M2 is done, nor mark the task complete; it is mid-slice, not finished (`TASK-0099-b.md:9-10`).
- Stay inside authority level 2 (限定范围); level 4 is 禁止 and level 3 需确认 (`governance.md:8`).
- Level C matters (architecture, public API, data model) require `decisions.md` **and user confirmation** (`governance.md:7`) — so an adapter change that touches a public API would be Level C, needing confirmation, not a routine Level B step.

## 4. Next concrete action

The task is blocked, so the next action is a **blocker check**, not implementation:

1. Determine whether the upstream v2 contract has been frozen — `handoff.md:8`: "Blockers: 等待上游接口冻结（上游 v2 契约未定）". Nothing in the vault records it as frozen, and the handoff is dated 2026-09-14 (one day before today, 2026-09-15).
2. **If not frozen**: no M2 work. The correct move is to surface the blocker to the owner and stop.
3. **If frozen**: resume M2 (`handoff.md:9` — "上游契约冻结后继续 M2"), and per `handoff.md:9` run first:
   - `python3 -m unittest tests.test_adapter`
   - the `adapter 兼容性冒烟脚本`

   Both are also the required verification at `TASK-0099-b.md:16-20`.

Caveat on insufficiency: **neither `tests/test_adapter.py` nor the smoke script exists anywhere in this directory** (verified by full recursive listing), and there is no adapter source to adapt. So the resume path cannot actually be executed from this project as it stands — that gap needs to be raised with the owner rather than worked around.

## 5. What must be updated/verified before work counts as done

- **Verification, not assertion**: both items in the task's `## Verification / Required` block must actually pass (`TASK-0099-b.md:16-20`): the unittest run and the compatibility smoke script. Fabricating either violates `AGENTS.md:11`.
- **Task state updated**: because `task_storage` is `tracked` (`index.md:7`) and this is Level B (`governance.md:6`), `vault/tasks/TASK-0099-b.md` must be updated — the `trellium-task-state` block (`lifecycle`, `current_slice`) and its status.
- **Runtime projection updated**: `vault/runtime.md` Active Tasks row (status / Next Action) must be brought in line.
- **Handoff updated**: `vault/handoff.md` for a new resume point — Completed / In progress / Blockers / Next best action, per its existing structure (`handoff.md:3-10`).
- **Level-C escalation if applicable**: if any part of the work touches architecture, public API, or data model, it additionally requires a `decisions.md` entry and user confirmation (`governance.md:7`). Note `decisions.md` does not exist yet — it would have to be created, which needs the owner's go-ahead.
- **No out-of-scope writes**: changes must stay within the authority_level 2 envelope, with no silent overwrites of user changes.

## Insufficiencies to flag rather than guess

- `AGENTS.md:5` promises `vault/index.md` contains a "任务与授权速查表", but `index.md` holds only the `trellium-policy` block — the cheat sheet lives in `governance.md` instead. I used `governance.md` as the authoritative source for level/authority definitions.
- The verification commands reference code that does not exist in the project directory.
- `SKILL.md:13` routes mechanical operations (adopt/upgrade/check/status) to user-level `trellium`/`trellium-zh` skills, which are not present in this session — so those operations are not available to me here.
- Nothing in the vault states whether the upstream v2 contract is frozen as of today; that must be confirmed externally, not inferred.