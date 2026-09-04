# Agent-Native Vault 最小状态层与确定性检查器执行方案

> 面向 Claude 的实施任务书。严格按 M1 → M2 → M3 执行；前一里程碑验收未通过，不得开始下一里程碑。M3 完成后停止，不自动进入后续路线图。

- 日期：2026-09-04
- 状态：Ready for implementation after red-team and ablation
- 反馈来源：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md`
- 当前协议版本：`2026.09.1`
- 实施级别：Level C（Agent 治理和公开 CLI 行为变更）

## 1. 交付目标

第一周期只交付两项生产能力：

1. Level B/C TASK 顶部有一个带版本的 `trellium-task-state` JSON 状态块，成为 lifecycle、当前 slice 和 Gate 结果的唯一 owner；
2. 现有 `trellium.py` 增加完全只读、确定性、标准库实现的 `check` 子命令。

同时修订协议，使以下边界不再含混：

- Level A 与 Level B/C 的状态 owner；
- TASK 与 runtime 的两套状态词汇；
- 项目预算的唯一配置来源；
- TASK tracked/local 策略；
- handoff 中持久叙事与实时 Git 事实的边界。

第一周期不承诺解决上下文自动组装、evidence freshness 或 runtime 自动生成。

## 2. Red-team：必须先验证的承重假设

以下按“错误影响 × 出错可能性 × 测试便宜程度”排序。

### K1 — 状态块确实比纯 Markdown 更少漂移

- **Claim：** 一个小型状态块能减少 Agent 重复推导和复合状态歧义。
- **Steelman：** 深度使用反馈已给出 TASK/runtime/handoff 多处重复及多 slice 复合状态的真实案例；严格 JSON 又能用标准库校验。
- **Fails if：** 实际状态变化仍需手工修改多个 owner，或 Agent 经常忘记更新状态块，使它比现有 Status 段更不可信。
- **本周证据：** 在两个真实项目 shadow 记录至少 10 次状态变化，比较修改位置数量和漂移次数。
- **Kill criterion：** 状态块引入后仍平均需要编辑两个以上权威位置，或漂移率不低于当前 prose 基线。
- **Cheapest test：** M2 完成后只给新建/重新激活 TASK 添加状态块，runtime 仍人工投影，由 checker 报漂移；不迁移历史。

### K2 — 一个项目级 tracked/local 策略足够表达现实

- **Claim：** TASK storage 可以用一个项目级枚举表达，不需要逐任务配置。
- **Steelman：** 反馈中的主要错误来自同一路径一部分 tracked、一部分 ignored；全局规则最容易机械验证。
- **Fails if：** 同一项目持续存在合理且不可消除的 tracked/local 混合需求。
- **本周证据：** 检查至少一个 tracked-TASK 项目和反馈来源的 local-TASK 项目，列出所有合法例外。
- **Kill criterion：** 任一项目需要长期保留一个以上逐任务例外。
- **Cheapest test：** 只实现 `tracked | local`；遇到合法例外时停止，不添加 `hybrid`、glob DSL 或逐任务开关。

### K3 — 不解析任意 Markdown 也能产生高价值检查

- **Claim：** 仅检查结构块、runtime TASK 行、预算和 Git storage，已经能捕获主要机械错误。
- **Steelman：** 反馈中的最高优先问题正是状态漂移、预算失真和 local-only 误跟踪；都不需要语义理解。
- **Fails if：** shadow 使用中所有真实错误都来自自由文本引用/契约语义，而最小 checker 没有捕获任何问题。
- **本周证据：** 在两个真实 Vault 上只读运行，记录 error/warning 是否对应真实修复动作。
- **Kill criterion：** 连续两次真实检查只有无行动价值的 warning，且遗漏已知的状态/storage/预算错误。
- **Cheapest test：** 第一版明确不解析 `Context Required`、canonical contract 或任意 Markdown 链接；这些等 context compiler 有真实需求再做。

### K4 — checker 应先于 context compiler

- **Claim：** 先证明权威状态可稳定解析，再做上下文编译，能降低错误放大风险。
- **Steelman：** context compiler 若读取不稳定 schema，会把一次人工歧义变成稳定的错误输出。
- **Fails if：** checker 的结构约束没有改善任何读取判断，而用户成本主要来自上下文选择，不是状态错误。
- **本周证据：** shadow 记录 checker 发现数、状态判断耗时和 owner 需要手工打开的文件数。
- **Kill criterion：** 状态准确率已接近 100%，checker 零有效发现，但上下文读取成本仍明显高。
- **Cheapest test：** 只完成本周期；达到 kill criterion 时不继续扩 checker，直接重新评估最小 context manifest。

### Red-team 后仍成立的判断

- 标准库、默认只读、确定性、无网络依赖是正确边界；它们直接保障可移植性和可审查性。
- legacy 必须明确 `unresolved`，不能启发式补齐授权。
- runtime 自动生成必须晚于 schema 稳定，否则只是把漂移自动化。
- 用户批准、Accepted 和真实环境证据不能由 checker 推导。

### 当前无法判断

- 只有一个深度使用项目的量化数据，无法证明其 TASK 数量、Gates 或 local-only 偏好代表全部 Trellium 用户。
- 尚无两个真实项目的 shadow 数据，因此 byte 阈值、context compiler 收益和 evidence freshness 优先级都不能冻结。

## 3. 消融结果

统一问题：删除候选后，本周期是否仍能捕获状态漂移、预算失真或 TASK storage 违规？

| Candidate | 删除后的影响 | 结论 |
| --- | --- | --- |
| `trellium-task-state` 小状态块 | lifecycle 仍需从 prose 猜测 | 保留 |
| `trellium-policy` 项目策略块 | 预算/storage 继续多源 | 保留 |
| `trellium.py check` | 无法机械发现漂移 | 保留 |
| `--format json` | 难以做稳定测试和后续工具复用 | 保留 |
| `current_slice` 可选字符串 | 多阶段任务当前状态仍含混 | 保留，但不保存历史数组 |
| 可选 `gates` map | 已观察到的 `not_authorized/partial` 等边界会退回 prose | 保留，但不规定 Gate ID、不建立全局 Gate 本体 |
| `slices[]` 历史状态数组 | 当前 slice 仍可由单字段表达 | 删除；需要时升 schema |
| `canonical_contract` 结构字段 | TASK 自身仍是当前契约 owner | 删除；等 context compiler |
| `updated_at` | Git/执行记录仍保存历史；checker 不依赖日期 | 删除 |
| 任意 Markdown/`Context Required` 引用解析 | 核心三类错误仍可检查 | 删除；等 context compiler |
| `max_line_bytes` 配置 | 仍可报告最大单行值 | 删除；只保留 measurement |
| 独立 testdata fixture 目录 | unittest 临时项目仍能覆盖行为 | 删除 |
| 独立 M0 基线里程碑 | preflight 足以保护基线 | 删除 |
| 第一周期 LLM 冷启动 eval | 静态 checker 仍可验收 | 延后到 context 周期 |
| fact type 系统 | 路径和 owner 已足够支撑 checker | 延后 |
| evidence receipt/inbox/review pack | 不影响 checker 正确性 | 延后 |
| RAG/数据库/daemon/锁/权限 DSL | 不解决当前机械漂移 | 禁止进入本周期 |

消融后，第一周期只剩：

```text
一个 TASK 状态块
+ 一个项目 policy 块
+ 一个只读 check 命令
```

## 4. 冻结后的最小设计

### 4.1 当前事实 owner

| 事实 | 唯一 owner | 其他位置 |
| --- | --- | --- |
| Level A 当前状态 | `vault/runtime.md` inline 记录 | 无 TASK 文件 |
| Level B/C lifecycle、current slice、Gate 结果 | TASK 的 `trellium-task-state` 块 | runtime 是 derived projection |
| Level B/C 当前契约 | TASK 顶部 Objective/Scope/Authority/Acceptance 等 current-contract 段 | Execution Record 只存 journal |
| 当前 Focus | `vault/runtime.md` | 只表示注意力，不等于 lifecycle |
| 长期事实 | `project.md`、Active decision 或明确权威文档 | TASK 可记录实施来源 |
| 中断原因和下一动作 | `handoff.md` | 不保存实时 Git 状态为权威 |
| branch、HEAD、dirty files | 实时 Git | handoff 只能保存带时间的历史 snapshot |
| 项目 Vault 策略和预算 | `vault/index.md` 的 `trellium-policy` 块 | 其他文件只路由，不复制当前值 |

`index.md` 的职责改为“路由 + 项目策略，不保存运行态”。

### 4.2 TASK state block v1

固定标记：`trellium-task-state`。放在 TASK 标题之后、叙事正文之前。严格 JSON，不支持 YAML、注释或尾逗号。

```html
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0060",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review",
  "current_slice": "A4",
  "gates": {
    "review": "passed",
    "live": "not_authorized"
  }
}
-->
```

字段规则：

- 必填字段只有：`schema_version`、`task_id`、`level`、`authority_level`、`lifecycle`。
- `schema_version` 只接受整数 `1`。
- `task_id` 匹配 `TASK-[0-9]{4,}`，且与文件名开头一致。
- `level` 只允许 `B | C`。
- `authority_level` 只允许整数 `0..4`；Python `bool` 必须拒绝。
- `lifecycle` 只允许：`draft | active | blocked | ready_for_review | accepted | superseded`。
- `current_slice` 可选，为非空字符串；存在时 lifecycle/Gates 描述当前 slice，而非整个历史容器。
- `gates` 可选；Gate ID 为非空字符串，不固定 G0-G4。
- Gate 值只允许：`pending | in_progress | passed | partial | blocked | not_authorized | not_applicable`。
- v1 未定义字段报错；改变字段含义必须提升 `schema_version`。
- 当前任务实体恰好零或一个状态块：零个是 legacy warning，多个是 error。
- `TASK-*-review.md` 是 ledger，不是任务实体；`vault/tasks/archive/` 是冷历史。两者不要求状态块，也不进入 runtime/active-task 检查。
- 状态块不能授予批准。Allowed、Requires Approval、Forbidden 和验收条件仍由 TASK 正文与用户指令决定。

新模板删除独立可编辑的 `## Status` 和 Authority `Level:` 副本。人类直接读取状态块；Authority 正文只保留 Allowed、Requires Approval、Forbidden。

