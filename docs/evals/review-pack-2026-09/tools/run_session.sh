#!/usr/bin/env bash
# Dispatch one frozen experiment session via headless CLI (protocol v1.1 §2a).
# usage: run_session.sh <s1|s2|s3> <R0|R1> <a|b|c...>
set -euo pipefail
EVAL=<host-path>/git/trellium/docs/evals/review-pack-2026-09
RUNROOT=/tmp/claude-headless-neutral
sid="$1-$2-$3"
pdir="$EVAL/runs/$sid"
prompt="$pdir/prompt.md"

mkdir -p "$RUNROOT"
t0=$(date +%s.%N)
cd "$RUNROOT"
set +e
NODE_OPTIONS="--max-old-space-size=1024" timeout 3000 claude -p \
  --output-format json \
  --max-turns 128 \
  --allowedTools "Read" "Grep" "Glob" "Bash" \
  --disallowedTools "Write" "Edit" "NotebookEdit" "WebFetch" "WebSearch" "Task" "TodoWrite" "Skill" "SlashCommand" "Agent" \
  > "$pdir/cli-result.json" 2> "$pdir/cli-stderr.txt" < "$prompt"
rc=$?
set -e
t1=$(date +%s.%N)
printf '%s\n%s\n%s\n' "$t0" "$t1" "$rc" > "$pdir/cli-timing.txt"
echo "session $sid rc=$rc wall=$(echo "$t1 - $t0" | bc)s"
head -c 400 "$pdir/cli-result.json" || true
