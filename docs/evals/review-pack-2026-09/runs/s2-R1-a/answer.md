I have everything I need. Final answer.

---

# Review — TASK-0008, diff `55ae985..7ff75a8`

## 1. Verdict: **APPROVE**

The diff does what the frozen contract says, and the parts that matter most hold up under independent re-verification in this snapshot: the new `status` subcommand is read-only, fail-closed, exit-code-identical to `check`, and the refactor that feeds it (`run_vault_checks` → `collect_vault_state`, 2-tuple → 4-tuple runtime rows, additive `"state"` key in task records) contains no behavior change to the existing `check` path. Governance is respected: the task stops at `ready_for_review`, no tag/Release exists, no second 09.5 feature, no dependency or network.

## 2. Findings (P0/P1/P2)

**none.**

I looked specifically for: crash paths (`state["authority_level"]` / `open_buckets[lifecycle]` / `sorted(gates.items())` — all safe, since `authority_level`/`lifecycle` are required + enum-validated at `scripts/trellium.py:1144` and `gates` must be a dict); `IndexError` on short runtime rows (guarded by `len(cells) < 4` at `scripts/trellium.py:1383`); un-updated callers of the reshaped parser (none — only `:1713` and the new `:2089`); behavior-changing removed lines (none — the full removal list is signature/reshape/wrapper only); false id attribution from path-only findings (guarded — `vault/tasks`, `vault`, ledger and `archive/` names fail `TASK_FILE_ID_RE` or the archive/ledger filters).

Two observations I deliberately rate **below P2** and do not report as findings:

- **Duplicate-vs-drift asymmetry.** One drifted runtime row demotes a task to `unresolved`, but two *mutually contradictory* duplicate rows (e.g. `active` and `ready_for_review`) do not — the state block's lifecycle is kept, the projection is dropped, exit 2 (`build_status_payload`, `scripts/trellium.py:2094-2105`). This is documented (`MIGRATIONS.md`: "重复行或行状态非法的行不产出投影") and tested, the lifecycle authority is the state block by the protocol's own model, and the error is always surfaced with exit 2. The task file itself records the adjacent cases (P3-2/P3-5) as non-blocking.
- **`status` JSON `target` is an absolute path**, so output varies with mount point. Identical to the pre-existing `check` JSON v1 convention; determinism for a fixed target is verified.

Minor bookkeeping note: the task file records "S1 文本 1149 bytes"; I measured 1121. The delta is the absolute target path embedded in line 1 of the output — the guardrail itself holds by ~10×.

## 3. Scope / authority / API