### 4.3 Project policy block v1

固定标记：`trellium-policy`。放在 `vault/index.md` 开头说明之后。

```html
<!-- trellium-policy
{
  "schema_version": 1,
  "task_storage": "tracked",
  "budgets": {
    "runtime": {"max_lines": 120, "max_recent_entries": 10},
    "handoff": {"max_lines": 100, "max_entries": 3},
    "decisions": {"max_lines": 150, "max_records": 8},
    "parked": {"max_lines": 60, "max_entries": 20},
    "tasks": {"max_active_tasks": 40}
  }
}
-->
```

规则：

- 必填字段只有 `schema_version` 和 `task_storage`；`budgets` 可选。
- `schema_version` 只接受整数 `1`；未知字段报错。
- `task_storage` 只允许 `tracked | local`。
- 新接入项目默认 `tracked`，保持现有行为。
- 既有项目不得自动选择 storage；迁移时由 owner 根据已有治理确认。
- 所有预算是可选正整数；对象或键缺失表示“不设该上限”，不是使用脚本默认。
- checker 总是报告 lines、UTF-8 bytes、最大单行 UTF-8 bytes；最大单行只测量，不设 v1 配置键。不承诺未来 `max_bytes` 配置键；只有真实观察到“大文件导致 Agent 定位失败”才考虑引入。
- 缺少 policy 的旧项目产生 `POLICY_MISSING` warning；checker 不用硬编码默认冒充项目策略。
- agent-task 只要求读取 policy，不复制预算数字。

