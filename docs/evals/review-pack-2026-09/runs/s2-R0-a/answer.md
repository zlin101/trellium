I have enough evidence. Here is my review.

---

# Review: 55ae985..7ff75a8 (TASK-0008, 2026.09.5 read-only `status`)

## 1. Verdict: **APPROVE**

The diff implements precisely what `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md` §6 preregistered, nothing more. The three hard contracts all hold under my own re-execution:

| Contract | Evidence |
|---|---|
| `check` finding/severity/exit **zero change** | `check` text **and** JSON are byte-identical between the base script (via `git show 55ae985:scripts/trellium.py \| python3 -`) and the head script, same exit 0 |
| `status` never writes the target | `git status --porcelain` clean before and after repeated `status` runs; no network/deps in the path (only pre-existing `urllib` in `--fetch`) |
| Fail-closed, no authority/lifecycle invention | Drift probe: `unresolved` entry carries **no** `lifecycle`/`authority_level`/`runtime_projection`; text output leaks no `authority=` and quotes neither the conflicting objective nor next-action; exit 2 |

Governance is respected at the point that matters most: the task stops at `ready_for_review`, **no tag/Release is created** (`git tag -l` empty), and `vault/decisions.md` is deliberately untouched. The preregistration is verifiable in git time — the plan doc exists at base `55ae985` and `git diff --stat -- docs/` over the range is empty, so the code commit `4604a0c` postdates the freeze.

## 2. P0/P1/P2 findings

**none**

Sub-threshold observations (P3, recorded for completeness — none blocks):

- **P3 — misleading fallback reason code.** `scripts/trellium.py:2118` — for a dangling duplicate runtime row over a nonexistent task, status emits `reason: "TASK_RUNTIME_UNRESOLVED"` while `findings` contains only `TASK_RUNTIME_DUPLICATE` (probe-confirmed). `TASK_RUNTIME_UNRESOLVED` in check's vocabulary means *legacy/invalid state block*, not *file absent*, so the reason misdescribes the situation and dangles w.r.t. `findings`. Still fully fail-closed (exit 2, no lifecycle/authority, true finding printed verbatim in the same payload). Already logged by the implementer's own round-1 review as retained P3-2 and frozen by `test_broken_projection_rows_drop_next_action_but_not_lifecycle`. Fix direction: fall back to `TASK_RUNTIME_DUPLICATE` when `row_counts[task_id] > 1`, or join on the reason set actually present in `findings`.
- **P3 — unreadable `vault/tasks/archive` crashes instead of reporting.** `scripts/trellium.py:1615` (`sorted(archive_dir.iterdir())` has no `OSError` guard, unlike the sibling `vault/tasks` loop at 1571). Probe: `PermissionError` traceback, exit 1, for both `status` and `check`. **Pre-existing** — base `check` crashes identically on the same fixture. Fixing it would mean changing `check` behavior, which this task's own *Requires Approval* clause forbids; belongs in a separate owner-approved task.
- **P3 — duplicate `TASK_RUNTIME_MISSING`.** A missing task referenced by both Focus and an Active Tasks row yields two identical errors (`resolve()` at `trellium.py:1693` dedups only in `local_mode`). Probe-confirmed identical at base and head — pre-existing, and the check-byte-identity contract forbids changing it here.
- **P3 — stale measurements presented as current.** `vault/runtime.md` (Current Progress bullet) and `vault/details/shadow-run-2026-09.md` (K4 row) state "S1 1149 bytes < runtime 11039 bytes". At HEAD I measure **1121 / 11469** — the M5 vault edit changed the projection text (-26 bytes on the TASK-0008 Next Action cell). Direction is conservative (guardrail holds by a wider margin) and the shadow-run row explicitly discloses that runtime.md changed after the measurement. Fix: restate at HEAD values on the next vault touch.
- **P3 — ledger-named directory is silently skipped.** `vault/tasks/TASK-0009-review.md` created as a *directory* produces no finding from either command, while `TASK-0008-noleader.md` as a directory correctly yields `FILE_UNREADABLE`. Pre-existing; the new `REVIEW_LEDGER_RE` guard in `status_unresolved_reasons` only preserves, rather than creates, this gap.

## 3. Scope, authority, and public API/schema

