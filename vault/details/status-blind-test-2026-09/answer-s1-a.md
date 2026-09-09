依据且仅依据所给输出文本作答（未读取任何文件、未使用任何工具）。

**1. 当前 Focus**
Focus 是 TASK-0008，输出原文为 `focus: TASK-0008 (resolved)`。注意：文本只声称 focus 指向 TASK-0008 且带 "(resolved)" 标记，但**没有**解释 "(resolved)" 具体指什么（是指 focus 指示本身已被处理，还是指该任务的状态），仅凭文本无法判定其含义。

**2. 开放状态的任务及 lifecycle 分类**
开放（非 closed）任务共 3 个：
- TASK-0001 —— 分类：active（authority=2，path=vault/tasks/TASK-0001-self-hosting-pilot.md）
- TASK-0008 —— 分类：active（authority=3，path=vault/tasks/TASK-0008-owner-status.md）
- TASK-0004 —— 分类：blocked（authority=2，path=vault/tasks/TASK-0004-post-release-validation.md）

另外输出明确声称：draft 为 (none)，ready_for_review 为 (none)，unresolved 为 (none)，因此没有其他开放分类的任务。

**3. 已关闭任务数量**
5 个（来自 summary 行 `5 closed`）。注意：输出**没有**列出这 5 个 closed 任务的具体 ID 或清单，仅给出计数。

**4. unresolved 任务**
没有任何任务处于 unresolved 状态。输出声称：summary 行写 `0 unresolved`，明细行写 `unresolved: (none)`。因此它对任何具体任务都**没有**声称"状态无法解析"，也**没有**声称存在未解析的任务 ID、原因或数量大于零的情况。

**5. 有 Next Action 的任务**
三个开放任务都带有 `next:` 行，即都有 Next Action：
- TASK-0001：Next Agent 继续试点工作；在 `vault/details/shadow-run-2026-09.md` 中记录状态转换。
- TASK-0008：计划/红队/预注册已冻结；GLM 执行手写输出的五问测试，仅在其通过后才进入 M1-M5。
- TASK-0004：M3 No-Go 已采纳为 D-0004；当 owner 在本地模式下提供第二个真实项目时，从 blocked 恢复为 active。

closed 的 5 个任务未在输出中出现，其是否有 Next Action **无法回答**（文本未提供任何信息）。

```json
{"q1_focus": "TASK-0008 (resolved)", "q2_open": {"TASK-0001": "active", "TASK-0008": "active", "TASK-0004": "blocked"}, "q3_closed_count": 5, "q4_unresolved": [], "q5_next_actions": {"TASK-0001": "Next Agent 继续试点工作；在 vault/details/shadow-run-2026-09.md 记录转换", "TASK-0008": "GLM 执行手写输出五问测试，通过后才进入 M1-M5", "TASK-0004": "M3 No-Go 已采纳为 D-0004；owner 提供第二个真实项目后恢复 active"}, "any_unanswerable": false}
```
