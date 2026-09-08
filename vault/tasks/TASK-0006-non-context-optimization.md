# TASK-0006 - 非 Context 优化：证据、发布边界与热路径实验

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0006",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "active"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-08-non-context-vault-optimization-glm-plan.md`：以消融实验（A0/A1/A2）评估六个非 Context 候选，产出逐项 `Go | No-Go | Blocked for evidence` 结论；唯一可条件进入生产实现的是 M2 Evidence Receipt v0（实验 Go 后按 v0 上限实现）。D-0004 Context No-Go 继续有效。

## Scope

### In Scope

- M0：preflight、本任务建立、`docs/evals/non-context-optimization-2026-09/` 实验目录与预注册（在看到结果前冻结 Gate）。
- M1：能力/问题基线矩阵（已解决/部分解决/未解决/无证据）、bytes 实测、证据来源分层（深度使用现场 vs 本仓库自托管）。
- M2：Evidence Receipt 消融（E0/E1/E2）——预注册、fixture、确定性 freshness 矩阵；判断 cell 由 owner 以无历史新会话执行；Go 后按 8.4 上限实现最小 v0 与聚焦测试。
- M3-M6：前置条件核验与只读实验/提案；按计划第 14 节产出 Blocked/No-Go/提案类结论。

### Out of Scope

