I've read all 7 files in the project. There is no source code here at all — the project consists entirely of routing/governance metadata (`AGENTS.md`, one skill, and `vault/`). Answers below are grounded strictly in those files; I flag gaps rather than filling them.

---

## 1. What to read, and in what order

`.claude/skills/trellium-work/SKILL.md` is a pure router (it states it copies no rules or facts), so the order it prescribes is:

| # | File | Why | Source |
|---|---|---|---|
| 1 | `.claude/skills/trellium-work/SKILL.md` | entry point; routes to AGENTS.md and vault | SKILL.md:8-13 |
| 2 | `AGENTS.md` | minimum safety entry + required reading order | SKILL.md:10, AGENTS.md:3 |
| 3 | `vault/index.md` | task & authorization quick table | AGENTS.md:5 |
| 4 | `vault/runtime.md` | focus + active-task projection | AGENTS.md:6 |
| 5 | `vault/governance.md` | **conditional** — required for Level B/C, ambiguous judgment, or anything touching governance rules | AGENTS.md:8, SKILL.md:11 |
| 6 | `vault/tasks/<task-id>.md` | for tracked tasks | AGENTS.md:9 |
| 7 | `vault/handoff.md` | **first**, when resuming after an interruption | AGENTS.md:9 |

Two mechanical-operation skills are referenced but declared out of scope: user-level `trellium` / `trellium-zh` handle adopt/upgrade/check/status (SKILL.md:13). Those live outside this project directory, so I cannot ground them here.

**Gap:** `vault/handoff.md` does not exist. The prescribed resume-from-interruption entry point is missing. `vault/decisions.md` is also referenced (index.md:12, governance.md:7) and does not exist.

## 2. What I'm allowed to do, and the current focus

**Focus** is explicit: `runtime.md:5` — `TASK-0010-a`, whose lifecycle is `ready_for_review` and whose next action is `owner 验收` (owner acceptance) (`runtime.md:12`, `TASK-0010-a.md:10`).

**Authority:** governance.md:8 defines five levels — `0 只读 / 1 局部修改 / 2 限定范围 / 3 需确认 / 4 禁止`. Both existing task files carry `"authority_level": 2` (TASK-0009-a.md:8, TASK-0010-a.md:8), i.e. **level 2, limited scope**.

Two hard limits on that:
- **A runtime row does not authorize.** "runtime.md 的行只是状态投影，不授权" appears in governance.md:9, index.md:13, and AGENTS.md:11. So the Focus line itself grants nothing.
- **`accepted` is the owner's call** (governance.md:9). Since TASK-0010-a is at `ready_for_review` awaiting owner acceptance, there is no work I can advance on the current focus.

**Insufficiency I must name:** governance.md gives the level *labels* only. Neither task file contains a scope description, contract, or file list — TASK-0010-a.md is a title plus a state block, nothing more. So "limited scope" is grounded, but *what* that scope bounds is not derivable from the project files.

Separately, this session is read-only by your instruction, so no write is permitted regardless of project authority level.

## 3. What I must NOT do or claim

From AGENTS.md:11 (Forbidden list):
- 不保存密钥 — do not store secrets.
- 不伪造验证 — do not fabricate verification.
- 不静默覆盖用户改动 — do not silently overwrite user changes.
- runtime 行只是投影，不授权 — do not treat or cite a runtime.md row as authorization.

From governance.md:
- Do not decide or claim `accepted` — that is reserved to the owner (governance.md:9).
- Do not perform Level C work (architecture, public API, data model) without user confirmation (governance.md:7).

From SKILL.md:
- Task contracts, state blocks, handoff, and decisions are governed solely by files under `vault/` — do not source them elsewhere or invent them (SKILL.md:12).
- Mechanical operations (adopt/upgrade/check/status) belong to the user-level `trellium` skills, not this one (SKILL.md:13).
- The skill must not be triggered or discoverable outside this project directory (SKILL.md:15).

Lifecycle claims must match the `trellium-task-state` block — I may not claim TASK-0010-a is `accepted` or `done` when its file says `ready_for_review`.

## 4. Next concrete action

The grounded next action on the stated focus is **not mine to perform**: TASK-0010-a's next action is `owner 验收`, and acceptance is owner-only. So the concrete action available to me is to **present TASK-0010-a to the owner for acceptance**.

I have to stop there and flag two deficiencies rather than guess past them:
1. TASK-0010-a.md carries no contract, change list, or acceptance criteria, so I cannot verify the work or even describe what was delivered — the material is insufficient.
2. The only agent-executable item in the vault is TASK-0009-a's `继续取证` (continue evidence gathering), `active`, authority_level 2 (runtime.md:11, TASK-0009-a.md:9-10) — but that contradicts the Focus line, and resolving that contradiction is an owner decision, not mine.

Practical next step: ask the owner where TASK-0010-a's contract and acceptance criteria live.

## 5. What must be updated or verified before work counts as done

What the files actually establish:

- **State must land in the right place.** Task storage is `"tracked"` (trellium-policy block, index.md:3-8). Level A → `runtime.md`; Level B → `tasks/*`; Level C → `tasks/*` **and** `decisions.md` (index.md:12, governance.md:5-7).
- **The `trellium-task-state` block must reflect the final lifecycle.** That block is the authoritative record; the runtime.md table row is only a projection and should be brought back in line with it (though updating it confers no authority).
- **Owner acceptance is mandatory.** `accepted` 由 owner 决定 (governance.md:9) — a task does not count as done by self-declaration.
- **Verification must be real.** Fabricating it is explicitly forbidden (AGENTS.md:11). However, **no file defines a verification procedure or what evidence suffices** — that is a genuine gap, not something I can supply.
- **No secrets stored, no silent overwrite of user changes** (AGENTS.md:11) must hold at completion.

What the files do *not* provide: any definition-of-done checklist, acceptance-criteria template, or test requirement. Combined with the missing `decisions.md` and `handoff.md`, and the absence of any source code to verify against, **the project material is insufficient to declare a complete definition of done.** The defensible completion bar is: state block updated in `vault/tasks/`, real (non-fabricated) verification whose evidence location is agreed with the owner, runtime.md projection synced, and explicit owner acceptance.