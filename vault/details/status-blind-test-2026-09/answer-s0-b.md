1. **当前 Focus**：TASK-0013，唯一一个。依据是 `vault/runtime.md` 的 "Focus" 段仅列出该项；其状态块（Level C、authority_level 3、lifecycle `ready_for_review`）与 Active Tasks 表中的行完全一致，两个证据源无冲突。

2. **开放状态的任务**：材料中"开放"的唯一可操作口径是 runtime.md 的 "Active Tasks" 表，共 4 个，各自的 lifecycle（状态块与表内 Status 一致）为：
   - TASK-0010 — `draft`（Level B，authority_level 1）
   - TASK-0011 — `active`（current_slice M2；gates：design=passed，launch=not_authorized）
   - TASK-0012 — `blocked`（gates：vendor=blocked）
   - TASK-0013 — `ready_for_review`

   需说明：材料本身未给出"哪些 lifecycle 值属于开放"的定义，此处以"被列入 Active Tasks 表"为口径。

3. **已关闭（closed）任务数**：**严格意义上无法仅凭材料回答**——材料没有提供 lifecycle 值与 open/closed 分类之间的映射（即没有定义 `accepted`、`superseded` 是否属于 closed）。缺失的是工作流的 lifecycle 分类学定义。可给出的有依据推断是：全部 6 个任务文件中，4 个在 Active Tasks 表内，其余 2 个（TASK-0014 `accepted`、TASK-0015 `superseded`）不在表内；若采用"不在 Active Tasks 表即为关闭"的操作口径，则 closed = 2。但这是推断口径，不是材料的直接陈述。

4. **无法解析（unresolved）的状态**：**没有解析层面的失败**。6 个状态块均为格式良好、`schema_version: 1` 的 JSON，`lifecycle` 字段齐全；TASK-0010–0013 的 lifecycle 与 runtime.md 状态列逐项一致。就 open/closed 归类而言，TASK-0014 与 TASK-0015 依赖第 3 问所述的推断口径（材料未定义其分类归属）。对这两个任务，我的回答**声称**：任务文件存在、状态块可解析、其声明的 lifecycle 分别为 `accepted` / `superseded`、且未出现在 runtime.md 的 Active Tasks 表中；**不声称**：`accepted` / `superseded` 等于"已关闭/已归档"（材料无此定义），也不声称它们的状态块损坏或与 runtime.md 存在冲突。

5. **有 Next Action 的任务**（共 4 个，全部来自 runtime.md 表的 Next Action 列）：
   - TASK-0010：Split the outline into reviewable sections.
   - TASK-0011：Run the characterization suite after the slice lands.
   - TASK-0012：Blocked on the vendor patch; revisit after upstream merges.
   - TASK-0013：Owner review of the documented retention rules.

   TASK-0014 与 TASK-0015 在材料中没有任何 Next Action 记录。我只声称"材料中没有记录"，不声称它们实际不存在下一步行动。

{"q1_focus": "TASK-0013", "q2_open": {"TASK-0010": "draft", "TASK-0011": "active", "TASK-0012": "blocked", "TASK-0013": "ready_for_review", "_caveat": "文本未定义 open，此处为非 closed 非 unresolved 的四个任务"}, "q3_closed_count": 2, "q4_unresolved": "无解析失败；6 个状态块均可解析，仅 TASK-0014/0015 的 closed 归类依赖材料未定义的 lifecycle 分类学", "q5_next_actions": {"TASK-0010": "Split the outline into reviewable sections.", "TASK-0011": "Run the characterization suite after the slice lands.", "TASK-0012": "Blocked on the vendor patch; revisit after upstream merges.", "TASK-0013": "Owner review of the documented retention rules."}, "any_unanswerable": true}
