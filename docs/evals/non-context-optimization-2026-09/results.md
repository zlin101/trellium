# 非 Context 优化实验 — 结果与基线（append-only）

> 只追加，不改写；错误记录以带日期更正说明修正。污染样本必须标注。本文件不在默认必读路径。

## M1 — 能力/问题基线矩阵（2026-09-08）

### 已被 09.3 解决（从候选范围删除）

状态块与 policy block；lifecycle/Authority/tracked-local 规范化；只读 `check` 与 CI 门禁；UTF-8 bytes 测量；runtime 投影校验；handoff live-Git 边界；覆盖计数单源（D-0005）。

### 证据来源等级

A = 深度使用现场报告（约 63 TASK、43–52 KB 默认读取、50–80 KB 大任务，外部项目）；B = 本仓库可重放观测；C = 受控实验；D = 单次主观感受。

### 候选问题证据矩阵

| 候选 | 问题证据 | 来源 | 本仓库事件（2026-09-08 审计） | 基线判定 |
| --- | --- | --- | --- | --- |
| M2 Evidence Receipt/freshness | 旧 PASS 被误作当前证据的摩擦明确存在 | A | none observed in this repository（S5 为 synthetic 探测，非真实事件） | 实验条件成立：synthetic 边界验证 + owner 判断 cell |
| M3 Local 发布边界 | accepted local TASK 的长期事实跨 clone 丢失风险 | A | n/a（本仓库 tracked，无 local 样本） | **Blocked for evidence**（需第二真实 local 项目 + 自然 accepted TASK） |
| M4 热路径分离 | 50–80 KB 长任务定位成本 | A | 本仓库最大 TASK 实测 14,150 bytes（TASK-0003），无热路径障碍事件 | 仅交付迁移规则草案（见下）；实现 No-Go until 真实长任务 |
| M5 Slice-native | 复杂 amendment TASK 的复合状态歧义 | A | none observed in this repository（无多 amendment 并存任务） | **Blocked for evidence**（需 ≥2 个真实复合任务；synthetic 仅限 parser fixture） |
| M5 Decision 重开 | 被否/冻结决策需要可判断的重开条件 | B | 正面样本：D-0004 prose 重开条件在本轮被准确引用（冷启动 S6 及 runtime 引用），无导航失败事件 | D1 文本实验条件成立；D2 显式边不触发（<2 次失败） |
| M6 Owner inbox | owner 查找待决项成本 | A（陈述）；B | none observed in this repository | 延后（缺 2 次真实成本事件 + M2 证据来源） |

### Bytes 实测（2026-09-08，HEAD 5924753 后工作树）

- 默认必读路径（AGENTS+index+runtime+project）：**14,288 bytes**；含 governance（B/C 任务）17,304 bytes。深度现场为 43–52 KB。
- 最大 TASK：14,150 bytes（TASK-0003）；次大 10,011（TASK-0004）。深度现场 50–80 KB。
- decisions.md：8,642 bytes / 140 行 / 5 records（接近索引化线 150 行/8 records，暂不触发）。
- 小仓库限制：以上规模差异意味着本仓库实验只能验证正确性与流程，不能证明热路径收益（R1 迁移性待第二项目）。

### 自 09.3 真实事件审计

旧 PASS 误用：none observed in this repository。重复状态：1 次（TASK 计数 3 vs 4 漂移，checker 0 finding，已由 D-0005 单源化修复）。owner 查找成本：none recorded。local 发布丢失：n/a。slice 歧义：none observed。来源均为 B 级（本仓库 git/ledger 可溯）。

## M2 — Evidence Receipt 消融

### 预注册

见 `protocol.md` §4（冻结于任何结果采集前）。判断 cell 由 owner 以无历史新会话投放 `prompts.md`，评分用 `scoring.md`。

### 确定性 freshness 矩阵（E2 冻结规则 × 10 边界场景，GLM 按规则推演，非 LLM 判断）

| 场景 | E2 比较器输出 | golden（scope-aware） | 假阳性? |
| --- | --- | --- | --- |
| 快照未变 | fresh | fresh | — |
| 相关代码变化 | historical | historical | — |
| 仅无关文档变化 | historical | fresh | **是（设计内 FP，R3 证据）** |
| untracked 文件变化 | fresh | fresh | — |
| 提交后内容等价（hash 变） | fresh | fresh | — |
| head 不可解析、树可比 | fresh | fresh | — |
| head 不可解析、树不可比 | unresolved | unresolved | — |
| PARTIAL | historical | historical | — |
| NOT_RUN | unresolved | unresolved | — |
| scope 外部系统变化 | fresh（限 scope） | fresh | — |

确定性矩阵结论：保守全树规则产生 **1/10 假阳性**（无关 docs 变化），无误标 fresh；FP 是否可接受由 agent 判断 cell 与 R3 kill criterion 裁定——若 agent 盲从比较器的 historical 判定（场景 C golden 为 fresh），E2 相对 E1 为负收益。

### 判断 cell（E0/E1/E2 × 场景 A-D，2026-09-08 执行完毕）

执行方式：协议修订 1——GLM 经隔离子代理投放（每 cell 一个全新无历史会话，封闭书，指示不读 docs/evals/）；无 cell 申报或发现读取评分材料，无 contaminated。n=1/cell，全部标 **exploratory**；成本仅有子代理 tokens/时长代理值，bytes 未采集。

原始首答（golden：A fresh / B historical / C fresh / D fresh）：