### 4.4 TASK storage

`local`：

- `vault/tasks/TASK-*.md`、`vault/tasks/archive/TASK-*.md` 和 TASK review ledger 不得 tracked 或 staged；违反即 error。
- `vault/tasks/README.md`、占位文件和非 TASK 文档不受影响。

`tracked`：

- 被 ignore 的 TASK 是 error；
- `accepted/superseded` TASK 未 tracked 是 error；
- archive TASK 未 tracked 是 error；
- 其他 lifecycle 未 tracked 是 warning，允许任务创建后的正常未提交窗口。

非 Git 项目或 Git 不可用时，storage 检查标为 skipped warning，不声称 PASS。checker 不修改 `.gitignore`，不运行任何 Git 写命令。

### 4.5 `check` CLI

```bash
python3 scripts/trellium.py check <target>
python3 scripts/trellium.py check <target> --format json
```

- target 默认 `.`；format 只允许 `text | json`，默认 text。
- 不创建独立 `vaultctl`，不向目标项目安装新脚本。
- `check` 不支持 `--fetch` 或 `--templates`。
- `ERROR`：结构非法、状态冲突或明确违反 policy；退出 `2`。
- `WARNING`：legacy/unresolved、Git 不可用、active TASK 尚未 tracked；不改变退出码。
- operational/argument error 退出 `1`。
- 无 ERROR 退出 `0`，但 summary 必须显示 warning，不能显示为无条件 PASS。
- JSON 顶层：`schema_version`、`target`、`summary`、`findings`、`measurements`。
- finding：`code`、`severity`、`path`、`message`，可选 `task_id`。
- text/JSON 使用同一内部结果模型和检查逻辑。

