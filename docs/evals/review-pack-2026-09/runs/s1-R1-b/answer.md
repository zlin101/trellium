Verification complete. Here is my review.

---

## 1. Verdict — **APPROVE**

The diff `f98d302..430de35` implements exactly what TASK-0007 authorizes, and every gate I could re-run passes in this snapshot: `check` 0 error/0 warning exit 0, 99 tests OK (88+5+6, of which 12 are the new focused tests), `sync-skills.py --check` in sync, `git diff --check` clean, distribution snapshots byte-identical to source, and both bundled `assets/trellium.py` copies identical to `scripts/trellium.py`.

The checker change is faithful to the frozen decision table. I probed the table's edges with throwaway fixtures (same mechanism the test suite itself uses): local + missing open pointer → `TASK_RUNTIME_LOCAL_UNRESOLVED` warning only (exit 0); local + closed row with and without the file → `TASK_RUNTIME_CLOSED_LOCAL` error; local + open task with no row → `TASK_PROJECTION_MISSING` error; row+Focus dedup collapses to one finding; tracked dangling → `TASK_RUNTIME_MISSING` error unchanged; invalid/missing policy → `POLICY_INVALID`/`POLICY_MISSING` + legacy `TASK_RUNTIME_MISSING`, local semantics not applied. Tracked and policy-missing paths are untouched as required. No forbidden surface is touched: no tag (0 tags), no `.gitignore`/CI/dependency changes, no new CLI subcommand, no schema v1 change, no network in tests.

Approval is not acceptance: M6's CI claim is unverifiable here (see §4/§6), and the two P2s below should be addressed around the owner's gate.

## 2. Findings (P0/P1/P2)

No P0, no P1.

**P2-1 — Review ledger's F3 root-cause measurement is not reproducible.**
- Evidence: `vault/tasks/TASK-0007-review.md:14` ("reviewer 实测 bf3f84b 为 124"), repeated in `vault/tasks/TASK-0007-local-task-lifecycle.md` (F3 handoff/record lines).
- Violated clause: acceptance criterion M5 ("F1/F3 已修复") — the fix is real, but the evidence cited for it is wrong; also the project's own evidence-accuracy rule (counts must trace to a single source, `vault/handoff.md` preamble).
- Facts (fresh, from blob inspection): `bf3f84b` is an ancestor commit *before* the task ("conclude M2 ablation No-Go; TASK-0006 ready for review"); its `scripts/test_trellium.py` is byte-identical to `f98d302`'s (blob `c062201`) and contains **no** `LocalProjectionTest`, so the three-module total there is 87 (76+5+6), not 124. The duplication state actually lives at `1b55ace`/`c09cab2` (`class LocalProjectionTest(VaultCheckTest)`), where `VaultCheckTest` has exactly 37 test methods, giving 76+12+37 = 125 → 136 total, which is the figure the Execution Record itself reports. Neither 87 nor 136 is 124; `124 = 87 + 37` is a reconstruction, yet it is recorded as a measurement ("实测").
- The mechanism and the fix are sound and freshly verified (Mixin refactor; 99 = 88+5+6 with no inherited re-run). Minimal fix: correct that one ledger line to cite 87 at `bf3f84b` and 136 at `c09cab2` before `accepted`.

**P2-2 — Stale *Focus* pointer to a closed local task passes silently.**
- Evidence: `scripts/trellium.py:1761-1762` (the Focus loop calls `resolve(task_id)` with no status); protocol text at `init/protocol/10-vault.md` new bullet ("closed 任务不占热路径") and `skills/trellium/assets/templates/vault/runtime.md` ("Closed local tasks … leave no row here").
- Repro (fresh): local policy, `vault/tasks/TASK-0001-*.md` with `lifecycle=accepted`, `Focus: TASK-0001`, no Active Tasks row → **zero** projection findings, exit 0.
- Violated clause: none in the frozen table — row 7 covers "accepted/superseded | 行不存在 | PASS", and the table speaks only of Active Tasks rows; the Focus line carries no lifecycle. So this is a documented-intent gap, not a table violation. Note that "fixing" it by extending `TASK_RUNTIME_CLOSED_LOCAL` to Focus pointers would expand semantics, which the task forbids without owner approval.
- Minimal fix direction: either document that Focus pointers are out of scope for the closed-local rule, or take the one-line extension to the owner as a decision point.

## 3. Scope / authority / public API

- **Out-of-scope changes:** none. Every changed file maps to an authorized surface (M1 protocol + bilingual templates, M2 checker, M3 tests, M4 VERSION/MIGRATIONS/README/sync snapshots, M5 ledger, plus the standard task Memory Updates: `vault/runtime.md`, `vault/handoff.md`, `vault/index.md`, `vault/governance.md`, `vault/tasks/README.md`, and the F1 evidence file `vault/details/task-0007-w-group-records.md`). The three self-hosting "small diff" files named in M1 are exactly the ones touched.
- **Authority violations:** none. No tag/Release, no `.gitignore`/untrack, no batch backfill, no `TASK_RUNTIME_MISSING` global downgrade (verified tracked unchanged), no policy guessing from `.gitignore` (storage comes only from the policy block), no network in tests, no synthetic fixture counted as TASK-0001 coverage. The self-hosting repo is `task_storage: tracked`, so TASK-0007 entering `ready_for_review` without a disposition line is correct (`not_applicable` default).
- **Unapproved public API/schema changes:** none. The only signature change is the internal `check_runtime_projection(..., policy=None)` with a default that preserves old behavior; no new CLI subcommand, `trellium-task-state` schema v1 untouched, no machine-readable receipt added.