- Context Compiler、持久 context pack、替代 AGENTS.md 必读路径（D-0004）。
- RAG/数据库/daemon/Web UI、权限 DSL、自动审批、自动 accepted、从 TASK 文本提取执行命令、保存完整 stdout/请求/响应/凭据。
- 批量迁移历史 TASK；worktree 锁；修改版本、tag、Release、CI 权限、业务代码。
- M3-M6 任一候选的生产 schema/checker/CLI（需 owner 二次批准）。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/decisions.md`（D-0001..D-0005）
- `docs/superpowers/plans/2026-09-08-non-context-vault-optimization-glm-plan.md`
- `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md`（既有能力基线）
- `vault/details/shadow-run-2026-09.md`、`vault/details/cold-start-baseline-2026-09.md`、`docs/evals/cold-start-v2/`
- `vault/tasks/TASK-0001/0004/0005`

## Capability Tags

- documentation
- testing
- review

## Authority

Allowed:

- 计划第 4 节授权：M0-M2 基线/实验/Go 后最小 Evidence Receipt v0；M3-M6 只读实验、文档提案与结论；必要的 `docs/`、`vault/`、`scripts/trellium.py`（仅限 M2 v0）、聚焦测试、init 模板与同步快照更新；正常提交、推送 develop 并观察既有 CI。

Requires Approval:

- M3-M6 任一候选进入生产 schema、checker 或 CLI；
- 改变 `trellium-task-state` schema_version 或既有字段语义；新增公开 CLI 子命令；
- 改变 tracked/local 策略、自动生成 runtime、修改治理规则；
- 发布新版本或创建 Release；
- 本任务 accepted（owner 验收）。

Forbidden:

- 计划第 3.4 节"明确不做"全部条目；
- 用 synthetic 样本冒充真实收益；污染TASK-0001 覆盖计数；
- 未经 owner 二次批准越过任一生产化门；
- 自行推进本任务到 accepted。

## Acceptance Criteria

- [ ] M0：TASK-0005 状态复核记录（未替 owner accepted）；实验目录四件套就位；Gate 在看到结果前冻结；实验样本标注 synthetic 并排除在 TASK-0001 覆盖计数外。
- [ ] M1：基线矩阵完成，每个候选有问题证据与来源等级；本仓库"无事件"处如实标 `none observed in this repository`；09.3 已解决能力从实现范围删除。
- [ ] M2：E0/E1/E2 预注册与 fixture 齐全；确定性 freshness 矩阵完成；旧证据误标 fresh = 0；判断 cell 交 owner 执行；v0 仅在实验 Go 后实现且不超 8.4 上限。
- [ ] M3-M6：逐项 `Go | No-Go | Blocked for evidence` 结论及引用；M4 交付迁移规则草案（无长 TASK 不迁移）；生产化提案不越二次批准门。
- [ ] 门禁与 review：每 milestone 门禁通过；finding 走独立 review ledger；最终 `ready_for_review`，不自动 accepted。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`、`python3 scripts/sync-skills.py --check`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`（实现性提交）
- `git diff --check`、`git status --short --branch`

Completed:

- 2026-09-08 Preflight：交接产物已先行提交（`5924753`，CI 34209304778 success）；HEAD=origin=5924753，工作树干净；TASK-0005 = ready_for_review（未 accepted，本任务不代决）。

## Execution Record

### 2026-09-08 - Agent: GLM (ZCode)

Context read:

- 本计划全文；vault 必读文件（均为本会话维护的当前版本）；冷启动 v2 协议与首轮记录；TASK-0001/0004/0005。

Changes made:

- M0：创建本任务（draft → active）；建立 `docs/evals/non-context-optimization-2026-09/` 四件套并在采集任何结果前冻结预注册。

Checks run:

- 见各 milestone 提交前门禁记录。

Review and reflection:

- 计划第 1 节对 7/7 冷启动结论的权重修正是本任务的前提：冷启动证明"小仓库必读路径可用"，不反证深度现场的 63 TASK / 50-80 KB TASK 结构性摩擦。
- M3（local 发布）与 M5（slice）的硬前置（第二 local 项目 / 两个真实复合任务）当前不满足，按计划只能产出 `Blocked for evidence`，不制造样本。

Risks:

- M2 判断 cell 依赖 owner 新会话执行；采集节奏不受本任务控制。
- 六候选中仅 M2 具备立即实验条件，其余结论强度受限于当前仓库规模。

Next action:

- 预注册冻结后进入 M1 基线矩阵。

### 2026-09-08 - Agent: GLM (ZCode) — M0-M2 落地，M3-M6 结论交付（实验/提案边界内）

Context read:

- 本计划全文；vault 必读；首轮冷启动记录与 v2 协议；实测 bytes（check measurements + wc）。

Changes made:

- M0：TASK-0005 复核（ready_for_review，未代决）；本任务 draft → active；`docs/evals/non-context-optimization-2026-09/` 四件套就位，预注册在任何结果前冻结。
- M1：基线矩阵写入 results.md——六候选问题证据 + 来源分层（A 深度现场 / B 本仓库）、bytes 实测（默认路径 14,288 B；最大 TASK 14,150 B vs 现场 43-52 KB / 50-80 KB）、自 09.3 真实事件审计（重复状态 1 次已修；其余 none observed）。
- M2：E2 比较规则冻结（10 场景确定性矩阵完成：1 个设计内假阳性，0 误标 fresh）；判断 cell 材料（E0/E1/E2 × 场景 A-D）就绪待 owner 投放；v0 未实现（无 Go）。
- M3/M5-slice：`Blocked for evidence`；M4：迁移规则草案（触发 20 KB / H1 先行 / H2 冷 journal）；M5-decision：D-0004 reconsider_when 提案草案（未应用）、D2 不触发；M6：延后。

Checks run:

- `python3 scripts/trellium.py check . --format json` → 0 error / 0 warning（提交前终验）。
- sync in sync；87/87 tests；`git diff --check` 通过。

Review and reflection:

- 六候选中四项的瓶颈是真实样本而非技术；本轮交付把"能实验的实验化（M2）"、"不能实验的显式 Blocked（M3/M5）"、"只能提案的提案化（M4/M5-decision/M6）"三类边界全部显式化，未越过任何二次批准门。
- 确定性矩阵中唯一的保守假阳性（无关 docs 变化 → historical）正是 R3 的关键证据点，已设计进判断 cell 场景 C。

Risks:

- M2 判断 cell 的执行节奏依赖 owner；结果回来前 M2 维持 Pending evidence，v0 不实现。
- synthetic 材料只证明边界正确性；生产收益主张需真实样本（协议 §1）。

Next action:

- owner 跑 M2 判断 cell；结果回填 results.md 后出 M2 最终结论；第二 local 项目到位解锁 M3。

## Memory Updates

- `vault/runtime.md`、`vault/handoff.md`（投影）
- `docs/evals/non-context-optimization-2026-09/results.md`（实验数据，append-only）
- `vault/decisions.md`（仅当 owner 作出长期选择时）
