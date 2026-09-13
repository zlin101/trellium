# TASK-0010 - status 缺陷修复（短行 unresolved / refused-vault unresolved:0 / 管道截断）

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0010",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "draft"
}
-->

## Objective

修复 TASK-0009 实验发现并经 owner 裁定（2026-09-13）的三个真实 `status` 缺陷；不改变既有 check 语义与退出码契约（字节级基线继续成立）。

## Scope

### In Scope

1. **短行 id 缺口（P1）**：malformed 短行引用的任务不进 `unresolved`（`TASK_RUNTIME_INVALID` 无 task_id）——在 status 层物化该 id（复用 `7e494da` 的"物化在 status、不动 check 记录"先例），补聚焦测试。
2. **refused-vault `unresolved: 0`（P1）——输出设计冻结（owner review 2026-09-13，二次修正同日）**：`vault/` 或 `vault/tasks` 被拒绝枚举时，不得简单把 `summary.unresolved` clamp 为 1（会与 `tasks.unresolved` 空数组矛盾），也**不得伪造合成 task_id**（如 `VAULT_SCOPE`——会被消费者误认为任务 ID）。冻结设计：输出**明确的联合记录**，示例形状
   `{"scope": "vault", "path": "vault", "reason": "SYMLINK_INPUT"}`
   ——无 task_id 字段，scope/path/reason 三键显式表达作用域；`summary.unresolved` 计数与该数组严格一致；JSON v1 的这一增量形状在 MIGRATIONS 中明确说明。
3. **管道截断投影（P2）**：Next Action 含 `|` 导致投影静默截断且 exit 0——status 层检测过切行并抑制该任务投影（沿用既有 duplicated/enum-invalid 抑制模式）。

### Out of Scope

- 任何 `check` 输出/退出码变化；R2/review-pack/Context/Evidence；同 id 不可读副本（owner 裁定维持 P3，不动）；新 schema、新依赖、网络。

## Context Required

- `vault/tasks/TASK-0009-review-pack-ablation.md`、`docs/evals/review-pack-2026-09/results.md` §附带缺陷清单（含 owner severity 裁定）
- `scripts/trellium.py`（status 段、`build_status_payload`、`status_unresolved_reasons`、`parse_runtime_task_pointers`）、`scripts/test_trellium.py`
- D-0007、MIGRATIONS、双语 README 的 status 契约描述

## Capability Tags

- development
- testing

## Authority

Allowed:

- Owner 2026-09-13 指示"另立产品任务"立项本任务；上述三缺陷的 status 层修复、聚焦测试、MIGRATIONS 一行说明。
- 正常里程碑提交与本地门禁。

Requires Approval:

- 任何 check 字节级行为变化；JSON v1 形状变更（超出 unresolved 计数语义的最小修订）；accepted 与 tag/Release。

Forbidden:

- 修复中夹带 R2/review-pack 能力；改 `check` 记录逻辑；fail-open 修复。

## Acceptance Criteria

- [ ] 三个缺陷各有一个能复现原始报告的失败测试，修复后转绿。
- [ ] `check --format json` 与基线逐字节一致（既有契约不变）。
- [ ] 全量测试无退化；check 0/0；snapshot in sync；`git diff --check`（含 TASK-0009 豁免口径）通过。
- [ ] 独立 review 无 open P0/P1/P2；任务停在 ready_for_review。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status .` 与 `--format json`
- 三个缺陷的 fixture 级复现脚本（修复前红、修复后绿）

## Execution Record

### 2026-09-13 - Agent: GLM — 立项（draft，未开始实现）

- Owner 在 TASK-0009 review 中裁定三个 status 缺陷为真实缺陷（P1/P1/P2）并指示另立产品任务；本文件即该合同。
- Owner 复核修正（同日）：lifecycle 保持 **draft**——不以 Authority 3 直接 active，实现需 owner 排期启动；refused-vault 输出设计按 owner 意见冻结为显式 vault-scope unresolved 记录（禁止 clamp 方案）。

## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)
