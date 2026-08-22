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
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

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

- 状态为 Accepted 或 Superseded 且早于最近里程碑的任务文件移入 `vault/tasks/archive/`。
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
git diff --stat HEAD
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
