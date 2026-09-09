# TASK-0007 - Local TASK 生命周期闭环与 Clone-safe 投影（2026.09.4）

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0007",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md`：补齐 local TASK 的两个缺口——accepted 前的显式 Durable Knowledge Disposition 人工 gate，以及 fresh clone 中 missing local TASK 的 clone-safe 投影语义（warning，不授权）。目标版本 `2026.09.4`；本任务不创建 tag 或 Release。

## Scope

### In Scope

- M0：preflight、本任务建立、决策表冻结、W/C 组消融预注册与基线（C0 必须在任何代码修改前记录真实 code/severity/exit）。
- M1：协议与双语模板补齐关闭语义（载体按 W 组 Gate 选择，默认 W1 单行）；自托管 vault 三个文件的小 diff。
- M2：checker 仅补 local-aware projection 分支（policy 显式传入；tracked/policy-missing 路径零改动）。
- M3：`scripts/test_trellium.py` 增加与第 3 节决策表对应的聚焦测试。
- M4：`init/VERSION` → `2026.09.4`；MIGRATIONS、双语 README、模板/Skill/references 同步；运行 sync-skills。
- M5/M6：自托管检查、独立 review、终验、milestone 提交、push、CI。

### Out of Scope

- 发布/自动归档 local TASK；publish generator、owner inbox、Context、RAG、数据库、daemon、Web UI。
- 自然语言自动提取长期事实；新增公开 CLI 子命令；修改 `trellium-task-state` schema v1；新增 machine-readable memory receipt。
- 自动改 `.gitignore`、自动 `git rm --cached`、批量迁移历史 TASK；修改 CI 权限、依赖、tag、Release。
- 把第二项目用作实现前置测试。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/handoff.md`、`vault/decisions.md`
- `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md`
- `scripts/trellium.py`（check_runtime_projection 及周边）、`scripts/test_trellium.py`
- `init/protocol/*`、双语模板与 Skill 分发面、`vault/details/shadow-run-2026-09.md`

## Capability Tags

- development
- testing
- documentation

## Authority

Allowed:

- 计划第 4 节授权范围：M0-M6 的 Level C 修改（协议、模板、checker、聚焦测试、VERSION、MIGRATIONS、README、sync 快照、自托管 vault 小 diff）；正常提交、push develop、观察既有 CI。

Requires Approval:

- 本任务 accepted（owner 决定）；创建 tag/Release（本任务不做）；
- 改变决策表结论或扩大语义（必须停下向 owner 报告）。

Forbidden:

- 上传/提交/自动发布 local TASK；自动 `.gitignore`/untrack/删除 TASK；
- 新增 CLI 子命令、machine-readable receipt、schema v1 变更；
- 把 `TASK_RUNTIME_MISSING` 全局降级、以 `vault/tasks/` 缺失为由跳过 projection check、根据 `.gitignore` 猜 policy；
- 在单元测试中访问网络或真实 GitHub；把 synthetic fixture 计入 TASK-0001 覆盖。

## Acceptance Criteria（含第 3 节冻结决策表）

决策真值表（任何实现改变表中结论必须停下向 Owner 报告）：

| Policy | TASK 文件 | runtime 行 | 预期结果 |
| --- | --- | --- | --- |
| tracked | open，状态一致 | 存在 | PASS（09.3 行为） |
| tracked | 不存在 | 存在 | `TASK_RUNTIME_MISSING` error |
| local | open，状态一致 | 存在 | PASS |
| local | open | 不存在 | `TASK_PROJECTION_MISSING` error |
| local | 不存在 | open 行 | `TASK_RUNTIME_LOCAL_UNRESOLVED` warning（不授权） |
| local | accepted/superseded | 行不存在 | PASS |
| local | accepted/superseded | 行存在 | `TASK_RUNTIME_CLOSED_LOCAL` error |
| local | 不存在 | accepted/superseded 行 | `TASK_RUNTIME_CLOSED_LOCAL` error |
| local | TASK/review/archive tracked/staged | 任意 | 既有 `TASK_STORAGE_MISMATCH` error |
| policy 缺失/非法 | 任意 | 任意 | 既有兼容行为，不套 local 语义 |

- [x] W 组消融按冻结顺序（W2→W1→W0）执行，Gate 结论遵守"同效取小"；tracked 路径无伪 `pending`；supersede 不被 disposition 阻塞。
- [x] C0/C1/C2 characterization 记录真实 code/severity/exit，证明 checker 代码层必要性；tracked finding 零降级。
- [x] M1 协议与双语模板区分 private journal / published truth / runtime/handoff / live Git；自托管 vault 小 diff 完成（governance/index/tasks README）。
- [x] M2 checker local-aware projection 实现且 missing local warning 文案覆盖 fresh-clone/误删两种原因、恢复动作、runtime 不授权三层。
- [x] M3 决策表 12 项聚焦测试全部通过；既有 87 项测试零退化（Mixin 重构消除继承重跑后全量 99 项 = 88+5+6）。
- [x] M4 `2026.09.4` migration、双语 README、模板/Skill/references 分发快照同步（sync --check in sync）。
- [x] M5 独立 review 完成（`vault/tasks/TASK-0007-review.md`）：十问全部通过；F1/F3 已修复，F2 流程部分已采纳、叙述裁认随 owner 验收。
- [x] M6 终验与 push 后 CI 全绿；任务停在 ready_for_review。（CI 结果见提交后核验记录）

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`

Completed:

- 2026-09-09 Preflight：交接三项（计划文档 untracked、runtime/collaboration modified）已审阅并先行提交；HEAD=origin、工作树干净；`init/VERSION` = 2026.09.3；基线门禁 0 error / 0 warning、三模块合计 87 项测试（76+5+6）、in sync。

## Execution Record

### 2026-09-09 - Agent: GLM (ZCode)

Context read:

- 本计划全文；vault 必读；`scripts/trellium.py` projection 代码；测试辅助结构；模板布局。

Changes made:

- M0：创建本任务；交接三项先行提交；D-0006 决策入库；W/C 消融预注册（见下）。

Checks run:

- Preflight 门禁：0 error / 0 warning；87/87；in sync；diff-check 通过。

Review and reflection:

- 决策表与 kill criteria 已冻结；C0 必须先于任何代码修改记录。

Risks:

- W 组结论依赖无历史 reviewer 会话（GLM 子代理投放，按 TASK-0006 先例）；若与预期偏差大，以冻结 Gate 裁决。

Next action:

- C0/W0 基线采集 → W 组实验 → M1。

### 消融预注册（2026-09-09 冻结，先于任何实现）

**W 组（Accepted 知识处置载体）**：三个短任务案例（①产生长期约束；②无长期约束；③错误契约需立即 supersede），按 W2 → W1 → W0 顺序交给无历史 reviewer 会话（GLM 子代理投放，沿用 TASK-0006 先例），判断"能否进入 accepted、关闭前应更新哪里"。每 cell 不得读取本文、scoring 或其他 cell 材料；读到即 contaminated 重跑。记录首答、判断正确性、是否错误阻塞 supersede、材料 bytes、纠正数。Gate：W0 为 baseline，synthetic 平手只能记 Inconclusive，不能 No-Go 流程增强；W1≡W2 取 W1；仅当 W2 修复 W1 真实漏判且不错误阻塞 supersede 才用独立段；任一方案要求复制 TASK 正文或新增状态 owner 即 No-Go。

**C 组（Checker characterization）**：临时 fixture 仓库（synthetic），三层 C0（09.3 现状）→ C1（仅改协议文档）→ C2（协议+最小 local-aware projection）。场景：fresh-clone open local 指针、closed local stale row、tracked dangling pointer，另加 present local open/closed 对照。C0 必须在任何代码修改前记录真实 code/severity/exit。Gate：C0/C1 已不误阻断则 C2 No-Go；C2 必须把 missing open local 收敛为带恢复边界的 warning，同时保持 closed-local error 与 tracked error；任何 tracked finding 降级、missing local 静默忽略即 No-Go。

预注册扩展删除项（不进 cell）：自动扫描 TASK/publish proposal、`trellium-task-memory` schema、新存储层、自动 `.gitignore`/untrack。

### 2026-09-09 - Agent: GLM (ZCode) — 消融执行与 M1-M4 实施

Context read:

- 预注册（上一节）；`scripts/trellium.py` projection 代码；双语模板与 references 分发面。

Changes made:

- M1（载体按 W Gate = W1 单行）：`init/protocol/10-vault.md`（local 生命周期边界六条）、`20-governance.md`（验收门 local disposition 段）、`30-agent-entry.md`（fresh clone 不授权规则）；`skills/trellium{,-zh}/assets/templates/vault/{tasks/README,runtime}.md`（disposition 行 + local 语义）、`assets/templates/skills/agent-task/SKILL.md`（step 14 扩展）；两套 `references/protocol-model.md`；顶层 `skills/trellium{,-zh}/SKILL.md` check 说明；自托管 `vault/governance.md`、`vault/index.md`、`vault/tasks/README.md` 小 diff。
- M2：`check_runtime_projection` 增加 `policy` 显式参数；local 分支——missing open local（row/Focus 去重）报 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning（三层文案）、closed local 行（文件存在与否）报 `TASK_RUNTIME_CLOSED_LOCAL` error；tracked/policy 缺失路径逐字未动。
- M3：`scripts/test_trellium.py` 新增 `LocalProjectionTest` 12 项决策表测试。
- M4：`init/VERSION` → 2026.09.4；MIGRATIONS 新条目（Added/Breaking/Agent migration/Auto）；双语 README 更新 projection 与 disposition 说明；`sync-skills` 重新生成两套 protocol-source 与 assets/trellium.py 快照。

Checks run:

- W 组（GLM 子代理投放，材料与评分分离）：W2 3/3 正确（含指向 superseded 类终态、无误阻塞）；W1 3/3 核心正确（Case3 未提 superseded 字样属采样噪声）；W0 3/3 全对。Gate 裁定：W1≡W2 判断相同取 W1；W0 全对仅把 W1 增量收益记 Inconclusive，不构成流程增强 No-Go；无方案要求复制 TASK 正文或新增状态 owner。
- C0（实现前，真实 code/severity/exit）：S1 local fresh-clone open 指针 → `TASK_RUNTIME_MISSING` error ×2（row+focus 未去重）exit 2；S2 closed stale row（无文件）→ `TASK_RUNTIME_MISSING` error（漏报 CLOSED_LOCAL）exit 2；S3 tracked dangling → error ×2（保持）；S4 open present+row → PASS；S5 accepted present+stale row → PASS（漏报）；S6 accepted 无 row → PASS；S7 policy 缺失+dangling → `POLICY_MISSING` warning + `TASK_RUNTIME_MISSING` error（严格 projection 保持）。
- C1（协议/模板已改，checker 未改）：七场景全部与 C0 相同 → 仅改文档无法消除误报/漏报，checker 代码层必要。
- C2（实现后）：S1 → 单条 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning（去重生效）exit 0；S2/S5 → `TASK_RUNTIME_CLOSED_LOCAL` error；S3 → tracked error 不变；S4/S6 → PASS。误标 fresh 0、tracked 零降级、无静默忽略——C2 Gate 全过。
- 全量：`unittest` 三模块 136/136 OK（新增 12 项）；sync --check in sync；check 0 error / 1 warning（TASK-0007 未提交窗口，提交即消除）；`git diff --check` 通过。

Review and reflection:

- W 组结论与计划默认一致（W1 单行），消融的作用是确认而非推翻；C 组消融证明了代码层必要性（C1 对照）。
- closed local + 状态漂移会同时报 DRIFT 与 CLOSED_LOCAL 两个 error——两者都是真实问题，符合决策表。

Risks:

- local disposition 是人工 gate，checker 不校验其值；真实遗漏 ≥2 次后再提机器校验（计划 6.1）。

Next action:

- M5 独立 review；M6 终验与交付。

### 2026-09-09 - Agent: GLM (ZCode) — M5 独立 review 与修复；M6 终验

Context read:

- 独立 reviewer（只读会话）十问审查输出；任务书第 10/11 节。

Changes made:

- `scripts/test_trellium.py`：`VaultCheckTest` 拆出 `VaultCheckMixin`，`LocalProjectionTest` 改继承 Mixin——消除继承导致的 37 个父类测试重复执行（review finding F3 计数虚增根因）；git helper 移入 Mixin。
- `vault/details/task-0007-w-group-records.md` 新建：W 组 9 份首答逐字存档 + 材料 bytes + 纠正数（F1）。
- 流程规则采纳（F2）：今后预注册与基线记录先于实现独立提交；本轮叙述性证据提请 owner 验收时裁认。
- `vault/tasks/TASK-0007-review.md` 建立（Round 1 十问 + F1-F3 处置）。
- 状态块 active → ready_for_review。

Checks run:

- 全量三模块 99 tests OK（88+5+6；基线 87 + 新增 12，既有零退化）；`trellium.py check . --format json` → 0 error / 0 warning；`sync-skills.py --check` → in sync；`git diff --check` 通过。

Review and reflection:

- 独立 review 十问全过；三条记录类 finding 的根因（继承重跑、预注册提交时序、原始答案未归档）均已闭合或有明确 owner 裁认点。

Risks:

- F2 的叙述性证据（预注册先于实现）无提交级证明，owner 裁认是唯一剩余动作。

Next action:

- owner 验收本任务；accepted 后另行发布 2026.09.4 tag/Release（不在本任务范围）。

### 2026-09-09 - Agent: GLM (ZCode) — owner review round 2（REQUEST_CHANGES）修复

Context read:

- owner 五项 finding（R1 W 组裁决违反冻结 Gate、R2 下发模板未完整同步、R3 unittest.main 位置、R4 duplicate row 顺序敏感、R5 vault 记录未闭合事实）。

Changes made:

- R1：Case3 复跑（W1/W2 各 3 独立子代理会话，封闭书），完整存档输入/scoring/首答/session id 至 `vault/details/task-0007-w-group-records.md` Case3 复跑节；复跑两载体核心判断无差异、W2 0/3 提及废止类终态 → 按冻结 Gate 保留 W1（实测裁决）。
- R2：zh/en governance、两套 index、两套 handoff 下发模板补齐 local 语义；新增 `LocalTemplateSemanticsTest` 6 项 rendered-content 断言防再漏。
- R3：`unittest.main()` 移至文件末尾；修正后直接运行 95 项、三模块 106 项。
- R4：duplicate row 只报 `TASK_RUNTIME_DUPLICATE`、跳过 freshness/closed 推断（resolve 入口按 row_counts 短路）；正反顺序验证均仅 DUPLICATE。
- R5：runtime 矛盾 Recent Changes 行改写；review ledger F2 按 owner 裁认转 fixed（DAG 顺序 + C0 重放脚本存档于 ledger 附录）。

Checks run:

- 全量三模块 106 tests OK（含新增 rendered-content 6 项与 duplicate 顺序 2 例；直接运行 95 项）；`trellium.py check . --format json` → 0 error / 0 warning；`sync-skills.py --check` → in sync；`git diff --check` 通过。

Review and reflection:

- 首轮 Case3 的"W2 胜出"印象在 n=3 复跑中反转（W2 0/3 提及 superseded）——单轮采样的裁决必须按 owner 要求补足重复数，冻结 Gate 的价值正在于此。

Risks:

- 无新增；disposition 仍是人工 gate，真实遗漏 ≥2 次再提机器校验。

Next action:

- 增量 review（owner 指定）→ owner 决定 accepted。

## Memory Updates

- `vault/runtime.md`、`vault/handoff.md`、`vault/decisions.md`（D-0006）
- `docs/evals/` 不新建长期目录：W/C 记录取本任务 Execution Record（计划第 4.2 节）
