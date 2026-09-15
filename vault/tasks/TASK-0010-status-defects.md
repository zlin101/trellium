# TASK-0010 - status 缺陷修复（短行 unresolved / refused-vault unresolved:0 / 管道截断）

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0010",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "accepted"
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

- [x] 三个缺陷各有一个能复现原始报告的失败测试，修复后转绿。（`StatusDefectRegressionsTest` 3 项，red-first 实证：对 cbd8713 的 checker 全红；独立 reviewer 第一手复跑确认）
- [x] `check --format json` 与基线逐字节一致（既有契约不变）。（独立 review：健康仓库与错误 fixture 双态逐字节一致，payload diff 仅含预期 unresolved 增量）
- [x] 全量测试无退化；check 0/0；snapshot in sync；`git diff --check`（含 TASK-0009 豁免口径）通过。（121 tests OK；71c64b3 曾因 snapshot 漂移被远端 gate 拦截，7d5c589 regen 后 CI success）
- [x] 独立 review 无 open P0/P1/P2；任务停在 ready_for_review。（专项复审 APPROVE：三修复独立复现、冻结设计逐项核验；3 项非阻断观察已记录）
- [x] owner 验收（2026-09-15）：ready_for_review → **accepted**（远端 gate run 34927880245 success）。MIGRATIONS 的 Unreleased 节保持——本任务位于 `2026.09.5` tag 之后，属后续未发布内容，不改动既有 09.5 tag。

## Execution Record

### 2026-09-13 - Agent: GLM — 立项（draft，未开始实现）

- Owner 在 TASK-0009 review 中裁定三个 status 缺陷为真实缺陷（P1/P1/P2）并指示另立产品任务；本文件即该合同。
- Owner 复核修正（同日）：lifecycle 保持 **draft**——不以 Authority 3 直接 active，实现需 owner 排期启动；refused-vault 输出设计按 owner 意见冻结为显式 vault-scope unresolved 记录（禁止 clamp 方案）。

### 2026-09-13 - Agent: GLM — 激活（owner 排期生效）

- 方案 B 完成、push 成功、远端 CI 全绿（恢复提交 `5c4c0f6` 的 gate job success）；owner 排期条件满足，TASK-0010 draft→active，实现开工。

### 2026-09-14 - Agent: GLM — M1-M3 实现、门禁与专项复审

Context read: 合同、TASK-0009 实验记录（results.md 附带清单）、`scripts/trellium.py` status 段、`scripts/test_trellium.py` 夹具与 StatusSummaryTest 模式、MIGRATIONS。

Changes made:

- 三项 status 层修复（check 字节级零变化）：①短行 id 物化（`parse_runtime_task_pointers` problems 携带 id；`build_status_payload` 以实际码 `TASK_RUNTIME_INVALID` setdefault 物化进 unresolved）；②refused-vault 联合记录（`SYMLINK_INPUT` × {vault, vault/tasks} → `{"scope","path","reason"}`，计数与数组一致，无合成 id、无 clamp）；③oversplit 行投影抑制（>4 cells 记 id，投影按既有抑制模式丢弃，lifecycle 保留）。
- 3 项 red-first 回归测试（`StatusDefectRegressionsTest`）；MIGRATIONS 新增 Unreleased 节（JSON v1 增量形状）。
- 快照再生成（MIGRATIONS + assets/trellium.py + manifest ×2 包）。

Checks run:

- 121 tests OK（118+3，red-first 实证）；`check` text/JSON 对 cbd8713 逐字节一致（健康+错误 fixture 双态）；status text/JSON 真仓库 exit 0；snapshot in sync；范围级 whitespace CLEAN。
- 远端 CI：71c64b3 gate **failure**（snapshot 漂移：MIGRATIONS 编辑 + assets/manifest 过期——本地 `sync --check | tail -1` 管道遮蔽了退出码与输出，教训记录）→ 7d5c589 regen 后 gate **success**（独立 review 经 GitHub API 双向核实）。

Review and reflection:

- 独立专项复审 **APPROVE**：三修复独立复现；冻结设计（联合记录、无合成 id、无 clamp、计数==数组）逐项核验；MIGRATIONS 准确；范围干净。
- 3 项非阻断观察入档：(a) 短行指向已有效任务时不产生 unresolved 条目（信号仍经 check 错误可见，未测试未文档化）；(b) oversplit 抑制按设计无任何信号（exit 0）；(c) vault-scope 记录按冻结范围仅覆盖两路径的 SYMLINK_INPUT。
- 复审指出我表述不精：CI 成功的是 `gate` job（sync check-run 被 skip），不是整个 workflow——已按精确口径记录。

Next action:

- 2026-09-15 owner 验收通过转 accepted；handoff 条目按关闭任务规则归并回本文件；不新增决策记录（本次落实 D-0007 既有 status 契约）。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status .` 与 `--format json`
- 三个缺陷的 fixture 级复现脚本（修复前红、修复后绿）

Completed:

- 2026-09-14 全项通过（见 Execution Record 与独立复审）；远端 CI `7d5c589` gate success。


## Memory Updates

- `vault/runtime.md`
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)
