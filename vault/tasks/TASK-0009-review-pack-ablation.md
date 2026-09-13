# TASK-0009 - Review Pack R0/R1 消融与 R2 准入

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0009",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "accepted"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-11-review-pack-ablation-glm-plan.md`：以 TASK-0007/TASK-0008 的真实历史 review 快照完成 R0（reviewer 自行组装）与 R1（手工最小 Review Pack）消融，判断固定 review 输入集合是否在硬指标无损下带来可测成本收益。R2 确定性公共 CLI 仅可形成准入建议，不在本任务实现。

## Scope

### In Scope

- M0：方案、TASK、协作偏好、runtime/handoff/shadow ledger 同步。
- M1：实验 protocol/prompts/scoring/results 空模板预注册并独立先行提交。
- M2：三个冻结历史快照、owner finding golden、三份机械手工 R1 Pack。
- M3：R0/R1 至少 12 个独立无历史会话；按冻结分歧规则最多追加 6 个。
- M4：准确率、安全边界、读取成本和 builder 成本评分；R1 Go/No-Go/Inconclusive。
- M5：独立 review、门禁与 Vault 收尾，任务最多到 ready_for_review。

### Out of Scope

- 实现 `review-pack`/`context`/`inbox`/Evidence Receipt，修改任何产品代码、公开 CLI 或 schema。
- VERSION、MIGRATIONS、README、protocol、Skill 或分发快照更新。
- 持久化 Pack、自动测试/修复/批准/accepted、网络或外部项目验证。
- 重开 D-0004；将 R2 并入其他命令以绕过 Level C 审批。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/collaboration.md`
- `Vault-Agent-Native-使用评估与优化建议-2026-09-03.md` §14.6、§16
- `docs/superpowers/plans/2026-09-11-review-pack-ablation-glm-plan.md`
- `vault/tasks/TASK-0007-local-task-lifecycle.md`
- `vault/tasks/TASK-0007-review.md`
- `vault/tasks/TASK-0008-owner-status.md`

## Capability Tags

- documentation
- testing
- review

## Authority

Allowed:

- Owner 的“同意，开始吧”批准本计划内 Level B R0/R1 实验、历史快照读取、记录、评分、独立 review 和正常里程碑提交。
- 在临时目录创建只读历史快照；运行不改变当前工作树的本地检查。

Requires Approval:

- 任何 R2 公共 CLI/JSON、产品代码、schema/protocol、版本/发布或 Skill/快照修改。
- TASK-0009 进入 accepted；扩大场景到外部项目；改变预注册 Gate 后继续沿用旧结果。

Forbidden:

- 在 R0/R1 结论前实现 R2；用 LLM 摘要或 golden 提示制造 R1 优势。
- 把历史测试 claim 标 fresh；自动推断授权、accepted 或外部系统状态。
- 读取/保存凭据；checkout/reset 当前开发工作树；静默覆盖 owner 的 `vault/collaboration.md` 修改。

## Acceptance Criteria

- [x] M0 正式计划包含真实问题证据、R0/R1/R2 边界、历史正负场景、盲法、指标、停止条件和 red-team。
- [x] M1 预注册四件套的提交严格早于 Pack 和结果。（独立 review：DAG "airtight"，`543d8f3` 先于 `6e1b1bf` 与全部会话存档）
- [x] 三个历史场景可重放，golden 来自 Head 后 owner review，reviewer 无泄漏。（三快照五点验收；泄漏 grep 全净；独立 review 10 项审计 PASS）
- [x] R0/R1 初始 12 会话及必要 tie-breaker 原文、工具与成本完整存档。（19 个会话目录：12 有效 + 7 污染作废 + 5 infra 中断，全部逐字留档；工具存档 `tools/`）
- [x] 硬指标/成本可从原始记录重算，R1 结论严格使用冻结 Gate。（独立 review 逐项机械重算确认；正式结论 Inconclusive——control_invalidated 触发计划 §10.1 封顶，召回/成本缺口作为决策记录保留）
- [x] R2 未实现；Go 时只交 owner 审批的 Level C 提案。（Inconclusive，无提案，产品代码零改动；R2 本周期不实现）
- [x] 独立 review 无 open/needs-discussion，Vault 门禁通过，任务停在 ready_for_review。（独立 review 四轮：R1/R2/R3.5/R4，终局 APPROVE；owner 两轮 review 共 8 项发现全部修正）
- [x] owner 验收（2026-09-13）：R1 = Inconclusive；R2 本周期不实现、不提案；实验数据 12 clean / 7 contaminated；**owner 指令：不得恢复早期 No-Go 或 "over-determined" 表述**。

## Verification

Required:

- `git cat-file -e 'f98d302^{commit}'`
- `git cat-file -e '430de35^{commit}'`
- `git cat-file -e '55ae985^{commit}'`
- `git cat-file -e '7ff75a8^{commit}'`
- `git cat-file -e '5317784^{commit}'`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`

Completed:

