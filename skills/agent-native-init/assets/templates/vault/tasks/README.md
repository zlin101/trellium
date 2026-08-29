# Task Files

Use task files for tracked or governed work.

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

Use `Superseded` when replaced by another task.

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

Multi-round review uses a `TASK-xxxx-review.md` ledger and converges in
batch, not through message ping-pong.
Statuses: `open` | `fixed` | `wont-fix` (with reason) | `needs-discussion`.
The checklist prefers the task file's Acceptance Criteria; `wont-fix` and
`needs-discussion` go back to the user.
Archive the ledger into the task file's Execution Record once converged (no
`open` or `needs-discussion` left).

```md
# TASK-0001 - Review Ledger

## Findings

- R1 · open · one-line finding
- R2 · fixed · one-line finding
- R3 · wont-fix · one-line finding · reason

## Round 2026-01-01

- Handling notes and verification results.
```
