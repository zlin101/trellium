你是一个没有任何历史上下文的评审员，正在模拟现行工作流：人工阅读 `vault/runtime.md` 全文与各任务文件的 `trellium-task-state` 状态块，手工编译项目状态。规则：只能依据下面给出的材料回答，绝对不要读取任何文件、目录或使用任何搜索工具；材料就是全部输入（该场景下没有其他任务文件）。若某问仅凭材料无法回答，必须明确写"无法回答"并说明缺什么。

---材料 1：vault/runtime.md 全文开始---
# Runtime Context

## Focus

- TASK-0013

## Active Tasks

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0010 | Draft the onboarding guide rewrite. | draft | Split the outline into reviewable sections. |
| TASK-0011 | Migrate the exporter to the stable writer API. | active | Run the characterization suite after the slice lands. |
| TASK-0012 | Cut the 3.2 release once the vendor fix lands. | blocked | Blocked on the vendor patch; revisit after upstream merges. |
| TASK-0013 | Land the retention policy documentation. | ready_for_review | Owner review of the documented retention rules. |
---材料 1 结束---

---材料 2：全部 6 个任务文件的状态块开始===
=== TASK-0010-draft ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0010",
  "level": "B",
  "authority_level": 1,
  "lifecycle": "draft"
}
-->
=== TASK-0011-active ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0011",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "active",
  "current_slice": "M2",
  "gates": {
    "design": "passed",
    "launch": "not_authorized"
  }
}
-->
=== TASK-0012-blocked ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0012",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "blocked",
  "gates": {
    "vendor": "blocked"
  }
}
-->
=== TASK-0013-ready ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0013",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->
=== TASK-0014-accepted ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0014",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "accepted"
}
-->
=== TASK-0015-superseded ===
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0015",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "superseded"
}
-->
---材料 2 结束---

五问：

1. 当前 Focus 是哪个（哪些）任务？
2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？
3. 已关闭（closed）的任务有几个？
4. 有哪些任务的状态无法解析（unresolved）？你的回答对它们声称了什么、没有声称什么？
5. 哪些任务有 Next Action 可用？分别是什么？

请在最终回复中按 1-5 编号逐条作答（用中文），并在最后用一行 JSON 概括：{"q1_focus": "...", "q2_open": {...}, "q3_closed_count": N, "q4_unresolved": "...", "q5_next_actions": {...}, "any_unanswerable": true/false}
