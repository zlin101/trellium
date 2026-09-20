# TASK-0014 - 完整语言 Profile 项目级持久化

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0014",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

修复语言 profile 只在首次控制 Skill 会话可见、后续普通会话遗忘完整工程规则的缺陷。显式选择的 profile 必须以项目文件持久化，由 `AGENTS.md` 一跳按 root 条件路由；fresh clone 不依赖再次发现或调用 Trellium Skill。

## Scope

### In Scope

- `--profile PROFILE=ROOT` 为每个已选 profile 生成 `docs/engineering/profiles/<profile>.md`，文档包含完整工程规则和全部声明 roots。
- 多 profile、多 root 独立路由；未选 profile 零新增，不自动猜语言。
- stamp 记录 profile、roots、source hash、项目文件路径；upgrade/diff 支持 pristine 刷新与定制冲突 proposal。
- v1/v2 stamp 兼容；既有 `docs/engineering/code-comments.md` 不覆盖、不删除、不静默丢失定制。
- 更新协议、迁移说明、README、双语 Skill 产物和确定性测试。

### Out of Scope

- 改写 TASK-0013 的冻结合同或结论。
- 自动检测语言、自动 Git add/commit/push、tag、Release 或版本号升级。
- 修改 owner 既有 `vault/.agent-init.json` 与未跟踪 `docs/engineering/code-comments.md`。
- 把完整 profile 放入 Vault 或默认必读路径。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/handoff.md`
- `vault/tasks/TASK-0012-code-comment-routing.md`
- `vault/tasks/TASK-0013-adoption-durability.md`
- `init/protocol/profiles/go-backend.md`
- `init/protocol/70-adoption-flow.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`
- `docs/evals/durable-language-profiles-2026-09/preregistration.md`

## Capability Tags

- agent-governance
- cli
- profile
- adoption
- migration
- testing
- ablation

## Authority

Allowed:

- Owner 在本轮明确授权 Level C / Authority 3 的实现、测试、协议与记忆更新。
- 使用临时 fixture 验证 adopt/upgrade/fresh-clone，不触碰真实外部项目。

Requires Approval:

- accepted、commit、push、tag、Release、版本号升级或外部项目升级。
- 自动选择 profile、删除既有项目工程规范或引入第三方依赖。

Forbidden:

- 覆盖或暂存 owner 的 `vault/.agent-init.json`、`docs/engineering/code-comments.md`。
- 只写指向机器全局 Skill 的链接。
- 用压缩版本遗漏 module/workspace、分层、依赖、错误链、资源、并发、HTTP、测试/工具链、注释/API 任一关键类。
- 自动执行 Git 写操作。

## Preregistered Ablation

比较载体，不比较“是否持久化”（持久化由 owner 强制要求）：

- R0：完整 profile 项目副本，每 profile 一个文件，一跳条件路由。
- R1：压缩 capsule，每 profile 一个文件，一跳条件路由。

冻结覆盖清单：module/workspace、package/分层、依赖、错误链、资源生命周期、context/并发、HTTP 生命周期、测试/工具链、注释/API 规则。

Kill criteria：候选遗漏任一关键类，或需要读取机器全局 Skill/二跳 Vault 才能恢复规则，即淘汰。R1 只有在逐类语义等价且明显更小时才可采用；否则选择 R0。确定性章节/关键词覆盖优先，不收集不必要的会话 transcript。

## Acceptance Criteria

- [x] 新 adopt Go profile 生成完整项目 profile、AGENTS 一跳 route 与完整 stamp metadata。
- [x] fresh clone / HEAD checker 把 profile 文件视为协作 core。
- [x] 后续会话只靠 AGENTS + 项目文件可发现九类关键规则。
- [x] multi-profile / multi-root 路由不混用语言。
- [x] 未选 profile 不新增 profile 文件。
- [x] pristine upgrade 刷新；本地定制与上游同时变化时 proposal 且不覆盖。
- [x] legacy v1/v2 stamp 保持可读和可升级。
- [x] 中英文包输出语言一致；canonical/derived 关系有防漂移测试。（显式 `PROFILE_LOCALE` 决定渲染语言，不再依赖正文标题）
- [x] 既有测试、checker/status 与 Skill snapshots 无回归。
- [x] owner 文件未被覆盖、删除或暂存。
- [x] 独立主 Agent review 无 open P0/P1/P2，技术验收 APPROVE。（2026-09-20 终验覆盖 symlink/hardlink、未选 profile、fallback 与显式 locale）
- [ ] tracked 任务文件与实现提交后再进入 accepted；未授权 commit 前不得制造 `TASK_STORAGE_MISMATCH`。

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`
- 临时 fixture：Go-only、Go+Python 多 root、无 profile、fresh clone、pristine/customized upgrade、legacy v1/v2、双语输出

Completed:

- 2026-09-19：`python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 164 tests OK。
- 2026-09-19：`sync-skills.py --check` 与 `git diff --check` 通过。
- 2026-09-19：self-check 如实为 2 errors / 1 warning；2 errors 是未触碰的 owner `code-comments.md`/stamp 现场，warning 是本任务文件按要求未 commit。

## Required Memory Updates

- `vault/runtime.md`
- `vault/handoff.md`
- `vault/decisions.md`
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

保持 active 交主 Agent 独立验收；不得 commit/push/tag/release。报告消融裁决、测试结果、owner 文件保护事实与剩余风险。

## Execution Record

### 2026-09-18 - Agent: Codex sub-agent — 合同与预注册

Context read:

- 项目必读 Vault、TASK-0012/0013、完整 Go profile、adoption 协议、CLI/profile tests、Trellium Skill reference。

Changes made:

- 建立 Level C / Authority 3 合同并冻结九类覆盖与 kill criteria。
- 明确 TASK-0013 合同冻结、owner 两个现场文件禁止触碰、版本保持 2026.09.8。
- 证据边界：设计文本先于实现编辑写入，但全部仍处于同一未提交变更集；只能由执行记录说明时序，不存在独立 commit DAG 证明。

Next action:

- 先记录确定性消融裁决，再实施完整 profile 载体和迁移测试。

### 2026-09-18 - Agent: Codex sub-agent — 实现与自查

Changes made:

- R0 完整 profile 成为项目级条件载体；多语言各自文件、同语言多 root 写入同一文件。
- stamp 新增 `project_profile`，完整 profile 加入 Git core、diff/upgrade、proposal 和 source hash；legacy v2 自动补文件。
- 中文模板从 canonical init profile 机械派生，英文提供本地化完整语义；既有注释文档保留兼容。
- 协议、迁移、README、双语 Skill/snapshots、D-0011 与 fixture 测试同步。

Checks run:

- 162 tests OK；sync check 与 whitespace check clean。
- fresh-clone fixture 证明完整 profile 进入 HEAD 后存在且 check 0 error。
- self-check 的 2 errors / 1 warning 均为已知 owner/未提交状态，未伪称通过。

Review and reflection:

- R1 capsule 因无逐类语义等价证据被淘汰；文件复杂度留在按需工程文档，不进入 AGENTS 默认上下文或 Vault。
- owner 的 `vault/.agent-init.json` 与 `docs/engineering/code-comments.md` 未写入、删除或暂存。

Next action:

- 保持 active，交主 Agent 独立验收；不 commit/push/tag/release。

### 2026-09-19 - Agent: Codex sub-agent — 独立审查 finding 闭合

Changes made:

- legacy v2 已选 profile 路径若预存自定义文件，不再作为普通 `add_skip` 遗漏；升级生成 proposal 且不覆盖，`--complete` 后 stamp 的 `files`、`project_profile` 与 core path 全部纳入该文件。
- upgrader 对 profile 写路径使用有限 `PROFILE_IDS` 精确白名单；未知 profile 和 `..` 穿越路径在 anchored writes 不可用时仍 fail closed。
- AGENTS 与 adoption protocol 明确双载体优先级：重叠的注释/API 规则以兼容文档的项目定制为准，完整 profile 继续约束其他工程事项；中英文路由测试锁定语义。
- shadow ledger 仅把 TASK-0014 计为第 14 个真实任务；因其直接创建为 active，没有追加虚构转换，累计仍为 29。
- 证据限制不变：预注册和实现同属一个未提交变更集，没有可由 Git DAG 独立验证的先后关系。

Checks run:

- 聚焦 4 tests OK；完整 suite 164 tests OK。
- `python3 scripts/sync-skills.py --check` 与 `git diff --check` 通过。
- self-check 仍为既有 owner 状态的 2 errors / 1 warning；没有声称 0/0。

### 2026-09-19 - Agent: Codex — 最终独立验收

Checks run:

- 四项高风险聚焦测试（legacy 自定义 profile proposal/complete、非 anchored 精确写白名单、双语优先级、profile fresh clone）→ 4/4 OK。
- 全量 `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 164/164 OK。
- `sync-skills.py --check` 与 `git diff --check` 通过。
- 当前 self-check 如实为 2 errors / 1 warning：两项 owner 现场未提交，warning 为本 tracked TASK 尚未 commit；均未被伪装成 0/0。

Review and reflection:

- Round 1 的三个产品 finding（legacy 纳管、写白名单、双载体优先级）及两个记录 finding（无 DAG 证据、真实 TASK 计数）全部闭合，无 open P0/P1/P2。
- R0 完整载体满足 owner 的强制持久化要求；消融只裁决载体，没有把能力本身错误地判为 No-Go。
- Owner 指令“修复然后验收”授权技术验收；因 tracked 任务文件仍未提交，生命周期停在 ready_for_review，避免制造 `TASK_STORAGE_MISMATCH`。commit/push/tag/release 仍未授权且未执行。

### 2026-09-20 - Agent: Codex — 第二轮安全修复终验

Changes made:

- 显式 `PROFILE_LOCALE` 已替代正文标题启发式；中文 canonical/derived byte-equality 与英文语义覆盖测试保持有效。
- legacy profile 的预存 symlink、hardlink、FIFO 与外部内容读取均 fail closed，proposal 不泄漏外部正文。
- managed-file 授权收窄到当前项目实际选择的 profile；未选择的另一受支持 profile 不再因处于合法 namespace 而可被删除。

Checks run:

- profile/upgrade/durability 聚焦测试包含在 58/58 OK；fresh-clone profile core 回归通过。
- 完整 suite 177/177 OK；双语 snapshots in sync；whitespace clean。
- 当前 self-check 仍为 owner 排除现场的 2 errors 与未提交 TASK-0014 的 1 warning，未伪装为 0/0。

Review and reflection:

- P0/P1/P2 全部闭合，技术结论 APPROVE；任务进入 `ready_for_review`。tracked task 与实现仍未提交，因此 accepted gate 保持打开，且未执行 commit/push/tag/release。
