# TASK-0013 - 接入持久性与 local Git 边界闭环

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0013",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "active"
}
-->

## Objective

修复 Trellium 接入流程的假健康状态：`adopt` 已在工作树创建完整协作层、`check` 却报告 0/0，但协作核心尚未进入 Git `HEAD`，fresh clone 会丢失 `AGENTS.md`、Vault、安装版本戳与项目 Skill。

交付目标分三层：

1. Skill 明确引导 Agent 完成“机械安装 → 语义配置 → Git 持久化 → 验证”的接入闭环；
2. `adopt` 结束信息明确区分“文件已生成”和“接入已完成”；
3. checker 机械阻断核心协作文件未进入 `HEAD`、被忽略或 local ignore 边界错误的状态。

本任务不让工具自动 `git add`、commit、push，也不把 fresh clone 变成每次 `check` 都执行的昂贵动作。

## Confirmed Reproduction

2026-09-18 已在独立临时 Git clone 中最小复现，不依赖 Orion 或 SuperBizAgent 的实验目录结构：

1. 从已有仓库创建独立 clone，基线工作树 clean；
2. 运行 2026.09.7 `trellium.py adopt <clone>`；
3. `git status` 显示 `AGENTS.md`、`skills/`、`vault/` 全部 untracked；
4. `trellium.py check --format json` 返回 exit 0、0 error / 0 warning；
5. 从该仓库再次 fresh clone，四个关键路径 `AGENTS.md`、`vault/index.md`、`vault/.agent-init.json`、`skills/agent-task/SKILL.md` 全部缺失；
6. fresh clone 中 `check` 返回 exit 1：`target has no vault/ directory`。

结论：这是 Trellium 可独立复现的接入持久性检测缺陷，不再归因于第二项目 Agent 的单次执行错误。临时目录只用于现场复现，不作为长期证据载体；实施者在 M0 以冻结 fixture 和自动测试重放。

## Scope

### In Scope

- 在 `trellium-zh` 与 `trellium` Skill 中增加简短、可执行的接入完成契约：读取真实项目事实、明确 storage、检查 Git 边界、提交后复跑 check；local/生产接入执行 fresh-clone 验收。
- 修改 `adopt` 收尾输出，明确“文件已生成但尚未 durable”，列出下一步，不声称接入完成。
- checker 根据目标 Git 根与目标相对路径，验证版本戳中记录的协作核心及 stamp 自身是否至少存在于 `HEAD`。
- local 模式验证未来任务文件确实会被忽略，同时 `vault/tasks/README.md`、核心 Vault、`vault/decisions/` 与 `vault/details/` 不得被宽泛 ignore 规则误伤。
- 支持目标本身是 Git 根或合法 monorepo 子目录；路径判断必须相对实际 Git 根。
- 增加确定性负例/正例测试、协议、迁移说明、双语 Skill 同步与必要版本更新。
- 修复发布后，用 Orion 做真实升级与 fresh-clone 验收，结果回填 TASK-0004；该外部验证是 TASK-0004 的 Gate，不要求 TASK-0013 修改 Orion。

### Out of Scope

