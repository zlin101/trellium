你是一个没有任何历史上下文的评审员。下面是一份工具输出的完整文本。规则：只能依据这份文本回答问题，绝对不要读取任何文件、目录或使用任何搜索工具。如果仅凭该文本无法回答某个问题，必须明确写"无法回答"，并说明还缺什么信息。

---输出文本开始---
trellium status: /home/liam/git/trellium
focus: TASK-0008 (resolved)
summary: 0 draft, 2 active, 1 blocked, 0 ready_for_review, 5 closed, 0 unresolved
draft: (none)
active (2):
  TASK-0001 authority=2 path=vault/tasks/TASK-0001-self-hosting-pilot.md
    objective: Run the self-hosting pilot and collect K1-K4 shadow evidence.
    next: Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`.
  TASK-0008 authority=3 path=vault/tasks/TASK-0008-owner-status.md
    objective: Ship one 2026.09.5 feature from the Codex feedback audit: deterministic read-only status summary.
    next: Plan/red-team/preregistration frozen; GLM runs the handwritten-output five-question test, then M1-M5 only if it passes.
blocked (1):
  TASK-0004 authority=2 path=vault/tasks/TASK-0004-post-release-validation.md
    objective: Post-release validation: cold-start baseline, second-project pilot, Context Go/No-Go.
    next: M3 No-Go adopted as D-0004; resumes (blocked -> active) when the owner provides a second real project in local mode.
ready_for_review: (none)
unresolved: (none)
findings: none
result: 0 error(s), 0 warning(s)
---输出文本结束---

五问：

1. 当前 Focus 是哪个（哪些）任务？
2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？
3. 已关闭（closed）的任务有几个？
4. 有哪些任务的状态无法解析（unresolved）？输出对它们声称了什么、没有声称什么？
5. 哪些任务有 Next Action 可用？分别是什么？

请在最终回复中按 1-5 编号逐条作答（用中文），并在最后用一行 JSON 概括：{"q1_focus": "...", "q2_open": {...}, "q3_closed_count": N, "q4_unresolved": [...], "q5_next_actions": {...}, "any_unanswerable": true/false}
