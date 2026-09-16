# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0012 - 2026-09-16

- Objective: 将真实 Go 开发中发生的注释知识丢失转化为跨语言工程规范，同时用一跳条件路由避免默认上下文与 Vault 膨胀。
- Completed: M0 预注册、R0/R1/R2 结构消融（R1 Go）、公共核心 + Go/Python 适配、`adopt --profile PROFILE[=ROOT]` 多语言/多 root、单一项目文档、stamp schema 2、安全 upgrade/proposal、双语文档与 2026.09.7；实现提交 `bbae794`。136 tests、check 0/0、status 0 unresolved、snapshot/whitespace 通过。
- In progress: 无；任务已按真实顺序 active → ready_for_review，等待 owner 验收。
- Failed attempts: structured review 初轮发现 root 文档注入与 malformed stamp fail-open 两项 P1，均已改为写入前拒绝并补回归；无剩余 P0/P1/P2。
- Blockers: owner acceptance；push/tag/Release 未授权。
- Next best action: owner 复核 TASK-0012、`bbae794` 和 2026.09.7 迁移契约，决定 accepted 与后续发布。
- Files to read first: `vault/tasks/TASK-0012-code-comment-routing.md`、`docs/evals/code-comment-routing-2026-09/results.md`、`scripts/trellium.py`、`init/MIGRATIONS.md`。

## TASK-0011 - 2026-09-15

- Objective: 验证项目级工作 Skill 是否比 `AGENTS.md + vault` 有独立价值；仅在消融 Go 后把 `agent-task` 最小迁移为项目限定、语言无关 ID 的 `trellium-work`。
- Completed: M0 预注册冻结（`docs/evals/project-work-skill-2026-09/`，先于任何实现）+ M1 消融与结构测试。**判定 No-Go**：两臂全场景 0 关键遗漏/0 需要纠正/0 硬指标违规（A0 的 AGENTS.md+vault 底座充分，地板效应），A1 唯一差异是成本更高（visible +79%）；结构记录：经 `.claude/skills` 的项目级 trellium-work 未被 Codex 发现（其项目级发现位置 unverified）；`agent-task` 全局泄漏在 Codex 复现（与合同 Baseline 一致）。独立材料：`docs/evals/project-work-skill-2026-09/results.md`。
- In progress: 无——4 阻断闭合（历史重写经授权执行、CI 绿；Codex 结论收回为 unverified；P2 已改）；验收清单/Verification 于本轮补闭合（owner review 指出此前未闭合、且存在过早的"owner 复核通过"表述——已更正），任务以 ready_for_review 等 owner 复核。
- Failed attempts: 无。已知反例是 `AGENTS.md` 可能已经足够；若 A1 无关键遗漏或成本改善，必须 No-Go，不以架构整洁为由开发第二 Skill。
- Blockers: none。消融 Gate 已裁决 No-Go（`AGENTS.md` 底座充分的假设成立）；Codex 的项目级发现位置 unverified，未来任何项目 Skill 方案需先验证。
- Next best action: owner 验收 TASK-0011（ready_for_review）；2026.09.5 Release 对象（UI）仍待创建。原始归档与本地备份引用保留至 owner 验收后处置。
- Files to read first: `vault/tasks/TASK-0011-project-work-skill.md`、`vault/runtime.md`、`scripts/trellium.py`、`skills/agent-task/SKILL.md`、`scripts/install.sh`。

## TASK-0004 - 2026-09-08

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0（记录表与基线结论在协议文件）；M3 结论 **No-Go 已被 owner 采纳为 D-0004**（M4 不立项、不实现 context、暂不补 A/B、AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件）。
- In progress: 无（等待外部输入）。
- Failed attempts: 无；实验设计备忘登记了评分 key 污染路径（3/7 场景读到 key，准确率按上限值口径）与 bytes/耗时未采集两项局限。
- Blockers: M2 等待 owner 提供第二个真实 local 项目；任务 active → blocked，项目到位后 blocked → active 继续 M2 与跨项目证据。
- Next best action: owner 提供第二个真实项目；期间由真实工作（TASK-0001）继续累积 K1-K4 证据，D-0004 的误判/成本重开证据若出现须先登记 ledger。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。
