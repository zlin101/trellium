# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。

## TASK-0004 - 2026-09-08

- Objective: 执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3（冷启动基线、第二个真实项目试点、Context Go/No-Go）；M4 仅在 Go 后另立 Level C 任务。
- Completed: 阶段立项与 M1 协议初稿（`vault/details/cold-start-baseline-2026-09.md`，7 个场景卡 + 指标定义 + 记录表）；M0（TASK-0002 accepted，D-0003）同日完成。
- In progress: 等待 owner 用无聊天历史的新会话逐场景跑 M1；M2 等 owner 提供第二个真实项目（local 模式）。
- Failed attempts: 无。
- Blockers: M1/M2 的执行主动权在 owner（新会话与第二个项目）；无其他阻塞。
- Next best action: owner 选 5-7 个场景逐个开新会话，按协议记录表逐行填写；跑完汇总后进入 M3 分析。
- Files to read first: `vault/details/cold-start-baseline-2026-09.md`、`docs/superpowers/plans/2026-09-08-post-release-validation-plan.md`、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/runtime.md`。

## TASK-0003 - 2026-09-08（已 accepted，保留供下一会话快速入场）

- Objective: 执行 `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` 的 M0-M3（M1 校准 K1-K4、M3 self-hosting CI 门禁；M2 归 TASK-0002；M4 长期观测留在 TASK-0001）。
- Completed: 全部完成并 accepted。M1 reconciliation 落地（canonical 映射，历史未改写）；M2 复核 latest 仍 2026.09.2；M3 CI 接入只读 self-hosting check（写权限仅限 PR self-heal job）。Review round 1（REQUEST_CHANGES，R1-R6）修复后 round 2 通过（canonical K1-K4 映射与 CI 范围获准）；push `fa2c7f4..7af24cf` 后首跑 run 34181086563 全绿（`gate` job 执行 vault check，`sync` job 正确跳过）；ready_for_review → accepted 转换经 owner 授权并计入 ledger。
- In progress: 无。
- Failed attempts: 首轮实现 6 项 review finding（权限暴露、转换漏记、提前勾选、失效风险、K3 误定性、模板残留），均已修复并复核。
- Blockers: 无（TASK-0002 已于同日 accepted）。
- Next best action: 进入「09.3 Post-release Validation」阶段（TASK-0004）；TASK-0002 交接已按压缩规则并入其任务文件。
- Files to read first: `vault/tasks/TASK-0003-review.md`、`vault/details/shadow-run-2026-09.md`（顶部 reconciliation）、`vault/runtime.md`。

## TASK-0001 - 2026-09-04

- Objective: 完成 review 修复并发布 2026.09.3；随后把本仓库接入为 tracked 自托管试点，开始 K1-K4 shadow 取证。
- Completed: 四项 check 修复已发布（commit 97d5506，tag 2026.09.3）；本仓库已 adopt（tracked）；创建 TASK-0001 与 `vault/details/shadow-run-2026-09.md`；完成首次转换 draft → active 与首次 handoff；交接前 `check --format json` 为 0 error / 0 warning。
- In progress: 试点覆盖指标（累计 5 真实 TASK / 6 次转换 / 2 次 handoff / 1 次 blocked → active）随真实工作逐步累积，当前 1 TASK / 1 转换 / 1 handoff / 0 blocked。
- Failed attempts: 无。
- Blockers: none。
- Next best action: 阅读 TASK-0001 的 Acceptance Criteria 与 shadow-run 台账；继续以真实开发任务填充试点覆盖；发现旧 prose TASK 语义与 check 冲突时按治理升级（Level C，另立任务）。
- Files to read first: `vault/tasks/TASK-0001-self-hosting-pilot.md`、`vault/details/shadow-run-2026-09.md`、`vault/runtime.md`、`docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 10 节。
- Environment snapshot（可选，观察于 2026-09-04，历史快照）: 协议 2026.09.3，GitHub Release 对象尚未创建（releases/latest 仍指向 2026.09.0，需用户在网页创建）。
