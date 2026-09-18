# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0013 - 2026-09-18

- Objective: 修复 `adopt` 后协作核心未进入 Git `HEAD`、checker 却报告 0/0 的假健康；同时收紧 local ignore 边界，并用最小提示词帮助 Agent 完成语义接入。
- Completed: owner 已批准 Level C 范围与 error 严重级别；独立复现已确认；状态块 `draft → active`（2026-09-18，K1 已记）；M0 完成——预注册冻结于 `docs/evals/adoption-durability-2026-09/`（P0/P1 材料、场景 fixture 快照、评分、污染规则、停止条件、checker severity 矩阵含非 Git `CORE_STORAGE_UNVERIFIED` warning），红测 7 例（6 expectedFailure 红 + 1 committed+dirty 绿控制）143 tests OK，证据存档 `runs/red-run-2026-09-18.md`。
- In progress: 无；等待 M0 提交授权，之后进入 M1。
- Failed attempts: SuperBizAgent 早期三臂实验不能作为正式对照（保留为 exploratory）；红测撰写发现非 Git 目标现状为全静默而非显式 warning，已在预注册 v1 内冻结为 `CORE_STORAGE_UNVERIFIED` warning 契约并设为红格。
- Blockers: M0 产出尚未提交——需 owner 批准独立提交，不得混入 owner 既有改动（`vault/.agent-init.json`、`docs/engineering/`）。
- Next best action: owner 批准后独立提交 M0（prereg + 红测 + 状态转换投影，早于任何 `scripts/`/`init/`/`skills/` 产品修改）；随后按 protocol §4 ABBA 顺序运行 P0/P1 四个无历史会话（工具 {Read}，先冻结全部首答再评分），Gate 裁决回填任务文件后进入 M2/M3 checker。不修 Orion。
- Files to read first: `docs/evals/adoption-durability-2026-09/protocol.md`、`vault/tasks/TASK-0013-adoption-durability.md`、`scripts/test_trellium.py`（AdoptionDurabilityTest）、`scripts/trellium.py`。

## TASK-0004 - 2026-09-18

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0；M3 **No-Go 已被 owner 采纳为 D-0004**。Orion 已作为第二个真实 local 项目进入 M2，并产生首条真实观测：accepted local TASK 的 runtime 残留被 checker 以 `TASK_RUNTIME_CLOSED_LOCAL` 捕获。
- In progress: M2 Partial。Orion 已证明真实 local TASK 工作流与 Durable Knowledge Disposition 写入动作可执行，但尚未完成关闭投影清理与 tracked durable boundary。
- Failed attempts: Orion 首次 check 为 exit 2、1 error / 0 warning；这不是实验失败，而是待修复的真实产品信号。原有局限仍包括冷启动评分 key 污染与 bytes/耗时未完整采集。
- Blockers: 独立最小复现已确认 Trellium 2026.09.7 会把“核心协作层未进入 HEAD、fresh clone 全丢失”报告为 check 0/0；先由 TASK-0013 修复并发布，再要求 Orion 收尾，避免手工补丁掩盖产品缺陷。
- Next best action: 等 TASK-0013 accepted/release 后升级 Orion；随后删除 accepted TASK 的 runtime 行/Focus，明确 tracked core/stamp，执行 fresh-clone 0/0 验证并回填最终 K1-K4。D-0004 继续生效，不实现 Context。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。
