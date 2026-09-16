# TASK-0012 - 按需路由的跨语言代码注释规范

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0012",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "M5 — owner review"
}
-->

## Objective

把 owner 在真实 Go 开发中观察到的“关键设计信息因缺少注释而丢失”转化为可持续的项目工程规范，同时避免把完整语言规范塞进默认 Agent 上下文或继续膨胀 Vault。

目标架构：

- 上游协议保存一份跨语言核心原则，并由 Go/Python profile 提供语言适配；
- 目标项目只保留一个 `docs/engineering/code-comments.md`，内容为核心原则加已选择的语言章节；
- `AGENTS.md` 只保留一跳、机械触发的读取路由；
- `.agent-init.json` 记录显式选择的 profile、目录作用域、源 hash 和项目规则位置，支持一个项目选择多种语言；
- 既有项目的工程规范不被静默覆盖，升级遵守现有 merge/proposal 边界。

## Scope

### In Scope

1. 冻结并执行载体消融：完整内联、直接路由、Vault 二跳路由。
2. 新增语言无关的注释/API 文档核心原则。
3. 为 `go-backend` 与 `python-backend` 增加符合各自官方惯例的适配规则。
4. 让 adopt 接受显式、可重复的 profile 选择和相对目录作用域；同一项目可选择多种语言。
5. 生成单一项目文档 `docs/engineering/code-comments.md`，不为每种语言创建单独文件。
6. 在 `AGENTS.md` 增加一行直接、条件式路由，不通过 Vault 二跳。
7. `.agent-init.json` 在保持旧 stamp 可读的前提下记录 profile 元数据。
8. 覆盖新接入、多语言、路径校验、已有文档保护、升级冲突与幂等测试。
9. 更新初始化/接入协议、MIGRATIONS、版本、双语说明和两套 Skill 快照。

### Out of Scope

