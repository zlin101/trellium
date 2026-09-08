# TASK-0004 - Post-release Validation：冷启动基线与 Context Go/No-Go

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0004",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "active"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md` 的 M1-M3：用冷启动对照实验建立新 Agent 的判断准确率与读取成本基线，推动第二个真实项目（local 模式）试点，最终产出 Context 功能的 Go/No-Go 结论。本任务不实现任何 Context 功能。

## Scope

### In Scope

- M1：维护冷启动协议（`vault/details/cold-start-baseline-2026-09.md`）；在无聊天历史的新会话中运行 5-7 个场景；如实记录准确率、越权、成本、过期证据误用与 owner 纠正次数。
- M2：owner 提供第二个真实项目后，以 local 模式接入并在 `vault/details/shadow-run-2026-09.md` 记录观测；推动 canonical K1-K4 达到"两个项目、累计 10 次状态变化"。
- M3：基于 M1/M2 记录写 Go/No-Go 结论（引用具体记录行），交 owner 决策。
- TASK-0001 五问复盘的协调与记录（复盘本体属 TASK-0001 验收）。

### Out of Scope

- M4 `trellium.py context` 命令的任何实现（仅 Go 后另立 Level C 任务）。
- evidence freshness、owner inbox、runtime 自动生成、schema v2、Release 自动化、RAG/数据库/daemon、自动审批（计划"明确不做"清单）。
- 修改 `scripts/trellium.py`、协议模板或 Skill 内容。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`
- `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md`
- `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 2 节（canonical K1-K4）
- `vault/details/cold-start-baseline-2026-09.md`、`vault/details/shadow-run-2026-09.md`
- `vault/tasks/TASK-0001-self-hosting-pilot.md`

## Capability Tags

- documentation
- testing
- review

## Authority

Allowed:

- 创建与更新本任务、协议文件与观测记录；
- 更新 runtime/handoff 投影与 ledger（append-only）；
- 在冷启动场景中修改本仓库 vault 状态以构造真实判断点（每次构造在协议中登记）。

Requires Approval:

- 第二个真实项目的接入与 storage 模式选择（owner 提供）；
- Go/No-Go 结论的最终采纳与 M4 立项（owner）；
- 冷启动场景涉及仓库可见的对外变更时（如 push 构造场景）。

Forbidden:

- 伪造场景、伪造观测、用主会话 Agent 代答冷启动问题；
- 提前实现 context/evidence/runtime generator；
- 回写历史观测行；为指标制造 TASK/转换/handoff。

## Acceptance Criteria

M1：

- [ ] 协议文件含场景卡、评分 key、指标定义与记录表；
- [ ] ≥5 个场景各有一次新会话冷启动记录（无聊天历史），指标逐项如实填写；
- [ ] 每次记录标注场景构造方式与会话标识，可复溯源。

M2：

- [ ] 第二个真实项目以 local 模式接入并产生真实观测；或如实记录"暂无第二个项目，未满足"，不降标准。

M3：

- [ ] Go/No-Go 结论文件引用 M1/M2 的具体记录行与数字；
- [ ] 结论交 owner，采纳与否由 owner 决定；
- [ ] 若 No-Go：明确记录"当前必读路径已准确/快速"的证据。

整体：

- [ ] 未夹带"明确不做"清单中的任何实现；
- [ ] 全部门禁（check / sync / 87 tests / git diff --check）在每个工作节点通过。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`（每次记录后与交接前）
- `python3 scripts/sync-skills.py --check`、`python3 -m unittest ...`（涉及提交时）
- `git diff --check`

Completed:

- 2026-09-08：任务创建，协议文件初稿完成（M1 可执行）。

## Execution Record

### 2026-09-08 - Agent: GLM (ZCode)

Context read:

- Owner 修订方案全文；TASK-0002/0003 收尾状态；shadow ledger（含 Codex 本日新增记录）。

Changes made:

- 创建本任务与 `vault/details/cold-start-baseline-2026-09.md` 协议初稿；阶段计划文档入库。
- 同一提交内完成 M0（TASK-0002 accepted，D-0003）。

Checks run:

- 见本轮提交前的门禁记录（check / sync / 87 tests / git diff --check）。

Review and reflection:

- M1 的证据效力取决于"新会话无历史"这一条件是否被严格遵守；协议中把会话标识列为必填字段。
- M2 是当前最大缺口，主动权在 owner（需提供真实项目）；不降标准、不造样本。

Risks:

- 冷启动场景由 agent 构造可能引入"为实验而改 vault"的噪音；协议要求每次构造登记并尽量复用真实状态。

Next action:

- owner 挑选时间逐场景开新会话跑 M1；或提供第二个项目启动 M2。

## Memory Updates

- `vault/runtime.md`（状态投影）
- `vault/details/cold-start-baseline-2026-09.md`（协议与记录）
- `vault/details/shadow-run-2026-09.md`（K1-K4 观测）
- `vault/handoff.md`（中断或交接时）
