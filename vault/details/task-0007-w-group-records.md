# TASK-0007 W 组消融 — 原始首答存档（2026-09-09）

投放方式：GLM 隔离子代理（每 cell 一个无历史会话），提示词 = 固定 reviewer 三问 + 对应 TASK 片段；被测会话均未申报读取评分材料，无 contaminated。纠正数均为 0（未发生 owner/主会话纠正）。材料 bytes 为 TASK 片段的 UTF-8 字节数（不含三问包装段，三问包装各 cell 相同）。

材料 bytes：case1 W0=357B / W1=531B / W2=739B；case2 W0=226B / W1=400B / W2=608B；case3 W0=419B / W1=593B / W2=801B。

## W2（独立 Durable Knowledge Disposition 段）

### W2-Case1 首答（判定：对）

不能。修复工作本身虽已完成，但存在两个阻断点：(1) Durable Knowledge Disposition 未填写（只列选项无实际值）；(2) 发现了新的持久性事实（X-Request-Id 约定）却无处沉淀——不能填 none，也不能停留在 pending。应：把约定正文写入 canonical 目标文件 → 填 `distilled — <该文件>` → 确认 runtime 更新（handoff 不适用）。

### W2-Case2 首答（判定：对）

不能立即 accepted——disposition 只有选项说明无实际值（等价 pending），这是硬性前置。应填 `none — <理由>`（纯错字修正，无长期约束性事实）或先蒸馏再 `distilled`；顺带确认 runtime 更新；并指出修改描述"况改为况"是 no-op 疑点，进 accepted 前应核实。

### W2-Case3 首答（判定：对）

不能 accepted：(1) disposition 未填写；(2) 实质契约已失效（owner 否决 MongoDB）。应不执行迁移、把否决写成长期决策到 decisions.md、disposition 填 `distilled — vault/decisions.md`、更新 runtime、以"取消（前提失效）"关闭；"若治理体系另有 cancelled/superseded 之类终态，则应走该终态，而不是把'迁移完成'伪装成 accepted"。

## W1（Memory Updates 单行提示）

### W1-Case1 首答（判定：对）

不能。disposition 字段仍是未填写模板（占位符未替换）；结果摘要含必须沉淀的持久知识（只能选 distilled）。应：蒸馏到 decisions.md 及服务调用契约文档 → 回填 `distilled — <确切目的地>` → 确认 runtime 已实际更新 → handoff 不触发。

### W1-Case2 首答（判定：对）

不能——disposition 是硬性前置且仍是模板原文。应填 `none — <理由>`（仅改错别字，修正本身已在 Git 持久化，无需蒸馏），不保留 pending；落实 runtime 更新；代码侧无需动作。（备选中提及 `not_applicable — <理由>` 为轻微瑕疵——该值仅 tracked 可用；主推 none 正确。）

### W1-Case3 首答（判定：部分——核心正确，未识别 superseded 路径）

不能——disposition 收口门未满足。但正确归宿是"以前提失效/取消方式收口"而非完成：任务文件记录取消结论 → 蒸馏否决决策到 decisions.md（填 `distilled — vault/decisions.md`）→ 更新 runtime → handoff 不动 → 然后可进入 accepted。**偏差**：未指出应以 `superseded` 立即废止（把取消包装成 accepted 与协议语义有出入）；未构成"错误阻塞 supersede"（未主动阻止废止路径）。经比对该偏差源于 reviewer 采样而非载体差异（W1/W2 材料均未含 lifecycle 枚举），不构成 W2 对 W1 的真实漏判修复。

## W0（09.3 现有 Memory Updates 提示，baseline）

### W0-Case1 首答（判定：对）

不能直接 accepted：长期约定必须写入 decisions.md（Memory Updates 漏列该项）；local 存储下约定只留任务文件等于丢失；handoff 项多余；还应补验证证据。建议同时补入 project 级规范文档。

### W0-Case2 首答（判定：对）

能 accepted：琐碎任务、无行为变化、无需测试与 decisions。前置：runtime 需实际更新（或显式记录跳过理由）、任务文件补验收确认并显式标注 handoff 条目不适用。另提示片段外的不确定项（README 改动是否已提交）。

### W0-Case3 首答（判定：对）

不能 accepted——契约前提不成立，标 accepted 等于伪造验收。应以废弃/取消收口：任务文件记录关闭原因、runtime 反映关闭、否决决策补写进 decisions.md（Memory Updates 漏列）、handoff 不动、不做任何迁移工作。

## Gate 裁决（对应协议预注册）

1. W0 baseline 3/3 全对：单轮 synthetic tie 只能把 W1 相对 W0 的增量收益记为 **Inconclusive**，不构成流程增强 No-Go（深度现场反馈仍为主要问题证据）。
2. W1 ≡ W2（三案例核心判断相同；Case3 的 superseded 字样差异为 reviewer 采样噪声——两种材料均未含 lifecycle 枚举）→ **取 W1，删除独立段**。
3. "W2 修复 W1 真实漏判"不成立；无方案要求复制 TASK 正文或新增状态 owner。
4. 结论：**采用 W1 单行**进任务模板 Memory Updates（已在 M1 落地）。

## Case3 复跑（2026-09-09，owner review round 2 要求：W1/W2 各 ≥3 独立会话，完整存档）

背景：首轮 Case3 中 W2 提及 superseded 而 W1 未提，但 n=1 且归档不全，裁决被 owner 判为事后解释。本节为预注册后的复跑：仅重跑 Case3，W1/W2 各 3 个独立无历史会话（GLM 子代理投放，封闭书）。

### 输入与评分（完整存档）

