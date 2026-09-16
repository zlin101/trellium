# Code Comment Routing — Results

Status: M1 complete. Preregistration commit: `e4f58c9`.

## Structural Measurements

The frozen Chinese policy is 4,413 bytes / 96 lines. `diff` confirms that the policy embedded in R0 is byte-identical to the standalone R1/R2 policy after removing the arm-only preamble.

| Arm | Unconditional entry-path bytes | Source-task bytes after following the route | Routing hops | New project rule files | Vault route owner |
| --- | ---: | ---: | ---: | ---: | ---: |
| R0 inline | 4,562 | 4,562 | 0 | 0 | 0 |
| R1 direct | 254 | 4,667 | 1 | 1 | 0 |
| R2 two-hop | 327 (`122 + 205`) | 4,740 | 2 | 1 | 1 |

Interpretation:

- R1 reduces unconditional entry material by 4,308 bytes (94.4%) relative to R0. It pays a 105-byte route/preamble overhead only when the policy is actually relevant.
- R2 has the same policy and project-file count as R1 but adds 73 unconditional bytes, one routing hop, and a second editable route owner in `vault/index.md`.
- R0 remains slightly smaller for a source task that always needs the policy, but charges the complete policy to release, Vault, status, documentation-only, and other non-source tasks. The owner explicitly chose progressive disclosure for this class of rule.
- These are carrier measurements, not evidence that an Agent's review accuracy improves.

## Rule Classification

The owner-supplied Go document was classified without dropping a rule:

| Original area | Common core | Go adapter | Python adapter |
| --- | --- | --- | --- |
| Purpose / no comment-rate target | yes | — | — |
| Why, domain rules, invariants, boundaries, safety, concurrency, lifecycle, deployment, workaround | yes | Go examples | Python async/context-manager additions |
| Public API documentation | caller-visible contract | package/exported-name Doc Comment form | module/class/function/method docstring form |
| Internal comments explain why | yes | `//` examples | `#` examples |
| Comments do not replace code quality | yes | — | — |
| Infra/Kubernetes knowledge | yes | original examples remain valid | same principle applies |
| TODO/FIXME | yes | Go syntax may be used in examples | Python syntax may be used in examples |
| Synchronization and final review questions | yes | generated files and Go directives | generated files and docstrings |

Language-specific corrections/additions:

- Go: package is not an "exported identifier"; every package gets a package comment and exported declarations get Doc Comments. Identifier-leading complete sentences, zero value, concurrency, panic/blocking/resource ownership, and directive semantics stay in the Go adapter.
- Python: public API is determined by project convention, `__all__`, leading underscores, and published documentation rather than capitalization. PEP 257-style triple-double-quoted summaries, existing parameter-section style, exceptions/side effects, and avoiding signature/type-hint repetition stay in the Python adapter.
- The common core does not prescribe comment syntax, visibility syntax, or a docstring markup dialect.

## Decision

**Go: R1 direct route.**

R1 passes all frozen hard gates at the carrier level and dominates R2. R0 is rejected as the default carrier because it imposes the full policy on unrelated tasks. Implementation is authorized to proceed with:

- one conditional line in `AGENTS.md` pointing directly to the project rule;
- one project-owned `docs/engineering/code-comments.md` containing common rules plus selected language sections;
- zero engineering-policy files under `vault/`;
- explicit profile selection only; no automatic language choice in this cycle.

Residual risk: this structural ablation does not measure route-following behavior. A future real missed-route event reopens the carrier decision; it does not authorize copying the full policy into every default context without a new comparison.
