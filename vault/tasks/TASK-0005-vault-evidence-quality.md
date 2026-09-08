# TASK-0005 - Vault 证据质量与重复状态收敛

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0005",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

消除试点覆盖计数的多 owner 漂移（计数单源化，记为 D-0005），并修复冷启动实验的方法学污染（评分 key 隔离、成本采集强制化、场景前提事实预检），使既有证据链可信、下一轮实验可复现。本任务为 owner 立项、非演示、针对已发生真实缺陷的治理修复；**不是为了满足 TASK-0001 数量门槛而创建**（按既有计数规则计入真实 TASK）。

## Scope

### In Scope

- M1：以 git 历史 + ledger 事件行逐条审计 TASK / transition / blocked→active / 跨 Agent handoff 计数；D-0005 入库；runtime 计数副本收敛为一句话+指针+未满足 Gate；handoff 头部加计数快照规则；ledger 汇总段标注 derived snapshot 截至 commit；TASK-0001 已满足 AC 勾选并附证据引用。
- M2：新建 `docs/evals/cold-start-v2/`（prompts.md = owner 投放原文；scoring.md = reviewer 评分规则，被测 Agent 禁读）；S3/S5 场景前提事实预检并修正；协议文件 append-only 追加 Protocol v2 指针、污染判定规则与下一轮强制指标。

### Out of Scope

- 修改 `scripts/trellium.py`、CI、init/协议模板、Skill 内容、公开 CLI、版本号、Release（含标题/notes）。
- 扩展或增强 checker；实现 Context Manifest；重开 D-0004；实现 evidence receipt / runtime generator / schema v2。
- 创建第二个（虚假）项目；创建 PR 制造 self-heal 证据；重跑 S1-S7；Manifest A/B。
- 删除或回写历史观测；推进 TASK-0001 lifecycle（其 Gate 未全满足）；推进 TASK-0004（保持 blocked）。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/handoff.md`、`vault/decisions.md`
- `vault/tasks/TASK-0001-self-hosting-pilot.md`、`vault/tasks/TASK-0004-post-release-validation.md`
- `vault/details/shadow-run-2026-09.md`、`vault/details/cold-start-baseline-2026-09.md`
- `docs/superpowers/plans/2026-09-08-post-release-validation-plan.md`
- Owner 任务书「Vault 证据质量与重复状态收敛」（2026-09-08，本任务的实施批准）

## Capability Tags

- documentation
- review

## Authority

Allowed:

- 本任务书明确列出的 vault/ 与 docs/ 修改（含创建 TASK-0005、D-0005、docs/evals/cold-start-v2/）；
- 提交并推送 develop，观察该 push 的 CI。

Requires Approval:

- 最终 accepted（owner 在 ready_for_review 后验收）；
- 范围外任何修改（一律需新的 owner 指令）。

Forbidden:

- 修改 `scripts/trellium.py`、CI、init/模板、Skill、公开 CLI、VERSION、tag、Release；
- 扩展 checker；引入 machine-readable coverage schema 或自动生成器；
- 删除/回写历史观测或首轮实验记录；为指标制造任务/观测；
- 创建额外 PR、Release、tag 或修改外部项目。

## Acceptance Criteria

- [x] 计数审计完成：审计基准（commit fd4287b）TASK=4、转换=8、blocked→active=1、跨 Agent handoff=2，逐条引用事件证据；本任务自身又产生 draft→active 与 active→ready_for_review 两次转换，现行值 TASK=5、转换=10（均以 ledger 事件行为准）；handoff.md 现存 3 条目 ≠ 历史 2 次跨 Agent handoff 的区别已在 derived snapshot 中说明。
- [x] D-0005 入库：覆盖事件为唯一事实源、汇总为 dated derived snapshot、runtime 只引用。
- [x] runtime 不再维护独立数字副本（TASK-0001 行改为一句话 + ledger 指针 + 未满足 Gate）；handoff 头部注明计数快照规则。
- [x] ledger 汇总段标注"derived snapshot，审计基准 commit fd4287b"。
- [x] TASK-0001 已满足且证据充分的 AC 勾选并附证据引用（转换≥6、handoff=2、blocked→active≥1、canonical K1-K4 观测）；未满足项（5th TASK 待 owner 确认 TASK-0005 计入口径、五问复盘）保持未勾选；TASK-0001 lifecycle 不变（active）。
- [x] `docs/evals/cold-start-v2/prompts.md` 与 `scoring.md` 就位：scoring.md 标明被测 Agent 禁读与 contaminated 判定；S3/S5 前提经事实预检修正（预检记录见 prompts.md 头部）。
- [x] 协议文件 append-only 追加 Protocol v2 指针、污染判定、下一轮强制指标；首轮 S1-S7 历史记录原样保留（仅追加，未改写）。
- [x] 门禁全绿：check 0/0、87/87、snapshot in sync、`git diff --check`；TASK/runtime/handoff/decision 投影一致；热文件预算正常（仅测量）。——终验记录：2026-09-08 owner review round 2 后复跑，check 0 error / 0 warning、87/87 OK、两套 snapshot in sync、`git diff --check` 通过、工作树干净；实施提交 5602228/a521650 的 CI 均绿。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/sync-skills.py --check`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `git diff --check`、`git status --short --branch`

Completed:

