# TASK-0008 - 2026.09.5 确定性 Status Summary

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0008",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md`：在不新增状态 owner、schema、依赖或写入行为的前提下，为 Trellium 增加确定性只读 `status` 命令，解决 owner 反复从 runtime/TASK 手工编译当前进度的真实痛点。它不推断 owner approval，不是完整 inbox。本任务是 2026.09.5 唯一功能开发候选，实施由 GLM 执行。

## Scope

### In Scope

- M0：Codex 反馈剩余功能审计、唯一候选裁决、S0/S1 消融预注册，独立先行提交。
- M1：当前仓库 S0 golden/runtime bytes 基线。
- M2：`scripts/trellium.py status` text/JSON 输出，复用现有 TASK state/runtime/check parser，聚焦测试。
- M3：冻结场景、只读性、fail-closed 和 bytes 消融。
- M4：Gate 通过后更新 2026.09.5 VERSION/MIGRATIONS/双语 README/Skill 与同步快照。
- M5：独立 review、终验、`ready_for_review`；不代 owner accepted，不发布 Release。

### Out of Scope

- Context compiler/manifest、Evidence Receipt/freshness、review pack、slice-native schema、fact types、byte 阈值、runtime generator、decision edges。
- 持久 inbox/approvals 文件、LLM 总结、网络访问、数据库、daemon、RAG、Web UI。
- 自动修改 Vault、自动授权/accepted、运行 TASK 内命令，批量迁移历史 TASK。
- 创建 tag/Release；同时启动第二个 09.5 功能。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/decisions.md`
- `Vault-Agent-Native-使用评估与优化建议-2026-09-03.md`
- `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md`
- `vault/tasks/TASK-0006-non-context-optimization.md`、`docs/evals/non-context-optimization-2026-09/results.md`
- `scripts/trellium.py`、`scripts/test_trellium.py`、双语 README/Skill 分发面

## Capability Tags

- development
- testing
- documentation
- review

## Authority

Allowed:

- Owner 当前指令批准本计划内唯一 `status` 功能的 Level C / Authority 3 开发、测试、文档、版本和 Skill 快照同步。
- 正常的里程碑提交、本地门禁和独立 review。

Requires Approval:

- 本任务进入 `accepted`；创建 tag/Release；新增第二个 09.5 功能。
- 改变状态 schema、`check` 语义/退出码、或突破预注册实现上限。

Forbidden:

- 任何 fail-open 的 lifecycle/Authority 推断；将 runtime 投影当成独立授权源。
- 自动修复/写入 Vault；自动批准/accepted；执行文档命令；添加依赖或网络调用。
- 用 synthetic 样本声称生产需求；重开 D-0004。

## Acceptance Criteria

- [x] 剩余功能清单完成，已解决能力不重复开发；Context/Evidence/slice 结论未被越过。
- [x] Status Summary 作为 09.5 唯一 Go-with-experiments 项；S0/S1 场景、硬指标、guardrail 和 kill criteria 在任何代码前冻结。
- [x] `status` text/JSON 同源，正确分类 draft/active/blocked/ready_for_review，closed 不进行动清单。
- [x] malformed/duplicate/drift/local missing/symlink 全部 fail-closed；不声称未解析的 Authority/lifecycle。
- [x] 命令不写目标，不访网，不执行文档命令；现有 check finding/severity/exit 零变化。
- [x] 当前仓库 S1 输出 bytes < S0 `runtime.md` bytes，分类 golden 100%。
- [x] `init/VERSION=2026.09.5`，migration/双语 README/Skill/快照只描述已验证行为。
- [x] 全量门禁通过；独立 review 无 open finding；任务停在 `ready_for_review`。

## Verification

Required:

- `python3 scripts/trellium.py status .`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/trellium.py check . --format json`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`

Completed:

- 2026-09-09 M0 preflight：09.4 Release/Vault 已闭环；`develop==origin/develop`；工作树干净；基线 106/106 tests、check 0/0、snapshot in sync。
- 2026-09-09 R1 盲测（实现前）：3 份手写 golden（当前仓库 / fixture-mixed / fixture-conflict-local）交 3 个无历史会话只看输出作答五问，3/3 场景全部首答正确、0 纠正、未触发 kill criterion；契约未修改即冻结。
- 2026-09-09 M1：S0 基线留档——`vault/runtime.md` 11039 bytes、check JSON 802 bytes（审计基准 `55ae985`，存 `/tmp/check-before.json` 用于逐字节对照）；场景 1 golden 真值 = active{0001,0008}/blocked{0004}/closed 5/focus 0008。
- 2026-09-09 M2/M3（提交 `4604a0c`）：`status` text/JSON 实现 + 8 项聚焦测试；当前仓库 S1 文本 1149 bytes < 11039 bytes；三场景 S1 输出与手写 golden 逐字节一致（A/B exit 0，C exit 2）；`check --format json` 与变更前逐字节一致；六冻结场景全过，kill criteria 零命中。
- 2026-09-09 M4（提交 `62c2a0e`）：VERSION 2026.09.5、MIGRATIONS 条目、双语 README status 小节、两包 protocol-model 引用、sync-skills 快照刷新且 `--check` in sync。
- 2026-09-09 M5 review round 1：REQUEST_CHANGES（1×P1：指针未引用的不可读任务不进 unresolved；4×P3）。P1+P3-3 于提交 `7e494da` 修复并补 2 项测试；round 2 复审 APPROVE（0 open P0/P1/P2；剩余 P3-1/P3-2/P3-5 为非阻断可选，P3-4 即本次 vault 同步）。
- 2026-09-09 M5 终验：116/116 tests、check 0/0 且与 M0 基线逐字节一致、snapshot in sync、`git diff --check` 通过、真仓库多次运行 status 后工作树无新增脏文件。

## Execution Record

### 2026-09-09 - Agent: Codex — M0 审计与预注册

Context read:

- Codex 反馈原文全文；Vault 必读；TASK-0006 与非 Context 实验结果；09.4 实现与 CLI/check 现状。

Changes made:

- 产出 2026.09.5 剩余功能审计，将 09.4 已解决项、No-Go/Inconclusive/Blocked 与真正候选分开。
- 根据 A+B 证据选定 Status Summary；冻结实现上限、S0/S1 对照、六场景、硬指标与 kill criteria。
- 按 owner 纠正，Codex 只交付文档 review/反思/消融，不实现代码；增加 strategy red-team R1-R5 与最便宜实验。

Checks run:

- 基线沿用提交 `909d720` 的 106/106、check 0/0、snapshot in sync；M0 提交前重跑 check/diff-check。

Review and reflection:

- TASK-0006 M6 在 2026-09-08 的“本仓库 0 次 owner 查找事件”保持历史有效；本轮是由后续 owner 反复 status/进度询问与深度反馈提供新的 B+A 证据，不回改旧结论。
- 选择 status 而不是新 inbox 文件，是为了复用现有真相且不增加第二 owner。

Risks:

- runtime objective/Next Action 是投影文本，不授权；status 必须在输出中保持这个边界。
- 如现有 schema 无法安全表达 owner 视图，任务必须 No-Go，不得扩 schema。

Next action:

- 独立提交 M0 文档与交接；由 GLM 先执行 R1 的手写输出五问测试，再按 M1-M5 开发。

### 2026-09-09 - Agent: GLM — R1 盲测与 M1-M5 实现

Context read:

- 计划全文、TASK-0008 契约、`vault/index.md`/`runtime.md`/`governance.md`/`decisions.md`/`project.md`、`scripts/trellium.py`、`scripts/test_trellium.py`、shadow ledger、双语 README 与 skill 引用。

Changes made:

- R1 最便宜实验先行：按 §4 契约手写 3 份预期 status 文本输出（场景 1 当前仓库、场景 2 混合 fixture、场景 3+4 冲突+local-missing fixture），3 个无历史子代理各只看一份输出回答五问——3/3 首答全对、0 纠正，未触发 kill criterion；契约未修改，随后才写 parser。
- M1：S0 基线留档（runtime 11039 bytes；check JSON 802 bytes 存档供对照）。
- M2/M3（`4604a0c`）：`trellium.py` 新增 `status` 子命令——复用 `collect_vault_state`（check 全管线，行为不变）与既有 parser；`discover_task_files` 记录补 `state` 键、`parse_runtime_task_pointers` 行扩为 4 元组（仅内部形状，check 语义零变化）；text/JSON 从同一 payload 渲染；drift→unresolved、closed 只计数、unresolved 附阻塞发现码且无 lifecycle/authority；8 项聚焦测试。
- M4（`62c2a0e`）：VERSION 2026.09.5 + MIGRATIONS 条目 + 双语 README + 两包 protocol-model 一行引用 + sync 快照。
- M5：独立 review round 1 REQUEST_CHANGES（1×P1：不被 runtime/focus 引用的不可读任务不进 unresolved；另 4×P3）；`7e494da` 修复 P1 并顺带闭合 P3-3（路径回退限定当前任务文件，ledger/archive 发现码不再污染 reason），补 2 项测试。

Checks run:

- 每里程碑：`python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`（106→114→116 全绿）；`trellium.py status .`（text/JSON）；`trellium.py check . --format json` 与 M0 基线逐字节一致（每轮重验）；`sync-skills.py --check` in sync；`git diff --check`。
- S1 对照：三场景输出与手写 golden 逐字节一致；当前仓库 S1 1149 bytes < S0 11039 bytes；真仓库只读性以快照+`git status --porcelain` 断言。
- 独立 review round 2（复审 `7e494da`）：APPROVE——P1-1/P3-3 确认闭合且回归全过；无 P0/P1/P2 open；新报告 1 项非阻断 P3-5（同 id 不可读副本在有效副本存在时不可见，check 既有语义的投影，随 owner 裁量）。

Review and reflection:

- 盲测暴露两处外观观察（focus `(resolved)` 标记未在文本内定义；场景 C 无 Next Action 的原因需推断）——均不影响五问作答，按最小修改保留原契约。
- 场景 C 手写 golden 首轮与实现有一处转写差（finding 消息的 `!r` 引号与 severity 对齐）；实现复用 check 原样渲染是正确行为，修正的是手写誊抄。
- review P1 根因与 check 既有行为一致（读失败不产生任务记录），status 层未把 findings 中的孤儿 id 物化；修复选择物化而非改 check 记录逻辑，保持 check 逐字节不变。

Risks:

- runtime 投影文本与 bytes guardrail 不证明人类时间节省；owner 可用性复核未做，不声称降幅。
- 悬空重复 runtime 行的 unresolved reason 落到回退码 `TASK_RUNTIME_UNRESOLVED`（round-1 P3-2，保留现状，确定且 fail-closed）。

Next action:

- Owner 验收；接受后由 owner 侧打 `2026.09.5` tag 并发布 Release（本任务不代做）。

## Memory Updates

- `vault/runtime.md`
- `vault/collaboration.md`
- `vault/details/shadow-run-2026-09.md`
- `vault/decisions.md` only after owner accepts a durable CLI decision
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)