- **Out-of-scope changes: none.** All 19 files map to a named milestone: M2/M3 (`scripts/trellium.py`, `scripts/test_trellium.py`), M4 (`init/VERSION`, `init/MIGRATIONS.md`, both READMEs, both skill packages + `protocol-source` snapshots), M5 (vault-only: `runtime.md`, `TASK-0008-owner-status.md`, `shadow-run-2026-09.md`). Commit boundaries confirm this — `4604a0c` code+tests only, `62c2a0e` docs+snapshots only, `7e494da` fix+tests+asset-sync only, `7ff75a8` vault-only.
- **Authority violations: none.** Lifecycle moved to `ready_for_review`, not `accepted` (M5's defined terminal state); `git tag` returns empty, so no tag/Release; no second 09.5 feature; no dependency, network, daemon, or persistent inbox file; `check` findings/severity/exit codes unchanged.
- **Unapproved public API/schema changes: none.** `status` + JSON v1 *is* new public API surface, but it is precisely the single feature the owner's current instruction approved at Level C / Authority 3, and it is registered as `Added` in `MIGRATIONS.md`. The existing task-state schema (`STATE_REQUIRED_FIELDS`/`STATE_OPTIONAL_FIELDS`) is untouched. The vault edits are the standard 2-edit lifecycle transition (state block + runtime row) plus the K1/K3/K4 ledger rows required by D-0005, matching the TASK-0005/0007 precedent.

## 4. Verification claims — classification

| Claim | Class | Basis |
|---|---|---|
| Snapshot at `7ff75a8`, clean, 19 files, +1304/−58 | **fresh** | re-ran `git log`/`rev-parse`/`status`/`diff --stat` |
| `git diff --check` passes | **fresh** | exit 0 |
| 116/116 tests green | **fresh** | re-ran the suite: `Ran 116 tests … OK` |
| `check` → 0 findings / 0 warnings, exit 0 | **fresh** | re-ran on the repo |
| `status` classifies active{0001} / blocked{0004} / ready_for_review{0008} / closed 5 / focus resolved | **fresh** | re-ran `status .`, exit 0 |
| S0 `runtime.md` = 11039 bytes; head = 11469 bytes; S1 < S0 | **fresh** | measured 11039 (base), 11469 (head), 1121 (S1) |
| Skill snapshots in sync; `manifest.json` sha256 current | **fresh** | `sync-skills.py --check` → `in sync` ×2 |
| 3 × `trellium.py` copies identical | **fresh** | identical md5 across all three |
| `check` semantics/exit codes unchanged | **fresh (by construction)** | all 106 pre-existing `check` tests pass + I read every removed line of the script diff; I could *not* do a base-script-vs-head-script byte diff (see Q6) |
| `status` is read-only & deterministic | **fresh** | `test_status_is_read_only_and_deterministic` ran within my suite run (3 identical runs + `git status --porcelain` + tree snapshot unchanged), and the status path contains no write call |
| R1 blind test 3/3, 0 corrections | **historical** | handwritten goldens are not in the snapshot |
| Three S1 outputs byte-identical to handwritten goldens | **historical** | goldens not committed |
| M1 baseline `/tmp/check-before.json` byte comparison | **unverified** | file lives outside the snapshot; outside my read boundary |
| Review round 1 REQUEST_CHANGES / round 2 APPROVE, P1 fixed in `7e494da` | **historical** (the *fix* is **fresh**-verified: the pointer-less-unreadable materialization loop and the +2 tests are present at head and pass) | no review ledger file for this task; narration lives in the task file |
| `upgrade --apply` only refreshes version pointers | **unverified** | would require a write; not exercised |
| M0 preflight (`develop==origin/develop`, clean tree) | **unverified** | remote state not observable in a frozen snapshot |

## 5. Files read and commands run

All commands were run inside `/tmp/rp-eval-20260911/s2` unless noted. Nothing was created, modified, or deleted in the snapshot; no network access.

**Commands**
- `git log --oneline -5`; `git rev-parse HEAD`; `git status --porcelain`; `git diff --stat 55ae985..7ff75a8`; `git diff --check 55ae985..7ff75a8`
- `python3 --version`; `ls scripts/`; `ls vault/tasks/`; `git tag | wc -l`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`; `python3 scripts/trellium.py check .`
- `python3 scripts/trellium.py status .`
- `python3 scripts/trellium.py status . | wc -c`; `git show 55ae985:vault/runtime.md | wc -c`; `wc -c < vault/runtime.md`
- `python3 scripts/sync-skills.py --check`
- `md5sum` on the three `trellium.py` copies; `diff` between the two skill assets
- Reads: `sed -n` over `scripts/trellium.py` at lines 120-132, 895-925, 1140-1145, 1345-1400, 1470-1500, 1663-1800, 1949-1967, 2000-2013, and the status block (2013-2283); `sed -n` for `parse_task_state_block`, `validate_state_object`, `discover_task_files`, `read_regular_text`, `check_project`; `grep -n` for `TASK_RUNTIME_INVALID`, `parse_runtime_task_pointers|run_vault_checks|collect_vault_state`, `STATE_REQUIRED_FIELDS|STATE_OPTIONAL_FIELDS`, `LIFECYCLE_VALUES|GATE_VALUES`, `CHECK_ERROR_EXIT|^def fail|def resolve_existing_target`
- `git diff 55ae985..7ff75a8 -- scripts/trellium.py | grep '^-')` (full removal audit); `git show --stat` on `4604a0c`, `62c2a0e`, `7e494da`, `7ff75a8`
- **Denied, not executed:** `mkdir`/`cp -r` of the snapshot to `/tmp` plus output redirects, intended to diff the base script against the head script on an identical tree. The permission layer blocked it as a write; I did not work around it.

## 6. What could not be answered from this material

- **The "分类 golden 100%" / byte-identical-to-handwritten-golden acceptance criterion is not independently verifiable here.** The handwritten goldens and the M1 baseline file (`/tmp/check-before.json`) are outside the snapshot. Those ACs rest on historical claims; the *mechanical* parts they feed (classification correctness, S1 < S0 bytes) are fresh-verified.
- **A byte-for-byte `check` diff between the base and head scripts on an identical tree was not possible** under the read-only constraint. I substituted the two strongest available equivalents: the full 106-test pre-existing `check` suite passing fresh, and a line-by-line audit of every removed line in `scripts/trellium.py`. A maintainer with write access could close this in one command.
- **`upgrade --apply` behavior is unverified** (it writes), so the MIGRATIONS "Auto: 无模板变更" line rests on the authority of the diff itself, which does show no template changes — consistent, but not re-executed.