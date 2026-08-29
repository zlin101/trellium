# Task Files

追踪任务和治理任务使用任务文件。

## Status Flow

```text
Draft -> Active -> Ready for Review -> Accepted
          |
          v
        Blocked
          |
          v
        Active
```

任务被替代时使用 `Superseded`。

## Naming

```text
TASK-0001-short-title.md
```

## Template

```md
# TASK-0001 - Short Title

## Status

Draft | Active | Blocked | Ready for Review | Accepted | Superseded

## Objective

## Scope

### In Scope

### Out of Scope

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`

## Capability Tags

- documentation
- testing

## Authority

Level:

Allowed:

- ...

Requires Approval:

- ...

Forbidden:

- ...

## Acceptance Criteria

- ...

## Verification

Required:

- ...

Completed:

- ...

## Execution Record

### YYYY-MM-DD - Agent: unknown

Context read:

- ...

Changes made:

- ...

Checks run:

- ...

Review and reflection:

- ...

Risks:

- ...

Next action:

- ...

## Memory Updates

- `vault/runtime.md`
- `vault/decisions.md` if durable decisions were made
- `vault/handoff.md` if interrupted or handed off
```

## Review Ledger

多轮 review 使用 `TASK-xxxx-review.md` 台账批量收敛，不逐条消息往返。
状态：`open` | `fixed` | `wont-fix`（附理由）| `needs-discussion`。
checklist 优先用任务文件的 Acceptance Criteria；`wont-fix` 与 `needs-discussion` 交还用户判断。
收敛（无 `open` 与 `needs-discussion`）后归档进任务文件 Execution Record。

```md
# TASK-0001 - Review Ledger

## Findings

- R1 · open · 一句话发现
- R2 · fixed · 一句话发现
- R3 · wont-fix · 一句话发现 · 理由

## Round 2026-01-01

- 处理说明与验证结果。
```
