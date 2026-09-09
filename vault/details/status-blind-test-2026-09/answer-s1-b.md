1. **当前 Focus**：TASK-0013（文本原值为 `focus: TASK-0013 (resolved)`）。即 Focus 指向 TASK-0013，括号中标注 "resolved"，该字样的确切含义文本未定义，仅按原值报告。该任务同时出现在 `ready_for_review` 分组下。

2. **开放状态任务**：文本本身没有出现 "open/开放" 这一术语，无法从文本直接断言某任务"处于开放状态"。文本能明确声称的是：四个任务分别属于以下 lifecycle 分类，另有 2 个 closed 任务（未列出身份）和 0 个 unresolved。若按"非 closed 即开放"的通常理解，开放任务即这四个：
   - TASK-0010 — draft
   - TASK-0011 — active
   - TASK-0012 — blocked
   - TASK-0013 — ready_for_review
   （缺口：文本未定义哪些分类算"开放"，尤其未说明 blocked、ready_for_review 是否计入。）

3. **已关闭任务**：2 个（summary 原文 "2 closed"）。文本只给出计数，没有任何 closed 分组的明细，因此无法从该文本得知这 2 个任务分别是哪些。

4. **无法解析（unresolved）的任务**：没有。输出声称 `unresolved: (none)`，summary 为 "0 unresolved"；因此不存在任何被标记为状态无法解析的任务，输出也没有对任何具体任务做出 unresolved 声称（自然也没有未声称的任务条目）。旁证：`result: 0 error(s), 0 warning(s)`。

5. **有 Next Action 的任务**（四个列出任务均有 `next:` 行）：
   - TASK-0010：Split the outline into reviewable sections.（无 gate/slice 标记）
   - TASK-0011：Run the characterization suite after the slice lands.（标记原值：`slice=M2`；`gates: design=passed, launch=not_authorized`）
   - TASK-0012：Blocked on the vendor patch; revisit after upstream merges.（标记原值：`gates: vendor=blocked`）
   - TASK-0013：Owner review of the documented retention rules.（无 gate/slice 标记）
   以上 gate/slice 值均按字面原样报告，不对其含义做超出字面的推断。

{"q1_focus": "TASK-0013 (resolved)", "q2_open": {"TASK-0010": "draft", "TASK-0011": "active", "TASK-0012": "blocked", "TASK-0013": "ready_for_review", "_caveat": "文本未定义 open，此处为非 closed 非 unresolved 的四个任务"}, "q3_closed_count": 2, "q4_unresolved": [], "q5_next_actions": {"TASK-0010": "Split the outline into reviewable sections.", "TASK-0011": "Run the characterization suite after the slice lands. [slice=M2; gates: design=passed, launch=not_authorized]", "TASK-0012": "Blocked on the vendor patch; revisit after upstream merges. [gates: vendor=blocked]", "TASK-0013": "Owner review of the documented retention rules."}, "any_unanswerable": false}