### 4.6 第一版检查范围

固定按以下顺序执行和排序：

1. target 和 Trellium 必需文件；
2. policy block；
3. TASK discovery 和 state block；
4. runtime 中 `TASK-` 行的 lifecycle 投影；
5. hot-file budgets 和 measurements；
6. Git task storage；
7. summary。

第一版不解析任意 Markdown 链接、`Context Required`、外部 contract pointer 或自然语言授权。

runtime 规则：

- 只校验 Task 列以 `TASK-` 开头的行；Level A inline 行不要求 TASK 文件。
- runtime TASK 状态使用 canonical lifecycle。
- runtime 指向不存在 TASK 是 error。
- legacy TASK 对应行是 unresolved warning，不猜 lifecycle。
- objective 和 next action是人类摘要，第一版不比较文本。
- task discovery 只把 `vault/tasks/` 直属的 `TASK-*.md`（排除 `TASK-*-review.md`）视为当前任务实体；archive 只参与 storage 检查。

budget 规则：

- 总是测量 runtime/handoff/decisions/parked 的 lines、UTF-8 bytes、最大单行 UTF-8 bytes 及可解析 entries/records。
- 只对 policy 中显式存在的阈值报超限。
- `max_active_tasks` 只计算当前任务实体，并排除 `accepted/superseded` TASK。
- legacy TASK 单列计数；无法确定 active 总数时 warning，不猜状态。

Git 规则：

- 参数数组调用 Git，禁止 `shell=True`，优先使用 `-z` 处理空格和 Unicode。
- target 位于更大 worktree 子目录时，只统计 target 内 pathspec。
- 不运行 `git add/rm/update-index/commit` 等写命令。

## 5. 全局约束