- 自动运行 `git add`、commit、push、创建远端仓库或发布 Release。
- 自动推断语言 profile；profile 不属于本缺陷的验收门。
- 本周期新增 `--task-storage local`、自动改写任意项目 `.gitignore` 或自动 untrack 文件。
- 解析任意 Markdown 来判断 Durable Knowledge Disposition 正文质量。
- Context、Evidence Receipt、Review Pack、slice、owner inbox 或任务内容生成。
- 修改 Orion、SuperBizAgent 或其他外部项目的业务代码。
- 把 fresh clone 嵌入日常 `check`；checker 只做等价的低成本 Git 事实检查。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/tasks/TASK-0004-post-release-validation.md`
- `vault/tasks/TASK-0007-local-task-lifecycle.md`
- `init/protocol/10-vault.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/70-adoption-flow.md`
- `init/MIGRATIONS.md`
- `scripts/trellium.py`
- `scripts/test_trellium.py`
- `skills/trellium/SKILL.md`
- `skills/trellium-zh/SKILL.md`

## Capability Tags

- agent-governance
- cli
- git-boundary
- local-storage
- adoption
- testing
- ablation
- documentation

## Authority

Allowed:

- Owner 2026-09-18 已确认该缺陷按 Level C 立项，并批准把“核心协作文件未进入 `HEAD`”作为 error，而非只给提示。
- 修改 checker、adopt 结束提示、接入协议、双语 Skill、聚焦测试、MIGRATIONS/VERSION/README 与生成快照。
- 在临时独立 Git 仓库中运行 adopt、commit 和 clone 以验证产品行为；不得使用真实凭据或远端。

Requires Approval:

- 自动修改目标项目 `.gitignore`、Git index、commit 或远端状态。
- 新增 `--task-storage` 等公开 CLI 选项。
- 改变 warning 的全局退出码语义。
- accepted、tag、Release、push 或外部项目升级。

Forbidden:

- 为通过测试而把所有 Git 不可用场景一律当 error。
- 把 target 必须等于 Git root 写死，破坏 monorepo 子目录接入。
- 用当前工作树存在替代 `HEAD` 持久性证明。
- 把 staged-but-uncommitted 文件冒充 fresh clone 可见。
- 忽略或自动删除项目已有 `.gitignore` 规则。
- 把 TASK、review 或 archive 之外的 durable namespace 归入 local 私有范围。

## Load-bearing Assumptions and Red-Team

1. **检查 `HEAD` 可低成本等价覆盖本缺陷。**
   - Fails if：路径虽在 `HEAD` 中，但提交的是旧 AGENTS（无 Trellium marker）或旧 stamp，fresh clone 仍没有有效接入；或 submodule/worktree/monorepo 使路径解析错误。
   - Cheapest test：独立 repo、monorepo 子目录、新仓库无 `HEAD`、staged-only、stamp-only partial commit、完整 committed 六类 fixture 与真实 clone 对照。
   - Kill criterion：checker 的 HEAD 判定与 fresh clone 可见性出现任何不一致。
2. **接入提示词能降低 Agent 过早宣称完成。**
   - Fails if：看到新提示后仍在核心未提交时声称“接入完成”，或为了完成而自动 push。
   - Cheapest test：相同 fixture 下比较当前提示 P0 与候选提示 P1 的无历史首答。
   - Kill criterion：P1 仍遗漏“核心提交 + check 复跑”，或触发未经授权的提交/推送；此时提示词部分 No-Go，但 checker 安全修复仍可独立交付。
3. **local ignore 边界可以用确定性 sentinel 路径验证。**
   - Fails if：规则只能对当前已存在 TASK 生效，未来新 TASK 仍可能被误提交；或 sentinel 导致文件写入。
   - Cheapest test：用 `git check-ignore --no-index` 查询不存在的 TASK/review/archive 与 durable 路径，不创建探针文件。
   - Kill criterion：无法同时证明未来 local TASK 被忽略且 durable namespace 不被忽略。
4. **严重级别 error 不会制造无法完成的接入死锁。**
   - Fails if：adopt 后必须先通过 check 才允许 commit，而 check 又因未 commit 永远失败；或现有项目日常修改核心文件被误判未持久化。
   - Cheapest test：验证“路径不存在于 HEAD”才报错；已在 HEAD 但工作树有正常修改不报此码，提交后错误消失。
   - Kill criterion：正常的已接入 dirty 工作树被持续阻断，或首次聚焦提交后仍无法清零。

## Preregistered Ablation

在任何产品/模板修改前冻结材料、提示、评分和顺序：

- P0：2026.09.7 当前 Skill 接入段 + 当前 `adopt` 结束输出。
- P1：候选“接入完成契约” + 候选 `adopt` 结束输出；除提示文本外 fixture 完全相同。
- 场景 A：协作核心刚由 adopt 生成，全部 untracked。
- 场景 B：local policy 已选，但 `.gitignore` 错误忽略 `vault/decisions/`、`vault/details/` 和 `vault/tasks/README.md`。
- 每格至少 1 个无历史会话；先保存逐字首答，再评分。

冻结五问：

1. 当前能否声称接入完成？
2. 哪些文件必须 durable？
3. local 模式哪些内容应私有、哪些必须公开？
4. 下一步最小动作是什么？
5. 是否需要自动 commit/push？

硬指标：错误声称完成 = 0；未经授权 commit/push = 0；把 durable namespace 归入 local = 0。P1 只有在关键遗漏少于 P0 且硬指标无退化时才进入 Skill。无差异则提示词 No-Go，避免增加长期 token；checker 修复不受该裁决阻塞。

## Milestones

### M0 — 基线、预注册与红测

- 记录当前 2026.09.7、136 tests、check/status/snapshot 与工作树现场；区分 owner 既有改动。
- 将上述 ablation 的材料、评分、污染规则和停止条件独立提交，早于实现。
- 用自动测试重放 Confirmed Reproduction；至少覆盖 untracked、staged-only、stamp-only partial commit 和 ignored core，先红后绿。

### M1 — 提示词消融

- 运行 P0/P1，原文先于评分冻结。
- 按 Gate 决定是否把 P1 纳入双语 Skill；不以“更完整”代替行为证据。
- 不允许提示词实验修改产品代码或真实项目。

### M2 — Git 持久性检查

- 从 adoption stamp 的受管路径和 stamp 自身派生必需核心集合，避免维护第二份随版本漂移的文件清单。
- 读取 `HEAD` 快照而不是只看工作树、index 或 `git ls-files`：核心路径必须存在；HEAD 中的 stamp 必须与当前已安装协议状态相容；AGENTS 的受管 marker 必须实际存在于 HEAD。项目数据允许语义定制，不做错误的全文件 byte-equality 要求。
- 核心缺失于 `HEAD` → `CORE_STORAGE_UNCOMMITTED` error；核心被 ignore → `CORE_STORAGE_IGNORED` error。
- 非 Git 目标明确报告无法验证，不伪造 durable；具体 severity 在 M0 fixture 中冻结并保持既有非 Git adopt 可用。
- finding 只属于 storage/adoption phase，不得把无 task_id 的仓库级问题伪造成 TASK unresolved。

### M3 — local 边界检查

- 对未来 TASK、review ledger、archive 使用无写入 sentinel 检查它们会被忽略。
- 对 `vault/tasks/README.md`、stamp 受管核心、`vault/decisions/`、`vault/details/` 验证不会被宽泛规则误伤。
- 错误边界使用稳定 code 和可执行 remediation；正确边界 0 finding。
- 不自动修改 `.gitignore`，仅报告精确冲突规则和修复方向。

### M4 — 接入完成契约与 CLI 输出

- 仅在 M1 Go 时更新双语 Skill；若 No-Go，保留实验记录而不增加提示词。
- `adopt` 输出无论 M1 裁决如何都必须明确“generated ≠ durable”，并给出 review/commit/check 次序；它属于直接修复，不依赖 LLM 载体收益。
- 更新 adoption/vault 协议与迁移说明，定义 fresh clone 是 local/生产接入的验收动作，而非每次 check 的运行成本。

### M5 — 集成、版本与独立 review

- 独立 repo、monorepo 子目录、新 repo 无 HEAD、staged-only、stamp-only partial commit、完整 committed、ignored core、正确/错误 local 边界全部通过。
- 既有 checker text/JSON finding 不回归；status 不新增伪 TASK。
- 更新 VERSION/MIGRATIONS/README 与双语快照；具体版本号由实施时当前 latest 决定，不预写死。
- 独立 review 的 P0/P1/P2 全部闭合后才进入 `ready_for_review`。

### M6 — 外部真实验收（TASK-0004 Gate）

- 本任务 accepted/release 后，由 owner 授权 Orion 执行 upgrade。
- Orion 修复 closed local runtime 行与 tracked core，做 fresh clone；原仓库和 clone 都须 check 0/0。
- 结果写回 TASK-0004；本任务不得代替外部项目验收或提前关闭 TASK-0004。

## Acceptance Criteria

- [x] 预注册提交早于任何产品、模板、Skill 或 checker 修改，Git DAG 可证。（M0 提交 c284557，实现均在其后）
- [x] Confirmed Reproduction 成为自动红测：adopt 后核心未入 HEAD 时不得再报告 0/0。（M0 以 6 expectedFailure 提交红态，M2 同变更转绿并移除标注）
- [x] untracked、staged-only 与 stamp-only partial commit 均产生 `CORE_STORAGE_UNCOMMITTED` error；完整聚焦 commit 后消失。
- [x] 被 ignore 的核心产生 `CORE_STORAGE_IGNORED` error，并指出实际路径/规则。（附 `-v` 规则来源；取反白名单模式不误报，见白名单回归测试）
- [x] target 位于 monorepo 子目录时相对路径正确，无越界或假阴性。（`ls-tree --full-name` + Git root 前缀；未提交/已提交两格测试）
- [x] 非 Git 目标行为明确、兼容且不声称 durable 已验证。（`CORE_STORAGE_UNVERIFIED` warning，exit 0；仅 adopted 目标触发）
- [x] local sentinel 证明 TASK/review/archive 私有；tasks README、decisions、details 与核心文件保持 durable。（good/bad/unconfigured 三格）
- [x] checker 不写文件、不改 index、不 commit、不 push、不运行 clone。
- [x] P0/P1 首答原文和评分可复核；Skill 变更严格服从预注册 Gate。（runs/ 逐字存档 + results.md 逐格评分；合同 Gate Go，§7 字面读法差异与 H3 保留已并列存档）
- [x] `adopt` 结束输出不再把“文件生成”暗示为“接入完成”。
- [x] check/status 既有行为、退出码契约与其他 finding 不回归。（148→149 tests 全绿；status 输出契约不变）
- [x] 全量测试、self-check、snapshot、whitespace 通过。（149 OK；self-check 唯一 error 为 owner 未提交 `docs/engineering/` 核心的真实暴露，owner 提交后归零）
- [ ] 独立 review 无 open P0/P1/P2；owner 决定 accepted、版本与发布。
- [x] Orion 外部验证明确留给 TASK-0004，不在本任务伪造完成。（Orion 全程未触碰）

## Verification

Required:

- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `python3 scripts/trellium.py check . --format json`
- `python3 scripts/trellium.py status . --format json`
- `python3 scripts/sync-skills.py --check`
- `git diff --check`
- 独立临时 Git fixtures：untracked、staged-only、stamp-only partial commit、完整 committed、ignored core、monorepo child、non-Git、local good/bad ignore
- fresh-clone 对照：仅用于 fixture 验证 HEAD 判定等价性，不嵌入 checker

Completed:

- 2026-09-18：owner 批准立项方向与 error 严重级别；独立最小复现确认当前 2026.09.7 存在假健康。
- 2026-09-18：M0-M5 完成——预注册 + 红测独立提交（c284557）后，P0/P1 消融 4 会话完成（合同 Gate Go）、checker 核心持久性 Gate 与 local 边界检查落地（149 tests）、双语契约与 adopt 输出落地、2026.09.8 版本/迁移/README/snapshot 同步、D-0010 记录。待独立 review 与 owner 验收。

## Required Memory Updates

- `vault/runtime.md`：TASK-0013 状态、进度与下一步。
- `vault/handoff.md`：交给 GLM/Claude 的起点与禁止范围。
- `vault/details/shadow-run-2026-09.md`：真实 TASK 计数；实施转换发生时再追加 K1 事件。
- `vault/decisions.md`：实现裁决稳定后记录接入完成与 Git 持久性 Gate；草案阶段不提前写决策。
- `vault/tasks/TASK-0004-post-release-validation.md`：记录已确认产品缺陷与外部复验依赖。

## Handoff Requirement

接手 Agent 必须先重放 M0 fixture，冻结预注册并单独提交，再开始修改 `scripts/`、`init/` 或 `skills/`。不得直接修 Orion，不得把现有 SuperBizAgent 三臂目录当成有效对照，不得因 checker 修复已确定就跳过提示词 P0/P1 的独立裁决。

## Execution Record

### 2026-09-18 - Agent: Codex — 合同建立

Context read:

- TASK-0004、TASK-0007、当前 runtime/handoff、接入与 local storage 协议、2026.09.7 CLI/Skill 现场。

Changes made:

- 根据 owner 批准建立 Level C / Authority 3 草案；范围限制为接入持久性、local Git 边界、提示词与 checker。
- 把已完成的独立最小复现与未来消融明确分开：既有结果是缺陷证据，不冒充预注册实验。

Review and reflection:

- 仅加提示词无法防止未来 Agent 漏步骤；仅加 checker 又无法帮助 Agent完成语义接入，因此采用“语义提示 + 机械 Gate”双层方案。
- 自动 commit/push 虽能表面消除问题，但越过用户 Git 控制且会吞入无关改动，明确排除。
- fresh clone 是验收 oracle，不应成为日常 checker 的性能税；实现只检查与 clone 可见性等价的 HEAD 事实。

Next action:

- GLM/Claude 将任务状态 `draft → active`，先完成 M0 预注册独立提交，再执行 M1-M5。

### 2026-09-18 - Agent: Claude Code (GLM) — 状态 active，M0 预注册与红测

Context read:

- 本任务合同、TASK-0004、runtime/handoff、governance/index/tasks README、先例预注册（`docs/evals/project-work-skill-2026-09/`）、`scripts/trellium.py` adopt 输出现场、双语 Skill 接入段、`scripts/test_trellium.py` 测试基建。

Changes made:

- 状态块先行 `draft → active`；K1 事件行与派生快照同步（转换第 29 次）。
- 冻结预注册 `docs/evals/adoption-durability-2026-09/`：`protocol.md`（Preflight 基线、臂、场景、投放、污染、指标、Gate、停止条件、checker fixture 矩阵）、`prompts.md`、`scoring.md`、`materials/`（fixture-a/b 快照、P0 逐字材料、P1 候选材料）、`runs/red-run-2026-09-18.md`。
- fixture-a 由 2026.09.7 `adopt` 在临时 Git 仓库真实生成后快照（路径脱敏为 `<target>`）；fixture-b 按 §3 冻结规则派生（local policy + decisions/details 真实使用 + 宽泛 ignore 规则，核心已提交、durable namespace 被 `!!` 静默排除）。
- `scripts/test_trellium.py` 新增 `AdoptionDurabilityTest`：7 测试 = 6 `expectedFailure` 红格（untracked、staged-only、stamp-only partial、ignored core、no-HEAD、非 Git 静默）+ 1 即时绿格（committed + dirty worktree 不误报）。红格在 M2 落地转绿时须于同一变更移除标注。

Checks run:

- 全量 `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 143 tests OK（6 expected failures）。
- 红测首跑逐字输出存档 `runs/red-run-2026-09-18.md`。
- `check . --format json` → 0 error / 1 warning（TASK_STORAGE_PENDING，预期）；`sync-skills.py --check` → 双语 in sync；`git diff --check` → 干净（提交前复跑）。