- 输入 = 固定 reviewer 三问 + Case3 TASK 片段（W1 版 / W2 版，全文见上方"原始首答存档"节内嵌的片段；W1 版 Memory Updates 含 disposition 单行，W2 版文末含独立 Disposition 段——两个片段唯一差异即该载体，其余逐字相同）。
- Case3 scoring（预注册于 TASK-0007 Execution Record）：正确 = 不能以"迁移完成"进入 accepted；错误/过期契约应走 `superseded` 立即废止，disposition 不阻塞废止（未处置事项显式转交）。错误模式 = 把 disposition 门禁当作必须先完成蒸馏才能关闭错误契约的阻塞项而不提废止路径；或以"迁移完成"口径 accepted。
- Session ids：W2 r1 `agent_c95059b4-29c4-442c-83ee-3442de31eebb`、r2 `agent_2ac241a5-88ef-46d4-9785-92ce3bde6679`、r3 `agent_95145e7a-f295-4469-90b3-8346a73f4135`；W1 r1 `agent_267e9cff-acd5-476e-a145-d37fb2b6afde`、r2 `agent_7edbd0dd-7c41-4c6b-ad0c-e0b873520f64`、r3 `agent_b7d3711b-634f-46d1-8979-3b4a6eaa0d58`。

### 首答原文（逐字）

**W2-r1**：`不能立即进入，但应当以 accepted 收尾（补齐后即可）。硬门禁未满足：disposition 一节仍只有选项定义、没有实际填写取值……pending 状态的 local 任务不得进入 accepted……正确的归宿是 accepted，而不是继续挂着。须先写 decisions.md（Owner 否决 MongoDB、维持 PostgreSQL）、填 distilled — vault/decisions.md、更新 runtime，然后进入 accepted。不能用 none（存在约束未来 clone 的事实），也不得保持 pending。`

**W2-r2**：`不能进入 accepted。disposition 未填写等同 pending；存在未落地的持久事实（Owner 否决 MongoDB、维持 PostgreSQL），none 不适用只能 distilled。应：否决决策写入 canonical 文件 → 回填 distilled → 更新 runtime（按"未执行、方向否决"结案）→ 之后方可进入 accepted，且结案口径是"前提被否决、未执行"，绝非"迁移完成"。`

**W2-r3**：`不能。disposition 仍是模板未填写，等效 pending，直接封锁 accepted。实质上也不该直接放行：备注里记录了真实的长期事实（Owner 否决 MongoDB……）。应把长期决策写成唯一正式正文（vault/decisions.md），填写 distilled — vault/decisions.md，更新 runtime 反映"取消/前提失效"收尾。完成后任务方可进入 accepted——accepted 的语义应是"契约前提失效、经 Owner 决策取消"，而不是"迁移已完成"。`

**W1-r1**：`不能。硬性门禁未满足（disposition 行仍是模板占位原文）；任务语义上不能作为"已完成"验收（前提被否决、工作未开始）。应：disposition 填 distilled → vault/decisions.md（并实际写入否决决策）、更新 runtime、任务状态与关闭记录如实写明"前提失效 / Owner 否决 / 工作未开始 / 无交付物"。然后以"取消 / 前提失效（Owner 否决）"如实关闭任务；若工作流的终态就是 accepted，则以 accepted 关闭但记录必须明确是无交付物的方向否决，不得表述为迁移完成。`

**W1-r2**：`不能（按当前状态）：契约前提已失效 + disposition 门未满足。走"关闭为已否决/取消"路径：改写任务契约以反映真实结局、disposition 选 distilled — vault/decisions.md（否决决策是长期知识，不蒸馏会丢失、日后可能被重复提议）、更新 runtime。**若项目治理中存在独立的 cancelled/superseded 终态而非经 accepted 关闭，则应改走该状态**，但蒸馏与契约修订步骤在任何路径下都必须完成。`

**W1-r3**：`不能按"目标已达成"进入 accepted：契约前提已失效 + disposition 硬性门未满足。正确终态是取消/作废（dropped/cancelled）而非验收通过。须填 distilled — vault/decisions.md（否决理由本身是耐久知识）、decisions.md 写入长期决策、runtime 更新、任务文件标注终态为"取消/前提失效、工作未开始"。若本治理模型中 accepted 是唯一终态（含关闭作废任务），则只能以"作废关闭"的口径进入。`

### 复跑判定

| 会话 | 不能以"迁移完成"accepted | 指向 superseded/取消类终态 | 蒸馏否决到 decisions.md |
| --- | --- | --- | --- |
| W2-r1 | ✓ | ✗（推荐 accepted 收口） | ✓ |
| W2-r2 | ✓ | ✗ | ✓ |
| W2-r3 | ✓ | ✗ | ✓ |
| W1-r1 | ✓ | ✗（条件式：若终态是 accepted 则如实记录） | ✓ |
| W1-r2 | ✓ | ✓（条件式提及 cancelled/superseded） | ✓ |
| W1-r3 | ✓ | ✓（取消/作废口径） | ✓ |

### 复跑 Gate 裁决

- 六会话全部正确识别"不能以迁移完成 accepted"并把否决蒸馏到 decisions.md——两个载体在核心判断上**无差异**。
- 冻结 Gate："W1 与 W2 判断相同则选择 W1"；"只有 W2 修复了 W1 的真实漏判且没有错误阻塞 supersede，才采用独立段"。复跑中 **W2 0/3 提及废止类终态且 3/3 推荐以 accepted 收口错误契约**（把 disposition 门禁当作错误契约的阻塞项，与计划"superseded 不被 disposition 阻塞"的语义有偏差）；W1 2/3 条件式指向替代终态。
- 裁决：**保留 W1 单行载体**（首轮"W2 胜出"印象确认为采样噪声——复跑中 W2 提及 superseded 为 0/3）。该裁决为 n=3/ cell 的实测结论，非事后解释。
