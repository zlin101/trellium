# Code Comment Routing — Preregistration

Frozen: 2026-09-16, before product/template implementation.

## Decision Under Test

The code-comment standard is owner-mandated and is not subject to a feature Go/No-Go. This ablation decides only how a target project carries and discovers the standard.

## Frozen Arms

- **R0 — inline:** the complete common and selected-language rules are embedded in `AGENTS.md`.
- **R1 — direct route:** `AGENTS.md` contains one mechanical trigger that points directly to one project-owned `docs/engineering/code-comments.md`.
- **R2 — two-hop route:** `AGENTS.md` points to `vault/index.md`, which then points to the same project-owned document.

All arms use byte-identical policy content. Only the carrier and discovery path differ.

## Frozen Scenarios

1. Go-only project rooted at `.`.
2. Python-only project rooted at `.`.
3. Polyglot project: Go under `services/api`, Python under `services/model`.
4. Non-source release/Vault task where the comment policy is irrelevant.
5. Existing target already owns `docs/engineering/code-comments.md`.
6. Invalid profile root: absolute path, `..` escape, empty root, or duplicate root.

## Metrics

- unconditional bytes added to the Agent entry path;
- conditional bytes read for a source task;
- number of routing hops before the canonical policy;
- number of new target-project files;
- selected-language section accuracy;
- preservation of every owner-mandated semantic rule;
- silent overwrite count;
- path-escape count;
- number of Vault files added for engineering policy.

No behavioral Agent-session accuracy is claimed by this experiment. It is a deterministic carrier and packaging ablation. Any later claim that the route improves human/Agent correctness requires a separately preregistered behavioral experiment.

## Hard Gates

- zero loss of owner-mandated semantics;
- zero silent overwrite of an existing project rule;
- zero path escape;
- zero engineering-policy files added under `vault/`;
- a selected profile emits its own section exactly once;
- an unselected profile emits no section;
- old stamp files remain readable.

## Decision Rule

- Choose **R1** if it preserves the hard gates, has one routing hop, and its unconditional entry-path bytes are lower than R0.
- Reject **R2** if it has the same policy and conditional bytes as R1 but adds a routing hop or another editable route owner.
- Choose **R0** only if R1 cannot make the source-task trigger mechanical and reliable without a second lookup.
- Stop implementation if all carriers require a second authoritative copy or any existing project document must be overwritten.

## Contamination and Evidence Discipline

- The owner preference for routing is recorded as a product constraint, not scored as an experimental result.
- Material sizes must be measured from frozen rendered fixtures, not estimated from prose.
- Implementation may not change the arms, hard gates, or decision rule after measurements are recorded.
- Synthetic fixtures may validate mechanics but do not count as cross-project adoption evidence.