## 4. Verification classification

**Fresh** (re-ran by me in this snapshot): `git status`/`git rev-parse HEAD` (clean tree at `430de35`); `python3 scripts/trellium.py check . --format json` → 0 error / 0 warning, exit 0; `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 99 OK; module count 88, `LocalProjectionTest` 12 OK; `python3 scripts/sync-skills.py --check` → in sync; `git diff --check` → clean; `cmp` of `scripts/trellium.py` vs both `assets/trellium.py` → identical; `git ls-files -s` + `diff` proving `init/protocol/*`, `init/VERSION`, `init/MIGRATIONS.md` byte-identical to both `references/protocol-source` snapshots; `git tag | wc -l` → 0; diff greps for `.github`/`.gitignore`/`add_parser` → none; fixture probes A–H for the decision-table edges; per-class test-method counts at five commits via `git show` (VaultCheckTest = 37); commit-timestamp listing (four commits share `10:47:19 +0800`, confirming the ledger's F2 premise).

**Historical** (recorded in the snapshot, not re-run, and not re-runnable here): the W-group ablation's 9 first answers / material bytes / correction counts; the C0/C1/C2 characterization records; the independent reviewer's ten-question pass; F1/F2/F3 dispositions; the 2026-09-09 preflight claims.

**Unverified:** M6 "push 后 CI 全绿" — the task text itself defers it to "提交后核验记录", and no CI log exists anywhere in this snapshot. I also could not re-run the suite at `1b55ace`/`c09cab2` without writing to disk, so the 136 figure there is derived fresh from blob inspection plus the task's own record, not executed.

## 5. Files read and commands run

**Files:** `vault/tasks/TASK-0007-local-task-lifecycle.md` (full); `scripts/trellium.py` (L1140, 1350-1420, 1456-1478, 1511-1560, 1560-1780, ~1944); `scripts/test_trellium.py` (L82-121, 944-1003); `vault/index.md` (L1-20); `README.en.md` (L258-266); `README.md` (L260-264); the full patch and ledger text supplied in the review pack. (Everything else in the diff was covered by the pack's untruncated patch and verified via git plumbing rather than re-reading.)

**Commands** (all inside `/tmp/rp-eval-20260911/s1`): `git log --oneline -5`; `git status --porcelain`; `git rev-parse HEAD`; `git tag | wc -l`; `git diff --name-only f98d302..430de35 | grep -E '\.github|\.gitignore|workflows|package.json|requirements'`; `git diff f98d302..430de35 -- scripts/trellium.py | grep -E 'add_parser|add_argument'`; `grep -nE 'urllib|requests|http|socket' scripts/test_trellium.py`; `python3 scripts/trellium.py check . --format json`; `git diff --check`; `python3 scripts/sync-skills.py --check`; `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`; `python3 -m unittest scripts.test_trellium -v` (count + `LocalProjectionTest -v`); `cmp scripts/trellium.py skills/trellium{,-zh}/assets/trellium.py`; `grep -n 'LIFECYCLE_VALUES =' scripts/trellium.py`; `sed -n '1,20p' vault/index.md`; `ls -R skills/trellium/assets/templates`; `find … -name '*.md' | xargs grep -ln 'Memory Updates'`; a `git show <ref>:scripts/test_trellium.py | class/def test_` counter over `f98d302, bf3f84b, 1b55ace, c09cab2, 430de35`; `git merge-base --is-ancestor bf3f84b HEAD`; `git log --oneline -1 bf3f84b`; `git diff --stat f98d302 bf3f84b`; `git rev-parse f98d302:scripts/test_trellium.py bf3f84b:scripts/test_trellium.py`; `git ls-files -s` on protocol/VERSION source+snapshots; `diff init/protocol/*.md` and `diff init/VERSION|MIGRATIONS.md` vs the en snapshot; `git ls-files -s init/protocol/10-vault.md …`; `sed -n '258,266p' README.en.md` / `'260,264p' README.md`; `ls docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md`; `git log --format='%h %ci %s' f98d302~1..HEAD`; `grep -n check scripts/sync-skills.py`; and one Python probe script using `tempfile` fixtures through `scripts.test_trellium` helpers plus `run_vault_checks` (cases A–H). One earlier probe was re-run twice after fixing my own harness errors (helpers are module-level; `make_project` needs `setUp`; `policy` takes block text, not a bare string). My first blob-identity check via `git rev-parse <path>` was wrong (it echoes the path) and was replaced with `git ls-files -s` + `diff`.

## 6. Questions I cannot answer from this material

- **Whether CI actually went green after the push (M6).** No CI log, run ID, or remote state exists in this snapshot, so the `[x]` on that criterion cannot be confirmed or refuted here. The owner should confirm it at acceptance.
- **Whether the W-group ablation sessions were genuinely uncontaminated** — only the archived first answers and a self-reported "corrections = 0" exist; the sessions themselves are not reproducible.
- **Whether preregistration truly preceded implementation (F2).** Four commits share one timestamp, so commit history cannot prove ordering; the ledger already flags this for owner adjudication, and I have nothing to add beyond noting that the *recorded* characterization results are consistent with the old code's behavior I can observe at `f98d302`.

Everything else was answerable from the snapshot.