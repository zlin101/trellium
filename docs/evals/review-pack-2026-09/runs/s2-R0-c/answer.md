I have everything I need. Here is the review.

---

# Review: 55ae985..7ff75a8 (TASK-0008, 2026.09.5 `status`)

## 1. Verdict

**REQUEST_CHANGES** — one P2. Everything else in the diff is solid, well-tested, and contract-conformant; the change is a single ~5-line boundary fix away from approve.

I verified independently (see §4) that the implementation matches the frozen plan, that `check` is byte-for-byte unchanged, and that every re-runnable verification claim in the task file reproduces. The P2 below is a fail-open boundary that the task marks as satisfied (`[x]`) but is not.

## 2. Findings (P0/P1/P2 only)

### P2 — `status` reports `unresolved: 0` when vault enumeration is refused, asserting a clean bill of health for an unreadable vault

**Evidence:** `scripts/trellium.py:2060-2074` (`status_unresolved_reasons` path-only filter) interacting with `scripts/trellium.py:2143-2169` (the unresolved-materialisation loops) and `scripts/trellium.py:2214` (`summary.unresolved`).

**Reproduced in this snapshot** by driving `build_status_payload` with the exact records `collect_vault_state` returns on a refused vault (`scripts/trellium.py:1950-1952` returns `run, {}, []` when `vault/` is a symlink; `discover_task_files` returns `[]` at `scripts/trellium.py:1548-1550` when `vault/tasks` is a symlink):

```
summary: {"draft": 0, "active": 0, "blocked": 0, "ready_for_review": 0, "closed": 0, "unresolved": 0}
unresolved list: []
findings codes: ['SYMLINK_INPUT', 'SYMLINK_INPUT']
rendered: "summary: 0 draft, 0 active, 0 blocked, 0 ready_for_review, 0 closed, 0 unresolved"
          "unresolved: (none)"
```

The root cause is the path-only branch at `scripts/trellium.py:2066-2073`: `Path("vault/tasks").name` → `"tasks"`, which does not match `TASK_FILE_ID_RE`, so the directory-level `SYMLINK_INPUT` finding is discarded and no id is materialised.

**Precise trigger (so the owner can judge realism):** the all-zero output needs *both* `vault/tasks` and `vault/runtime.md` refused. I confirmed the single-failure case is handled correctly — with `vault/tasks` refused but `runtime.md` readable, status correctly emits `unresolved: 8`. So this is a compound-input case, not the common one.

**Contract violated:**
- Acceptance criterion 4 (`vault/tasks/TASK-0008-owner-status.md:73`): *"malformed/duplicate/drift/local missing/symlink 全部 fail-closed"* — marked `[x]`.
- Plan §4 (`docs/.../2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md:72`): *"missing/legacy/invalid/local-only 指针显式 `unresolved`，不推断 Authority，不 fail-open"*.
- Kill criterion (plan §5.4, line 137): *"对 closed/unresolved 任务产生任何 fail-open 表述"* — `summary.unresolved == 0` is a machine-readable "no unresolved items" statement about a vault whose contents were never read. The plan froze JSON v1 for exactly this kind of programmatic consumption (§4, line 77).
- Same defect class as the round-1 P1 already agreed blocking (`TASK-0008-owner-status.md:97` — *"指针未引用的不可读任务不进 unresolved"*), one level coarser: the `7e494da` fix materialises ids from `reasons`, and `reasons` is empty here.

