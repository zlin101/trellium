# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0004 - 2026-09-08

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0（记录表与基线结论在协议文件）；M3 结论 **No-Go 已被 owner 采纳为 D-0004**（M4 不立项、不实现 context、暂不补 A/B、AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件）。
- In progress: 无（等待外部输入）。
- Failed attempts: 无；实验设计备忘登记了评分 key 污染路径（3/7 场景读到 key，准确率按上限值口径）与 bytes/耗时未采集两项局限。
- Blockers: M2 等待 owner 提供第二个真实 local 项目；任务 active → blocked，项目到位后 blocked → active 继续 M2 与跨项目证据。
- Next best action: owner 提供第二个真实项目；期间由真实工作（TASK-0001）继续累积 K1-K4 证据，D-0004 的误判/成本重开证据若出现须先登记 ledger。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。
