你是一个没有任何历史上下文的评审员，正在模拟现行工作流：人工阅读 `vault/runtime.md` 全文与各任务文件的 `trellium-task-state` 状态块，手工编译项目状态。规则：只能依据下面给出的材料回答，绝对不要读取任何文件、目录或使用任何搜索工具；材料就是全部输入（该场景的任务文件只有下面列出的这一个，没有其他任务文件，也没有 TASK-0021 的任务文件）。若某问仅凭材料无法回答，必须明确写"无法回答"并说明缺什么。

---材料 1：vault/runtime.md 全文开始---
# Runtime Context

## Focus

- TASK-0020

## Active Tasks

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0020 | Objective for the drifted task. | active | Next action for the drifted task. |
| TASK-0021 | Objective for the missing local task. | active | Next action for the missing local task. |
=== TASK-0020-drift ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0020",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "draft"
}
-->
---材料 1 结束---

---材料 2：唯一存在的任务文件状态块（TASK-0020）开始---
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0020",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "draft"
}
-->
---材料 2 结束---

五问：

1. 当前 Focus 指向哪个任务？它的状态能否被可信地确定？
2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？
3. 已关闭（closed）的任务有几个？
4. 有哪些任务的状态无法解析（unresolved）或存在疑问？你的回答对它们声称了什么、没有声称什么？
5. 哪些任务有 Next Action 可用？如果都无法确定，请说明。

请在最终回复中按 1-5 编号逐条作答（用中文），并在最后用一行 JSON 概括：{"q1_focus": "...", "q2_open": {...}, "q3_closed_count": N, "q4_unresolved": {...}, "q5_next_actions": "...", "any_unanswerable": true/false}
