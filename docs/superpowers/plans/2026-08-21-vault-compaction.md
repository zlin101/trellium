# Vault Compact 与记忆生命周期 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Agent Native Init 协议加入热文件压缩（Compact）、治理文件激活回路、decisions 索引化与读路径分级，并同步到双语 Skill 分发包。

**Architecture:** 协议源（`init/`，中文权威）新增 15 号压缩模块并修订 10/20/30/90 号模块；能力内化进 agent-task 模板（zh+en 两套 skill 包）；`scripts/agent-init.py` 的内嵌入口片段对齐读路径分级；`sync-skills.py` 重新生成快照；README 双语更新；临时项目实测。

**Tech Stack:** Markdown 协议文档（中文权威 + 英文人工翻译）、Python 3 标准库脚本、unittest、git。

**Spec:** `docs/superpowers/specs/2026-08-21-vault-compaction-design.md`

## Global Constraints

- 中文协议源是权威；英文 skill 包为人工语义翻译，两套必须同步修改。
- 任何文件不出现密钥、Token、真实凭据、本地绝对路径。
- 预算线全部用行数表达，`wc -l` 可度量：runtime ≤ 120 行；handoff ≤ 3 条交接或 ≤ 100 行；decisions ≤ 150 行或 ≤ 8 条完整记录；tasks/（不含 archive）≤ 40 个文件。
- 决策状态四态，措辞逐字使用：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx`、`Expired`。
- 决策 ID 格式 `D-xxxx`（四位数字），顺序分配。
- 压缩五阶段顺序措辞：测量 → 分类 → 重组 → 校验 → 记录。
- 语义判定（Superseded/Merged/Expired）只提案、用户批量确认；未确认一律保持 `Active`。
- 新模块文件名：`init/protocol/15-vault-compaction.md`。
- 所有协议改动完成后必须运行 `python3 scripts/sync-skills.py` 重新生成两套快照，且 `--check` 必须通过（CI 同款）。
- 测试命令：`uv run pytest`（在仓库根目录）。工作分支：`improve/vault-compaction`。
- 每个 Task 结束单独提交；提交信息用仓库惯例（`feat:`/`docs:`/`test:` 前缀），结尾加 `Co-Authored-By: Claude <noreply@anthropic.com>`。
- `decisions/` 目录与 `tasks/archive/` 目录均由压缩时创建，初始化/接入不创建，不进入 `agent-init.py` 的 `TEMPLATE_FILES`。

---

### Task 1: 新建协议模块 15-vault-compaction.md 并更新模块清单

**Files:**
- Create: `init/protocol/15-vault-compaction.md`
- Modify: `init/INIT.md`（"协议模块"清单 + "验收标准"）
- Modify: `init/protocol/README.md`（"读取顺序"清单）

**Interfaces:**
- Consumes: `10-vault.md` 的文件职责词汇（runtime/handoff/decisions/tasks）、`20-governance.md` 的 Level A/B/C 与 Authority 词汇。
- Produces: 模块名 `init/protocol/15-vault-compaction.md`（Task 2/3 的修订会引用它；sync-skills 会把它带入快照）。

- [ ] **Step 1: 写入新模块全文**

创建 `init/protocol/15-vault-compaction.md`，内容如下（完整写入，不改结构）：

```markdown
# 15 - Vault 记忆压缩

## 定位

本模块定义热文件的记忆生命周期和压缩（Compact）机制。它回答：热文件何时超出健康预算、压缩如何执行、哪些操作 Agent 可以自主做、哪些必须留给用户判断。

它补充 `10-vault.md`，不改变 `20-governance.md` 的授权和验收规则。

