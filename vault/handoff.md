# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。

## TASK-0002 - 2026-09-04

- Objective: 为既有 `2026.09.3` tag 创建 GitHub Release，使 latest release 解析拿到新版。
- Completed: K4 policy 已校正为 measurement-only；87/87 tests、Skill 快照同步和提交后的 check 0/0 均通过；commit `1d9d19b` 已推送。用户已创建 **2026.09.2** 的 Release（latest 从 2026.09.0 改善到 2026.09.2），但 2026.09.3 的 Release 仍缺。
- In progress: Release 创建与 latest 验证。
- Failed attempts: `gh release create` 未触发远端写入，因为执行环境没有 `gh`；未读取或转存本地凭据。
- Blockers: 需要为既有 tag `2026.09.3` 创建 Release（notes 已备好在 `/tmp/trellium-2026-09-3-release-notes.md`；注意上次建到了 2026.09.2 tag 上）。
- Next best action: 打开 `https://github.com/zlin101/trellium/releases/new?tag=2026.09.3`（务必选 2026.09.3 tag），标题 `Trellium 2026.09.3 — Agent-native Vault checks`，粘贴已备好的 notes 并发布；或提供带 repo 权限的 token 由 Agent 经 API 创建。随后验证 `releases/latest` 解析到 2026.09.3，执行 blocked → active → accepted。
- Files to read first: `vault/tasks/TASK-0002-release-2026-09-3.md`、`vault/runtime.md`、`vault/details/shadow-run-2026-09.md`。

## TASK-0001 - 2026-09-04

- Objective: 完成 review 修复并发布 2026.09.3；随后把本仓库接入为 tracked 自托管试点，开始 K1-K4 shadow 取证。
- Completed: 四项 check 修复已发布（commit 97d5506，tag 2026.09.3）；本仓库已 adopt（tracked）；创建 TASK-0001 与 `vault/details/shadow-run-2026-09.md`；完成首次转换 draft → active 与首次 handoff；交接前 `check --format json` 为 0 error / 0 warning。
- In progress: 试点覆盖指标（累计 5 真实 TASK / 6 次转换 / 2 次 handoff / 1 次 blocked → active）随真实工作逐步累积，当前 1 TASK / 1 转换 / 1 handoff / 0 blocked。
- Failed attempts: 无。
- Blockers: none。
- Next best action: 阅读 TASK-0001 的 Acceptance Criteria 与 shadow-run 台账；继续以真实开发任务填充试点覆盖；发现旧 prose TASK 语义与 check 冲突时按治理升级（Level C，另立任务）。
- Files to read first: `vault/tasks/TASK-0001-self-hosting-pilot.md`、`vault/details/shadow-run-2026-09.md`、`vault/runtime.md`、`docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 10 节。
- Environment snapshot（可选，观察于 2026-09-04，历史快照）: 协议 2026.09.3，GitHub Release 对象尚未创建（releases/latest 仍指向 2026.09.0，需用户在网页创建）。
