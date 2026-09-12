## 1. Verdict

**APPROVE** for `f98d302..430de35` (4 commits: `45517ef` protocol, `1b55ace` checker/tests, `c09cab2` release/docs, `430de35` test-dedupe + vault records).

Basis: the checker change is minimal and correctly guarded; the frozen decision table is implemented faithfully in every row I could trace; distribution surfaces are byte-identical and the sync manifest digest recomputes exactly; no forbidden action (no `.gitignore`, untrack, tag, Release, CI-permission, schema-v1, or CLI change) occurs; the self-hosted gate is green when I run it myself. The one P2 below is an evidence-recordation gap, not a code defect, and it sits exactly at the gate this task is designed to stop at (`ready_for_review`, owner acceptance pending) — it should be closed *before* the owner flips the lifecycle, but it does not justify rejecting the diff.

## 2. Findings (P0/P1/P2 only)

**P2 — M6 acceptance criterion asserts "CI 全绿" [x] with no evidence anywhere in the snapshot.**
- Evidence: `vault/tasks/TASK-0007-local-task-lifecycle.md:90` — `- [x] M6 终验与 push 后 CI 全绿；任务停在 ready_for_review。（CI 结果见提交后核验记录）`; the pointer "提交后核验记录" resolves to nothing in the repository. Contradicts plan §11 (`docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md:302` "记录 run id 与真实结果"; `:312` "若不能做到，逐项列出原因，不宣称完成").
- Violates: M6 acceptance criterion; the project's own established practice, which does record run ids (`vault/tasks/TASK-0003-review.md:20` run `34181086563`; `vault/tasks/TASK-0005-…md:72`; `vault/details/shadow-run-2026-09.md:37`).
- Fix direction: record the real run id + result in the shadow ledger / task Verification section before owner acceptance, or demote the M6 checkbox to `[ ]` with the pending reason. Nothing in `scripts/` needs to change.

Not counted as findings (below P2, recorded for transparency):
- Plan §8.6 names "local accepted row + missing TASK"; `test_local_closed_row_without_task_file_is_closed_local_error` (`scripts/test_trellium.py:1713` area) uses `superseded`. Same `row_status in closed_lifecycles` branch, and §8.7's "accepted 与 superseded 至少各覆盖一次" is met (`test_local_closed_task_without_row_passes` covers both) — coverage nuance only.
- Both READMEs state the disposition gate blocks `accepted` only, omitting the protocol/template rule that `pending` also blocks `ready_for_review`. EN and ZH agree with each other, so plan §9.3 (双语一致) holds; the normative files (`init/protocol/20-governance.md:206`, both `tasks/README.md` templates, both `agent-task/SKILL.md` templates) state it correctly.
- Deliberate semantic loosening an owner should accept consciously: in `local` projects a mistyped or locally-lost runtime pointer is now a warning with exit `0` (was an error). This is pre-registered in the frozen decision table (row 5), recorded in D-0006, scoped to `local_mode` only (tracked/policy-missing paths are byte-for-byte the old branch), and the message carries the no-authority clause.

No P0 or P1 findings.

## 3. Out-of-scope / authority / public API & schema

- **Out-of-scope changes: none.** All 41 files map to authorized surfaces (protocol, templates, checker, focused tests, `VERSION`, `MIGRATIONS`, bilingual READMEs, sync snapshots, self-hosted vault). Extra vault files beyond the "three-file small diff" (`vault/handoff.md`, `vault/runtime.md`, task file, new review ledger, new `vault/details/task-0007-w-group-records.md`) are protocol-mandated bookkeeping and the F1 fix, not scope creep. `docs/evals/` untouched (0 files), as the Memory Updates line itself requires.
- **Authority violations: none.** No `.gitignore`/`git rm --cached`/batch backfill; no tag (repo has zero tags), no Release, no CI/dependency/permission change; no network or real GitHub in tests (fixtures are local temp dirs + `git init`/`git add` only); lifecycle stops at `ready_for_review` and does not self-accept. The W-group gate conclusion follows the pre-registered "同效取小" rule (W1≡W2 → W1; W0 3/3 recorded as Inconclusive, not No-Go).
- **Unapproved public API/schema changes: none.** CLI subcommand set unchanged (5 `add_parser` calls before and after; no new flags); `trellium-task-state` schema v1 untouched — `grep -ci disposition` returns 0 in all three checker copies, confirming the gate is a human gate and not a second source of truth. `check_runtime_projection` gained a parameter but is internal, with exactly one call site per copy, passing the parsed policy explicitly as plan §7.1 requires.

