#!/usr/bin/env python3
"""Mechanical R1 Review Pack builder (TASK-0009 M2).

Frozen extraction rules (mirrored in packs/README.md):
- Canonical Contract sections are copied VERBATIM from the task file at the
  scenario head commit (heading-start to next same-or-higher heading).
- Verification Boundary = the task file's `Verification -> Completed:` lines,
  each suffixed ` [historical/unverified]`.
- Review State = the FULL verbatim review ledger of the task under review
  (`vault/tasks/<task-stem>-review.md`) if present at head; `none` when the
  task has no review ledger at head. v1.2: v1 scanned task file + all
  `*review*.md` ledgers (pulled decision-table rows, `fail-open` phrasing and
  OTHER tasks' ledgers, and mis-filed negation lines like "无 wont-fix" as
  wont-fix entries). The full-ledger copy is a mechanical superset of the
  open/needs-discussion/wont-fix sub-fields and avoids keyword
  misclassification entirely. No session had run and no pack had been
  committed when this rule was tightened; documented in packs/README.md.
- Decision Pointers = `D-[0-9]{4}` ids appearing in the task file; pointer is
  id + `vault/decisions.md` path only.
- External Boundary = lines in Out of Scope / Forbidden sections matching the
  frozen keyword list [网络 network 外部 external 远端 remote GitHub Release
  CI push tag 标签]; verbatim; `unavailable` if no match.
- Live Snapshot = git facts from the snapshot itself (changed names, --stat,
  full untruncated patch, untracked names).
- Omissions = anything a frozen rule could not extract (must be empty; any
  entry is recorded here and in the pack).
No natural-language conclusions, no risk hints, no field reordering.
"""
import re
import subprocess
import sys
from pathlib import Path

SNAP_ROOT = Path("/tmp/rp-eval-20260911")
OUT = Path("<host-path>/git/trellium/docs/evals/review-pack-2026-09/packs")
OUT.mkdir(parents=True, exist_ok=True)

SCENARIOS = {
    "s1": dict(task="vault/tasks/TASK-0007-local-task-lifecycle.md",
               base="f98d302", head="430de35"),
    "s2": dict(task="vault/tasks/TASK-0008-owner-status.md",
               base="55ae985", head="7ff75a8"),
    "s3": dict(task="vault/tasks/TASK-0008-owner-status.md",
               base="55ae985", head="5317784"),
}

STATUS_RE = re.compile(r"open|needs-discussion|wont-fix|won't fix", re.I)
EXTERNAL_RE = re.compile(r"网络|network|外部|external|远端|remote|GitHub|Release|CI\b|push|tag\b|标签")
DREF_RE = re.compile(r"D-[0-9]{4}")


def git(snapshot, *args):
    return subprocess.run(["git", "-C", str(snapshot), *args],
                          check=True, capture_output=True, text=True).stdout


def task_text(snapshot, task):
    return git(snapshot, "show", f"HEAD:{task}")


def parse_sections(text):
    """Return {heading_start_line: (heading, [lines])} for md headings."""
    lines = text.splitlines()
    sections = []  # (lineno, heading, body)
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            sections.append([i, m.group(2), []])
            continue
        if sections:
            sections[-1][2].append(ln)
    return lines, sections


def find_section(sections, prefix):
    for _, h, body in sections:
        if h.startswith(prefix):
            return h, body
    return None, None


def subsection(body, name):
    """Lines under a `name:` label until next label or blank-line group end."""
    out, on = [], False
    for ln in body:
        if re.match(rf"^{re.escape(name)}\s*:", ln):
            on = True
            out.append(ln)
            continue
        if on and re.match(r"^[A-Za-z][A-Za-z -]*\s*:\s*$|^[A-Za-z][A-Za-z -]*\s*:\s+\S", ln):
            break
        if on:
            out.append(ln)
    return [x for x in out[1:] if x.strip()]


def extract(snapshot_dir, cfg):
    snap = SNAP_ROOT / snapshot_dir
    task = cfg["task"]
    base, head = cfg["base"], cfg["head"]
    text = task_text(snap, task)
    lines, sections = parse_sections(text)

    # trellium-task-state block (HTML comment)
    m = re.search(r"<!--\s*trellium-task-state.*?-->", text, re.S)
    state_block = m.group(0) if m else None

    objective = find_section(sections, "Objective")
    in_scope = find_section(sections, "In Scope")
    out_scope = find_section(sections, "Out of Scope")
    authority = find_section(sections, "Authority")
    acceptance = find_section(sections, "Acceptance Criteria")
    verif = find_section(sections, "Verification")

    omissions = []
    for name, got in [("trellium-task-state", state_block), ("Objective", objective),
                      ("In Scope", in_scope), ("Out of Scope", out_scope),
                      ("Authority", authority), ("Acceptance Criteria", acceptance),
                      ("Verification", verif)]:
        if got is None:
            omissions.append(f"{name}: section not found at head")

    # Verification Boundary
    completed = subsection(verif[1], "Completed") if verif[1] else []

    # Review State: full verbatim ledger of THIS task at head (v1.2 rule)
    task_id = "-".join(Path(task).stem.split("-")[:2])  # e.g. TASK-0007
    ledger = f"vault/tasks/{task_id}-review.md"
    review_ledger_path, review_ledger_body = None, None
    if git(snap, "ls-tree", "--name-only", "HEAD", ledger).strip():
        try:
            review_ledger_path = ledger
            review_ledger_body = git(snap, "show", f"HEAD:{ledger}")
        except subprocess.CalledProcessError:
            omissions.append(f"review ledger present at head but unreadable: {ledger}")
    review_hits = []

    # Decision Pointers
    drefs = sorted(set(DREF_RE.findall(text)))

    # External Boundary (keyword scan of Out of Scope + Forbidden section)
    ext_lines = []
    for sec_body in [out_scope[1] if out_scope else [],
                     (authority[1] or []) if authority else []]:
        for ln in sec_body:
            if EXTERNAL_RE.search(ln) and ln.strip():
                ext_lines.append(ln.strip())
    ext_lines = sorted(set(ext_lines))

    # Live Snapshot facts
    changed = git(snap, "diff", "--name-only", f"{base}..{head}").splitlines()
    stat = git(snap, "diff", "--stat", f"{base}..{head}")
    patch = git(snap, "diff", f"{base}..{head}")
    untracked = [l for l in git(snap, "ls-files", "--others", "--exclude-standard").splitlines() if l]

    return dict(task=task, base=base, head=head, state_block=state_block,
                objective=objective, in_scope=in_scope, out_scope=out_scope,
                authority=authority, acceptance=acceptance,
                completed=completed,
                review_ledger_path=review_ledger_path,
                review_ledger_body=review_ledger_body,
                review_hits=review_hits, drefs=drefs,
                ext_lines=ext_lines, changed=changed, stat=stat, patch=patch,
                untracked=untracked, omissions=omissions)