- 2026-09-08 Preflight：HEAD = origin/develop = `fd4287b`，工作树干净；与任务书预期基线一致。
- 2026-09-08 终验（owner review round 2 后）：check 0 error / 0 warning；87/87 tests；snapshot in sync；`git diff --check` 通过；工作树干净。实施提交：5602228（vault M1）+ a521650（evals M2），CI 均绿。

## Execution Record

### 2026-09-08 - Agent: GLM (ZCode)

Context read:

- 任务书全部 Required Reading（本会话内均为当前版本，preflight 现场核验 HEAD/工作树）。

Changes made:

- M0：创建本任务并完成 Red-team 反思；draft → active。
- M1/M2 待后续条目追加。

Checks run:

- Preflight：`git status --short --branch`（clean，与 origin 一致）；`git log`（HEAD=fd4287b）。

Review and reflection（Red-team，任务书第一节）:

1. **已真实发生**：①覆盖计数多 owner 漂移——runtime/ledger 写"3 TASK"、checker 报 current_task_files=4，checker 0 finding，人工复核才发现（ledger canonical K3 行有档）；②冷启动方法学缺陷——S5/S6/S7 在自然读取路径读到评分 key（三会话主动声明）、bytes/耗时大部分未采集、S3/S5 场景前提与事实不符（D-0003 作用对象、87/87 归属）且登记前未预检。
2. **非缺陷**：暂无第二个 local 项目（外部输入缺失）；PR self-heal 无真实 PR 证据（未发生，非失效）；Context 为 D-0004 No-Go（owner 决策）；Release 标题/notes 空（D-0003 已降 Optional）。均不得伪装成修复对象。
3. **最小修复**：①计数单源——D-0005（ledger 事件行 = 唯一事实源；汇总 = dated derived snapshot；runtime 只留一句话+指针+未满足 Gate；handoff 不存累计计数）；②Protocol v2——evals 目录隔离 prompts/scoring、contaminated 判定、强制成本指标、场景事实预检。
4. **删除修复后问题仍在？** 是：无 D-0005 则 runtime 仍是可独立编辑的第二计数 owner，漂移已发生会复发；无 v2 隔离则评分 key 仍在 AGENTS.md 细节路由上，污染会重现。
5. **副作用检查**：本修复减少状态 owner 数量（runtime 数字副本降为指针），不引入第二状态源；checker 一行不改；D-0004 不重开（v2 本轮不重跑、不做 A/B）。

补充说明：owner 消息末尾附有另一会话的 "Conversation recap"，其中"增强 checker 使重复/遗漏/漂移导致失败"与本任务书"不修改或扩展 checker"直接冲突；**以 owner 正式任务书为准**，不修改 checker。recap 其余建议（隔离评分 key、补齐 bytes/耗时、预检）与任务书一致，已涵盖。

Risks:

- 审计若发现计数与证据冲突，按任务书停止并报告，不猜测。

Next action:

- M1 计数审计与单源化实施。

### 2026-09-08 - Agent: GLM (ZCode) — M1 + M2 实施完成

Context read:

- 计数审计直接读取 ledger 事件行、handoff 条目、tasks 目录与 check 台账（grep 逐条核对，见 Checks run）。

Changes made:

- M1：D-0005 入库（索引+正文）；ledger 追加本任务 draft→active 行、汇总段重标为 derived snapshot（审计基准 fd4287b，现行 5 TASK / 10 转换 / blocked→active 1 / 跨 Agent handoff 事件 2 次含证据引用）；runtime TASK-0001 进度行收敛为一句话+指针+未满足 Gate；handoff 头部增加计数快照规则；TASK-0001 AC 证据勾选（4 项）。
- M2：新建 `docs/evals/cold-start-v2/prompts.md`（v2 提示词，S3 改用真实 TASK-0002/D-0003 序列、S5 修正 87/87 归属至 TASK-0002 文件，登记前完成事实预检）与 `scoring.md`（评分 key + 被测禁读声明 + contaminated 判定 + 七项强制指标 + 预检要求）；协议文件 append Protocol v2 节并在 v1 提示词节加追注。首轮历史未改写。

Checks run:

- 审计：K1 事件行 8 行（fd4287b 基线）+ blocked→active 定位 + check 台账 104/105 行证据定位（grep）。
- `python3 scripts/trellium.py check . --format json` → 0 error / 0 warning（提交前终验）。
- `python3 scripts/sync-skills.py --check` → in sync；87/87 tests；`git diff --check` 通过。

Review and reflection:

- 计数单源化后，runtime 首次不再持有任何可独立漂移的数字——这是本轮对"证据可信"最大的结构性改进。
- 跨 Agent handoff=2 的证据链依赖执行记录的 Agent 署名 + check 台账行，两处独立来源互相印证；若未来压缩规则把 handoff 条目进一步归并，证据仍在任务文件与 ledger 中，不受影响。

Risks:

- TASK-0005 计入 5-TASK Gate 与否由 owner review 裁定（AC 已注明两种口径）。

Next action:

- owner review（最终 accepted 与否由 owner 决定）；期间本轮修复即冻结，不追加范围。

## Memory Updates

- `vault/decisions.md`（D-0005）
- `vault/runtime.md`、`vault/handoff.md`（投影）
- `vault/details/shadow-run-2026-09.md`（snapshot 标注）、`vault/details/cold-start-baseline-2026-09.md`（v2 追加）
