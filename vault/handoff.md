# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0007 - 2026-09-09

- Objective: 执行 `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md`——local TASK 生命周期闭环（Durable Knowledge Disposition 人工 gate）与 clone-safe 投影（2026.09.4）。
- Completed: M0-M6 全部落地。W 组消融（W2→W1→W0，9 会话）裁定采用 W1 单行载体（原始记录见 `vault/details/task-0007-w-group-records.md`）；C0/C1/C2 characterization 证明 checker 代码层必要；checker 新增 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning（去重、三层文案、不授权）与 `TASK_RUNTIME_CLOSED_LOCAL` error；12 项决策表聚焦测试；VERSION 2026.09.4 + MIGRATIONS + 双语 README + 分发快照同步。独立 review 十问全过，F1（W 原始答案归档）/F3（测试计数虚增根因=继承重跑，已用 Mixin 消除）已修复，F2（预注册提交级证据）流程已采纳、叙述裁认随验收。
- In progress: 无。
- Failed attempts: 首版测试类继承 VaultCheckTest 导致父类 37 测试重复执行（计数 136 虚增）——已重构 Mixin，真实口径 87 基线 + 12 新增 = 99。
- Blockers: 无。
- Next best action: owner 验收 TASK-0007；accepted 后另行发布 2026.09.4 tag/Release（不在本任务范围）；第二真实 local 项目到位后按计划第 13 节做真实验证。
- Files to read first: `vault/tasks/TASK-0007-local-task-lifecycle.md`、`vault/tasks/TASK-0007-review.md`、`docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md`、`vault/decisions.md`（D-0006）。

## TASK-0004 - 2026-09-08

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0（记录表与基线结论在协议文件）；M3 结论 **No-Go 已被 owner 采纳为 D-0004**（M4 不立项、不实现 context、暂不补 A/B、AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件）。
- In progress: 无（等待外部输入）。
- Failed attempts: 无；实验设计备忘登记了评分 key 污染路径（3/7 场景读到 key，准确率按上限值口径）与 bytes/耗时未采集两项局限。
- Blockers: M2 等待 owner 提供第二个真实 local 项目；任务 active → blocked，项目到位后 blocked → active 继续 M2 与跨项目证据。
- Next best action: owner 提供第二个真实项目；期间由真实工作（TASK-0001）继续累积 K1-K4 证据，D-0004 的误判/成本重开证据若出现须先登记 ledger。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。

## TASK-0001 - 2026-09-04

- Objective: 完成 review 修复并发布 2026.09.3；随后把本仓库接入为 tracked 自托管试点，开始 K1-K4 shadow 取证。
- Completed: 四项 check 修复已发布（commit 97d5506，tag 2026.09.3）；本仓库已 adopt（tracked）；创建 TASK-0001 与 `vault/details/shadow-run-2026-09.md`；完成首次转换 draft → active 与首次 handoff；交接前 `check --format json` 为 0 error / 0 warning。
- In progress: 试点覆盖指标（累计 5 真实 TASK / 6 次转换 / 2 次 handoff / 1 次 blocked → active）随真实工作逐步累积，当前 1 TASK / 1 转换 / 1 handoff / 0 blocked。
- Failed attempts: 无。
- Blockers: none。
- Next best action: 阅读 TASK-0001 的 Acceptance Criteria 与 shadow-run 台账；继续以真实开发任务填充试点覆盖；发现旧 prose TASK 语义与 check 冲突时按治理升级（Level C，另立任务）。
- Files to read first: `vault/tasks/TASK-0001-self-hosting-pilot.md`、`vault/details/shadow-run-2026-09.md`、`vault/runtime.md`、`docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 10 节。
- Environment snapshot（可选，观察于 2026-09-04，历史快照）: 协议 2026.09.3，GitHub Release 对象尚未创建（releases/latest 仍指向 2026.09.0，需用户在网页创建）。