- Python 3 标准库；不新增依赖、服务、网络访问或遥测。
- `check` 完全只读：不得创建 cache、stamp、proposal、临时文件或修复目标内容。
- 不执行 Markdown、TASK 或 policy 中出现的命令。
- discovery 不跟随 target 外 symlink；符号链接 Vault/TASK 输入直接形成 error。
- 不输出目标文件全文、凭据、请求体、响应体或历史 stdout。
- 保持 `adopt/baseline/diff/upgrade` 行为和退出码兼容。
- 中文 `init/` 是协议权威；英文和中文 Skill 模板语义一致。
- `references/protocol-source/` 只通过 `scripts/sync-skills.py` 生成。
- 不批量迁移历史 TASK，不自动修改 protected project data。
- 不覆盖用户 worktree 改动；每个里程碑前后检查 `git status --short`。

## 6. Preflight（不单独提交）

Claude 开始前必须运行并记录：

```bash
git status --short
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
```

当前基线为 49 tests PASS。若执行时基线失败或出现不属于本计划的 dirty files，停止并报告；不得通过修改旧测试掩盖问题。

## 7. 开发顺序

### M1 — 收敛协议与模板

#### 修改范围

- `init/protocol/10-vault.md`
- `init/protocol/15-vault-compaction.md`
- `init/protocol/20-governance.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/80-execution-patterns.md`（仅在现有执行规则确需同步时）
- `init/MIGRATIONS.md`
- 英/中两套 `assets/templates/vault/{index,runtime,governance,handoff,tasks/README}.md`
- 英/中两套 `assets/templates/skills/agent-task/SKILL.md`
- 英/中两套 `references/{protocol-model,templates-guide}.md`
- 运行 sync 生成两套 `references/protocol-source/`
- 本阶段不改 `init/VERSION`。

#### 顺序

1. 在协议源写入 §4 owner、lifecycle、state/policy 和 legacy 规则。
2. runtime 的 TASK 行改用 canonical lifecycle，移除 `paused/waiting-review` 作为 TASK 状态；暂停事项进入 parked。
3. handoff 去掉 branch/dirty files 必填项，改为可选、带观察时间、明确非权威的 snapshot；每个 handoff entry 自带 Files To Read First。
4. index 模板加入唯一 policy block；人类说明只引用该 block，不建立第二配置面。
5. task 模板加入 state block，删除独立 Status/Authority Level 副本；current-contract 段在 Execution Record 前。
6. agent-task 删除具体预算数字，只要求读取 policy；缺失时报告 legacy。
7. MIGRATIONS 明确：历史 TASK 不批量迁移；新建/重新激活时加状态块；runtime/handoff 是 protected data；storage 由 owner 决定；不自动 untrack。
8. 同步两种语言和协议快照。

#### 验收 M1

- [ ] 一个 lifecycle 枚举贯穿协议、runtime TASK 行和任务模板。
- [ ] lifecycle/authority level 没有第二个可编辑字段。
- [ ] 项目当前预算只由 policy block 拥有；agent-task 无数字副本。
- [ ] state v1 只有五个必填字段，slice/Gates 只做可选当前状态，不含历史数组。
- [ ] 通用模板没有固定 G0-G4，也没有 local-only 全局默认。
- [ ] handoff 不把动态 Git 事实当权威。
- [ ] legacy 行为 fail-closed，不推断批准或状态。
- [ ] runtime/handoff/decisions/project/collaboration 的 upgrader data role 未改变。
- [ ] 中英文模板与协议快照一致。

#### 必跑检查

```bash
python3 scripts/sync-skills.py
python3 scripts/sync-skills.py --check
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
git diff --check
```

M1 独立 review 无 open finding 后提交，再进入 M2。

### M2 — Test-first 实现最小 `check`

#### 修改范围

- `scripts/trellium.py`
- `scripts/test_trellium.py`
- 运行 sync 更新两套 `assets/trellium.py`
- 不创建持久 fixture 目录；测试使用现有 `TemporaryDirectory` 风格构建最小项目。

#### 实施顺序

