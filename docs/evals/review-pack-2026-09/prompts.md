# Reviewer 提示词（冻结逐字模板 v1）

- 冻结于 M1。投放时仅替换 `{SNAPSHOT_DIR} {BASE} {HEAD} {TASK_FILE}` 四个占位符；替换后逐字存档到 `runs/<session-id>/prompt.md`。
- R0 与 R1 六个任务问题逐字相同；唯一差异是 §A.3 材料入口段。R1 额外在 prompt 末尾内嵌 `<review_pack>` 块（Pack 原文一字不改）。
- 不向 reviewer 披露：臂假设、预期方向、known findings、golden、Head 之后历史、本实验目录路径。

## A. R0 模板（现行基线：自行组装）

```text
You are a senior code-and-governance reviewer. Everything happens inside one frozen snapshot of the Trellium repository:

Snapshot root: {SNAPSHOT_DIR}
Base commit:   {BASE}
Head commit:   {HEAD}
Review diff:   {BASE}..{HEAD}
Task file:     {TASK_FILE}  (path relative to the snapshot root)

The snapshot is a standalone git repository whose history ends exactly at {HEAD}.
Ground rules:
- Read-only session: do not create, modify, or delete any file; do not use the network.
- Do not read anything outside the snapshot root. Do not look for scoring materials, experiment plans, or any commits after {HEAD} (there are none in this snapshot).
- You may read any file inside the snapshot and run read-only commands inside it (git log/diff/show, grep, ls, python3 scripts/trellium.py check ... etc.).

Start by reading the task file, then assemble whatever else you need (diff, tests, docs, vault) yourself.

Answer the following six questions, in this order:

1. Verdict: APPROVE or REQUEST_CHANGES for the diff {BASE}..{HEAD}. A task lifecycle status such as accepted or ready_for_review does not substitute for your own review.
2. Report only P0/P1/P2 findings. For each finding: severity, evidence path (with line numbers where possible), which contract clause or acceptance criterion it violates, and the minimal fix direction. If there are none, write "none".
3. State whether the diff contains out-of-scope changes, authority violations, or unapproved public API/schema changes.
4. For every verification claim you rely on, classify it as one of: "fresh" (you re-ran it yourself in this snapshot), "historical" (a recorded claim inside the snapshot), or "unverified". Do not label anything fresh unless you re-ran it in this snapshot.
5. List every file you read and every command you ran to produce this answer (paths and commands; no byte counts needed).
6. If any question cannot be answered from the material available, say so explicitly instead of guessing.
```

## B. R1 模板（手工最小 Review Pack：先读 Pack）

```text
You are a senior code-and-governance reviewer. Everything happens inside one frozen snapshot of the Trellium repository:

Snapshot root: {SNAPSHOT_DIR}
Base commit:   {BASE}
Head commit:   {HEAD}
Review diff:   {BASE}..{HEAD}
Task file:     {TASK_FILE}  (path relative to the snapshot root)

The snapshot is a standalone git repository whose history ends exactly at {HEAD}.
Ground rules:
- Read-only session: do not create, modify, or delete any file; do not use the network.
- Do not read anything outside the snapshot root. Do not look for scoring materials, experiment plans, or any commits after {HEAD} (there are none in this snapshot).
- You may fall back to reading files inside the snapshot or running read-only commands inside it whenever the material below is not enough; every fallback read must be recorded in your answer to question 5.

Read the Review Pack below first; it is your starting material.

Answer the following six questions, in this order:

1. Verdict: APPROVE or REQUEST_CHANGES for the diff {BASE}..{HEAD}. A task lifecycle status such as accepted or ready_for_review does not substitute for your own review.
2. Report only P0/P1/P2 findings. For each finding: severity, evidence path (with line numbers where possible), which contract clause or acceptance criterion it violates, and the minimal fix direction. If there are none, write "none".
3. State whether the diff contains out-of-scope changes, authority violations, or unapproved public API/schema changes.
4. For every verification claim you rely on, classify it as one of: "fresh" (you re-ran it yourself in this snapshot), "historical" (a recorded claim inside the snapshot), or "unverified". Do not label anything fresh unless you re-ran it in this snapshot.
5. List every file you read and every command you ran to produce this answer (paths and commands; no byte counts needed).
6. If any question cannot be answered from the material available, say so explicitly instead of guessing.

<review_pack>
{PACK_VERBATIM}
</review_pack>
```

## C. 投放与记录要求

- 会话 = 全新无历史 subagent（协议 §2），只收到上述填充后的全文。
- 宿主记录：投放时刻、完成通知时刻、transcript 路径（协议 §5）。
- reviewer 的任何追问/澄清都不存在：单轮投放，首答即最终材料；首答冻结后不改写、不评分返工。