- 2026-09-11 M0 现场：五个冻结 commit 均存在；TASK-0007/0008 的 Head 后 owner findings 与 accepted 控制可追溯；未修改产品代码。
- 2026-09-11 M1（`543d8f3`）：预注册四件套独立提交，先于全部 Pack 与会话；scoring golden 锚点逐条在对应 Head 验证。
- 2026-09-11 M2（`6e1b1bf`）：三快照五点验收（首建因 refs 未清判 FAIL 后重建）；v1.2 冻结规则机械生成三份 Pack；独立只读检查 10/10 PASS；宿主泄漏 grep 全净；12 份 prompt 预装配。
- 2026-09-11/12 M3：19 个会话串行投放（16 有效 + 3 污染作废），5 次 infra 中断留档；协议 v1.1–v1.4 演进全部先于受影响评分；逐会话存档提交。
- 2026-09-12 M4（`493f8dc`）：首答全部冻结后评分。初版判定 No-Go（后被 owner review 更正，见下）。当时记录：负对照 fabricated blocker=1；S1/S2 召回缺口；wall-clock 恶化；control_invalidated 双登记。
- 2026-09-12 M5：独立 review Round 1 REQUEST_CHANGES（4×P1+5×P2，全部记录准确性问题）→ 修复 `10647bd` → Round 2 **APPROVE**；全门禁绿。
- 2026-09-13 M5.1（owner review，REQUEST_CHANGES → 修正）：①正式判定按计划 §10.1 封顶改为 **R1 = Inconclusive**（初版 No-Go 违反"control_invalidated 后结论最多 Inconclusive"）；②v1.4 白名单严格适用，新作废 4 个 Skill 会话（漏检根因：审计脚本未实现白名单+扫描时点过早），有效会话 16→12，聚合重算（visible −57.6%、vault −46.2%、wall +24.4%）；③召回改用冻结 known P0/P1 分母（S1 1/4=25% FAIL、S2 2/2=100%）；④push 前隐私/历史三选一方案待 owner 授权，未 push 未重写；⑤status 缺陷 severity 按 owner 裁定入档并另立 TASK-0010；⑥vault 同步矛盾修正、`git diff --check` 范围级口径 + 逐字证据豁免入 Required Checks。
- 2026-09-13 M5.2（owner 二轮 2×P1 → 修正 → Round 4 APPROVE → **owner 验收**）：①最终 v1.4 审计对 19 个 transcript 落盘（mechanical/裁决/终判三层，12 clean / 7 contaminated，机械-最终分歧仅 s3-R0-b/c 两例且裁决在案）；②方案 B 增补五项历史安全设计（git bundle 保留至 push+CI 绿、commit-map 与锚点 hash 映射、可重算性分级、全历史 0 命中扫描、备份引用不 push）；③TASK-0010 refused-vault 设计改 owner 联合记录形状。owner 最终验收：**accepted**，结论锁定（Inconclusive / R2 不实现 / 12c-7v / 不得恢复 No-Go 与 over-determined 表述）；方案 B 获准执行（顺序与门禁按 owner 列举）；TASK-0010 批准排期（B 完成 + push + CI 绿后 draft→active）。

## Execution Record

### 2026-09-11 - Agent: Codex — M0 方案、反思与消融契约

Context read:

- AGENTS、Vault index/runtime/governance/collaboration/handoff、TASK 规则、shadow ledger。
- Codex 深度反馈 §14.6/§16、TASK-0007 review、TASK-0008 任务与历史提交。

Changes made:

- 将 R0/R1/R2 从“三个要开发的修复”校正为两臂验证 + 条件式实现候选。
- 冻结两个真实返工正样本和一个 accepted 负对照；加入 full-patch、golden 隔离、污染和 builder 成本规则。
- R2 明确锁在另行 Level C 审批之后；本任务不修改 CLI/schema/version/Skill。

Checks run:

- 五个冻结 commit 均经 `git cat-file -e` 验证存在。
- `python3 scripts/trellium.py check . --format json`：0 error / 1 warning；唯一 warning 是新 tracked TASK 在 M0 提交前的预期 `TASK_STORAGE_PENDING`，不得冒充 0/0。
- `python3 scripts/sync-skills.py --check`：两套 snapshot in sync。
- `git diff --check`：通过。

Review and reflection:

- 单看 bytes 会把人工 Pack 构建成本藏起来，因此 reviewer 成本和端到端成本分开报告。
- 只用缺陷快照会奖励过度报错，因此加入最终 accepted 负对照与 fabricated-blocker 硬失败。
- M0 自审修复两处方法问题：耗时改由宿主记录首答完成时间、正确性事后评分；负对照若出现可独立复现的新 blocker，标 `control_invalidated` 并把结论限制为 Inconclusive，不把真实缺陷压成误报。
- 30% 只是本实验准入阈值，不进入 Vault budget policy。

Risks:

- 本仓库历史样本只有三个，外部有效性有限；每格 n=2 仍属探索性证据。
- reviewer 能否取得精确模型 id 依运行环境而定；不可得时必须标 unavailable。

Next action:

- GLM 先审阅并独立提交现有 M0 change set，再完成 M1 独立预注册提交；随后才能制作 Pack，禁止直接修改 `scripts/trellium.py`。

## Memory Updates

- `vault/runtime.md`
- `vault/handoff.md`
- `vault/details/shadow-run-2026-09.md`
- `vault/collaboration.md`
- Durable knowledge disposition: not_applicable（tracked TASK）
