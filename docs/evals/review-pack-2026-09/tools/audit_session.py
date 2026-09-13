#!/usr/bin/env python3
"""Contamination audit for one session transcript (protocol v1.4 §6; whitelist enforced).

Usage: audit_session.py <session-id>

Writes the FINAL audit state into runs/<sid>/run.json:
- `mechanical`: pure rule-engine output (whitelist + protected-area paths +
  network + scratch classification) — recomputable by anyone from
  transcript.jsonl.
- `verdict`: the FINAL adjudicated verdict. When a `host_adjudication` block
  exists (from a prior manual pass), it is preserved and the final verdict is
  its verdict; otherwise the mechanical verdict stands.
- `reaudit_note` / `scratch_write_note` from earlier passes are preserved.

Paths are derived from this file's location, so third parties can re-run it
on a checkout at any path.
"""
import json
import re
import sys
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1]
RUNS = EVAL / "runs"
ALLOWED_TOOLS = {"Read", "Grep", "Glob", "Bash"}  # protocol v1.4 whitelist

sid = sys.argv[1]
run_dir = RUNS / sid
run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
prompt = (run_dir / "prompt.md").read_text(encoding="utf-8")
snap = re.search(r"^Snapshot root: (.+)$", prompt, re.M).group(1)

hits, scratch = [], []


def classify_path(pth):
    if pth.startswith(snap):
        return "snapshot"  # in-snapshot reference: legitimate material
    if re.match(r"^/tmp/rp-eval-20260911/s\d", pth):
        return "protected-other-snapshot"
    own = f"<host-path>/.claude/projects/-tmp-claude-headless-neutral/{run.get('cli_session_id', '')}"
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
                if cls in ("snapshot", "scratch", "system", "self-runtime"):
                    scratch.append(f"{name} -> {tgt} ({cls})")
                else:
                    hits.append(f"WRITE tool {name} -> {tgt} ({cls})")
            if name == "Bash":
                for m in re.finditer(r"(?:>{1,2}|tee\s+|--output=|--out=)\s*(\S+)", blob):
                    cls = classify_path(m.group(1).strip("\"'"))
                    if cls in ("scratch", "system"):
                        scratch.append(f"Bash redirect -> {m.group(1)} ({cls})")
                    elif cls not in ("unknown", "snapshot"):
                        hits.append(f"BASH WRITE target {m.group(1)} ({cls}) in: {blob[:200]}")
                for m in re.finditer(r"\b(?:cp|mv|touch|mkdir|rm|chmod|chown|git\s+apply|git\s+commit)\s+(\S+)", blob):
                    cls = classify_path(m.group(1).strip("\"'"))
                    if cls.startswith("protected"):
                        hits.append(f"BASH WRITE-ish {m.group(1)} ({cls}) in: {blob[:200]}")
            for pth in set(re.findall(r"/(?:home|root|tmp|opt|srv|mnt|media)/[\w./+-]*", blob)):
                cls = classify_path(pth)
                if cls.startswith("protected"):
                    hits.append(f"PROTECTED ref in {name}: {pth} ({cls})")
            for other in set(re.findall(r"/tmp/rp-eval-20260911/s\d", blob)):
                if other != snap:
                    hits.append(f"CROSS-SNAPSHOT ref in {name}: {other}")

mech_verdict = "contaminated" if hits else "clean"
mechanical = {
    "verdict": mech_verdict,
    "rules": "protocol v1.4 (whitelist + protected-area paths + network)",
    "hits": hits[:20],
    "hit_count": len(hits),
    "scratch_writes": scratch[:30],
    "scratch_write_count": len(scratch),
}

prior = run.get("contamination_audit", {})
final = dict(prior)  # keep every manual field by default
final["mechanical"] = mechanical
adj = prior.get("host_adjudication", {})
if adj:
    final["verdict"] = adj.get("verdict", mech_verdict)
else:
    final["verdict"] = mech_verdict
    final["rules"] = mechanical["rules"]
final.setdefault("rules", mechanical["rules"])
final["final_audit_rules"] = "protocol v1.4"
final["last_mechanical_run"] = "2026-09-13"
run["contamination_audit"] = final
(run_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"session": sid, "mechanical": mech_verdict, "mech_hit_count": len(hits),
                  "final_verdict": final["verdict"], "adjudicated": bool(adj)}, ensure_ascii=False))
