# TASK-0006 - Review Ledger

## Findings

- R1 · fixed · E0 材料直递被测会话，未测真实仓库中"自由文本记录散落难检索"的成本（深度现场的主要痛点）· 已在 results.md M2 结论的已知局限中声明；扩展需新预注册，不在本周期伪造
- R2 · fixed · 判断 cell 由 GLM 子代理投放，bytes/工具调用/耗时无法精确采集，强 Go 信号（≥30% 成本改善）不可确立 · 协议修订 1 已声明；结论限定准确率维度 + exploratory
- R3 · fixed · E2 场景 C 判错（盲从设计内假阳性）· 这正是实验目标信号：按任务书 8.3 删除自动 freshness，保留 E1 争议随 E1 整体 No-Go 一并归档
- R4 · fixed · receipt 样本使用 schema_version: 0 标记 · 已确保不被误读为已授权 schema；v0 未实现

## Round 2026-09-08（GLM 自查，对照任务书第 15 节 review 门）

- proposal/experiment 未写成 approved behavior（receipt 标 0 号实验稿；reconsider_when 为未应用草案）✓
- 未新增第二事实源（results.md 为实验数据，非状态 owner；计数 owner 仍是 ledger）✓
- 未扩大 CLI、依赖、权限或数据收集 ✓
- 未用 synthetic 冒充真实收益（全部标注 synthetic/exploratory/none observed）✓
- D-0004 未被改变（reconsider_when 草案未应用）✓
- 失败 cell 与污染状态如实记录（C-E2 判错入表；0 contaminated）✓
- 消融已到更小方案：E2 被 kill，E1 随无收益整体 No-Go，v0 零代码 ✓

无 `open`、无 `needs-discussion` 遗留；两项局限（R1/R2）以声明形式记录，扩展归 owner 决策。任务进入 ready_for_review。

### Round 2（owner 独立 review，REQUEST_CHANGES，2026-09-08）

- R5 · fixed · TASK-0005 最终门禁 AC 未勾选（检查实际通过但形式验收未闭合）· 终验已补记、AC 已勾选；TASK-0005 留待 owner accepted
- R6 · fixed · results.md 未保存 12 份首答原文，"可复现"表述过强 · 原始首答已逐字存档（results.md"原始首答存档"节，含全部 12 cell）
- R7 · fixed · M2 结论范围过大：E1 不能声称触发完整 kill criterion（成本未测），v0 不能表述为方向被证伪 · 口径修正为 E2 No-Go / E1 Inconclusive（Blocked for cost evidence）/ v0 本周期 No-Go for implementation；协议修订 3 同步
- R8 · fixed · untracked 场景 golden"一律 fresh"不安全（新 untracked 源码/配置可能改变行为）· 拆分为 scope 外 fresh / scope 内或影响不明 historical-or-unresolved；协议修订 2 废弃原规则（未被已跑 cell 使用，无结果失效）
- R9 · fixed · M4 的 20 KB 阈值无证据（当前最大任务无阅读障碍事件，违背"先观察障碍再冻结阈值"）· 已删除；改为"真实障碍事件 + H0/H1/H2 基线后再定"
- R10 · fixed · D-0004 reconsider_when 草案冗余（D-0004 已完整包含相同条件，D0 已被正确使用）· 裁定 **D0 sufficient；D1/D2 当前 No-Go**；草案标注已否决并保留记录

Round 2 结论：6 项 finding 全部修复，无 wont-fix。任务按修正后口径（**E2 No-Go、E1 Inconclusive、v0 本周期不实现**）留待 owner accepted。
