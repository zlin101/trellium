你是一个没有任何历史上下文的评审员。下面是一份工具输出的完整文本。规则：只能依据这份文本回答问题，绝对不要读取任何文件、目录或使用任何搜索工具。如果仅凭该文本无法回答某个问题，必须明确写"无法回答"，并说明还缺什么信息。

---输出文本开始---
trellium status: /tmp/fixture-mixed
focus: TASK-0013 (resolved)
summary: 1 draft, 1 active, 1 blocked, 1 ready_for_review, 2 closed, 0 unresolved
draft (1):
  TASK-0010 authority=1 path=vault/tasks/TASK-0010-draft.md
    objective: Draft the onboarding guide rewrite.
    next: Split the outline into reviewable sections.
active (1):
  TASK-0011 authority=2 slice=M2 gates: design=passed, launch=not_authorized path=vault/tasks/TASK-0011-active.md
    objective: Migrate the exporter to the stable writer API.
    next: Run the characterization suite after the slice lands.
blocked (1):
  TASK-0012 authority=2 gates: vendor=blocked path=vault/tasks/TASK-0012-blocked.md
    objective: Cut the 3.2 release once the vendor fix lands.
    next: Blocked on the vendor patch; revisit after upstream merges.
ready_for_review (1):
  TASK-0013 authority=3 path=vault/tasks/TASK-0013-ready.md
    objective: Land the retention policy documentation.
    next: Owner review of the documented retention rules.
unresolved: (none)
findings: none
result: 0 error(s), 0 warning(s)
---输出文本结束---

五问：

1. 当前 Focus 是哪个（哪些）任务？
2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？
3. 已关闭（closed）的任务有几个？
4. 有哪些任务的状态无法解析（unresolved）？输出对它们声称了什么、没有声称什么？
5. 哪些任务有 Next Action 可用？分别是什么？（若输出中出现 gate 或 slice 标记，请一并说明它们的原值，不要推断其含义超出字面。）

请在最终回复中按 1-5 编号逐条作答（用中文），并在最后用一行 JSON 概括：{"q1_focus": "...", "q2_open": {...}, "q3_closed_count": N, "q4_unresolved": [...], "q5_next_actions": {...}, "any_unanswerable": true/false}