**Mitigations, for fairness:** exit code is `2`, and both `SYMLINK_INPUT` errors are rendered in full in text and JSON — so nothing is silent to a caller that checks the exit code. No lifecycle or authority is fabricated (the criterion's second clause holds).

**Minimal fix direction:** when a `required-files`/`task-state` error names `vault` or `vault/tasks` (i.e. enumeration was refused rather than merely one file unreadable), `build_status_payload` should not emit `unresolved: 0` — either clamp `summary["unresolved"]` to ≥1, or emit one summary-level unresolved entry carrying the real code. Note this touches the frozen JSON v1 shape (§4, line 79-96), so it needs a deliberate one-line note in MIGRATIONS rather than a silent change. Do not widen it into a `check` change — `check` is currently byte-identical to baseline and must stay so.

**Non-blocking, not counted as a finding:** `status` is documented in both READMEs, both `references/protocol-model.md` files, and both synced `MIGRATIONS.md`, but appears nowhere in `skills/trellium/SKILL.md` or `skills/trellium-zh/SKILL.md` (grep: 0 matches), while `check` gets a full paragraph at `skills/trellium/SKILL.md:53`. The gap is softened because SKILL.md mandates reading `references/protocol-model.md`, which does cover it. Worth a one-line follow-up; it does not violate the stated M4 criterion, which is an accuracy constraint, not a completeness one.

## 3. Scope, authority, and API changes

**Out-of-scope changes: none.** All 19 changed files fall inside plan §6 允许 (lines 145-150): `scripts/trellium.py`, `scripts/test_trellium.py`, `init/VERSION`, `init/MIGRATIONS.md`, both READMEs, both skill packages' `protocol-model.md` + synced `protocol-source` + embedded `assets/trellium.py`, and the self-hosting vault (`runtime.md`, `shadow-run-2026-09.md`, `TASK-0008`). No second 09.5 feature, no context/evidence/review-pack/inbox/runtime-generator, no dependency, no network path.

**Authority violations: none.** Level C / Authority 3 as declared. The diff stops at `ready_for_review` (`vault/tasks/TASK-0008-owner-status.md:9`); `vault/decisions.md` and `vault/collaboration.md` are untouched, matching the Memory Updates gate at line 172. No tag, no Release, no self-acceptance. The pre-registration ordering is verifiable in-tree: plan commit `55ae985` precedes code commit `4604a0c`.

**Unapproved public API/schema changes: none.** The `status` subcommand *is* the approved deliverable, and its JSON v1 shape matches the frozen plan §4 shape exactly (I confirmed the six top-level keys and the five `tasks` keys, and that unresolved entries carry no `lifecycle`/`authority_level`). `check`'s CLI, findings, severities, and exit codes are unchanged — verified, not assumed (see §4).

## 4. Verification claim classification

**Fresh (re-run by me in this snapshot):**

| Claim | Result |
|---|---|
| `python3 scripts/trellium.py status .` | exit 0; focus TASK-0008 resolved; 1 active / 1 blocked / 1 rfr / 5 closed / 0 unresolved |
| `python3 scripts/trellium.py status . --format json` | exit 0; exactly the six frozen keys; unresolved entries carry no lifecycle/authority |
| `python3 scripts/trellium.py check . --format json` | exit 0, 0 findings |
| `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` | **116/116 OK** — matches the claimed 116 |
| `python3 scripts/sync-skills.py --check` | both packages `in sync` |
| `git diff --check` (range and worktree) | clean |
| **"check finding/severity/exit 零变化"** | **Strongest result:** I ran the *base* `55ae985` script against the head tree and diffed its `check --format json` against the head script's — **byte-identical** |
| S1 bytes < S0 bytes | status text 1121 B < `vault/runtime.md` 11469 B |
| Read-only / no writes | SHA-256 of all 136 tracked files before vs. after the whole run: **identical**; `git status --porcelain` clean; no bytecode written (`-B` throughout) |
| shadow-ledger bytes figure (line 122: "测量变为 bytes 11469") | corroborated: I measured exactly 11469 |

**Historical (recorded in the snapshot, not re-runnable here):** the R1 handwritten-golden blind test and its 3/3 result; the per-scenario byte-comparison against the handwritten goldens; the `/tmp/check-before.json` S0 archive; review rounds 1 and 2 and their findings; the M0 preflight. I corroborate the *plausibility* of these from the committed tests and the byte-identical `check` result, but I did not and cannot re-run them.

**Unverified:** nothing load-bearing beyond the above. Two candidate findings I investigated and *rejected* were confirmed as non-issues rather than assumed away — a >4-cell runtime row is silently truncated (P3: inherited from `check`, no worse than reading `runtime.md` by hand), and the fabricated `TASK_RUNTIME_UNRESOLVED` fallback at `scripts/trellium.py:2118` for dangling duplicate rows (P3: fail-closed, locked in by `test_broken_projection_rows_drop_next_action_but_not_lifecycle`, and explicitly recorded as retained P3-2 in the task's Risks). Neither is reportable at P0/P1/P2.

## 5. Material consulted

**Files read:**
- `vault/tasks/TASK-0008-owner-status.md`
- `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md`
- `AGENTS.md`, `vault/governance.md`
- `scripts/trellium.py` — regions 124-126, 1129, 1137-1140, 1354-1390, 1490-1550, 1690-1770, 1940-1975, 2013-2285
- `scripts/sync-skills.py` (structure, via grep)
- `scripts/test_trellium.py` (full new `StatusSummaryTest` block, via diff)
- `skills/trellium/SKILL.md`
- `.gitignore`, `.github/workflows/skill-sync.yml`
- Diffs of `README.md`, `README.en.md`, `init/VERSION`, `init/MIGRATIONS.md`, `vault/runtime.md`, `vault/details/shadow-run-2026-09.md`, `vault/tasks/TASK-0008-owner-status.md`, `skills/*/references/protocol-model.md`, `skills/*/references/protocol-source/{manifest.json,init/VERSION,init/MIGRATIONS.md}`

**Commands run:**
`git log --oneline -20` · `git status --short` · `git rev-parse HEAD` · `git diff --stat 55ae985..7ff75a8` · `git diff 55ae985..7ff75a8 -- <path>` (per file) · `ls`/`ls -la --time-style=full-iso` · `cmp` (assets vs. canonical script) · `git ls-files -z | xargs -0 sha256sum` (before/after) · `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/trellium.py status .` (text and `--format json`) · `... check . --format json` · `python3 -B -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` · `python3 -B scripts/sync-skills.py --check` · `git diff --check` (worktree and range) · `git show 55ae985:scripts/trellium.py` piped to a checker run · `wc -c`/`wc -l` · `grep -n` over `trellium.py`, `sync-skills.py`, `skills/` · three `python3 -B -c` in-process probes importing `scripts/trellium.py` to exercise `parse_runtime_task_pointers`, `status_unresolved_reasons`, and `build_status_payload`/`render_status_text` with synthetic inputs

**Note on method:** the sandbox denies all file creation, so I could not build on-disk adversarial fixtures. I substituted in-process calls to the pure functions with exactly the records `collect_vault_state` returns, which is sufficient for the P2 above (the trigger and the output are both reproduced), but means the P2 was not confirmed through the real filesystem path. Flagging it so the owner can weigh that.

## 6. Questions I could not answer from the material

- **Whether `status` is actually smaller/faster for a human.** The plan itself says bytes are a guardrail only and no owner usability review was done (`TASK-0008-owner-status.md:160`); I can confirm 1121 < 11469 bytes and nothing more.
- **Whether the R1 blind test was sound.** Three sessions, their prompts, and their answers are not in the snapshot. I can only confirm the claim is recorded consistently in three places and that no kill criterion is recorded as hit.
- **Whether `summary.unresolved` has real machine consumers.** Nothing in the snapshot consumes it yet, so the P2's practical blast radius is a judgement call — if the owner decides no consumer will key on that field without checking the exit code, downgrading to P3 and approving is a defensible call, and I'd say so rather than argue.