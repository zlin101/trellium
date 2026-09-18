# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0013 - 2026-09-18

- Objective: 修复 `adopt` 后协作核心未进入 Git `HEAD`、checker 却报告 0/0 的假健康；同时收紧 local ignore 边界，并以冻结 Gate 决定提示词是否进入 Skill。
- Completed: M0 预注册 + 红测已独立提交（c284557，早于全部产品修改）；M1 四格原始结果保留，owner review 按冻结 §7 正式改判 Inconclusive（P1 H3=1），双语候选契约已撤回；M2/M3 checker 主体、场景无关 `adopt` 提醒与 2026.09.8 文档保留。当前分支已有三笔 TASK-0013 本地提交（c284557、3eaa9d6、7b27cb6），均未 push/tag/release。
- In progress: owner review 修复已实现并经 Codex 主 Agent 三轮独立复审通过（无 open P0/P1/P2）；任务仅因 owner 核心文件尚未进入 HEAD 而保持 active。
- Failed attempts: checker 实现两次踩坑并由红测/自检暴露——`ls-tree` 需 `--full-name`（cwd 相对导致 monorepo 全漏报）；`check-ignore -v` 对取反模式也输出（本仓库白名单式 ignore 被整体误报 13 error，已按 `!` 前缀过滤并加回归测试）。
- Blockers: 加固后的 self-check 当前 2 errors：owner 未提交 `docs/engineering/code-comments.md`，且 owner 工作区 stamp 的核心集合与 HEAD stamp 不同；两者均属禁止触碰的 owner 状态，不能据此勾选全量 self-check 通过。
- Next best action: owner 决定并提交既有 `docs/engineering/code-comments.md` 与 `vault/.agent-init.json`，复跑 self-check 0/0 后转 ready_for_review；当前不 push/tag/release。TASK-0004 的 Orion 升级仍需后续 owner 授权。
- Files to read first: `docs/evals/adoption-durability-2026-09/results.md`、`vault/tasks/TASK-0013-adoption-durability.md`、`scripts/trellium.py`（check_core_storage/check_local_boundary）、`scripts/test_trellium.py`（AdoptionDurabilityTest）。

## TASK-0004 - 2026-09-18

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 已被 D-0004 关闭，仅在重开条件触发后另立 Level C 任务。
- Completed: M1 完成——S1-S7 七个独立新会话，判定 7/7 对、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0；M3 **No-Go 已被 owner 采纳为 D-0004**。Orion 已作为第二个真实 local 项目进入 M2，并产生首条真实观测：accepted local TASK 的 runtime 残留被 checker 以 `TASK_RUNTIME_CLOSED_LOCAL` 捕获。
- In progress: M2 Partial。Orion 已证明真实 local TASK 工作流与 Durable Knowledge Disposition 写入动作可执行，但尚未完成关闭投影清理与 tracked durable boundary。
- Failed attempts: Orion 首次 check 为 exit 2、1 error / 0 warning；这不是实验失败，而是待修复的真实产品信号。原有局限仍包括冷启动评分 key 污染与 bytes/耗时未完整采集。
- Blockers: 独立最小复现已确认 Trellium 2026.09.7 会把“核心协作层未进入 HEAD、fresh clone 全丢失”报告为 check 0/0；先由 TASK-0013 修复并发布，再要求 Orion 收尾，避免手工补丁掩盖产品缺陷。
- Next best action: 等 TASK-0013 accepted/release 后升级 Orion；随后删除 accepted TASK 的 runtime 行/Focus，明确 tracked core/stamp，执行 fresh-clone 0/0 验证并回填最终 K1-K4。D-0004 继续生效，不实现 Context。
- Files to read first: `vault/decisions.md`（D-0004）、`vault/details/cold-start-baseline-2026-09.md`（记录表+基线结论）、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。
