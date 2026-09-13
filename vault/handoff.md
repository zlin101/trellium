# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。累计计数（TASK/转换/handoff 等）不在 handoff 保存：条目中的数字仅为撰写时点快照，权威来源是 `vault/details/shadow-run-2026-09.md` 的 append-only 事件行与 dated 汇总（D-0005）。

## TASK-0009 - 2026-09-13

- Objective: 以 TASK-0007/TASK-0008 的真实历史 review 快照，比较 R0 自行组装与 R1 手工最小 Review Pack；只在硬指标无损且成本收益明确时建议另立 R2 Level C。
- Completed: **owner 验收（accepted，2026-09-13）**，结论锁定：R1 = Inconclusive；R2 本周期不实现、不提案；12 clean / 7 contaminated；不得恢复 No-Go 与 over-determined 表述（D-0008）。M0-M5 + 两轮 owner review 修正全部闭合；独立 review 四轮 APPROVE。
- In progress: 方案 B 已执行完毕并 push（`ee4f223..a997f0e` 与 `a997f0e..c14ad60`）；全历史敏感扫描 0 命中、门禁全绿。**GitHub 未为两次 push 创建 workflow run——owner 诊断为 GitHub Actions 平台事故**（status 页 17:16 登记降级；两次 push 均已形成公开 PushEvent；workflow blob 与上次成功运行完全相同；账户级 Disable actions 项公共 API 无法排除，恢复后仍不触发才由 owner 登录检查）。恢复序列（owner 指定）：①等 Actions 恢复 operational；②提交一笔"记录事故恢复/CI 重触发"的正常 Vault 提交并 push（禁止 force-push）；③确认新 HEAD 产生 workflow run 且 gate success；④CI 绿后才可删除 bundle（`~/trellium-eval-raw-archive-20260913/develop-full-pre-rewrite.bundle`），并将 TASK-0010 draft→active。
- Failed attempts: 快照首建 refs 未清（重建）；两次 harness 内存守护击杀、一次 provider 配额、一次 argv 超长、一次宿主漏装配 prompt——均已留档并顺延补齐。
- Blockers: none（方案 B 已获批）。
- Next best action: 完成方案 B 执行与 CI 确认；CI 绿后将 TASK-0010 draft→active 作为下一产品任务。
- Files to read first: `docs/evals/review-pack-2026-09/results.md`（含 M4.1 修订记录与方案 B 设计）、`vault/tasks/TASK-0009-review.md`、`vault/tasks/TASK-0010-status-defects.md`。

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
