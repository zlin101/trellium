# Vault Compact 与记忆生命周期设计

- 日期：2026-08-21
- 状态：设计已与维护者逐节确认，待实施
- 分支：`improve/vault-compaction`

## 背景

来自重度使用反馈的三个问题：

1. **热文件与休眠文件的不对称**。runtime/handoff/decisions 被高频读写；governance、collaboration 等文件初始化后极少更新——规则设计了，但没有被实际运行的工作流激活。
2. **热文件持续膨胀**。协议中已有零散的压缩散文规则（`10-vault.md` 的"膨胀时迁移细节"、handoff"只保留最近 1-3 次"、runtime"建议 50-120 行"），但缺少触发时机、操作步骤、归档去向和压缩后校验，Agent 不会可靠地自发执行。
3. **decisions 无法压缩**。现有模板把每条决策做成完整 ADR，无生命周期状态、无归档去向。模型面对的操作是"判断哪条决策不重要然后删除"——不可逆，模型拒绝执行。这是操作设计错误，不是模型能力问题。

同时确认的有效机制：index.md 的索引路由让模型在新会话中持续想起既有决策。这是本系统真正起效的核心机制，应升格为协议原则并主动复制。

## 目标

- 三个热文件永远处于预算内，读成本有界。
- decisions 可压缩且零信息损失。
- governance/collaboration 获得事件驱动的激活回路。
- 压缩与校验命令化，任何 Agent 可靠执行，零脚本依赖。
- Compact 内置于协议源（15 号模块）并内化进 agent-task；目标项目无需安装 init skill 即可压缩。

## 非目标

- 多 Agent 并发写 vault 的冲突处理（等真实痛点出现）。
- 决策 → 任务反向索引。
- 向目标项目安装运行时脚本。
- 重构中英双语包的语义同步机制（仍人工）。

## 设计