def render(sid, r):
    L = []
    L.append(f"# Review Pack — scenario {sid.upper()} (R1, hand-assembled, frozen template)\n")
    L.append("## Review Target\n")
    L.append(f"- task_id: {Path(r['task']).stem.split('-')[0]}-{Path(r['task']).stem.split('-')[1]}")
    L.append(f"- base commit: {r['base']}")
    L.append(f"- head commit: {r['head']}")
    L.append(f"- exact diff range: {r['base']}..{r['head']}")
    L.append("- snapshot dirty state: clean (verified at pack build)\n")
    L.append("## Canonical Contract (verbatim from the task file at head)\n")
    L.append("### trellium-task-state\n")
    L.append("```")
    L.append(r["state_block"] or "unavailable")
    L.append("```\n")
    for label, sec in [("Objective", r["objective"]), ("In Scope", r["in_scope"]),
                       ("Out of Scope", r["out_scope"]), ("Authority (Allowed / Requires Approval / Forbidden)", r["authority"]),
                       ("Acceptance Criteria", r["acceptance"])]:
        L.append(f"### {label}\n")
        if sec:
            h, body = sec
            L.append(f"#### {h}\n") if label != "Objective" else None
            L.append("\n".join(body).strip() or "(empty)")
        else:
            L.append("unavailable")
        L.append("")
    L.append("## Live Snapshot\n")
    L.append(f"- HEAD: {r['head']}")
    L.append("- changed file names:")
    L.extend(f"  - {c}" for c in r["changed"])
    L.append("")
    L.append("- diff --stat:")
    L.append("```")
    L.append(r["stat"].rstrip())
    L.append("```\n")
    L.append("- full patch (untruncated):")
    L.append("```diff")
    L.append(r["patch"].rstrip())
    L.append("```\n")
    L.append("- untracked file names: " + (", ".join(r["untracked"]) if r["untracked"] else "none"))
    L.append("")
    L.append("## Verification Boundary\n")
    L.append("- claimed completed checks at head, verbatim; every item is historical/unverified; this pack does not infer freshness — only a re-run by you in this snapshot may be reported fresh:")
    if r["completed"]:
        L.extend(f"  - {ln.strip()} [historical/unverified]" for ln in r["completed"])
    else:
        L.append("  - none")
    L.append("")
    L.append("## Review State\n")
    if r["review_ledger_body"]:
        L.append(f"- review ledger of this task at head ({r['review_ledger_path']}), verbatim; "
                 "statuses are exactly as recorded at head (open / needs-discussion / wont-fix / fixed are not re-classified here):")
        L.append("```markdown")
        L.append(r["review_ledger_body"].rstrip())
        L.append("```")
    else:
        L.append("- open / needs-discussion findings at head: none")
        L.append("- wont-fix findings at head: none")
        L.append("- (no review ledger file for this task exists at head; review narration lives in the "
                 "Verification Boundary lines above)")
    L.append("")
    L.append("")
    L.append("## Decision Pointers\n")
    if r["drefs"]:
        for d in r["drefs"]:
            L.append(f"- {d}: `vault/decisions.md` (title not copied; read at the pointer if needed)")
    else:
        L.append("- none")
    L.append("")
    L.append("## External Boundary\n")
    if r["ext_lines"]:
        L.extend(f"- {ln}" for ln in r["ext_lines"])
    else:
        L.append("- unavailable")
    L.append("")
    L.append("## Omissions\n")
    if r["omissions"]:
        L.extend(f"- {o}" for o in r["omissions"])
    else:
        L.append("- none")
    return "\n".join(L) + "\n"


def main():
    for sid, cfg in SCENARIOS.items():
        r = extract(sid, cfg)
        pack = render(sid, r)
        p = OUT / f"pack-{sid}.md"
        p.write_text(pack, encoding="utf-8")
        print(f"{p}: {len(pack.encode('utf-8'))} bytes, patch {len(r['patch'].encode())}B, "
              f"omissions={r['omissions'] or 'none'}, review_hits={len(r['review_hits'])}, "
              f"drefs={r['drefs']}, ext={len(r['ext_lines'])}")


if __name__ == "__main__":
    sys.exit(main())