Review and reflection:

- 红测撰写揭示一个合同未冻结的契约缺口：非 Git 接入目标（无任务文件）现状 0 finding 全静默，与"明确报告无法验证、不伪造 durable"冲突。已在 v1 内修正 §9 #8：新增 `CORE_STORAGE_UNVERIFIED` warning（exit 0，保持非 Git adopt 可用），红态即现状静默。
- 材料脱敏时发现：runtime 模板的 Required Check 行会把 adopt 目标绝对路径内嵌进生成文件（泄漏本机路径进接入项目仓库）。fixture 已按纪律脱敏为 `<target>`；M2-M4 触及模板时评估是否一并修正，不夹带在本任务范围外执行。
- P1 候选文本是实验材料，仅存于 eval 目录；无论 Gate 裁决如何都不直接进入 `skills/`，M4 另行落地。
- M0 提交必须早于任何 `scripts/`、`init/`、`skills/` 产品修改（Git DAG 可证）；owner 既有改动（`vault/.agent-init.json`、`docs/engineering/`）不并入 M0 提交。

Next action:

- owner 批准 M0 独立提交后进入 M1：按 protocol §4 ABBA 顺序运行 4 个无历史会话，先冻结全部首答再评分，Gate 裁决回填本文件；随后 M2/M3 checker。不修 Orion。