## 记忆分层

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；有预算线；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/*`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

不变量：压缩不直接修改治理文件与结构文件。

## 预算线

全部用行数表达，可由 `wc -l` 直接度量：

- `vault/runtime.md` 超过 120 行。
- `vault/handoff.md` 超过 3 条交接或超过 100 行。
- `vault/decisions.md` 超过 150 行或超过 8 条完整决策记录；首次超出时执行索引化拆分。
- `vault/tasks/`（不含 `archive/`）超过 40 个任务文件；执行里程碑归档。

## 触发时机

- agent-task 工作流收尾的记忆更新步骤检测到任一预算线超出。
- 用户显式要求压缩（例如 "compact vault"）。

## 压缩流程

五个阶段，顺序执行：

1. **测量**：运行预算线检查，列出超出的文件。
2. **分类**：对超出文件逐条分类；同时交叉核对治理文件与现实是否漂移（`governance.md` 的必要检查 vs `runtime.md` 实际命令；任务等级边界 vs 实际任务分布），漂移只形成提案。
3. **重组**：执行各文件的压缩算法；语义判定单独成批等用户确认。
4. **校验**：运行校验命令清单，确认全部不变量成立。
5. **记录**：在 `runtime.md` Recent Changes 写一行；形成独立 git 提交；核对 `project.md` 当前阶段与 `runtime.md` 一致，不一致时提出修订。

## 各文件压缩算法

### runtime.md：重写而非删减

以"新会话冷启动需要什么"为唯一标准生成全新文件：当前阶段、活跃任务指针、当前约束、必要检查、已知风险、下一步。

旧内容分流：

- 进行中的进展保留；
- 已完成的进展压缩为一行进 Recent Changes，执行历史已在 `tasks/*`；
- 长期结论迁入 `decisions.md`。

### handoff.md：滚动窗口加分流

- 保留最近 1-3 次交接。
- 更早的交接：有对应任务文件的，把失败尝试与教训合并进该任务文件的 Execution Record；已被 `runtime.md` 或 `decisions.md` 吸收的允许删除。handoff 是瞬态上下文，删除不视为信息损失。
- 无在途任务时恢复为模板态。

### decisions.md：生命周期加索引化

决策状态四态：

- `Active`
- `Superseded by D-xxxx`：被更新决策取代。
- `Merged into D-xxxx`：与同类决策合并。
- `Expired`：前提已消失。

单文件阶段：按现有模板记录，每条标注状态，默认 `Active`。

索引化拆分（首次超过预算线时执行）：

- `vault/decisions.md` 变为纯索引，每条 1-2 行：`D-xxxx · 标题 · 状态 · 一句话实质 · 日期`。
- 完整正文迁入 `vault/decisions/D-xxxx-slug.md`，文件内保留状态字段。
- ID 顺序分配：现有最大编号加一。
- 默认只读索引；需要完整背景时读单条文件。

### tasks/：里程碑归档

- 状态为 Accepted 且早于最近里程碑的任务文件移入 `vault/tasks/archive/`。
- 纯移动，不修改内容。

## 语义与非语义操作分离

这是压缩安全性的核心。

非语义操作，Agent 可自主执行：

- 正文搬运（decisions 索引化、任务归档）；
- 建立与维护索引；
- 状态标注为 `Active`；
- handoff 已吸收内容的删除。

语义操作，Agent 只能提案，由用户批量确认：

- 判定 `Superseded by D-xxxx`；
- 判定 `Merged into D-xxxx`；
- 判定 `Expired`。

提案格式：候选清单，每条含决策 ID、建议状态、一句话理由。未确认的一律保持 `Active`。

执行拆批：

1. 非语义部分先执行并提交；
2. 语义清单经用户确认后作为第二批提交。

## 校验清单

压缩后必须运行并确认：

```bash
wc -l vault/runtime.md vault/handoff.md vault/decisions.md
```

- 各热文件回到预算内。

```bash
grep -o "D-[0-9][0-9][0-9][0-9]" vault/decisions.md | sort -u
ls vault/decisions/
```

- 索引与目录一一对应：索引无悬挂，目录无孤儿。
- 压缩前的每条决策在压缩后索引中出现（无 Active 丢失）。
- `runtime.md` 活跃任务指针指向存在的文件。

```bash
git diff --stat
```

- 本次提交只包含 `vault/` 变更。

## git 安全

- 前置：`vault/` 无未提交变更；否则先提交或中止。压缩永远从干净基线开始。
- 校验失败：恢复 `vault/`（`git checkout -- vault/`），报告失败的不变量，不产生提交。
- 压缩产出独立提交，任意时刻可 `git revert`。

## 任务等级映射

- 例行压缩（纯搬运、无首次索引化、无语义批次）：Level A，在 `runtime.md` 记一行。
- 结构性压缩（decisions 首次索引化、含语义合并批次）：Level B，建立任务文件记录批次内容。
- governance 修订提案被用户接受后的治理变更：Level C，按 `20-governance.md` 执行。

## 治理文件的激活回路

压缩不修改治理文件，但分类阶段必须产出提案：

- `governance.md` 漂移（必要检查过时、等级边界与实际不符、升级规则空白）：输出修订提案清单，按 Level C 处理。
- `collaboration.md`：协作信号由 agent-task 工作流在任务收尾时捕获（见 `90-collaboration-profile.md`），压缩不做额外处理。
- `project.md`：记录阶段核对当前阶段与 `runtime.md` 一致；不一致时提出修订。

## 反模式

- 把压缩当作删除：任何"判断不重要然后丢弃"的操作都不属于压缩。
- 语义判定不打提案直接执行。
- 压缩提交混入非 vault 变更。
- 在 `vault/` 有未提交变更时开始压缩。
- 改写归档区文件（归档区只增）。
```

- [ ] **Step 2: 更新 `init/INIT.md` 模块清单**

在"协议模块"有序列表中，`2. init/protocol/10-vault.md` 之后插入一行（后续编号顺延为 3-11）：

```markdown
3. `init/protocol/15-vault-compaction.md`
```

在"验收标准"列表末尾追加：

```markdown
- 记忆系统具备压缩能力：热文件预算线、五阶段压缩流程、语义/非语义操作分离和校验清单已定义于 `init/protocol/15-vault-compaction.md`；
```

- [ ] **Step 3: 更新 `init/protocol/README.md` 读取顺序**

在"读取顺序"列表 `2. 10-vault.md` 之后插入：

```markdown
3. `15-vault-compaction.md`
```

（后续编号顺延。）

- [ ] **Step 4: 验证内容落位**

Run: `test -f init/protocol/15-vault-compaction.md && grep -c "Superseded by D-xxxx" init/protocol/15-vault-compaction.md && grep -n "15-vault-compaction" init/INIT.md init/protocol/README.md`
Expected: 文件存在；`Superseded by D-xxxx` 出现 ≥ 3 次；两个清单各有一处引用。

- [ ] **Step 5: Commit**

```bash
git add init/protocol/15-vault-compaction.md init/INIT.md init/protocol/README.md
git commit -m "feat(protocol): add vault compaction module (15)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 修订 10-vault.md（分层、索引原则、读路径分级、预算与信号）

**Files:**
- Modify: `init/protocol/10-vault.md`

**Interfaces:**
- Consumes: Task 1 的模块名 `15-vault-compaction.md`。
- Produces: 分层词汇与预算线表述（Task 3/4/5/6 引用同一措辞）。

- [ ] **Step 1: 结构图补归档目录**

将"必备结构"代码块替换为：

````markdown
```text
vault/
├── index.md
├── project.md
├── runtime.md
├── governance.md
├── decisions.md
├── decisions/            # 首次压缩时创建：决策正文
├── handoff.md
├── tasks/
│   ├── README.md
│   ├── .gitkeep
│   └── archive/          # 里程碑归档时创建
└── details/
    ├── architecture.md
    ├── development.md
    ├── api.md
    ├── agent.md
    └── domain.md
```
````

- [ ] **Step 2: "定位"之后插入"索引原则"与"记忆分层"两节**

```markdown
## 索引原则

增长进目录，读取走索引。任何会增长的内容（决策、任务、细节），正文进目录按需读取；索引层保证默认读取路径永远短。

`index.md` 是路由中枢，保持纯路由、不存状态；活跃任务指针唯一存在于 `runtime.md`。新增记忆类型一律按此模式扩展。

## 记忆分层

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；有预算线；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/*`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

预算线、压缩流程与安全边界见 `15-vault-compaction.md`。
```

- [ ] **Step 3: 更新文件职责段落**

- `runtime.md` 段：在"保持短小，建议 50-120 行。"后追加一句"超过 120 行即触发压缩（见 `15-vault-compaction.md`）。"
- `decisions.md` 段整段替换为：

```markdown
### decisions.md

长期有效决策。

当架构、技术栈、API 契约、数据模型、依赖、项目范围或 Agent 协作规则变化时更新。

每条决策标注生命周期状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。超过 150 行或 8 条完整记录时索引化：`decisions.md` 变纯索引，正文迁入 `vault/decisions/D-xxxx-slug.md`，默认只读索引。
```

- `details/*` 段的创建条件替换为："同一主题的长内容被重复读取或迁移 2 次以上时创建 `vault/details/<topic>.md`。"

- [ ] **Step 4: 默认读取路径改为分级**

将"默认读取路径"一节替换为：

```markdown
## 默认读取路径

非琐碎任务：

```text
AGENTS.md
vault/index.md    # 含任务等级与授权速查表
vault/runtime.md
```

满足任一条件时追加读取完整 `vault/governance.md`：

- 任务为 Level B 或 Level C；
- 任务等级或授权判定模糊；
- 任务涉及治理规则本身。

第一次进入项目追加读取：

```text
vault/project.md
```

接手交接任务追加读取：

```text
vault/handoff.md
```

追踪任务或治理任务追加读取：

```text
vault/tasks/<task-id>.md
```
```

- [ ] **Step 5: 更新规则补压缩触发**

在"更新规则"列表末尾追加两行：

```markdown
- 更新热文件时检查预算线；超出时按 `15-vault-compaction.md` 执行压缩。
- 压缩语义判定只提案，由用户确认；未确认的决策保持 `Active`。
```

- [ ] **Step 6: 验证**

Run: `grep -n "索引原则\|记忆分层\|15-vault-compaction\|速查表" init/protocol/10-vault.md`
Expected: 四个关键词全部命中。

- [ ] **Step 7: Commit**

```bash
git add init/protocol/10-vault.md
git commit -m "feat(protocol): vault tiers, index principle, leveled read path
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 3: 修订 20-governance.md、30-agent-entry.md、90-collaboration-profile.md

**Files:**
- Modify: `init/protocol/20-governance.md`（"升级规则"节）
- Modify: `init/protocol/30-agent-entry.md`（"Required Reading"节）
- Modify: `init/protocol/90-collaboration-profile.md`（"生成和更新"节）

**Interfaces:**
- Produces: 升级即反馈信号、分级读取路径、协作捕获接线——Task 4/6 模板引用相同语义。

- [ ] **Step 1: 20-governance.md 升级规则追加反馈回路**

在"升级规则"一节的条件列表之后追加：

```markdown
升级事件同时是治理反馈信号：当升级暴露 `governance.md` 的规则空白、边界模糊或必要检查过时时，记录为治理修订候选，并按 Level C 提请用户确认。治理文件不通过日常任务直接修改。
```

- [ ] **Step 2: 30-agent-entry.md Required Reading 分级**

将"Required Reading"一节的第一个代码块及其前导句替换为：

```markdown
入口文件必须要求非琐碎任务读取：

```text
vault/index.md    # 含任务等级与授权速查表
vault/runtime.md
```

任务为 Level B 或 Level C、等级或授权判定模糊、或任务涉及治理规则本身时，追加读取完整：

```text
vault/governance.md
```
```

（"第一次进入项目 / 接手交接任务 / 追踪任务"三段保持不变。）

- [ ] **Step 3: 90-collaboration-profile.md 补接线**

在"生成和更新"一节的时机列表末尾追加一项：

```markdown
- agent-task 工作流收尾的记忆更新步骤主动检查本次任务中的协作信号（用户纠正、偏好表达、验证有效的协作模式），发现时按本节规则记录。
```

- [ ] **Step 4: 验证**

Run: `grep -n "治理反馈信号" init/protocol/20-governance.md && grep -n "速查表" init/protocol/30-agent-entry.md && grep -n "agent-task 工作流收尾" init/protocol/90-collaboration-profile.md`
Expected: 三处全部命中。

- [ ] **Step 5: Commit**

```bash
git add init/protocol/20-governance.md init/protocol/30-agent-entry.md init/protocol/90-collaboration-profile.md
git commit -m "feat(protocol): governance feedback loop, leveled entry reading, collaboration wiring
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: zh skill 模板四件（AGENTS.md、index.md、decisions.md、agent-task）

**Files:**
- Modify: `skills/agent-native-init-zh/assets/templates/AGENTS.md`
- Modify: `skills/agent-native-init-zh/assets/templates/vault/index.md`
- Modify: `skills/agent-native-init-zh/assets/templates/vault/decisions.md`（整体重写）
- Modify: `skills/agent-native-init-zh/assets/templates/skills/agent-task/SKILL.md`

**Interfaces:**
- Consumes: Task 1/2 的预算线数字、四态措辞、五阶段措辞。
- Produces: zh 模板（Task 7 的 `agent-init.py` 从 zh 模板目录拷贝；Task 6 的 en 版按此翻译）。

- [ ] **Step 1: AGENTS.md 读路径分级**

"Required Reading"一节替换为：

```markdown
## Required Reading

执行任何非琐碎任务前，读取：

1. `vault/index.md`（含任务等级与授权速查表）
2. `vault/runtime.md`

任务为 Level B 或 Level C、判定模糊或涉及治理规则时，追加读取：

- `vault/governance.md`

第一次进入项目时，还要读取：

- `vault/project.md`

接手中断任务时，还要读取：

- `vault/handoff.md`

追踪任务或治理任务读取 `vault/tasks/` 下的活跃任务文件。
```

"Task Workflow"第 2 步替换为"根据 `vault/index.md` 速查表判断任务等级和授权等级；判定模糊或 Level B/C 时读取 `vault/governance.md`。"，并在原第 11 步后追加：

```markdown
12. 记忆更新时检查预算线；任一热文件超出时执行或提议压缩（测量→分类→重组→校验→记录）。
13. 任务中出现用户协作偏好或纠正信号时，记入 `vault/collaboration.md`。
```

- [ ] **Step 2: index.md 加速查表与压缩规则**

在"默认读取"一节之前插入：

```markdown
## 任务与授权速查表

- Level A 简单任务：低风险、一次会话、1-2 个文件；记 `runtime.md`。
- Level B 追踪任务：多文件、需审计、可能交接；记 `tasks/*`。
- Level C 治理任务：架构、公开 API、数据模型、框架、外部服务、安全、成本、部署或治理规则变化；记 `tasks/*` 和 `decisions.md`，需用户确认。
- 授权等级：0 只读 / 1 局部修改 / 2 限定范围 / 3 需确认 / 4 禁止。
- 判定模糊或涉及治理规则本身：读完整 `governance.md`。
```

"默认读取"改为分级（与 Task 2 Step 4 的 10-vault 版本相同的文件顺序：index → runtime，governance 按需）。"文件职责"中 `decisions.md` 一行替换为：

```markdown
- `decisions.md`：长期决策索引与（未拆分前的）决策记录；正文拆分后在 `vault/decisions/D-xxxx-*.md`。
```

"更新规则"末尾追加：

```markdown
- 更新热文件时检查预算线：runtime ≤ 120 行；handoff ≤ 3 条交接；decisions ≤ 150 行或 8 条记录。
- 超出预算线时执行压缩：测量→分类→重组→校验→记录；语义判定（Superseded/Merged/Expired）只提案，用户确认前保持 Active。
```

- [ ] **Step 3: 重写 decisions.md 模板**

整体替换为：

```markdown
# Decisions

长期决策记录。当前任务进展放 `vault/runtime.md` 或 `vault/tasks/*`。

每条决策标注状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。默认 `Active`。

超过 150 行或 8 条完整记录时索引化：本文件变纯索引（每条 1-2 行），正文迁入 `vault/decisions/D-xxxx-slug.md`。ID 顺序分配。

## 决策索引（索引化后使用）

- D-0001 · 决策标题 · Active · 一句话实质 · 2026-01-01

## YYYY-MM-DD - Decision Title

Status: Active

### Background

说明为什么需要这个决策。

### Decision

说明决策内容。

### Rationale

说明为什么选择这个方案。

### Alternatives

- 曾考虑的替代方案，以及为什么未选择。

### Impact

说明未来 Agent 因此应采取什么不同做法。
```

- [ ] **Step 4: agent-task SKILL.md 内化压缩**

"Steps"第 1 步替换为"读取 `AGENTS.md`、`vault/index.md`（含速查表）和 `vault/runtime.md`；Level B/C、判定模糊或涉及治理规则时读取 `vault/governance.md`。"原第 13 步后追加：

```markdown
14. 记忆更新时检查预算线（runtime ≤ 120 行、handoff ≤ 3 条、decisions ≤ 150 行或 8 条）；超出时把溢出内容迁到正确去向。
15. 任一热文件超出预算线时，执行压缩五阶段：测量→分类→重组→校验→记录。压缩规则：
    - decisions 索引化与任务归档是零信息损失的搬运，可自主执行。
    - Superseded/Merged/Expired 判定只出提案清单，用户确认前一律保持 Active。
    - 压缩前 `vault/` 必须无未提交变更；压缩形成只含 `vault/` 变更的独立提交；校验失败即恢复。
16. 本次任务中出现用户协作偏好或纠正信号时，按观察记入 `vault/collaboration.md`；重复出现或用户确认后升为偏好。
```

- [ ] **Step 5: 验证**

Run: `grep -c "速查表" skills/agent-native-init-zh/assets/templates/vault/index.md && grep -c "Status: Active" skills/agent-native-init-zh/assets/templates/vault/decisions.md && grep -c "测量→分类→重组→校验→记录" skills/agent-native-init-zh/assets/templates/skills/agent-task/SKILL.md`
Expected: 三项均 ≥ 1。

- [ ] **Step 6: Commit**

```bash
git add skills/agent-native-init-zh/assets/templates/
git commit -m "feat(skill-zh): templates for leveled reading, decisions lifecycle, compaction
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 5: zh skill references（protocol-model.md、templates-guide.md、SKILL.md）

**Files:**
- Modify: `skills/agent-native-init-zh/references/protocol-model.md`
- Modify: `skills/agent-native-init-zh/references/templates-guide.md`
- Modify: `skills/agent-native-init-zh/SKILL.md`

**Interfaces:**
- Consumes: Task 1/2 语义与数字。
- Produces: zh reference 措辞（Task 6 en 翻译基准）。

- [ ] **Step 1: protocol-model.md 加"记忆分层与压缩"节**

在"必需 Vault 文件"代码块之后（"只有存在重复读取长上下文的真实需求时"一句之前的位置调整为本句替换）插入新节：

```markdown
## 记忆分层与压缩

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；预算线内；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新 |
| 归档区 | `tasks/*`、`decisions/`、`details/*` | 只增 |

预算线：runtime ≤ 120 行；handoff ≤ 3 条交接；decisions ≤ 150 行或 8 条记录；tasks（不含 archive）≤ 40 个文件。

压缩五阶段：测量→分类→重组→校验→记录。非语义操作（搬运、索引、标注 Active）Agent 自主执行；语义判定（Superseded by D-xxxx / Merged into D-xxxx / Expired）只提案，用户批量确认，未确认保持 Active。压缩是只含 `vault/` 变更的独立提交。

决策索引化：decisions.md 变纯索引，正文入 `vault/decisions/D-xxxx-slug.md`。索引原则：增长进目录，读取走索引。

读路径分级：默认读 `index.md`（含速查表）+ `runtime.md`；Level B/C、判定模糊或涉及治理规则时读完整 `governance.md`。
```

同时把"文件职责"中 `vault/decisions.md` 一行替换为"决策索引与生命周期记录（Active / Superseded / Merged / Expired）；正文拆分后在 `vault/decisions/*`。"

- [ ] **Step 2: templates-guide.md 模板地图更新**

`vault/decisions.md` 一行替换为"长期决策；生命周期四态；超阈值索引化（正文入 `vault/decisions/`）。"；`vault/index.md` 一行末尾追加"含任务与授权速查表及压缩预算线。"；"既有项目接入"清单追加一条：

```markdown
5. 接入时不创建 `vault/decisions/` 与 `vault/tasks/archive/`；两者由首次压缩按需创建。
```

- [ ] **Step 3: SKILL.md Round 1 增补**

"Round 1 - Protocol Coverage Review"检查清单追加：

```markdown
- Hot-file budgets and the compact procedure are routed from `vault/index.md` (see the compaction module in `references/protocol-source/init/protocol/15-vault-compaction.md`).
```

- [ ] **Step 4: 验证**

Run: `grep -c "记忆分层与压缩" skills/agent-native-init-zh/references/protocol-model.md && grep -c "15-vault-compaction" skills/agent-native-init-zh/SKILL.md`
Expected: 两项均 ≥ 1。

- [ ] **Step 5: Commit**

```bash
git add skills/agent-native-init-zh/references/protocol-model.md skills/agent-native-init-zh/references/templates-guide.md skills/agent-native-init-zh/SKILL.md
git commit -m "feat(skill-zh): references cover compaction and tiers
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: en skill 全套（模板 + references + SKILL.md）

**Files:**
- Modify: `skills/agent-native-init/assets/templates/AGENTS.md`
- Modify: `skills/agent-native-init/assets/templates/vault/index.md`
- Modify: `skills/agent-native-init/assets/templates/vault/decisions.md`（整体重写）
- Modify: `skills/agent-native-init/assets/templates/skills/agent-task/SKILL.md`
- Modify: `skills/agent-native-init/references/protocol-model.md`
- Modify: `skills/agent-native-init/references/templates-guide.md`
- Modify: `skills/agent-native-init/SKILL.md`

**Interfaces:**
- Consumes: Task 4/5 的 zh 内容（逐段翻译，语义一致；状态词 `Active` / `Superseded by D-xxxx` / `Merged into D-xxxx` / `Expired` 与预算数字原样保留）。

- [ ] **Step 1: en AGENTS.md 读路径分级**

"Required Reading"替换为：

```markdown
## Required Reading

Before non-trivial work, read:

1. `vault/index.md` (includes the task-level and authority cheat sheet)
2. `vault/runtime.md`

For Level B or Level C work, unclear classification, or governance-rule changes, also read:

- `vault/governance.md`

On first entry to the project, also read:

- `vault/project.md`

When resuming interrupted work, also read:

- `vault/handoff.md`

For tracked or governed tasks, read the active task file under `vault/tasks/`.
```

"Task Workflow"第 2 步替换为"Classify task level and authority using the cheat sheet in `vault/index.md`; read `vault/governance.md` in full for Level B/C work or unclear classification."，并在第 11 步后追加：

```markdown
12. Check memory budgets when updating hot files; compact or propose compaction when exceeded (measure → classify → restructure → verify → record).
13. Record user collaboration preferences or corrections observed in this task in `vault/collaboration.md`.
```

- [ ] **Step 2: en index.md 速查表与压缩规则**

在"Default Reading"前插入：

```markdown
## Task And Authority Cheat Sheet

- Level A, simple: low risk, one session, 1-2 files; record in `runtime.md`.
- Level B, tracked: multi-file, auditable, may need handoff; record in `tasks/*`.
- Level C, governed: architecture, public API, data model, framework, external service, security, cost, deployment, or governance-rule changes; record in `tasks/*` and `decisions.md`; needs user confirmation.
- Authority: 0 read-only / 1 local edit / 2 scoped change / 3 approval required / 4 forbidden.
- Unclear classification or governance-rule work: read full `governance.md`.
```

"Default Reading"改为分级：`AGENTS.md` → `vault/index.md` (cheat sheet) → `vault/runtime.md`；governance 按需（Level B/C、模糊、治理规则）。"File Responsibilities"中 `decisions.md` 行替换为"durable decision index and, before the split, full records; bodies move to `vault/decisions/D-xxxx-*.md` after indexing."。"Update Rules"末尾追加：

```markdown
- Check hot-file budgets when updating them: runtime ≤ 120 lines; handoff ≤ 3 entries; decisions ≤ 150 lines or 8 full records.
- When a budget is exceeded, compact: measure → classify → restructure → verify → record. Semantic judgments (Superseded / Merged / Expired) are proposals only; keep Active until the user confirms.
```

- [ ] **Step 3: 重写 en decisions.md 模板**

```markdown
# Decisions

Record durable decisions here. Keep current task progress in `vault/runtime.md` or `vault/tasks/*`.

Every decision carries a status: `Active`, `Superseded by D-xxxx`, `Merged into D-xxxx`, or `Expired`. Default is `Active`.

When this file exceeds 150 lines or 8 full records, index it: this file becomes a pure index (1-2 lines per decision) and bodies move to `vault/decisions/D-xxxx-slug.md`. IDs are sequential.

## Decision Index (after indexing)

- D-0001 · Decision title · Active · One-line essence · 2026-01-01

## YYYY-MM-DD - Decision Title

Status: Active

### Background

Explain why this decision was needed.

### Decision

State the decision.

### Rationale

Explain why this option was chosen.

### Alternatives

- Alternative considered and why it was not chosen.

### Impact

Explain what future Agents should do differently because of this decision.
```

- [ ] **Step 4: en agent-task SKILL.md 内化压缩**

第 1 步替换为"Read `AGENTS.md`, `vault/index.md` (with the cheat sheet), and `vault/runtime.md`; read `vault/governance.md` in full for Level B/C work, unclear classification, or governance-rule changes."第 13 步后追加：

```markdown
14. Check hot-file budgets when updating memory (runtime ≤ 120 lines, handoff ≤ 3 entries, decisions ≤ 150 lines or 8 records); move overflow to the right destination.
15. When any hot file exceeds its budget, compact in five phases: measure → classify → restructure → verify → record. Compaction rules:
    - Decision indexing and task archiving are zero-loss moves an Agent may run autonomously.
    - Superseded / Merged / Expired judgments are proposal-only; keep Active until the user confirms.
    - Start only with a clean `vault/`; produce a dedicated commit containing only `vault/` changes; restore on verification failure.
16. Record observed user collaboration preferences or corrections in `vault/collaboration.md` as observations; promote to preferences after repetition or confirmation.
```

- [ ] **Step 5: en protocol-model.md / templates-guide.md / SKILL.md**

- protocol-model.md：在"Required Vault Files"代码块后插入：

```markdown
## Memory Tiers And Compaction

| Tier | Files | Lifecycle |
| --- | --- | --- |
| Hot files | `runtime.md`, `handoff.md`, `decisions.md` | Frequently updated; budgeted; compaction targets |
| Governance files | `governance.md`, `collaboration.md` | Event-driven updates; compaction only proposes |
| Structural files | `index.md`, `project.md`, `tasks/README.md` | Rarely updated |
| Archive | `tasks/*`, `decisions/`, `details/*` | Append-only |

Budgets: runtime ≤ 120 lines; handoff ≤ 3 entries; decisions ≤ 150 lines or 8 full records; tasks (excluding archive) ≤ 40 files.

Compaction runs five phases: measure → classify → restructure → verify → record. Non-semantic moves (relocating bodies, indexing, marking Active) run autonomously; semantic judgments (`Superseded by D-xxxx` / `Merged into D-xxxx` / `Expired`) are proposal-only, confirmed by the user in batch, and stay `Active` until confirmed. Compaction is a dedicated commit containing only `vault/` changes.

Decision indexing: decisions.md becomes a pure index and bodies move to `vault/decisions/D-xxxx-slug.md`. Index principle: growth goes to directories, reading goes through indexes.

Leveled reading: by default read `index.md` (with the cheat sheet) and `runtime.md`; read full `governance.md` for Level B/C work, unclear classification, or governance-rule changes.
```

"File Responsibilities"的 decisions 行替换为"- `vault/decisions.md`: durable decision index and lifecycle records (Active / Superseded / Merged / Expired); bodies move to `vault/decisions/*` after indexing."
- templates-guide.md：decisions 行替换为"durable decisions; four lifecycle statuses; index when over budget (bodies move to `vault/decisions/`)."；index 行追加"includes the task/authority cheat sheet and memory budgets."；"Existing Project Adoption"清单追加"5. Do not create `vault/decisions/` or `vault/tasks/archive/` during adoption; first compaction creates them."
- SKILL.md Round 1 清单追加：`- Hot-file budgets and the compact procedure are routed from vault/index.md (see references/protocol-source/init/protocol/15-vault-compaction.md).`

- [ ] **Step 6: 验证**

Run: `grep -rc "Cheat Sheet\|cheat sheet" skills/agent-native-init/assets/templates/vault/index.md skills/agent-native-init/assets/templates/AGENTS.md && grep -c "Status: Active" skills/agent-native-init/assets/templates/vault/decisions.md`
Expected: 命中 ≥ 3；decisions 模板含 `Status: Active`。

- [ ] **Step 7: Commit**

```bash
git add skills/agent-native-init/
git commit -m "feat(skill-en): leveled reading, decisions lifecycle, compaction templates
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: agent-init.py 对齐（读路径 + runtime 约束 + next 提示 + 测试）

**Files:**
- Modify: `scripts/agent-init.py`（`agent_entry_section()` 约 493-507 行；`render_runtime()` 约 600-644 行；末尾 print 约 747 行）
- Test: `scripts/test_agent_init.py`

**Interfaces:**
- Consumes: zh 模板（`TEMPLATES_ROOT` 指向 `skills/agent-native-init-zh/assets/templates`，Task 4 已更新）。
- Produces: 分级读路径的英文入口片段（adopt 输出）。

- [ ] **Step 1: 写失败测试**

在 `scripts/test_agent_init.py` 中合适的测试类内追加（跟随该文件既有的加载方式引用 `agent_init` 模块）：

```python
    def test_agent_entry_section_levels_governance_reading(self) -> None:
        section = agent_init.agent_entry_section()
        self.assertIn("cheat sheet", section)
        self.assertIn("Level B or Level C", section)
        self.assertNotIn("3. `vault/governance.md`", section)
```

- [ ] **Step 2: 运行确认失败**

Run: `uv run pytest scripts/test_agent_init.py -k levels_governance -v`
Expected: FAIL（`agent_entry_section` 现版无 "cheat sheet"）。

- [ ] **Step 3: 修改 `agent_entry_section()`**

函数体中列表部分替换为：

```python
For non-trivial work, read these files before editing:

1. `vault/index.md` (includes the task-level and authority cheat sheet)
2. `vault/runtime.md`

Read `vault/governance.md` in full for Level B or Level C work, unclear classification, or governance-rule changes.

Use `vault/project.md` on first entry, `vault/handoff.md` when resuming interrupted work, and `vault/tasks/` for tracked or governed tasks.
```

- [ ] **Step 4: render_runtime 约束与 next 提示**

`render_runtime()` 的 `## Constraints` 列表追加一行：

```python
- Keep this file within about 120 lines; move overflow to `vault/tasks/*` or `vault/decisions.md`.
```

末尾 `print("next: ...")` 替换为：

```python
    print("next: ask your Agent to read AGENTS.md, vault/index.md (cheat sheet), and vault/runtime.md; read vault/governance.md in full for Level B/C work")
```

- [ ] **Step 5: 运行测试确认通过**

Run: `uv run pytest scripts/test_agent_init.py -v`
Expected: 全部 PASS（含既有 60+ 用例）。

- [ ] **Step 6: Commit**

```bash
git add scripts/agent-init.py scripts/test_agent_init.py
git commit -m "feat(adopt): leveled entry reading and memory budget hints
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 8: 重新生成快照 + 全量门禁

**Files:**
- Regenerate: `skills/agent-native-init-zh/references/protocol-source/`、`skills/agent-native-init/references/protocol-source/`（含 `manifest.json` 与新文件 `init/protocol/15-vault-compaction.md`）

**Interfaces:**
- Consumes: Task 1-7 全部协议源改动。
- Produces: 与 `init/` 一致的可发布快照。

- [ ] **Step 1: 同步快照**

Run: `python3 scripts/sync-skills.py`
Expected: 输出 synced 到两个目标；新模块进入快照。

- [ ] **Step 2: 校验无漂移**

Run: `python3 scripts/sync-skills.py --check`
Expected: 两个目标均 `in sync`，退出码 0。

- [ ] **Step 3: 全量测试**

Run: `uv run pytest`
Expected: 全部 PASS。

- [ ] **Step 4: Commit**

```bash
git add skills/agent-native-init-zh/references/protocol-source/ skills/agent-native-init/references/protocol-source/
git commit -m "chore(sync): regenerate protocol snapshots with compaction module
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: README 双语更新 + 临时项目实测

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Test: 临时目录实测（不产生仓库文件）

**Interfaces:**
- Consumes: Task 1-8 的最终产物。

- [ ] **Step 1: README.md 增补**

"协议理念"的"Vault 作为项目记忆"小节之后插入：

```markdown
### 记忆压缩（Compact）

热文件（runtime、handoff、decisions）有明确预算线。agent-task 工作流在任务收尾检查预算；超线时执行五阶段压缩（测量→分类→重组→校验→记录）：runtime 重写而非删减，handoff 滚动保留，decisions 超阈值索引化（正文迁入 `vault/decisions/`，默认只读索引）。Superseded/Merged/Expired 等语义判定只出提案，由用户批量确认——压缩永远是零信息损失的重组，不是删除。压缩产出只含 `vault/` 变更的独立提交，可随时回滚。

治理文件（governance、collaboration）由事件驱动激活：升级事件与压缩审查产出治理修订提案，协作偏好在任务收尾被捕获。默认读取路径分级：`index.md` 内置任务与授权速查表，完整 `governance.md` 仅 Level B/C 或判定模糊时读取。
```

"使用开源 Skill 包"一节末尾追加：

```markdown
新版 Skill 包含记忆压缩能力。对已接入项目的既有 vault，重装 Skill 后让 Agent 执行一次压缩即可完成 decisions 索引化等结构迁移；旧 `agent-task` 可按协议源 15 号模块手动升级。
```

- [ ] **Step 2: README.en.md 同义翻译增补**

在"Vault as project memory"对应小节后插入英文版（"### Memory Compaction"，语义与 Step 1 一致：预算线、五阶段 measure → classify → restructure → verify → record、零损失重组、语义判定提案制、独立提交可回滚、治理文件事件激活、读路径分级），并在 Skill 包一节末尾追加升级说明英文版。

- [ ] **Step 3: 临时项目实测**

```bash
rm -rf /tmp/agent-init-compact-test
mkdir -p /tmp/agent-init-compact-test
python3 scripts/agent-init.py adopt /tmp/agent-init-compact-test
```

Expected: 输出 changed 列表含 AGENTS.md、vault/*、skills/agent-task/SKILL.md；AGENTS.md 含 "cheat sheet"。

然后人工膨胀与压缩（按 15 号模块执行，作为 Agent 操作）：

1. 向 `vault/decisions.md` 追加 9 条完整决策记录（D-0001 起，每条含 `Status: Active`）。
2. 向 `vault/runtime.md` 追加内容至 130+ 行；`vault/handoff.md` 追加 4 次交接。
3. 在临时目录 `git init && git add -A && git commit` 建立干净基线。
4. 按五阶段压缩：decisions 索引化（9 条正文迁入 `vault/decisions/`，索引 1-2 行/条）；runtime 重写至 ≤ 120 行；handoff 保留最近 3 次。
5. 校验：`wc -l`、索引/目录一一对应比对、`git diff --stat` 仅含 vault/。
6. 确认全部不变量成立后，清理 `rm -rf /tmp/agent-init-compact-test`。

- [ ] **Step 4: 验证 README**

Run: `grep -c "记忆压缩\|Memory Compaction" README.md README.en.md`
Expected: 两文件各 ≥ 1。

- [ ] **Step 5: Commit**

```bash
git add README.md README.en.md
git commit -m "docs(readme): memory compaction feature and upgrade notes
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 完成标准

- Task 1-9 全部勾选，`python3 scripts/sync-skills.py --check` 与 `uv run pytest` 通过。
- 临时项目实测五条不变量全部成立。
- 双语包语义一致（状态词、预算数字、五阶段措辞逐字对应）。
