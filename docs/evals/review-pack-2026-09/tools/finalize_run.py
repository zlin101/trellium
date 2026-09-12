#!/usr/bin/env python3
"""Host-side session finalizer for CLI-dispatched sessions (protocol v1.1 §5).

usage: finalize_run.py <session-id>
Reads runs/<sid>/{prompt.md,cli-result.json,cli-stderr.txt,cli-timing.txt},
locates the session transcript under ~/.claude/projects/, archives the
verbatim first answer + transcript copy, and writes run.json.
"""
import json
import re
import shutil
import sys
from pathlib import Path

EVAL = Path("<host-path>/git/trellium/docs/evals/review-pack-2026-09")
sid = sys.argv[1]
out_dir = EVAL / "runs" / sid

result = json.loads((out_dir / "cli-result.json").read_text(encoding="utf-8"))
timing = (out_dir / "cli-timing.txt").read_text().split()
t0, t1, rc = float(timing[0]), float(timing[1]), int(timing[2])
session_id = result["session_id"]

# locate transcript: cwd was /tmp/claude-headless-neutral -> project slug
slug = "-tmp-claude-headless-neutral"
cands = list(Path.home().glob(f".claude/projects/{slug}/{session_id}.jsonl"))
if not cands:
    cands = list(Path.home().glob(f".claude/projects/*/{session_id}.jsonl"))
transcript_src = cands[0] if cands else None
if transcript_src:
    shutil.copyfile(transcript_src, out_dir / "transcript.jsonl")

tool_uses = 0
result_bytes = 0
vault_opens = 0
models = set()
first_ts = last_ts = None
assistant_texts = []


def iter_content(content):
    if isinstance(content, str):
        yield {"type": "text", "text": content}
    elif isinstance(content, list):
        for c in content:
            yield c if isinstance(c, dict) else {"type": "text", "text": str(c)}


if transcript_src:
    with open(transcript_src, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            ts = rec.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            if msg.get("model"):
                models.add(msg["model"])
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for c in iter_content(content):
                ctype = c.get("type")
                if ctype == "tool_use":
                    tool_uses += 1
                    blob = json.dumps({k: v for k, v in c.get("input", {}).items() if isinstance(v, str)})
                    if re.search(r"vault/|TASK-000[78]", blob):
                        vault_opens += 1
                elif ctype == "tool_result":
                    cc = c.get("content")
                    if isinstance(cc, str):
                        result_bytes += len(cc.encode("utf-8"))
                    elif isinstance(cc, list):
                        result_bytes += sum(len((x.get("text") or "").encode("utf-8"))
                                            for x in cc if isinstance(x, dict))
                elif ctype == "text" and msg.get("role") == "assistant":
                    assistant_texts.append(c.get("text") or "")

answer = assistant_texts[-1] if assistant_texts else result.get("result") or ""
(out_dir / "answer.md").write_text(answer, encoding="utf-8")

usage = result.get("usage") or {}
run = {
    "schema_version": 1,
    "session_id": sid,
    "cli_session_id": session_id,
    "model_id": sorted(m for m in models if m) or ["glm-5.3-flash[1m] (inherited; result JSON model=null, client-side unrecognized_model warning)"],
    "material_bytes": (out_dir / "prompt.md").stat().st_size,
    "tool_calls": tool_uses,
    "visible_output_bytes": result_bytes,
    "file_opens_task_vault": vault_opens,
    "wall_clock_first_answer_s": round(t1 - t0, 3),
    "host_dispatch_epoch": t0,
    "host_return_epoch": t1,
    "cli_exit_code": rc,
    "wall_clock_transcript_span_s": None,
    "pack_contract_fallback": None,
    "platform_proxy": {
        "is_error": result.get("is_error"),
        "subtype": result.get("subtype"),
        "num_turns": result.get("num_turns"),
        "duration_api_ms": result.get("duration_ms"),
        "total_cost_usd": result.get("total_cost_usd"),
        "usage": usage,
        "stderr_head": (out_dir / "cli-stderr.txt").read_text(encoding="utf-8", errors="replace")[:400],
    },
    "transcript_path_host": str(transcript_src) if transcript_src else "unavailable",
    "contamination_audit": "pending",
}
if first_ts and last_ts:
    from datetime import datetime
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    try:
        span = (datetime.strptime(last_ts, fmt) - datetime.strptime(first_ts, fmt)).total_seconds()
        run["wall_clock_transcript_span_s"] = round(span, 3)
        run["transcript_first_ts"] = first_ts
        run["transcript_last_ts"] = last_ts
    except ValueError:
        pass
(out_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"session": sid, "cli_session": session_id[:8], "material_bytes": run["material_bytes"],
                  "tool_calls": tool_uses, "visible_output_bytes": result_bytes,
                  "vault_opens": vault_opens, "wall_s": run["wall_clock_first_answer_s"],
                  "answer_bytes": len(answer.encode("utf-8")), "transcript": bool(transcript_src),
                  "is_error": result.get("is_error")}))