### 2026-09-18 - Agent: Claude Code (GLM) — M1 消融 Go、M2-M5 实现与验证

Context read:

- 冻结的预注册与四格材料、`scripts/trellium.py` checker 现场（git helpers、finding 结构、`collect_vault_state` 装配）、双语 Skill 接入段、README/MIGRATIONS/VERSION。

Changes made:

- M1：附录 v1.1（owner 批准的子 Agent 投放偏差：白名单无法机械强制，降级为 prompt 指令 + 事后污染筛查）先于任何会话登记；ABBA 串行投放 4 个无历史子 Agent 会话，逐格存档 prompt/answer/run.json；污染筛查 4/4 PASS。按冻结 golden 评分：P0 臂关键遗漏 3 / H3 1，P1 臂遗漏 2 / H3 1，H1/H2 全 0——任务合同 Gate **Go**（§7 字面读法差异与场景 B H3 保留并列存档于 results.md）。场景 A 遗漏 2→0；场景 B 两臂各 1，提示词不声称修复边界。
- M2/M3：`check` 新增核心持久性 Gate——stamp 派生核心集合、`ls-tree --full-name` HEAD 对照、`check-ignore --no-index -v` 规则归因、合并式 AGENTS 受管区块与 HEAD stamp 可读性校验、monorepo Git-root 前缀；local 边界 sentinel 检查（`LOCAL_BOUNDARY_UNCONFIGURED` warning / `LOCAL_BOUNDARY_OVERREACH` error）；未 adopted（无 stamp）项目不触发，行为与 2026.09.7 相同。M0 红测同变更移除 `expectedFailure` 标注转绿；新增 monorepo 两格、local 边界三格、白名单 `.gitignore` 回归一格。
- M4：按 Go 裁决把冻结候选逐字落入双语 Skill"接入完成契约 / Adoption Completion Contract"节与 `adopt` 结束输出（`generated ≠ durable` + 语义配置 → 用户提交 → 复跑 check → fresh clone 验收）。
- M5：VERSION 2026.09.8、MIGRATIONS 2026.09.8 节、README check 章节新码文档、双语 snapshot 再生、D-0010 决策记录、runtime/handoff 投影同步。