1. 先为 state/policy 合法、legacy、malformed 和重复 marker 写失败测试。
2. 实现严格 JSON parser：字段类型、未知字段、枚举、TASK ID/文件名一致性；特别拒绝 `authority_level=true`。
3. 建立一个最小结果模型供 text/JSON 共用；不建立通用 rule engine、visitor、plugin registry 或 schema DSL。
4. 先写 runtime 投影失败测试，再实现只解析固定 Active Tasks 表的最小逻辑。
5. 先写 line/byte/entry 预算测试，再实现 measurements 和显式阈值判断。
6. 先写临时 Git 仓库测试，再实现 tracked/local 检查；覆盖 staged、ignored、空格和 Unicode 文件名。
7. 接入 CLI、排序、退出码和 renderer。
8. 在 repo layout 与英/中 embedded Skill layout 运行相同端到端用例。

#### 最小 finding codes

实现时允许按同一命名风格补充，但不得先设计分类层级：

```text
POLICY_MISSING
POLICY_INVALID
TASK_STATE_MISSING
TASK_STATE_INVALID
TASK_ID_MISMATCH
TASK_RUNTIME_MISSING
TASK_RUNTIME_DRIFT
BUDGET_EXCEEDED
TASK_STORAGE_MISMATCH
GIT_CHECK_SKIPPED
SYMLINK_INPUT
```

#### 验收 M2

- [ ] 合法 state/policy 退出 0；字段顺序和空白不影响结果。
- [ ] missing block 与 malformed block 分别产生 warning/error。
- [ ] 未知 schema/字段、重复 marker、非法 lifecycle/Gate/type、ID 不一致均被拒绝。
- [ ] runtime drift 和悬挂 TASK 被捕获；Level A inline 行不误报。
- [ ] lines/bytes/最大单行始终报告；只有显式 policy 阈值触发 error。
- [ ] review ledger/archive/accepted/superseded 不被误算为 active TASK。
- [ ] local 模式发现 tracked/staged TASK；tracked 模式发现 ignored 和已关闭未 tracked TASK。
- [ ] 非 Git target 产生 skipped warning，不声称 storage PASS。
- [ ] symlink Vault/TASK 不被跟随，外部内容不出现在输出。
- [ ] text/JSON findings 集合一致，排序稳定；连续运行三次结果一致（规范化 target 字段后）。
- [ ] `check` 前后目标目录内容和 Git 状态不变。
- [ ] 旧 CLI 全部回归通过。

#### 必跑检查

```bash
python3 -m unittest scripts.test_trellium
python3 scripts/sync-skills.py
python3 scripts/sync-skills.py --check
git diff --check
```

M2 独立 review 重点检查：只读性、symlink、安全的 Git 参数、legacy fail-closed、无通用抽象框架。无 open finding 后提交。

### M3 — 文档、迁移、版本与 shadow 验收

#### 修改范围

- `README.md`
- `README.en.md`
- 两套 `skills/trellium*/SKILL.md`
- `init/MIGRATIONS.md`
- `init/VERSION`（本周期唯一版本提升点，按 CalVer）
- sync 生成物及必要测试。

#### 顺序

1. 文档说明 check 只读、warning/error、退出码、legacy 和不会自动修复。
2. MIGRATIONS 记录 schema、模板、protected data 和 storage 迁移边界。
3. 提升版本并同步 Skill 包。
4. 对三个临时项目做机械验收：新 adopt、legacy、local Git storage；不得使用或提交真实项目内容。
5. 做一次最小消融复核，不增加生产开关：
   - 从合法项目移除 state block，确认 runtime lifecycle 只能变为 unresolved，不能继续被“成功校验”；
   - 从合法项目移除 policy block，确认 budget/storage 只剩测量或 unresolved，不能套用隐藏默认；
   - 让 runtime 行从一致改为不一致，确认只新增预期 drift finding；
   - 在相同 Git 状态下切换 `tracked/local`，确认 storage 结果按唯一 policy 改变。
6. 逐个审查本次新增的模块、类和函数：若删除后上述承诺检查仍全部成立，就删除该抽象。
7. 执行全量检查和最终 diff review。

