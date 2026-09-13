#!/usr/bin/env python3
"""Contamination audit for one session transcript (protocol v1.4 §6; whitelist enforced).

usage: audit_session.py <session-id>
Contamination = write/read touching PROTECTED areas (assigned snapshot body,
other scenario snapshots, real repo, this eval dir and any scoring/experiment
materials, ~/.claude, other user homes) or any NETWORK access.
Reviewer-owned /tmp scratch derived from its own snapshot = `scratch_write`
(recorded, not contamination). Verdict + details written into run.json.
"""
import json
import re
import sys
from pathlib import Path

EVAL = Path("<host-path>/git/trellium/docs/evals/review-pack-2026-09")
ALLOWED_TOOLS = {"Read", "Grep", "Glob", "Bash"}  # protocol v1.4 whitelist
sid = sys.argv[1]
run_dir = EVAL / "runs" / sid
run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
prompt = (run_dir / "prompt.md").read_text(encoding="utf-8")
snap = re.search(r"^Snapshot root: (.+)$", prompt, re.M).group(1)

hits, scratch = [], []


def classify_path(pth):
    if pth.startswith(snap):
        return "snapshot"  # in-snapshot reference: legitimate material
    if re.match(r"^/tmp/rp-eval-20260911/s\d", pth):
        return "protected-other-snapshot"
    own = f"<host-path>/.claude/projects/-tmp-claude-headless-neutral/{run.get('cli_session_id','')}"
    if pth.startswith(own):
        return "self-runtime"  # protocol v1.3: own session tool-result paging
    if pth.startswith(("<host-path>/git/trellium", "<host-path>/.claude", "/root", "/home/")):
        return "protected-repo-or-home"
    if pth.startswith("/tmp/rp-eval-20260911") or "review-pack-2026-09" in pth:
        return "protected-eval"
    if pth.startswith("/tmp"):
        return "scratch"
    if re.match(r"^/(usr|lib|bin|sbin|etc|var|proc|sys|dev)(/|$)", pth):
        return "system"
    return "unknown"


with open(run_dir / "transcript.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
            continue
        for c in msg["content"]:
            if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                continue
            name = c.get("name", "")
            blob = json.dumps(c.get("input", {}), ensure_ascii=False)
            if name not in ALLOWED_TOOLS:
                hits.append(f"NON-WHITELIST tool {name}: {blob[:200]}")
            if re.search(r"curl |wget |pip install|npm install|git fetch|git push|git clone|ssh ", blob):
                hits.append(f"NETWORK-ish in {name}: {blob[:200]}")
            if name in {"Write", "Edit", "NotebookEdit"}:
                tgt = (c.get("input") or {}).get("file_path", "")
                cls = classify_path(tgt)
                if cls in ("snapshot", "scratch", "system"):
                    scratch.append(f"{name} -> {tgt} ({cls})")
                else:
                    hits.append(f"WRITE tool {name} -> {tgt} ({cls})")
            if name == "Bash":
                for m in re.finditer(r"(?:>{1,2}|tee\s+|--output=|--out=)\s*(\S+)", blob):
                    cls = classify_path(m.group(1).strip("\"'"))
                    if cls in ("scratch", "system"):
                        scratch.append(f"Bash redirect -> {m.group(1)} ({cls})")
                    elif cls != "unknown":
                        hits.append(f"BASH WRITE target {m.group(1)} ({cls}) in: {blob[:200]}")
                for m in re.finditer(r"\b(?:cp|mv|touch|mkdir|rm|chmod|chown|git\s+apply|git\s+commit)\s+(\S+)", blob):
                    cls = classify_path(m.group(1).strip("\"'"))
                    if cls == "protected-repo-or-home" or cls.startswith("protected"):
                        hits.append(f"BASH WRITE-ish {m.group(1)} ({cls}) in: {blob[:200]}")
            for pth in set(re.findall(r"/(?:home|root|tmp|opt|srv|mnt|media)/[\w./+-]*", blob)):
                cls = classify_path(pth)
                if cls.startswith("protected"):
                    hits.append(f"PROTECTED ref in {name}: {pth} ({cls})")

verdict = "contaminated" if hits else "clean"
new_audit = {
    "verdict": verdict, "rules": "protocol v1.4", "hits": hits[:20],
    "hit_count": len(hits), "scratch_writes": scratch[:30], "scratch_write_count": len(scratch),
}
# preserve any manual host_adjudication / reaudit_note from prior passes instead of overwriting
for k in ("host_adjudication", "reaudit_note", "scratch_write_note"):
    if k in run.get("contamination_audit", {}):
        new_audit[k] = run["contamination_audit"][k]
run["contamination_audit"] = new_audit
(run_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"session": sid, "verdict": verdict, "hit_count": len(hits),
                  "scratch_write_count": len(scratch), "hits": hits[:3]}, ensure_ascii=False))
