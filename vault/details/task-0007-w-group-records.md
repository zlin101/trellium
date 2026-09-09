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