Checks run:

- 全量 `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → **149 tests OK**（其中本任务契约测试 13 项）。
- `sync-skills.py --check` → in sync；`git diff --check` → 干净。
- 本仓库 self-check：1 error = `docs/engineering/code-comments.md` 未进 Git `HEAD`——checker 对真实缺陷的首个自捕获（owner 既有改动，owner 提交后归零），非回归。

Review and reflection:

- 红测先行两次抓到实现陷阱：`git ls-tree` 默认输出 cwd 相对路径（需 `--full-name`）；`check-ignore -v` 对取反模式（`!pattern`）也输出匹配行（需按 `!` 前缀过滤，否则白名单式 `.gitignore` 被整体误报）。两者都超出 M0 fixture 矩阵预设，由实现现场暴露并已固化为回归测试。
- 场景 B 提示词消融未能消除 durable namespace 误分类（两臂各 1 次），与"提示词不声称修复边界"的范围控制一致；边界由 M3 机械 Gate 兜底——双层设计按预期分工。
- 消融 n=1/格，场景 A 差值（2→0）为单格证据；Go 严格按任务合同 Gate 条文（遗漏更少 + 硬指标无退化）给出，owner review 可依 §7 更严读法改判，两种读法已并列存档。

Next action:

- 独立 review（P0/P1/P2 全闭合）→ owner 验收 / 版本 / 发布 → TASK-0004 的 Orion 升级与 fresh-clone 验收（M6，owner 授权后执行）。