- 自动猜测并静默选择语言 profile；本任务只允许显式确认后的选择。
- 新增 Go/Python 项目 Skill、注释率门禁、lint 依赖或语义注释检查器。
- 为 Java、Rust、TypeScript 等新增适配章节。
- 把工程规范写入 `vault/details/`、`vault/index.md` 或 `vault/runtime.md`。
- 修改目标项目业务源码、依赖、CI 或既有工程文档内容。
- accepted、tag、Release 或 push。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/collaboration.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/50-engineering-constraints.md`
- `init/protocol/60-initialization-flow.md`
- `init/protocol/70-adoption-flow.md`
- `init/protocol/profiles/go-backend.md`
- `init/protocol/profiles/python-backend.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`
- `docs/evals/code-comment-routing-2026-09/preregistration.md`

## Capability Tags

- agent-governance
- cli
- documentation
- migration
- multi-language
- testing
- ablation

## Authority

Allowed:

- Owner 2026-09-16 明确批准把该方向作为下一优化目标并直接实施。
- 在本合同范围内修改协议源、模板、CLI、测试、版本迁移、双语说明、生成快照与 Vault 记录。
- 使用临时目录验证 adopt/upgrade，不触碰真实外部项目。

Requires Approval:

- 自动选择 profile 而不是只报告候选或要求显式选择。
- 新增第三方依赖、注释率 Gate、业务代码 lint 配置或新的项目 Skill。
- 把多语言工程规则写入 Vault 数据文件。
- accepted、tag、Release、push 或历史重写。

Forbidden:

- 为减少 Token 而删减 owner 指定的关键注释语义。
- 把 Go 的导出/Doc Comment 语法机械套用到 Python。
- 覆盖目标项目已有 `docs/engineering/code-comments.md` 或既有工程规范。
- 让 `.agent-init.json` 成为人类工程规范的唯一载体。
- 把实验性自动检测结果当成用户确认。

## Load-bearing Assumptions and Red-Team

1. **一跳路由能在不降低规则可达性的前提下降低默认上下文。**
   - Fails if：源码修改或评审任务无法由机械触发词命中，或路由目标不存在/需要二次查找。
   - Cheapest test：同一规则文本下比较完整内联、AGENTS 直达、AGENTS→Vault→文档三种载体的默认 bytes、条件 bytes、跳数和目标完整性。
   - Kill criterion：直达路由丢失任一强制语义、需要超过一跳，或非源码任务仍必须加载正文。
2. **一个公共核心加语言适配优于“伪通用”规则。**
   - Fails if：公共核心包含 Go 专属导出语法，或 Python 章节重复签名/类型而违反项目既有 docstring 风格。
   - Cheapest test：逐条把 owner 原规范分类为 common/Go/Python，并用官方规则核对差异。
   - Kill criterion：任一语言必须扭曲自身公开 API 或文档约定才能符合公共核心。
3. **单一项目文档足以承载多语言，而不会成为新的巨型协议。**
   - Fails if：未选择的语言也进入目标文档，或每个 profile 仍生成独立文件。
   - Cheapest test：Go-only、Python-only、Go+Python 三个 adopt fixture 比较文件数、章节和作用域。
   - Kill criterion：目标项目新增超过一个工程规范文件，或出现未选语言章节。
4. **显式 profile 选择比自动猜测更安全。**
   - Fails if：显式语法无法表达同语言多 root 或多语言项目。
   - Cheapest test：重复参数 fixture + 非法/逃逸路径负例。
   - Kill criterion：必须依赖 manifest 猜测才能表达现实项目，或路径可逃逸目标根。

## Milestones

### M0 — Preflight 与预注册

- 记录版本、测试、check、snapshot、工作树基线。
- 冻结载体臂、指标、停止条件、范围与不做范围。
- 预注册提交必须早于产品/模板实现。

### M1 — 载体与规则分层消融

- 对 R0/R1/R2 做确定性材料/读取成本比较。
- 把 owner 原规范逐条分类为 common/Go/Python。
- 输出 Go/No-Go；本任务中“规范必须存在”不参与裁决，只裁决载体。

### M2 — 协议与项目文档生成

- 新增公共核心与 Go/Python 适配。
- 渲染单一 `docs/engineering/code-comments.md`。
- AGENTS 只增加一跳条件路由。

### M3 — Profile 元数据与安全升级

- CLI 支持显式多 profile、多 root。
- stamp 向后兼容并记录 profile/source hash/project rules。
- 已有项目规则冲突只出 proposal，不静默覆盖。

### M4 — 文档、版本与快照

- 更新初始化/接入流程、README/MIGRATIONS/VERSION。
- 同步中英文 Skill 快照；不复制目标项目工程文档到 Vault。

### M5 — Review 与验收

- 自审协议完整性、路径安全、数据保护、幂等和多语言组合。
- 独立 review 或 owner review 的 P0/P1/P2 全部闭合后才进入 `ready_for_review`。

## Acceptance Criteria

- [x] 预注册在任何实现修改之前冻结，Git DAG 可证。（`e4f58c9`，产品/模板零 diff）
- [x] 载体裁决逐条对应冻结 Gate，不用“更整洁”代替证据。（R1 Go；R2 被同内容、额外一跳与第二 route owner 支配；R0 非源码任务默认成本过高）
- [x] owner 原规范的关键语义全部进入公共核心或 Go 适配，无静默删减。
- [x] Python 适配符合项目公共 API 与 PEP 257 约定，不照搬 Go 语法。
- [x] Go-only、Python-only、Go+Python 都只生成一个工程规范文件，且不含未选语言章节。
- [x] AGENTS 路由一跳直达；Vault 零新增工程规范文件。
- [x] 旧 stamp 可读；多 profile、多 root、非法路径、重复参数行为确定。
- [x] 已存在或已定制的工程规范零静默覆盖；升级冲突可恢复。
- [x] `check`/`status` 输出与退出码无非预期变化。
- [x] 全量测试、check、snapshot、whitespace 门禁通过。
- [x] review 无 open P0/P1/P2。
- [ ] owner 决定 accepted 与发布。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`
- 隔离 fixture：Go-only、Python-only、Go+Python、重复 root、路径逃逸、已有规范、升级冲突、重复升级

Completed:

- 2026-09-16 M0 preflight：123/123 tests；check 0 error / 0 warning；snapshot in sync；`git diff --check` clean；HEAD `19f2229`（`2026.09.6`，与 `origin/develop` 一致）。

## Execution Record

### 2026-09-16 - Agent: Codex — M0 合同与预注册

Context read:

- 项目必读 Vault、TASK-0011 当前边界、协议工程/接入模块、Go/Python profile、升级 stamp 与 adopt/upgrade 实现、现有测试。

Changes made:

- 将 owner 明确要求的注释知识持久化问题建立为独立 Level C 任务；TASK-0011 保持 ready_for_review，不夹带验收。
- 冻结“规范必须交付、只消融载体”的实验边界；默认候选为 AGENTS 一跳路由 + 单一项目工程文档。
- 明确 v0 只接受显式 profile 选择，不自动猜测技术栈。

Checks run:

- 实施前基线见 Verification Completed。

Review and reflection:

- 文件复杂度与 Token 不是单一指标：直达路由只有在触发机械、目标唯一、无第二事实源时才成立。
- 工程规范属于项目工程层，不应继续放入 Vault；`.agent-init.json` 仅承载升级元数据。

Next action:

- 单独提交 M0 预注册，然后执行 M1；裁决通过后才修改产品/模板文件。

### 2026-09-16 - Agent: Codex — M1 载体消融与规则分类

Changes made:

- 用同一份 4,413-byte / 96-line 中文规范构造 R0 inline、R1 direct-route、R2 Vault two-hop 三臂；R0 内联正文与独立规范逐字节一致。
- 逐条把 owner 原规范分类为 common/Go/Python；修正 package/导出表述，并补入 Python 公共 API/docstring 的语言适配边界。

Checks run:

- R0/R1/R2 真实材料 `wc -c -l`；R0 正文与独立 policy `diff -u` 无差异；`git diff --check` clean。

Review and reflection:

- R1 默认入口 254 bytes，相比 R0 4,562 bytes 减少 94.4%；R2 默认 327 bytes 且多一跳/一个 route owner，无收益。
- 裁决仅声称载体结构与成本，不声称 Agent 准确率提升；真实漏读事件是未来重开信号。

Next action:

- 提交 M1 结果，随后进入 M2；实现不得更改冻结 Gate 或把工程规范放回 Vault。

### 2026-09-16 - Agent: Codex — M2-M4 实现

Changes made:

- 公共核心与 Go/Python 语言适配落入协议源和双语模板；目标项目只生成 `docs/engineering/code-comments.md`，未选择的语言章节不渲染。
- `adopt --profile PROFILE[=ROOT]` 支持多语言与同语言多 root；不传 profile 时输出集合保持不变，不做语言自动检测。
- adoption stamp 升级为 schema 2，记录 profile、roots、source hash 与工程文档位置；v1 stamp 继续可读。
- 工程规范作为 merge 载体进入 upgrade：pristine 可刷新，项目定制与上游同时变化时生成 proposal；已有文件即使 `--force` 也不覆盖，重复 adopt 不允许静默更换 profile 集。
- `AGENTS.md` 只添加源码/API/注释/TODO 任务的一跳直达路由；版本升至 2026.09.7，README、初始化/接入流程、MIGRATIONS 与两套 Skill 快照同步。

Checks run:

- 实现提交：`bbae794`。
- 聚焦 adopt/upgrade/profile 与模板测试通过；随后全量 136/136 tests 通过。
- `check --format json` 0 error / 0 warning；`status --format json` 0 unresolved；两套 snapshot in sync；`git diff --check` clean。

Review and reflection:

- 规范正文属于工程层，不进入 Vault；stamp 只保存机器升级所需元数据，不能替代人类可读规范。
- profile root 只是显式声明，不以 manifest 猜测；路径重叠时按文件实际语言选适配，避免把 Go 语法套到 Python。

### 2026-09-16 - Agent: Codex — M5 structured review

Review result:

- `code-review-expert` 结构化审查初轮发现 2 项 P1：root 可通过换行/反引号破坏 Agent 规范边界；损坏的 v2 profile metadata 被宽容忽略，可能让 upgrade 错误分类工程规范。
- 两项均改为写入前 fail-closed：root 拒绝非打印字符/反引号/边缘空白；stamp metadata 严格验证，工程规范存在但 profile metadata 缺失时拒绝生成删除计划。
- 补充路径注入、malformed/inconsistent stamp、legacy v1 stamp 与 tooling-only v1→v2 测试；复跑后无 open P0/P1/P2，结论 APPROVE。

Next action:

- Owner 复核 TASK-0012 与 `bbae794`，决定是否 accepted；accepted 后才授权 push、tag 或 Release。

## Memory Updates

- `vault/runtime.md`
- `vault/collaboration.md`
- `vault/details/shadow-run-2026-09.md`
- `vault/decisions.md`：仅在 owner 验收最终架构后记录 durable decision
- Durable knowledge disposition: not_applicable (`task_storage=tracked`)