| Cell | 场景 A | 场景 B | 场景 C | 场景 D | 准确率 | tokens（代理成本） |
| --- | --- | --- | --- | --- | --- | --- |
| E2 自动比较 | fresh ✓ | historical ✓ | **historical ✗** | fresh ✓ | 3/4 | 9.0-9.5k |
| E1 结构化 receipt | fresh ✓ | historical ✓ | fresh ✓（以 scope 字段推理：变更在范围外） | fresh ✓ | 4/4 | 9.3-9.9k |
| E0 自由文本 | fresh ✓（答"new"） | historical ✓ | fresh ✓（以事实清单推理） | fresh ✓ | 4/4 | 8.9-9.5k |

要点：

- **E2 触发 kill criterion**：场景 C 比较器输出设计内假阳性（historical），被测会话盲从后判错——自动 freshness 未降低成本（时长/token 无优势）且引入误导。按任务书 8.3：删除自动 freshness；即使保留也仅为实验性。
- **E1 未显示相对 E0 的判断收益**（4/4 vs 4/4），且代理成本（tokens）持平略高、写入税为正（receipt 本身是新增强写内容）——触发"E1 与 E0 判断和成本无差异 → 删除 receipt 方案"（成本维度为代理值，exploratory）。
- 硬指标：误标 fresh = 0；无越权；无误判为 accepted。No-Go 是"无收益"，不是"不安全"。
- 已知局限（影响结论强度，均为如实声明）：n=1/cell；E0 材料直递未测真实仓库中的"检索成本"（深度现场的主要痛点之一）；bytes/耗时未采集。扩展任一项需新预注册。

### M2 最终结论（2026-09-08）

**No-Go**：不实现 Evidence Receipt v0，生产代码零改动；E2 自动 freshness 删除；E1 结构化 receipt 无已证明收益，方案归档（本文件与 prompts.md 样本保留为可复现记录）。重开路径：(a) owner 亲手投放并采集 bytes/耗时，验证成本维度；(b) 真实仓库中"自由文本记录散落难检索"场景的新预注册实验。

## M3 — Local 发布边界：`Blocked for evidence`

前置（第二真实 local 项目 + 自然 accepted TASK）不满足；按任务书第 9 节禁止构造。解除条件：owner 提供 local 项目并自然产生 accepted TASK 后，跑 P0/P1/P2（R4 allowlist 试验）。

## M4 — 热路径分离：实现 No-Go until 真实长任务；交付迁移规则草案

前置（50–80 KB 级真实 TASK）不满足；本仓库最大 14 KB。**迁移规则草案（供未来采用，不迁移任何现有 TASK）**：

1. 触发：TASK 实测超过 20 KB（本仓库最大实测 1.4 倍，冻结后按真实障碍修订）或 owner 报告定位障碍；
2. 第一步恒为 H1（不拆文件）：Current Contract 段（Objective/Scope/Authority/AC/Next Action）固定文件顶部，Execution Record 后置——v1 模板已基本如此，复核执行纪律即可；
3. H2 仅当 H1 后热路径仍超阈值：将旧 review/旧 evidence/执行流水移入 `TASK-xxxx-journal.md`（冷文件，原文移动不改写，源文件保留可验证链接）；
4. 不拆目录、不批量迁移、checker 不解析 journal；历史追溯问题的 golden 测试通过后才算迁移成功；
5. 真实长任务到手后跑 H0/H1/H2 对照，再冻结阈值与生产化提案。

## M5 — Slice-native：`Blocked for evidence`；Decision 重开：D1 足够，D2 不触发

- Slice：无 ≥2 个真实复合 amendment 任务；synthetic 只允许做 parser fixture，不产出收益结论。
- Decision：真实样本 D-0004 的 prose 重开条件已被准确使用（B 级证据，无失败事件）。按任务书 11.2，D1 规范化小节可作为**提案模板**（下方草案，未应用到真实文件）；D2 显式边需要 ≥2 次真实导航/冲突失败，当前 0 次，不提案。

D-0004 `reconsider_when` 草案（**proposal，未应用**；owner 采纳时才写入 decisions.md）：

```text
### Reconsider when（D-0004 提案草案）
- 真实工作累计出现 ≥2 次可复现的契约、授权或证据边界误判（事件须先登记于 shadow ledger）；
- 持续记录到明显的上下文读取成本，且 bytes/耗时数据已补齐；
- owner 明确批准手工 A/B，且结果证明成本降低 ≥约 30% 且无准确率、越权、验收判断退化。
```

## M6 — Owner Inbox：延后

缺 2 次真实 owner 查找成本事件（`none observed in this repository`）且依赖 M2 的证据来源确定。O2 拆分命令默认消融的判定继续有效。

## 汇总决策矩阵（2026-09-08，M2 判断实验后终版）

| 候选 | 结论 | 依据 |
| --- | --- | --- |
| M2 Evidence Receipt | **No-Go**（exploratory）：E1=E0 无收益，E2 假阳性误导；v0 不实现 | 本文件 M2 节 |
| M3 Local 发布边界 | **Blocked for evidence** | 缺第二 local 项目 |
| M4 热路径分离 | 实现 No-Go until 长任务；迁移规则草案已交付 | 最大 TASK 14 KB |
| M5 Slice | **Blocked for evidence** | 缺真实复合任务 |
| M5 Decision edges | D1 提案草案交付；D2 No-Go at current evidence | 0 次导航失败 |
| M6 Owner inbox | 延后 | 0 次真实查找成本事件 |

## 待 owner 执行

1. ~~M2 判断 cell~~ 已完成（2026-09-08，子代理 runner，exploratory）；M2 = No-Go。若 owner 不认可结论强度，可亲手重跑采集 bytes/耗时（需按协议修订流程登记）。
2. TASK-0005 review；D-0004 reconsider_when 草案采纳与否。
3. 第二真实 local 项目（解锁 M3、TASK-0004 M2）。
