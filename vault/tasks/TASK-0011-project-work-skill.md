# TASK-0011 - 项目级 `trellium-work` Skill 的价值验证与最小迁移

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0011",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "active"
}
-->

## Objective

验证项目级工作 Skill 相比 `AGENTS.md + vault` 是否具有独立价值；仅在预注册消融通过时，把当前通用且可能全局泄漏的 `agent-task` 最小迁移为项目限定的 `trellium-work`。

目标架构严格分层：

- 用户级 `trellium` / `trellium-zh`：控制面，负责 adopt、upgrade、diff、check、status 与协议维护；
- 项目级 `trellium-work`：执行面，负责在已接入项目中路由上下文、执行任务契约并完成验证与记忆收尾；
- `AGENTS.md`：没有 Skill 时仍成立的最低安全入口；
- `vault/`：项目事实与任务状态的权威数据面；
- `trellium.py`：确定性机械层。

本任务不把“双 Skill”预设为必然答案。若项目 Skill 对正确性、遗漏率或上下文成本没有可观察增益，则停止在 No-Go，保留 `AGENTS.md + vault`，只修复已证实的全局模板泄漏。

## Baseline（2026-09-15，实施前必须复核）

- 发行包为 `skills/trellium/` 与 `skills/trellium-zh/`，语言二选一；它们是用户级控制 Skill。
- adopt/upgrade 当前把 `skills/agent-task/SKILL.md` 当作协议模板文件下发。
- 当前 `agent-task` 名称过于通用，不能表达 Trellium 作用域，也容易与其他项目工作流冲突。
- 本次 Codex 会话实际把全局安装包内部的 `trellium-zh/assets/templates/skills/agent-task/SKILL.md` 发现为可用 `agent-task`；项目模板存在被递归发现为用户级 Skill 的真实信号。
- `scripts/install.sh --project` 当前只写入 `./.claude/skills`，且安装的是控制 Skill 包；它不是跨 Agent 的项目工作 Skill 安装方案。
- 当前协议版本为 `2026.09.5`；TASK-0010 已在 `init/MIGRATIONS.md` 留有 Unreleased 内容。

实施 Agent 必须先以现场文件和可用 Agent 的真实发现结果复核以上基线；不能把本段历史观察冒充跨平台事实。

## Scope

### In Scope

1. 预注册并执行 A0/A1 消融，判断项目 Skill 是否比 `AGENTS.md + vault` 有独立增益。
2. 在隔离目录验证 Codex 与 Claude Code 的用户级/项目级 Skill 发现边界；某 Agent 在当前环境不可运行时明确记为未验证，不得由目录猜测替代。
3. 修复控制 Skill 包内项目模板被递归发现为全局 Skill 的问题；模板源不得以可发现的嵌套 `SKILL.md` 形态存在。
4. 消融 Go 时：把项目工作流命名为稳定、语言无关的 `trellium-work`，让 adopt/upgrade 将其安装到经验证的项目级发现位置。
5. 保证中英文项目 Skill 使用同一 `name: trellium-work`，正文按所选语言生成。
6. 为旧 `skills/agent-task/SKILL.md` 提供零静默覆盖的升级迁移：未定制副本可自动迁移；本地定制或目标冲突必须生成 proposal。
7. 同步最小必要的升级器、安装说明、协议、双语模板、MIGRATIONS、版本与生成快照。
8. 添加行为测试，覆盖新接入、旧项目升级、定制冲突、重复升级与作用域隔离。

### Out of Scope

