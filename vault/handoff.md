# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0006 - 2026-09-08

- Objective: 执行 `docs/superpowers/plans/2026-09-08-non-context-vault-optimization-glm-plan.md`——六候选消融实验与逐项 Go/No-Go/Blocked 结论；仅 M2 可条件生产化。
- Completed: M0-M2 全部落地。预注册先于结果冻结；M1 基线矩阵（bytes 实测：默认路径 14.3 KB、最大 TASK 14.2 KB vs 深度现场 43-52/50-80 KB；事件审计多为 none observed）；M2 消融完毕——确定性矩阵 1 个设计内假阳性，判断 cell（E2→E1→E0，GLM 子代理封闭书投放，协议修订 1）：E0 4/4、E1 4/4、E2 3/4（场景 C 盲从假阳性判错）→ **M2 = No-Go**，v0 零代码；M3/M5-slice Blocked for evidence；M4 迁移规则草案；M5-decision D1 草案（未应用）；M6 延后。自查 review ledger 无 open finding。
- In progress: 无。
- Failed attempts: E2 自动 freshness 被 kill criterion 删除（假阳性误导）；E1 无已证明收益。
- Blockers: 无实现待办；M3/M5 解锁需第二 local 项目与真实复合任务（owner 侧）。
- Next best action: owner 验收 TASK-0006 各候选结论（可分别接受）；若不认可 M2 exploratory 强度，可亲手重跑采集 bytes/耗时（协议修订流程就位）。
- Files to read first: `docs/evals/non-context-optimization-2026-09/results.md`、`vault/tasks/TASK-0006-review.md`、`vault/tasks/TASK-0006-non-context-optimization.md`、`vault/runtime.md`。

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