- **Out-of-scope changes: none.** Every one of the 19 changed files maps onto plan §6's allowed list (`scripts/trellium.py`, `scripts/test_trellium.py`, `init/VERSION`, `init/MIGRATIONS.md`, both READMEs, `skills/**` snapshots, minimal vault sync). A grep for anything outside that set returns nothing. No second 09.5 feature, no context/evidence/review-pack/inbox/runtime-generator work.
- **Authority violations: none.** No tag/Release; lifecycle left at `ready_for_review` rather than self-accepted; `vault/decisions.md` untouched; `check` semantics/exit codes unchanged (so the *Requires Approval* trigger never fired); no new dependency, network access, or persistent state file; D-0004 not reopened. The vault's `trellium-task-state` block still carries `schema_version: 1`.
- **Public API/schema changes: additive only, and pre-authorized.** The new `status` subcommand and status JSON `schema_version: 1` *are* the approved feature (task §Authority "Allowed"; plan §5.3 "JSON 输出为稳定 schema v1"). Two internal shape changes — `discover_task_files` records gaining a `"state"` key and `parse_runtime_task_pointers` rows going 2-tuple → 4-tuple — are private to the script and provably behavior-neutral, as established by the byte-identical `check` output.

## 4. Verification-claim classification

**Fresh** (re-ran by me in this snapshot):
116/116 `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` · `check` text/JSON byte-identical base-vs-head with equal exit code · `status` text and `--format json`, exit 0, classification matching the vault (1 active / 1 blocked / 1 ready_for_review / 5 closed / focus TASK-0008) · read-only assertion via `git status --porcelain` · S1 = 1121 B < S0 `vault/runtime.md` = 11469 B · `sync-skills.py --check` in sync · `git diff --check` clean · `scripts/trellium.py` identical to both `skills/*/assets/trellium.py`; `init/` identical to both `protocol-source/` copies · drift probe (no authority/lifecycle/projection leak, exit 2) · duplicate-id probe with one valid + one invalid block (single unresolved entry, no double classification — `discover_task_files:1639` nulls `valid` for duplicated ids) · unreadable-archive probe · base-vs-head re-runs establishing that the archive crash and the double `TASK_RUNTIME_MISSING` both exist at `55ae985`.

**Historical** (recorded in the snapshot, not re-runnable here): the M0 baseline (`check` JSON 802 B at `55ae985`, archived to `/tmp/check-before.json`); the R1 pre-implementation blind test (3/3 five-question, 0 corrections); the three synthetic-scenario golden byte-identities and the recorded S1 = 1149 B at commit `4604a0c`; independent review round 1 (REQUEST_CHANGES, 1×P1) and round 2 (APPROVE); CI run `34181086563`.

**Unverified**: whether the R1 blind-test sessions were genuinely history-free; real-clone `task_storage=local` behavior (covered only by synthetic fixtures); the still-pending owner acceptance/tag/Release — correctly not claimed as done.

## 5. Files read and commands run

**Files:** `vault/tasks/TASK-0008-owner-status.md` · `scripts/trellium.py` (regions 1129-1171, 1236-1280, 1355-1396, 1489-1660, 1640-1800, 1946-2280) · `scripts/test_trellium.py` (range diff, plus helpers at 25-95 and the `StatusSummaryTest` block) · `README.md`, `README.en.md` · `init/MIGRATIONS.md`, `init/VERSION` · `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md` · `vault/runtime.md`, `vault/details/shadow-run-2026-09.md` · `skills/{trellium,trellium-zh}/references/protocol-model.md` and `protocol-source/{manifest.json,init/MIGRATIONS.md,init/VERSION}` · `.gitignore`.

**Commands:** `git log --oneline` · `git status --porcelain` · `git diff --stat|--name-only` (range, and per-path for `scripts/`, `README*`, `init/`, `skills/`, `vault/`, `docs/`) · `git rev-parse HEAD` · `git show 55ae985:{scripts/trellium.py,vault/runtime.md}` · `git ls-tree 55ae985` · `git tag -l` · `cmp -s` (script and protocol-source copies) · `wc -c` · `ls` · `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` · `python3 scripts/trellium.py status .` and `status . --format json` · `python3 scripts/trellium.py check .` and `check . --format json` · `git show 55ae985:scripts/trellium.py | python3 - check …` · `python3 scripts/sync-skills.py --check` · `git diff --check` · `grep`/`sed` region extraction · inline `python3 -c` probes building fixtures under `/tmp/rp-probe-s2/` (drift, duplicate id, unreadable archive, dangling duplicate row, focus+row missing, ledger-named directory).

**Disclosure:** the fail-closed probes required throwaway fixtures, which I wrote under `/tmp/rp-probe-s2/` — outside the snapshot. The snapshot itself is unmodified (`git status --porcelain` clean throughout). A second scratch-file write was denied by the permission layer; I switched to inline `python3 -c` for the remaining probes and did not work around it.

## 6. Questions I could not answer

All six are answerable from the material. Two residual limits worth stating rather than glossing: the local-mode "fresh clone" scenario is validated only against synthetic fixtures, since no second real project exists in this snapshot; and the R1 blind test's central claim (three genuinely history-free sessions answering 5/5) is a recorded assertion I have no way to independently corroborate from inside the repository. Neither affects the verdict — the first is a fixture-fidelity caveat, the second is an efficiency-guardrail claim that the plan itself already refuses to treat as proof of time savings.