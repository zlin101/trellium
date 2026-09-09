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
- 2026-09-09 S0 臂补齐（owner review round 后）：同三场景以现行流程材料（runtime 全文 + 全部状态块）盲测 3 个新无历史会话；双臂结果：S1 3/3 五问全对、0 纠正、零材料外推断；S0 场景 1 全对，场景 2 closed 计数只能靠材料未定义的推断（状态层不携带 open/closed 分类学），场景 3 把缺失文件任务的 Next Action 记录过度声称可用（1 次纠正）。原文存档（提示词/首答/golden/材料原字节/运行台账）在 `vault/details/status-blind-test-2026-09/`，索引与评分在 `vault/details/status-blind-test-2026-09.md`。
- 2026-09-09 M1：S0 基线留档——`vault/runtime.md` 11039 bytes、check JSON 802 bytes（审计基准 `55ae985`，存 `/tmp/check-before.json` 用于逐字节对照）；场景 1 golden 真值 = active{0001,0008}/blocked{0004}/closed 5/focus 0008。
- 2026-09-09 M2/M3（提交 `4604a0c`）：`status` text/JSON 实现 + 8 项聚焦测试；当前仓库 S1 文本 1149 bytes < 11039 bytes；三场景 S1 输出与手写 golden 逐字节一致（A/B exit 0，C exit 2）；`check --format json` 与变更前逐字节一致；六冻结场景全过，kill criteria 零命中。
- 2026-09-09 M4（提交 `62c2a0e`）：VERSION 2026.09.5、MIGRATIONS 条目、双语 README status 小节、两包 protocol-model 引用、sync-skills 快照刷新且 `--check` in sync。
- 2026-09-09 M5 review round 1：REQUEST_CHANGES（1×P1：指针未引用的不可读任务不进 unresolved；4×P3）。P1+P3-3 于提交 `7e494da` 修复并补 2 项测试；round 2 复审 APPROVE（0 open P0/P1/P2；剩余 P3-1/P3-2/P3-5 为非阻断可选，P3-4 即本次 vault 同步）。
- 2026-09-09 M5 终验：116/116 tests、check 0/0 且与 M0 基线逐字节一致、snapshot in sync、`git diff --check` 通过、真仓库多次运行 status 后工作树无新增脏文件。
- 2026-09-09 owner review round（3×P1）闭合：①unresolved 原因码按 check finding phase 结构化推导（task-state/runtime-projection 两相，删除手维护 code allowlist 与 `TASK_RUNTIME_UNRESOLVED` 伪造回退；owner 复现场景现输出实际诊断 `TASK_RUNTIME_CLOSED_LOCAL`）；②S0/S1 双臂消融补齐并存档；③handoff 条目同步。补 3 项测试（stale closed-local row / dangling duplicate rows 实际码 / storage findings 不进 reason）。

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

### 2026-09-09 - Agent: GLM — owner review round 三项 P1 闭合

Context read:

- Owner review 结论（3×P1）；`scripts/trellium.py` status 段与 `VaultCheckRun`；`vault/handoff.md`；既有测试。

Changes made:

- P1-1 原因码：`status_unresolved_reasons` 改为按 finding phase（`task-state`/`runtime-projection`）结构化过滤，新增 `VaultCheckRun.findings_with_phase()`；删除 `STATUS_UNRESOLVED_CODES` allowlist；unresolved reason 一律来自该任务实际产生的 finding，无 finding 时用中性标记 `UNVERIFIED`（非 checker 码，不可误导修复动作），不再伪造 `TASK_RUNTIME_UNRESOLVED`。checker 新增代码时 status 原因自动跟随，不再需要同步维护清单。
- P1-2 消融：补 S0 臂（3 场景 × 无历史会话，材料 = runtime 全文 + 全部状态块）；`vault/details/status-blind-test-2026-09.md` 存档双臂 golden/材料/提示词/逐字首答/评分/纠正数。
- P1-3：`vault/handoff.md` TASK-0008 条目更新为 ready_for_review 与本轮修复状态，消除"无实现、等 GLM"的过期指向。

Checks run:

- `python3 -m unittest scripts.test_trellium ...` 全绿（新增 3 测试：owner 复现的 stale closed-local row 输出实际码 `TASK_RUNTIME_CLOSED_LOCAL`；dangling duplicate rows 输出实际码 `TASK_RUNTIME_DUPLICATE`；storage finding 携带 task_id 也不进 reason、不降级分类）。
- owner 复现场景端到端复现：local + superseded 行 + 无文件 → unresolved reason=`TASK_RUNTIME_CLOSED_LOCAL`，exit 2。
- golden B/C 与实现输出仍逐字节一致；`check --format json` 发现/严重级/退出码与基线一致（仅 runtime 测量随 runtime.md 编辑变化）；`sync-skills.py --check` in sync。

Review and reflection:

- owner 指出的结构性风险成立：allowlist 与 checker 语义漂移是真实的维护负担；phase 过滤让"storage/budget 不影响 lifecycle"成为结构事实而非清单事实。
- S0 臂结果对消融结论是实质性补强：S1 的优势不只是 bytes——open/closed 分类学内建与 fail-closed 投影抑制在场景 2/3 产生了正确性差异；同时按 owner 要求，结论表述限定为"首答记录 + guardrail"，不声称完整用户收益。

Risks:

- 每格 n=1、评分者为实现方；细节与复跑指引见 details 文件局限一节。

Next action:

- Owner 复核本轮修复；通过后决定 accepted 与 `2026.09.5` tag/Release。

### 2026-09-09 - Agent: GLM — 增量复核闭合（证据原文存档）

Context read:

- Owner 增量审查结论（P1：存档非原文；P2：handoff 残留"修复中"）。

Changes made:

- 原始回答仍在实施会话上下文中，按 owner 的第一选项逐字落盘：新建 `vault/details/status-blind-test-2026-09/`——`prompt-s1-a/b/c.md`、`prompt-s0-a/b/c.md` 六份实际投放提示词（S0 材料段直接从原字节文件拼接）、`answer-s1-a/b/c.md`、`answer-s0-a/b/c.md` 六份未改写完整首答、`golden-scenario1/2/3.txt`（原字节）、`s0-material-scenario1-runtime.md`（`git show 55ae985` 原字节）、`blocks-scenario1/2.txt`（全部状态块全文）、`run-log.md`（六个 agentId、subagent_tokens、tool_uses=0、duration、宿主会话与模型标识说明、污染控制）。
- 重写 `status-blind-test-2026-09.md` 为索引：移除把摘要标注为"逐字首答"的表述，评分与结论以目录原文为准。
- handoff 条目改为"三项已处置 + 本轮存档闭合 + 118/118 通过 + 待 owner 复核"。

Checks run:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` 118/118；`trellium.py check .` 0/0；`sync-skills.py --check` in sync；`git diff --check` 通过；golden B/C 与实现输出仍逐字节一致。

Review and reflection:

- owner 的批评成立：上一版把"要点概括"标成"逐字首答"是不可接受的证据表述；正确顺序是先存原文再评分，本轮已按此补齐且未反向重构任何内容。
- 子代理模型标识未由运行时返回，已在 run-log 如实标注，不冒充可验证项。

Next action:

- Owner 复核证据原文目录后决定验收与发布。

## Memory Updates

- `vault/runtime.md`
- `vault/collaboration.md`
- `vault/details/shadow-run-2026-09.md`
- `vault/decisions.md` only after owner accepts a durable CLI decision
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)
