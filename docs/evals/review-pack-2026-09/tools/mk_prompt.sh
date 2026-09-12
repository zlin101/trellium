#!/usr/bin/env bash
# Assemble the verbatim prompt for one experiment session (protocol §4).
# usage: mk_prompt.sh <s1|s2|s3> <R0|R1> <a|b|c...>
set -euo pipefail
EVAL=<host-path>/git/trellium/docs/evals/review-pack-2026-09
SNAPROOT=/tmp/rp-eval-20260911

case "$1:$2" in
  s1:*) BASE=f98d302; HEAD=430de35; TASK=vault/tasks/TASK-0007-local-task-lifecycle.md;;
  s2:*|s3:*) BASE=55ae985; HEAD=7ff75a8; TASK=vault/tasks/TASK-0008-owner-status.md;;
  *) echo "bad scenario" >&2; exit 1;;
esac
[ "$1" = s3 ] && HEAD=5317784
SNAP="$SNAPROOT/$1"
PACK="$EVAL/packs/pack-$1.md"
OUT="$EVAL/runs/$1-$2-$3"
mkdir -p "$OUT"

python3 - "$EVAL/prompts.md" "$2" "$SNAP" "$BASE" "$HEAD" "$TASK" "$PACK" "$OUT/prompt.md" <<'PY'
import sys
from pathlib import Path
prompts_md, arm, snap, base, head, task, pack, out = sys.argv[1:9]
text = Path(prompts_md).read_text(encoding="utf-8")
# Extract the fenced template for the requested arm (section A = R0, B = R1)
sec = text.split(f"## {'A' if arm == 'R0' else 'B'}. ")[1].split("## ")[0]
tpl = sec.split("```text\n", 1)[1].rsplit("```", 1)[0]
body = (tpl.replace("{SNAPSHOT_DIR}", snap).replace("{BASE}", base)
           .replace("{HEAD}", head).replace("{TASK_FILE}", task))
if arm == "R1":
    pack_text = Path(pack).read_text(encoding="utf-8").rstrip("\n")
    body = body.replace("{PACK_VERBATIM}", pack_text)
for ph in ("{SNAPSHOT_DIR}", "{BASE}", "{HEAD}", "{TASK_FILE}", "{PACK_VERBATIM}"):
    assert ph not in body, f"unreplaced placeholder {ph}"
Path(out).write_text(body, encoding="utf-8")
print(f"{out}: {len(body.encode('utf-8'))} bytes")
PY