### 1. 记忆分层（修订版）

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | runtime / handoff / decisions | 高频更新；有预算线；compact 对象 |
| 治理文件 | governance / collaboration | 事件驱动更新（激活回路见 §5） |
| 结构文件 | index / project / tasks/README | 极少更新；index 为路由中枢 |
| 归档区 | tasks/* / decisions/ / details/* | 只增；压缩内容的去向 |

不变量：compact 不直接修改治理文件与结构文件，对它们只产出修订提案。

### 2. 索引原则（写入 `10-vault.md`）

> **增长进目录，读取走索引。** 任何会增长的内容（决策、任务、细节），正文进目录按需读取；索引层保证默认读取路径永远短。

应用：decisions 索引化（§4）、读路径分级（§6）。未来新增记忆类型一律按此模式扩展。index.md 保持纯路由、不存状态；活跃任务指针唯一存在于 runtime（避免双数据源）。

### 3. Compact 机制（新模块 `15-vault-compaction.md`）

#### 3.1 预算线（全部 `wc -l` 可度量）

| 对象 | 预算线 |
| --- | --- |
| runtime.md | > 120 行 |
| handoff.md | > 3 条交接 或 > 100 行 |
| decisions.md | > 150 行 或 > 8 条完整记录（触发首次拆分） |
| tasks/（不含 archive） | > 40 个文件（归档信号） |

#### 3.2 触发点

- agent-task 收尾的记忆更新步骤检测到超线（写入纪律的一环）。
- 用户显式指令（如 "compact vault"）。

#### 3.3 五阶段流程

**测量 → 分类 → 重组 → 校验 → 记录**

#### 3.4 各文件算法

- **runtime：重写而非删减。** 以"新会话冷启动需要什么"为唯一标准生成全新文件（阶段、活跃任务指针、约束、检查、下一步）。旧内容分流：进行中的保留；已完成的压成一行进 Recent Changes（执行历史已在 tasks/*）；结论进 decisions。
- **handoff：滚动窗口 + 分流。** 保留最近 1-3 次。更早的：有对应任务文件的，将失败尝试/教训合并进该任务文件 Execution Record；已被 runtime/decisions 吸收的允许删除（handoff 定义为瞬态上下文，删除不视为信息损失）；无在途任务时清回模板态。
- **decisions：生命周期四态 + 索引化。** 状态：`Active` / `Superseded by D-xxxx` / `Merged into D-xxxx` / `Expired`。首次拆分后 decisions.md 为纯索引（每条 1-2 行：ID、标题、状态、一句话实质、日期），正文入 `vault/decisions/D-xxxx-slug.md`。ID 顺序分配（现有最大 +1）。默认只读索引，按需读单条。
- **tasks：里程碑归档。** Accepted 或 Superseded 且早于最近里程碑的任务文件移入 `tasks/archive/`（纯移动，不改内容）。

#### 3.5 语义 / 非语义操作分离（安全阀核心）

- **非语义操作（模型自主执行）**：正文搬运、建立索引、状态标注为 Active、目录归档。零信息损失。
- **语义操作（模型仅提案，用户批量确认）**：Superseded / Merged / Expired 判定。输出候选清单 + 理由；**未确认的一律保持 Active**。
- 执行拆两批：非语义部分先执行先提交；语义清单经用户确认后作为第二批提交。

#### 3.6 校验不变量

1. 全部热文件回到预算内。
2. decisions 索引行与 `decisions/` 目录文件一一对应（无孤儿、无悬挂）。
3. 无 Active 决策丢失（压缩前的每条决策在压缩后索引中出现）。
4. runtime 活跃任务指针全部可解析。
5. compact 提交只含 `vault/` 变更。

#### 3.7 命令化校验清单（写入模块，模型直接执行）

- `wc -l` 检查各热文件行数。
- 索引 ID 列表与 `ls vault/decisions/` 比对（一一对应）。
- `git diff --stat HEAD` 确认提交范围仅 `vault/`。

#### 3.8 git 安全与回滚

- 前置：`vault/` 无未提交变更；否则先提交或中止。压缩永远从干净基线开始。
- compact 产出独立提交；校验失败即 `git checkout` 恢复 `vault/` 并报告失败的不变量。
- 任意时刻可 `git revert`。

#### 3.9 任务等级映射

| 压缩类型 | 等级 | 记录 |
| --- | --- | --- |
| 例行压缩（纯搬运、无首拆、无语义批次） | Level A | runtime 一行 |
| 结构性压缩（decisions 首次拆目录、含语义合并批次） | Level B | 任务文件 |
| governance 修订提案被接受后的治理变更 | Level C | 既有协议规则（需用户确认） |

### 4. decisions 形态

- 未超阈值：维持单文件（现有模板 + 生命周期状态标注）。
- 首次压缩拆分后：索引 + 目录（§3.4）。

### 5. 治理文件激活回路

- **A. collaboration 捕获点**：agent-task 收尾的记忆更新步骤追加一问——本次任务中用户是否表达了纠正/偏好/成功模式？有则按 `90-collaboration-profile.md` 既有规则记录（单次 = 观察，重复或用户确认 = 偏好）。
- **B. governance 反馈回路**：①治理升级事件触发且暴露规则空白时，记为修订候选；②compact 分类阶段交叉核对 governance 与现实（required checks vs runtime 实际检查命令、任务等级边界 vs 实际任务分布），输出修订提案清单。governance 修订 = Level C，需用户确认；compact 只出提案不改文件。
- **C. project 阶段同步**：里程碑或大任务 Accepted 时，核对 `project.md` 当前阶段与 runtime 一致。

### 6. 读路径分级（index.md 速查表）

index.md 内嵌约 10 行速查表：任务等级快速判定 + 授权等级一句话版。Level A 任务读完速查表即可开工；Level B/C 或判定模糊时读完整 governance.md。默认读取路径：`AGENTS.md` → `vault/index.md`（含速查表）→ `vault/runtime.md` →（按需）`vault/governance.md`。

### 7. details/ 创建信号具体化

将"存在真实重复读取场景"替换为协议既有信号：同一主题的长内容被重复读取/迁移 ≥ 2 次 → 创建 `details/<topic>.md`（与 `80-execution-patterns.md` 的 skill 沉淀信号一致）。

### 8. 写入纪律（agent-task 接线）

- 收尾记忆更新步骤追加预算检查：更新任一热文件时，顺手将溢出内容迁至正确去向。
- collaboration 捕获（§5A）。
- compact 触发检测：超线 → 执行 15 号模块流程或向用户提议。

## 改动面清单

### 协议源（中文，权威）

| 文件 | 改动 |
| --- | --- |
| `init/protocol/15-vault-compaction.md` | **新建**：§3 全部内容 + 校验命令清单 |
| `init/protocol/10-vault.md` | 分层表；索引原则节；结构图补 `decisions/` 与 `tasks/archive/`（压缩时创建，初始化不建）；**默认读取路径修订（governance 改为按需，见 §6）**；更新规则补触发线；details/ 信号具体化 |
| `init/INIT.md` | 模块清单插入 15 号；验收标准补压缩能力 |
| `init/protocol/README.md` | 模块列表同步 |
| `init/protocol/20-governance.md` | 升级事件 → governance 修订候选回路（§5B①） |
| `init/protocol/30-agent-entry.md` | 入口文件路由表述与 §6 读路径分级对齐（governance 按需） |
| `init/protocol/90-collaboration-profile.md` | 补捕获点与 agent-task 的接线说明（小改） |

### Skill 分发包（zh + en 两套）

| 文件 | 改动 |
| --- | --- |
| `assets/templates/AGENTS.md` | 入口路由与 §6 读路径分级对齐（governance 按需） |
| `assets/templates/vault/decisions.md` | 重写：生命周期四态 + 索引格式示例 + 归档约定 |
| `assets/templates/vault/index.md` | 速查表；decisions 索引优先读取路由；更新规则补压缩触发线 |
| `assets/templates/skills/agent-task/SKILL.md` | 写入纪律 + collaboration 捕获点 + 精简版 compact 流程（自包含，目标项目无 init/） |
| `references/protocol-model.md` | compact 概念节 + 分层修订 |
| `references/templates-guide.md` | 模板地图同步 |
| `references/protocol-source/` | 运行 `scripts/sync-skills.py` 自动重新生成（新模块自动进入） |

### 其他

- `README.md` / `README.en.md`：compact 特性说明 + 存量项目升级说明。
- `.gitignore`：白名单加 `docs/`（本设计文档所在地）。
- **预计不改** `scripts/agent-init.py`（adopt 清单无新增文件；`decisions/` 与 `tasks/archive/` 均为压缩时创建）——实现时验证。

## 错误处理

- 前置不满足（vault 有未提交变更）→ 先提交或中止。
- 校验失败 → `git checkout` 恢复 vault/，报告失败的不变量。
- 语义提案未确认 → 非语义批次先行执行提交；语义清单等确认后第二批。
- 任意时刻反悔 → `git revert`（compact 为独立提交且只含 vault/ 变更）。

## 验证

1. `python3 scripts/sync-skills.py --check` 通过（CI 同款检查）。
2. `uv run pytest` 通过。
3. 临时目录实测：初始化项目 → 人为膨胀三个热文件与 tasks/ → 走 agent-task compact 流程 → 核对全部校验不变量。

## 存量项目升级路径

已接入的老项目：重装 agent-native-init skill（或按 15 号模块手动升级 agent-task）→ 首次 compact 即完成 decisions 拆目录等结构迁移。

## 已确认的关键决策

| 决策点 | 结论 |
| --- | --- |
| 范围 | Compact + 冷热分层；不削减 vault 必备文件清单 |
| 交付 | 协议源 15 号模块 + 内化进 agent-task；不新建独立 compact skill |
| decisions 形态 | 索引 + 目录；超过阈值拆分；单文件起步 |
| 运行模式 | 写入纪律 + 门槛触发压缩（方案一） |
| 语义判定 | 模型仅提案、用户批量确认；未确认保持 Active |
| 附加优化 | 读路径速查表；tasks 里程碑归档；details 创建信号具体化；校验命令化 |
