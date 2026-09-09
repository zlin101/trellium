你是一个没有任何历史上下文的评审员。下面是一份工具输出的完整文本。规则：只能依据这份文本回答问题，绝对不要读取任何文件、目录或使用任何搜索工具。如果仅凭该文本无法回答某个问题，必须明确写"无法回答"，并说明还缺什么信息。

---输出文本开始---
trellium status: /tmp/fixture-conflict-local
focus: TASK-0020 (unresolved)
summary: 0 draft, 0 active, 0 blocked, 0 ready_for_review, 0 closed, 2 unresolved
draft: (none)
active: (none)
blocked: (none)
ready_for_review: (none)
unresolved (2):
  TASK-0020 reason=TASK_RUNTIME_DRIFT path=vault/tasks/TASK-0020-drift.md
  TASK-0021 reason=TASK_RUNTIME_LOCAL_UNRESOLVED
findings (2):
  ERROR   TASK_RUNTIME_DRIFT vault/runtime.md [TASK-0020]: runtime row for TASK-0020 says 'active' but the trellium-task-state block says 'draft'
  WARNING TASK_RUNTIME_LOCAL_UNRESOLVED vault/runtime.md [TASK-0021]: runtime points to local task TASK-0021, but its file is not in this worktree: this is expected in a fresh clone (local task files are ignored) or the file may have been lost locally; recover the original task file or rebuild the contract with owner approval; the runtime summary is an unverified clue and grants no authority
result: 1 error(s), 1 warning(s)
---输出文本结束---

五问：

1. 当前 Focus 指向哪个任务？它的状态能否被可信地确定？
2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？
3. 已关闭（closed）的任务有几个？
4. 有哪些任务的状态无法解析（unresolved）？输出对它们各自声称了什么、明确没有声称什么（例如 lifecycle 或 authority）？
5. 哪些任务有 Next Action 可用？如果都没有，输出是否让你清楚了原因？

请在最终回复中按 1-5 编号逐条作答（用中文），并在最后用一行 JSON 概括：{"q1_focus": "...", "q2_open": {...}, "q3_closed_count": N, "q4_unresolved": {...}, "q5_next_actions": "...", "any_unanswerable": true/false}
