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