- Context、Review Pack、Evidence Receipt、Vault schema、status/check 新功能。
- 合并 `trellium` 与 `trellium-zh` 的用户级 Skill ID；本周期继续保持语言包二选一。
- 长期同时保留两个可发现的项目 Skill 作为兼容层。
- 静默删除或覆盖用户定制的 `agent-task`。
- 未经 owner 追加批准，删除或改变 `install.sh --project` 的既有语义；可以修正文档、标注其不是推荐的日常项目工作流。
- 创建 tag、GitHub Release、修改 CI 权限、依赖、业务源码或公开数据模型。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/collaboration.md`
- 本任务文件
- `skills/agent-task/SKILL.md`
- `skills/trellium*/SKILL.md`
- `skills/trellium*/assets/templates/skills/agent-task/SKILL.md`
- `scripts/trellium.py` 的 `TEMPLATE_FILES`、`FILE_ROLES`、adopt/upgrade 路径
- `scripts/install.sh`
- `scripts/sync-skills.py` 与相关测试
- `init/protocol/30-agent-entry.md`、`init/protocol/70-adoption-flow.md`
- `init/MIGRATIONS.md`、`init/VERSION`、双语 README

## Capability Tags

- skill-design
- agent-governance
- migration
- testing
- documentation
- ablation

## Authority

Allowed:

- Owner 2026-09-15 已批准本 TASK 方案并交 Claude 实施；允许在本合同范围内完成消融、最小代码/模板修改、版本迁移、测试和 Vault 记录。
- 使用隔离临时目录和不含真实项目数据的 fixture 验证安装与发现行为。
- 按仓库惯例提交聚焦里程碑；push 前仍需遵守当前会话的外部写权限。

Requires Approval:

- 消融未通过但仍要安装第二个项目 Skill。
- 改变 `install.sh --project` 的行为或删除该参数。
- 将用户级 Skill ID 从 `trellium-zh` 统一为 `trellium`。
- 新增 Agent 专属 CLI 参数、符号链接方案或第三方依赖。
- accepted、tag、Release 或任何历史重写。

Forbidden:

- 为证明 A1 更好而把 A0 的必要 `AGENTS.md`/Vault 材料删减或降低质量。
- 让评分者读取 golden、预期裁决或另一实验臂的答案。
- 把不可运行的 Agent 标成已验证。
- 让控制 Skill 和项目 Skill 在同一请求上以重叠职责同时执行。
- 以兼容名长期发布两个内容相同、都可自动触发的 Skill。
- 静默覆盖项目自定义协议或保存本机路径、UUID、凭据等隐私数据。

## Load-bearing Assumptions and Red-Team

按影响 × 可能性 × 测试便宜程度排序：

1. **项目 Skill 有独立价值。**
   - Fails if：A0（`AGENTS.md + vault`）与 A1（增加 `trellium-work`）在核心判断、遗漏率和读取成本上无差异。
   - Cheapest test：三个冻结场景的 A0/A1 独立首答对照。
   - Kill criterion：A1 没有减少任何关键遗漏，也没有降低可见读取成本；或出现任一新增越权/错误完成声称。
2. **项目 Skill 能被限定在项目内。**
   - Fails if：离开目标项目仍可发现 `trellium-work`，或用户级安装包继续暴露嵌套工作 Skill。
   - Cheapest test：同一干净 Agent 环境在项目内外各列举/调用一次 Skill。
   - Kill criterion：任一受支持 Agent 出现全局泄漏且无法用不增加依赖的最小包装修复。
3. **跨 Agent 安装不需要第二套权威内容。**
   - Fails if：Codex 与 Claude Code 必须维护会独立漂移的 Skill 正文。
   - Cheapest test：验证一个 canonical 模板能否确定性生成各 Agent 项目投影，并由测试逐字比较。
   - Kill criterion：只能靠人工复制维护多个正文且无机械同步门禁。
4. **重命名可以安全升级。**
   - Fails if：旧项目定制无法可靠识别，或升级会同时激活 `agent-task` 与 `trellium-work`。
   - Cheapest test：未改旧文件、定制旧文件、目标已存在三种 fixture。
   - Kill criterion：任何 fixture 静默丢失内容，或完成升级后仍存在两个可发现 Skill。
5. **“小改动”不会扩成安装器重构。**
   - Fails if：必须新增通用插件系统、依赖或大幅改写 upgrade 状态机才能工作。
   - Cheapest test：M1 后列出最小 touched-file 集合与估算 diff。
   - Kill criterion：超出既有模板/`FILE_ROLES`/迁移机制即可表达的范围；此时停下向 owner 重提方案。

## Preregistered Ablation

### Evidence discipline

- 在任何产品代码或发行模板修改前，先建立独立的实验协议与 golden，并以单独提交冻结。
- 每次实际投放的 prompt、输入材料、首答、会话标识、可用的模型/工具元数据先逐字落盘，再评分。
- A0/A1 使用相同场景事实、相同问题和相同材料上限；唯一变量是是否提供项目级 `trellium-work`。
- 顺序交错或随机；同一会话不得看到两个实验臂；读到 golden、另一臂答案或本任务预期结论即 contaminated，不计分但保留记录。
- 每格最低 n=1，结论仅作为本任务准入证据，不外推为所有 Agent/项目的普遍结论。

### Arms

- **A0 — 最小底座：** `AGENTS.md + vault`，不暴露任何项目 Skill。
- **A1 — 候选方案：** 与 A0 完全相同，额外提供薄的项目级 `trellium-work`；该 Skill 只负责触发和路由，不复制完整 governance。
- 当前全局泄漏的 `agent-task` 只作为结构缺陷复现材料，不作为价值对照臂，避免把错误作用域当产品方案。

### Scenarios

1. **首次进入：** 判断当前阶段、Focus、允许修改范围和下一步。
2. **中断恢复：** 从 active Level B/C TASK 与 handoff 找到当前 slice、阻塞项和必要检查。
3. **local 收尾：** 判断 durable knowledge disposition、closed local runtime 行删除规则，以及 owner accepted 权限边界。

每个场景固定询问：要读什么、当前可做什么、什么不能声称、下一动作、完成前必须更新/验证什么。

### Metrics

- 核心判断准确率；
- 漏掉的必读文件、验收门或 memory update 数；
- 越权或错误声称 accepted/完成次数（硬指标）；
- 首答 owner 纠正次数；
- 可见输入 bytes、额外打开文件数、tool calls；
- Skill 在项目内/外的发现结果。

### Decision Gate

- **Go：** A1 零越权、零错误完成声称，且相对 A0 至少减少一个预注册关键遗漏，或在准确率不降时降低可见材料/打开文件成本；同时项目外不可发现。
- **No-Go：** A1 与 A0 无可观察增益，或 A1 引入越权、错误完成声称、重复触发或项目外泄漏。不得为了交付功能继续重命名/安装第二 Skill。
- **Inconclusive：** 会话污染、Agent 发现能力不可验证、实验材料不对称，或结果不足以区分。只允许修复已独立复现的模板全局泄漏；项目 Skill 迁移保持未实现。
- Go/No-Go/Inconclusive 必须逐条对照本节，不能以“架构更整洁”替代实证。

## Implementation Contract（仅消融 Go 后生效）

1. 项目 Skill 的 frontmatter `name` 固定为 `trellium-work`；中英文只改变说明文本，不改变能力 ID。
2. Skill 必须是薄路由层：引用 `AGENTS.md` 和 Vault 路由，不复制生命周期枚举、当前预算、TASK storage 等可漂移事实。
3. 用户级控制包的可发现 Skill 只有其顶层 `trellium` 或 `trellium-zh`；项目模板改用不可被 Skill 扫描器识别的模板文件名，adopt 时再渲染为 `SKILL.md`。
4. 经现场验证后建立 Agent 安装位置矩阵。只声明实际验证的平台；一个 canonical 模板确定性生成所需投影，投影必须有机械同步测试。
5. 旧 `skills/agent-task/SKILL.md`：
   - 与已知基线一致时，升级器可迁移到新位置并移除旧副本；
   - 有本地修改、目标已存在或无法证明基线时，生成 `vault/.upgrade/<version>/` proposal；
   - 不允许迁移完成后两个 Skill 同时可发现。
6. 新 adopt 只生成 `trellium-work`，不得再生成 `agent-task`。
7. `check`、`status` 的文本、JSON schema 与退出码不因本任务变化；除非现有命令本就报告受管文件清单，否则不扩 checker 职责。
8. 版本目标为下一个未发布版本（预期 `2026.09.6`，实施前核实 tag/Release 与 `init/VERSION`）；TASK-0010 的既有 Unreleased 内容必须保留。

## Milestones

### M0 — Preflight 与预注册

- 复核 Git、版本、Release、测试、snapshot、check/status 基线。
- 冻结实验协议、三场景材料、golden、评分规则、污染规则和停止条件。
- 单独提交预注册；提交必须早于任何产品/模板实现。

### M1 — 发现边界与 A0/A1 消融

- 在隔离用户目录和隔离项目运行结构发现测试。
- 运行 3 场景 × 2 臂的独立首答实验。
- 先落原文、后评分；输出 Go / No-Go / Inconclusive。
- No-Go 或 Inconclusive 时执行停止条件，不得进入 M2 的项目 Skill 实现。

### M2 — 最小 Skill 与模板包装（仅 Go）

- 创建薄 `trellium-work` canonical 模板和经验证的项目投影。
- 消除控制包中的嵌套 `SKILL.md` 全局发现路径。
- 新 adopt 生成项目 Skill；不修改 Vault 数据文件。

### M3 — 安全迁移（仅 Go）

- 接入既有 upgrade/FILE_ROLES 机制。
- 覆盖未定制、已定制、目标冲突、重复执行四类 fixture。
- `install.sh --project` 保持兼容，不在本任务内静默改义。

### M4 — 版本、文档与快照

- 更新 MIGRATIONS、VERSION、双语 README、协议源和两套发行快照。
- 文档明确：语言包二选一；逻辑上是一个用户级控制 Skill 加一个项目级工作 Skill，而非同时安装中英文包。

### M5 — 独立 review 与 owner 验收

- reviewer 独立读取 TASK、diff、测试与实验原文，检查消融时序、作用域、迁移零丢失和模板泄漏。
- P0/P1/P2 全部闭合后进入 `ready_for_review`；不得代 owner accepted、tag 或 Release。

## Acceptance Criteria

- [ ] 预注册提交在实现提交之前，Git DAG 可证；原始 prompt/材料/首答先于评分冻结。
- [ ] A0/A1 裁决严格符合 Decision Gate；No-Go/Inconclusive 时没有越权实现项目 Skill。
- [x] 全局模板泄漏有实施前复现和修复后反证；用户级包不再暴露嵌套项目工作 Skill。（Codex 项目外亦报告 agent-task 可用 = 复现；两包模板更名 AGENT_TASK_SKILL.template + TemplatePackagingTest 运行时断言 = 反证；Claude Code 侧嵌套模板本就不发现，实证 43 项全列表）
- [ ] 若 Go，新项目只发现 `trellium-work`，离开项目不可发现；中英文 `name` 一致。
- [ ] 若 Go，旧项目四类迁移 fixture 零静默覆盖、零双 Skill 残留、重复升级幂等。
- [ ] `trellium-work` 为薄路由层；没有复制当前预算、storage 值或完整 governance。
- [ ] `check`/`status` 既有输出与退出码无非预期变化。
- [ ] 版本、MIGRATIONS、双语 README、协议源、嵌入脚本和两套 snapshot 一致。
- [ ] 全量测试通过，`check` 0 error / 0 warning，`sync-skills.py --check` 通过，范围级 whitespace 检查通过。
- [ ] 独立 review 无 open P0/P1/P2；owner 决定 accepted 与后续发布。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status .`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`（若触及 TASK-0009 逐字证据，沿用 runtime 中的范围豁免；本任务不应触及这些文件）
- 隔离目录的新 adopt、旧版 upgrade、定制冲突、重复升级与项目内/外发现测试

Completed:

- 待 Claude 实施。

## Execution Record

### 2026-09-15 - Agent: GLM — M0 预注册与 M1 消融（判定：No-Go）

Context read: 合同、`skills/agent-task/SKILL.md`（顶层+两包模板）、AGENTS 模板、`scripts/trellium.py` TEMPLATE_FILES/FILE_ROLES、`scripts/install.sh`。

Changes made:

- M0：现场复核基线（含新事实：顶层 `skills/agent-task/` 本身即可被发现）；冻结 `docs/evals/project-work-skill-2026-09/` 四件套 + 三场景 fixture + A1 薄路由草案（`e2fe146`，先于任何实现）。
- M1：结构发现测试（Claude Code ×3 + Codex ×3 真实 headless 探测）+ 6 个 A0/A1 会话（交错顺序、先落原文后评分）。

Checks run:

- 121 tests、check 0/0、snapshot in sync、范围级 whitespace CLEAN（预注册提交时）。

Review and reflection:

- **判定 No-Go**：两臂全场景 0 关键遗漏、0 需要纠正、0 硬指标违规（A0 底座充分，地板效应）；A1 唯一可观察差异是读入更多材料（visible +79%）。附加结构事实：Codex 不发现项目级 `.claude/skills/`（项目 Skill 前提对 Codex 不成立），且 `agent-task` 全局泄漏在 Codex 复现（中性目录亦可见，来源为本机全局安装的控制包嵌套模板）。
- 按停止条件：不进入 M2/M3 项目 Skill 实现；仅执行已复现泄漏的最小修复（模板改不可发现文件名）。

Next action:

- CI 恢复验证预注册提交后，执行泄漏最小修复；M2/M3 其余项按 No-Go 取消。

### 2026-09-15 - Agent: Codex — 合同建立并激活

Context read:

- 项目必读 Vault、当前 Skill 模板、升级器文件角色、安装脚本、协议接入流程、双语 README 与 Skill 创建规范。

Changes made:

- 将 owner 认可的控制面/执行面方向写为 Level C 合同；名称候选收敛为 `trellium-work`。
- 用 red-team 反证把“第二 Skill 是否有独立价值”设为实现前 Gate，而非把架构偏好直接当产品事实。
- 冻结 A0/A1 单变量消融、污染纪律、停止条件、安全迁移和不做范围。

Review and reflection:

- 代码改动预计较小，但发现作用域与旧项目定制迁移具有高影响，不能按普通重命名处理。
- 当前 `agent-task` 的大部分规则已存在于 `AGENTS.md`/governance；如果薄 Skill 不能降低遗漏或读取成本，就应接受 No-Go。
- `trellium-zh` 与 `trellium` 的 ID 统一是另一项兼容决策，本任务刻意不夹带。

Checks run:

- 仅合同阶段检查，见本次交付说明。

Next action:

- Claude 从 M0 开始：先提交预注册与基线证据，再运行 M1；只有 Go 才进入模板和升级器实现。

## Memory Updates

- `vault/runtime.md`
- `vault/handoff.md`
- `vault/details/shadow-run-2026-09.md`（真实 TASK 派生计数，不伪造 lifecycle 转换）
- `vault/decisions.md`：仅在 owner 验收最终架构后记录 durable decision
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)

### 2026-09-16 - Agent: GLM — 泄漏最小修复、独立复审与验收前收尾

- 泄漏修复（No-Go 停止条件授权的唯一实现）：两控制包模板源更名 `AGENT_TASK_SKILL.template`；`trellium.py` 增加 `TEMPLATE_SOURCE_OVERRIDE`/`template_source()`，adopt/upgrade 对目标项目仍渲染/刷新 `skills/agent-task/SKILL.md`（独立 reviewer 实测 adopt 渲染与两包模板及 canonical 逐字节一致；diff/upgrade/--apply exit 0）。`TemplatePackagingTest` 运行时断言包内无可发现 SKILL.md。
- 独立复审 **APPROVE**：消融完整性（冻结提交 e2fe146 先于 934e892 评分提交、单变量纪律、计量逐位重算）、判定忠实（No-Go 无越级表述）、修复正确性、范围干净全部 PASS。
- P2 勘误：results.md 成本表 material_bytes 行初版误记 1,966/2,109（不可重算）→ 以 run.json 原值更正为 786/932（+18.6%）。
- owner review REQUEST_CHANGES（2026-09-16，4 阻断）：任务**保持 active**（曾误提前登记 ready_for_review 投影与转换，已撤销）；P1-1 实验记录隐私违规待历史脱敏授权；P1-3 验收清单未闭合；P1-4 Codex 结论越权已收回；P2 已改。R2/项目 Skill 实现按 No-Go 不做。