#### 验收 M3

- [ ] `check --help` 清楚且旧命令帮助/行为无回归。
- [ ] 新 adopt 项目直接 check 退出 0。
- [ ] legacy 项目退出 0 但 summary 明确 unresolved warnings，不显示无条件 PASS。
- [ ] validation error 退出 2；JSON stdout 仍是单个合法完整对象。
- [ ] operational/argument error 退出 1，信息清楚。
- [ ] repo script 与两套 Skill 脚本对相同输入产生相同 findings。
- [ ] README 中英文、SKILL、MIGRATIONS、VERSION 与实际 CLI 一致。
- [ ] check 不写文件、不访问网络、不执行文档命令。
- [ ] 四个最小消融场景的结果符合预期；任何“不影响检查能力”的组件已从实现中删除。
- [ ] 没有仅为未来 context/evidence/generator 服务的类、字段、registry、hook 或配置项。
- [ ] 临时项目的机械结果已记录；K1-K4 仍需真实项目数据的部分明确标为未证实，不宣称收益已证明。
- [ ] 独立 review 无 open/needs-discussion finding。

#### 最终检查

```bash
python3 scripts/trellium.py check --help
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
git diff --check
git status --short
```

#### 完成定义

只有同时满足以下条件才可声称第一周期完成：

- M1-M3 验收逐条记录结果；
- 协议、模板、CLI、测试、README、MIGRATIONS、VERSION 同步；
- 没有修改真实项目数据、批量迁移 TASK 或自动 untrack 文件；
- 没有 `context/evidence/generator/fact-type/DSL` 等范围外半成品；
- 所有提交可独立回滚，工作树没有遗漏的实施文件。

## 8. 建议提交边界

1. `docs(protocol): define minimal canonical vault state`
2. `feat(check): add deterministic vault state checks`
3. `docs(release): document check workflow and migration`

如果 M2 过大，可按 parser/core checks 与 CLI/renderers 拆成两个提交；禁止借拆分引入框架化抽象。

## 9. Claude 执行纪律

1. 开始前完整读取反馈、本计划、相关协议、脚本和测试。
2. 每个里程碑开始前列出修改文件；扩大范围先请求确认。
3. test-first，但测试只覆盖承诺行为，不为未来路线图预建接口。
4. 优先使用小函数和普通数据结构；只有同一逻辑真实重复三次以上才提取通用抽象。
5. 不从自然语言推断批准、权威、Gate 或 lifecycle。
6. 不自动修复目标 Vault，即使修复明显也只报告。
7. 每个里程碑后运行检查、review diff、记录验收、独立提交。
8. schema 需要 breaking change 时停止；不得在 `schema_version: 1` 下改变既有字段含义。
9. 最终报告包含改动、逐项验收、命令结果、shadow 证据、已知限制和明确未实施项。

## 10. 后续能力的重新进入条件

这些不是当前授权范围：

- **context manifest/compiler：** 仅当 K4 kill criterion 成立，或两个真实项目证明上下文选择仍是主要成本时重新设计；先做 manifest，不先拼接大文本 pack。
- **slice 历史数组：** 仅当可选 `current_slice` 无法表达至少两个真实任务，且错误不能通过 current contract 解决时升级 schema。
- **evidence freshness：** 仅当真实发生旧 PASS 被误作当前证据；先记录 receipt，不自动执行命令。
- **runtime 生成：** 仅当 state v1 在至少两个项目稳定使用，且手工投影漂移仍高频。
- **owner inbox/review pack：** 从同一状态派生，不创建新状态文件。
- **fact types、语义检索、多 Agent 协调：** 必须各自有可复现失败事件；不得因“更 Agent-native”提前建设。

最终产品判断仍只看：同一事实是否只有一个 owner、未知是否明确暴露、机械错误是否在提交前被发现、工具是否保持确定性与只读。新增 schema、命令或代码行数本身都不是成功。
