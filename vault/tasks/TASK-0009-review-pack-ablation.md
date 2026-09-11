# TASK-0009 - Review Pack R0/R1 消融与 R2 准入

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0009",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "active"
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
- [ ] M1 预注册四件套的提交严格早于 Pack 和结果。
- [ ] 三个历史场景可重放，golden 来自 Head 后 owner review，reviewer 无泄漏。
- [ ] R0/R1 初始 12 会话及必要 tie-breaker 原文、工具与成本完整存档。
- [ ] 硬指标/成本可从原始记录重算，R1 结论严格使用冻结 Gate。
- [ ] R2 未实现；Go 时只交 owner 审批的 Level C 提案。
- [ ] 独立 review 无 open/needs-discussion，Vault 门禁通过，任务停在 ready_for_review。

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
