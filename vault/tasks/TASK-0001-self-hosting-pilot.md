# TASK-0001 - Trellium 自托管试点与 shadow 取证

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0001",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "active"
}
-->

## Objective

把 Trellium 仓库自身作为第一个 tracked 模式自托管试点，在真实开发中积累 K1-K4 承重假设的 shadow 证据，并按期产出复盘，决定后续周期是否继续、调整或回退。

## Scope

### In Scope

- `vault/`、`AGENTS.md`、`skills/agent-task/SKILL.md` 的接入与日常维护。
- `vault/details/shadow-run-2026-09.md` 观测记录的持续填写。
- 每次交接与合并前运行 `python3 scripts/trellium.py check . --format json` 并留档结论。
- 试点结束后的简短复盘（五问）。

### Out of Scope

- 协议模板、`scripts/trellium.py`、Skill 包的任何功能改动（需要另立任务，且属 Level C）。
- context compiler、evidence freshness、runtime 自动生成、fact types 等后续能力。
- 对其他项目的接入。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md`（K1-K4 假设与重新进入条件）

## Capability Tags

- documentation
- testing
- review

## Authority

Allowed:

- 创建与更新 `vault/` 内文件；
- 以小 diff 方式更新 runtime/handoff 投影；
- 在观测记录中追加事实条目。

Requires Approval:

- 修改 `.gitignore` 的忽略策略（已获用户授权一次：解除 `AGENTS.md` 与 `vault/` 忽略）；
- 任何对协议模板或 checker 的修改；
- 删除或改写历史观测条目。

Forbidden:

- 为凑指标伪造观测数据；
- 把 check 的 warning 静默忽略不记录；
- 批量改写历史 TASK 文件。

## Acceptance Criteria

- [ ] 试点累计覆盖 5 个真实 TASK（不含纯演示任务）。
- [ ] 试点累计 6 次 lifecycle 转换，全部有对应观测条目。
- [ ] 试点累计 2 次跨 Agent handoff，每次交接前 `check --format json` 已运行且结论留档。
- [ ] 出现过至少 1 次 blocked → active 转换，阻塞原因与解除条件有记录。
- [ ] K1-K4 四个实验按预注册指标填写观测，不追加新指标。
- [ ] 复盘五问（check 真正捕获了什么 / 哪些字段没人用 / 投影维护成本 / 哪些规则需频繁解释 / 哪些预算只是理论值）逐条回答并形成结论。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`（每次交接与合并前，退出码必须为 0）。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`（涉及脚本提交时）。

Completed:

- 2026-09-04: adopt + check 退出 0（0 error / 0 warning）；`.gitignore` 解除忽略后任务文件可被 tracked。

## Execution Record

### 2026-09-04 - Agent: Claude (GLM)

Context read:

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`
- 用户试点指令（验收指标与四实验表）

Changes made:

- `.gitignore` 解除 `AGENTS.md` 与 `vault/` 忽略（用户已授权）。
- `trellium.py adopt .` 接入本仓库（tracked 模式）。
- 创建本任务文件与 `vault/details/shadow-run-2026-09.md` 观测记录。

Checks run:

- `trellium.py check . --format json` → 0 error / 0 warning（adopt 后基线）。

Review and reflection:

- 首个生命周期转换：draft → active（接入完成，试点开始执行）。

Risks:

- 单人开发可能长期只有 TASK-0001，5 个真实 TASK 的覆盖需要真实工作自然产生，不预造。

Next action:

- 由下一个会话/Agent 接手：按 runtime 的下一步推进，出现阻塞时记录 blocked → active 样本。

## Memory Updates

- `vault/runtime.md`（每次状态变化同步投影行）
- `vault/details/shadow-run-2026-09.md`（观测条目）
- `vault/handoff.md`（每次中断或交接）