## 4. Verification claims — classification

| Claim | Class |
| --- | --- |
| HEAD = `430de35`, tree clean, 4 commits, 41 changed files | **fresh** (re-ran) |
| All three `trellium.py` copies are one blob (`238f4a4`); both `protocol-source/` trees identical | **fresh** |
| `manifest.json` `source_sha256` = `f159356b…` over 17 files, both packages | **fresh** (recomputed with the repo's own `source_digest` algorithm) |
| Self-hosting gate: `check . --format json` → exit 0, 0 errors / 0 warnings | **fresh** |
| Test arithmetic: base 76 → head 88 in `test_trellium.py` (+5 +6 = 87 → 99); `VaultCheckTest` = 37 methods; `LocalProjectionTest` = 12 | **fresh** (static method counts only) |
| "既有 87 项测试零退化" (no removals/degradations) | **fresh** at the count level; "all 99 pass" remains **unverified** (not run — the suite writes fixture files, and this session is read-only) |
| Checker behaviors asserted by the 12 new tests (warning text layers, dedupe, exit codes) | **unverified** — I traced every branch statically against the decision table and found no mismatch, but did not execute them |
| W-group ablation (9 sessions, first answers, byte counts, zero corrections) | **unverified** — transcripts are not in the snapshot |
| C0/C1/C2 characterization and preregistration ordering (ledger F2) | **unverified** — narrative only; all four commits share one timestamp, exactly as the ledger itself discloses |
| "push 后 CI 全绿" (M6) | **unverified** — no run id or result anywhere in the snapshot (see P2) |
| Everything in the pack's "Verification Boundary" | **historical/unverified** as the pack states |

## 5. Files read and commands run (all inside `/tmp/rp-eval-20260911/s1`)

Read: `scripts/trellium.py` (1650–1770, 1975–1995, plus greps at 1511–1533, 2695–2739); `scripts/sync-skills.py` (16–53); `scripts/test_trellium.py` (944–1020, 25–76); `vault/index.md` (1–25); `vault/decisions.md` (D-0006 region, 143–166); `vault/.agent-init.json`; `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md` (headings, 220–340); `vault/tasks/TASK-0007-local-task-lifecycle.md` (state block + Memory Updates + M6 lines); grep sweeps over `vault/*.md`, `vault/details/*.md`, `docs/superpowers/plans/`, `skills/*/SKILL.md`, `init/MIGRATIONS.md`, `README*.md`.

Commands: `git rev-parse HEAD`; `git log --oneline f98d302..430de35`; `git status --porcelain`; `git diff --stat/--name-status/--name-only/--check f98d302..430de35`; `git rev-parse 430de35:<file>` ×3; `git ls-tree -r` on both `protocol-source` trees; `git show f98d302:<file>` (test_trellium, .agent-init.json); `git ls-files` (+ `grep docs/`, `grep 2026-09-09`); `git log --all -- <plan path>`; `git log --oneline -- vault/.agent-init.json` and `-- vault/decisions.md`; `git tag`; `sed -n` ranges above; `grep -n/-c/-rn/-ci` for policy parser, write ops, `add_parser`, `disposition`, CI mentions, `2026.09.3`; `python3` one-liners to count `def test_` per class at base and head, to recompute `source_digest`, and to parse the check JSON; `python3 scripts/trellium.py check . --format json` (read-only — verified first that `check_project` only reads and prints); `ls docs/superpowers/plans/`; `ls scripts/`; `diff <(git ls-tree …)` on both protocol-source trees and on the two tasks-README templates.

Also run: the `code-review` **Skill**. Its result is **discarded** — it reviewed `<host-path>/git/trellium` at TASK-0008 / `2026.09.5`, outside this snapshot and outside the `f98d302..430de35` range. None of its findings are used above. No other tool ran anything outside the snapshot root; no file was created, modified, or deleted; no network access.

## 6. Questions that cannot be answered from the material

- Whether the 99 tests actually pass, and whether CI is green for `430de35` — **cannot be answered from this snapshot** (no test run performed, by design; no CI record exists in the repository). Both remain open items for the owner's acceptance, and the second is the P2 above.
- Whether the W-group ablation and C0/C1/C2 preregistration really preceded implementation — **cannot be proven from commit history** (single shared timestamp); the snapshot only shows the records exist and that the ledger discloses this gap. That adjudication belongs to the owner, as F2 already routes it.
- Everything else (scope, authority, schema/API surface, decision-table fidelity, distribution sync, self-hosting gate) was answerable and is answered above.