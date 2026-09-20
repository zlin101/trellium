# Durable Language Profile Carrier Preregistration

Date: 2026-09-18
Task: TASK-0014

Evidence note: the design criteria were written before the implementation edits in this working session, but both remain in one uncommitted change set. The ordering is supported only by this execution record; there is no independent commit DAG evidence for preregistration timing.

## Fixed question

Profile durability is mandatory. This ablation selects only the smallest lossless project carrier.

## Arms

- R0: complete selected profile copied into `docs/engineering/profiles/<profile>.md`, with roots embedded and a one-hop conditional AGENTS route.
- R1: compressed capsule at the same path and with the same route.

Both arms must be fresh-clone durable and must not depend on discovering a machine-global Skill or reading Vault in a second hop.

## Frozen coverage checklist

1. module and workspace contracts;
2. package boundaries and layering;
3. dependency management;
4. error chains and public error boundaries;
5. resource lifecycle;
6. context and concurrency;
7. HTTP and service lifecycle;
8. tests and toolchain verification;
9. comments and public API documentation.

## Metrics and kill criteria

- Deterministic coverage: all nine categories must be recoverable from the project carrier.
- Route depth: exactly one hop from AGENTS to the carrier.
- Scope: only selected profiles and declared roots appear.
- Independence: no global Skill or Vault engineering-policy dependency.
- Size: measured only after coverage passes.

Any missing or weakened category kills that arm. R1 is selected only if deterministic assertions establish category-level semantic equivalence and it is materially smaller. Otherwise R0 wins by default. No model-session transcript is needed because the question is deterministic content preservation.

## Compatibility constraints

- Existing `docs/engineering/code-comments.md` is never overwritten or deleted.
- Existing project customization produces an upgrade proposal when upstream also changes.
- Legacy v1/v2 stamps remain readable.
- No language inference and no Git writes.

## Result recording rule

Results are appended after implementation evidence exists; this file's arms, checklist, and kill criteria do not change.

## Results — 2026-09-18

Verdict: **R0 complete profile selected**.

- R0 passes all nine frozen categories in the canonical Go profile: module/workspace, package/layering, dependencies, errors, resources, context/concurrency, HTTP/service lifecycle, tests/toolchain, and comments/API documentation. The Chinese distributed source is byte-identical to `init/protocol/profiles/<profile>.md`; the sync check enforces that relationship.
- The English package carries a localized complete-semantic rendering. Deterministic package tests require the corresponding category headings/concepts and verify actual embedded-package adoption produces only its own locale.
- R1 was not implemented: a smaller capsule had no evidence of category-level semantic equivalence beyond headings, so it failed the preregistered proof burden before size could authorize it.
- Route depth is one (`AGENTS.md` → matching `docs/engineering/profiles/<profile>.md`); roots are embedded per profile. Multi-profile tests prove roots do not leak across language files.
- Measured canonical sources: Go 12,530 bytes / 216 lines; Python 9,520 bytes / 237 lines. File complexity is accepted to preserve full engineering semantics outside the default context and outside Vault.
