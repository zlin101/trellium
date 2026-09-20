# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0013 / TASK-0014 - 2026-09-19

- Objective: 闭合 TASK-0013/0014 增量 review 中的 HEAD marker 漏报、fallback 路径穿越、profile symlink 外部读取与 locale 启发式四项 finding。
- Completed: 四项原 finding 与二次复核发现的“未选 profile 仍可被删除”授权过宽均已闭合；精确 managed-file 集合、统一 dirfd/fallback 防护、显式 locale 与 HEAD marker 回归通过，177/177 全绿，两任务进入 ready_for_review。
- In progress: 仅剩 owner 决定 accepted/commit；本轮未执行 commit/push/tag/release，TASK-0014 仍因 tracked 文件未提交产生预期 warning。
- Failed attempts: 原验收仅覆盖正常 committed snapshot，没有覆盖 marker 被后续提交删除、恶意 stamp 和 symlink profile 边界。
- Blockers: 技术层无 open P0/P1/P2；共享工作区 self-check 的 2 errors 仍只指向 owner 排除的 `vault/.agent-init.json` 与 `docs/engineering/code-comments.md`，不得由后续 Agent擅自修改或暂存。
- Next best action: owner 审阅并决定是否 accepted/commit；如授权提交，保持 owner 排除文件边界，提交后复跑 check/status，再另行决定发布动作。
- Files to read first: `vault/tasks/TASK-0013-adoption-durability.md`、`vault/tasks/TASK-0014-durable-language-profiles.md`、`scripts/trellium.py`、`scripts/test_trellium.py`。

## TASK-0004 - 2026-09-18

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0；M3 **No-Go 已被 owner 采纳为 D-0004**。Orion 已作为第二个真实 local 项目进入 M2，并产生首条真实观测：accepted local TASK 的 runtime 残留被 checker 以 `TASK_RUNTIME_CLOSED_LOCAL` 捕获。
- In progress: M2 Partial。Orion 已证明真实 local TASK 工作流与 Durable Knowledge Disposition 写入动作可执行，但尚未完成关闭投影清理与 tracked durable boundary。
- Failed attempts: Orion 首次 check 为 exit 2、1 error / 0 warning；这不是实验失败，而是待修复的真实产品信号。原有局限仍包括冷启动评分 key 污染与 bytes/耗时未完整采集。
- Blockers: 独立最小复现已确认 Trellium 2026.09.7 会把“核心协作层未进入 HEAD、fresh clone 全丢失”报告为 check 0/0；先由 TASK-0013 修复并发布，再要求 Orion 收尾，避免手工补丁掩盖产品缺陷。
- Next best action: 等 TASK-0013 accepted/release 后升级 Orion；随后删除 accepted TASK 的 runtime 行/Focus，明确 tracked core/stamp，执行 fresh-clone 0/0 验证并回填最终 K1-K4。D-0004 继续生效，不实现 Context。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。
