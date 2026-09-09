# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0008 - 2026-09-09

- Objective: 在 2026.09.5 交付唯一功能候选：确定性只读 `trellium.py status` summary；实现、消融与独立 review 全部完成后停在 `ready_for_review`，不代 owner accepted、不创建 tag/Release。
- Completed: Codex M0 预注册（`55ae985`）；GLM 完成实现前手写输出盲测并补齐 S0/S1 双臂消融（原始材料与逐字首答存 `vault/details/status-blind-test-2026-09.md`）；M1-M5 实现（`4604a0c`）、2026.09.5 版本/文档/快照（`62c2a0e`）；内部独立 review 两轮（round 1 P1 修复于 `7e494da`，round 2 APPROVE）。
- In progress: owner review round 的 3 项 P1 闭合中——①unresolved 原因码改为按 check finding phase 结构化推导（不再伪造 `TASK_RUNTIME_UNRESOLVED`，closed-local/dangling-duplicate 有专项测试）；②S0/S1 消融双臂补齐并存档；③本 handoff 条目同步。代码与记录更新后需复跑全量门禁。
- Failed Attempts: 无失败尝试；两轮 review 的 P1 均已修复或修复中（见上）。
- Blockers: 无外部 blocker。
- Next Best Action: 复核本轮 P1 修复提交；确认后由 owner 决定 accepted 与 `2026.09.5` tag/Release（D-0003：元数据可选）。不要重新实现——现状是修复与复验，不是从零开始。
- Files To Read First: `vault/tasks/TASK-0008-owner-status.md`、`vault/details/status-blind-test-2026-09.md`、`docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md`、`scripts/trellium.py`（status 段）、`scripts/test_trellium.py`（StatusSummaryTest）。

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
