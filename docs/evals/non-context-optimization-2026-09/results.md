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

- **E2 触发 kill criterion（准确率退化）**：场景 C 比较器输出设计内假阳性（historical），被测会话盲从后判错；时长/token 无优势。**E2 = No-Go**，自动 freshness 删除。
- **E1 = Inconclusive（未决）**：判断准确率与 E0 无差异（4/4 vs 4/4），但成本维度（bytes/耗时）未采集、材料为直递、n=1——任务书 8.3 的完整 kill criterion（"判断**和成本**无差异"）并未被完整触发。receipt 方案既未证明收益、也未被证伪。
- **E0 基线在本设计下已足够**：自由文本 + 事实清单即可全对。已知局限：材料直递未测"从散落记录中检索证据、scope 与适用版本"的成本（深度现场的主要痛点），检索场景需新预注册实验。
- 硬指标：误标 fresh = 0；无越权；无误判为 accepted。
- 已知局限（如实声明）：n=1/cell；成本数据未采集（子代理 runner）；synthetic 材料不证明生产收益。

### M2 最终结论（2026-09-08；owner review round 2 修正口径）

- **E2 自动 freshness：No-Go**（准确率退化，kill criterion 成立）。
- **E1 结构化 receipt：Inconclusive / Blocked for cost evidence**（判断无差异但成本未测；不能声称触发完整 kill criterion）。
- **Evidence Receipt v0：本周期 No-Go for implementation**（零代码）；**Evidence Receipt 方向整体未被证伪**，重开路径：(a) owner 亲手投放并采集 bytes/耗时，补全成本维度；(b) 真实仓库中"自由文本记录散落难检索"场景的新预注册实验；(c) 若未来成本证据成立，按 8.4 上限重新提案。

### 原始首答存档（12 cell verbatim，2026-09-08 执行记录）

E2-A：`fresh —— 记录的 HEAD（9f1c2ab）与当前 HEAD 一致，tracked 树摘要 t1 与当前树完全一致，worktree 状态 clean 也吻合。验证观察时间（2026-09-08）为当天，范围内命令结果为 PASS，且被排除项（external CI、GitHub Releases）不涉及本次判定。因此在给定材料下，该验证记录仍可作为当前代码树已通过这些验证的证据。`

E2-B：`historical —— 验证记录锚定的是 commit 4a7b1c0 的 tracked tree（t2），而事实清单权威表明此后 scripts/trellium.py 已被修改且未提交、工作树 dirty，即当前树与被验证的树不一致。该文件恰好位于验证 scope（scripts/）内，因此 PASS 只能证明旧树状态通过验证，无法证明当前代码树通过。comparator 规则（t2 != current → historical）与事实一致，判定明确无歧义。`

E2-C：`historical —— 记录的校验基准 tracked_tree "t3" 是对提交 7c8d9e0 时整个被跟踪树的指纹，而当前树因 docs/notes.md 变化已与之不等，比较器判定失败即降级为 historical。尽管变更仅在文档且验证范围 scripts/ 未变，该记录的效力规则以整树一致为准，因此不能再作为"当前代码树已通过验证"的新鲜证据。`

E2-D：`fresh —— 记录的 head aa11bb2 虽已不在当前历史（因 rebase），但事实清单权威确认 tracked 树 t4 与当前树逐字节一致，验证针对的是代码内容而非提交号。被验证的命令作用域（scripts/、init/）属于 tracked 内容且未发生任何变化，因此当时的 PASS 结果对当前代码树同样成立。记录中 worktree 为 clean 也排除了未跟踪文件影响，无失效信号。`

E1-A：`fresh —— 记录的 head（9f1c2ab）与当前 HEAD 一致，事实清单明确 tracked 树与记录时完全一致且工作区干净，即被验证的代码状态至今未变。观察时间与当前日期同为 2026-09-08，无时效性疑虑；excluded 项（外部 CI、GitHub Releases）只是界定证据范围，不影响对所列 unittest 命令的证明力。因此该记录仍可作为"当前代码树已通过这些验证"的证据。`

E1-B：`historical —— 验证记录的 scope 明确为 scripts/，而 scripts/trellium.py 恰好在记录生成后发生了未提交修改，即当前工作树在验证范围内已偏离被验证状态（head 4a7b1c0），该 PASS 不再覆盖当前树。记录本身如实描述了 4a7b1c0 时刻的状态，因此是有效但过时的历史证据，而非无效或存疑（非 unresolved）。要在当前树上重新确立证据，需在 dirty 工作树下重跑 python3 -m unittest scripts.test_trellium 并生成新记录。`

E1-C：`fresh —— 记录的 head（7c8d9e0）与当前提交一致，且观察时间为今天（2026-09-08）；此后唯一变化是 docs/notes.md 增加笔记，该文件不在验证范围（scope 为 scripts/，排除外部 CI）内，scripts/ 与 init/ 均未变。因此被测代码与当前树完全相同，PASS 结果仍适用于当前代码树的受验证范围。worktree 标记为 dirty 不影响结论，因为事实清单已确认自记录以来范围内文件无任何改动。`

E1-D：`新鲜 —— 记录所针对的 tracked 树（t4）与当前树逐字节一致，验证命令又只作用于 scripts/ 与 init/ 的代码内容，因此 PASS 结果对当前代码树依然成立。HEAD 从 aa11bb2 变为 cc33dd4 仅是一次内容为空的 rebase，不改变任何被验证的树内容。记录中 worktree 为 clean 且排除项（external CI）未涉足，也不存在使证据失效的未覆盖改动。`

E0-A：`new（= fresh）—— 验证记录的 commit（9f1c2ab）与当前 HEAD 完全一致，且 git status 干净、tracked 树与记录时逐字节相同，说明被验证的代码状态未发生任何变化。在此前提下，该验证结果可直接沿用为当前代码树已通过这些验证的证据。材料中不存在环境变更、部分通过或其他削弱有效性的信息。`

E0-B：`historical —— 该验证记录仅覆盖 commit 4a7b1c0 时的代码状态，而此后 scripts/trellium.py 已有未提交的工作树改动，当前代码树与已验证状态不一致。修改的恰是被测代码，无法保证 87/87 的测试结果在当前树上仍然成立。因此该记录只能作为历史证据，不能证明当前代码树已通过验证。`

E0-C：`fresh —— 验证后仅 docs/notes.md 增加了笔记，属于文档性变更，而被验证的 scripts/ 与 init/ 均未改动，unittest 与 vault check 的结果不会因此改变。因此该验证记录仍可作为当前代码树已通过这些验证的证据。`

E0-D：`fresh —— 该记录虽锚定于 aa11bb2，但事实清单表明当前 HEAD cc33dd4 的 tracked 树与记录时逐字节一致（rebase 仅为空内容变动），被验证的代码内容完全相同，unittest 87/87 的结果对当前树依然成立。提交哈希的变化不涉及任何代码内容差异，不构成使验证失效的因素。因此该验证记录仍可作为"当前代码树已通过这些验证"的证据。`

## M3 — Local 发布边界：`Blocked for evidence`

前置（第二真实 local 项目 + 自然 accepted TASK）不满足；按任务书第 9 节禁止构造。解除条件：owner 提供 local 项目并自然产生 accepted TASK 后，跑 P0/P1/P2（R4 allowlist 试验）。

## M4 — 热路径分离：实现 No-Go until 真实长任务；交付迁移规则草案

前置（50–80 KB 级真实 TASK）不满足；本仓库最大 14 KB 且无任何阅读障碍事件——**不预设数值阈值**（owner review round 2 修正：原草案的 20 KB 数字无证据依据，已删除；阈值必须从真实障碍事件 + H0/H1/H2 基线中产生）。**迁移规则草案（供未来采用，不迁移任何现有 TASK）**：

1. 触发：出现真实阅读障碍事件（Agent/owner 因 TASK 过长定位失败的具体事件，登记于 ledger），且 H0/H1/H2 基线对照完成——两者齐备后才冻结数值阈值；
2. 第一步恒为 H1（不拆文件）：Current Contract 段（Objective/Scope/Authority/AC/Next Action）固定文件顶部，Execution Record 后置——v1 模板已基本如此，复核执行纪律即可；
3. H2 仅当 H1 后热路径仍超冻结阈值：将旧 review/旧 evidence/执行流水移入 `TASK-xxxx-journal.md`（冷文件，原文移动不改写，源文件保留可验证链接）；
4. 不拆目录、不批量迁移、checker 不解析 journal；历史追溯问题的 golden 测试通过后才算迁移成功。

## M5 — Slice-native：`Blocked for evidence`；Decision 重开：**D0 sufficient，D1/D2 当前 No-Go**

- Slice：无 ≥2 个真实复合 amendment 任务；synthetic 只允许做 parser fixture，不产出收益结论。
- Decision：真实样本 D-0004 的 prose 重开条件（D0）已被准确使用且无失败事件；**owner review round 2 裁定：D0 sufficient，D1/D2 当前 No-Go**——D-0004 已完整包含相同的三条重开条件，无需追加 Reconsider when 重复段落（消融原则：能由更小方案解决时不升级）。下方草案保留为已否决记录。

~~D-0004 `reconsider_when` 草案~~（**已否决，2026-09-08 owner review round 2：D-0004 原文已含相同条件，D1 无增量**；未应用过）：

```text
### Reconsider when（D-0004 提案草案——已否决）
- 真实工作累计出现 ≥2 次可复现的契约、授权或证据边界误判（事件须先登记于 shadow ledger）；
- 持续记录到明显的上下文读取成本，且 bytes/耗时数据已补齐；
- owner 明确批准手工 A/B，且结果证明成本降低 ≥约 30% 且无准确率、越权、验收判断退化。
```

## M6 — Owner Inbox：延后

缺 2 次真实 owner 查找成本事件（`none observed in this repository`）且依赖 M2 的证据来源确定。O2 拆分命令默认消融的判定继续有效。

## 汇总决策矩阵（2026-09-08 终版；owner review round 2 修正口径后）

| 候选 | 结论 | 依据 |
| --- | --- | --- |
| M2 E2 自动 freshness | **No-Go**（准确率退化：场景 C 盲从假阳性） | 判断 cell + 确定性矩阵 |
| M2 E1 结构化 receipt | **Inconclusive / Blocked for cost evidence**（判断与 E0 无差异，成本未测，不构成完整 kill criterion） | 判断 cell 局限声明 |
| M2 Evidence Receipt v0 | **本周期 No-Go for implementation**（方向未被证伪） | E1 未决 + E2 No-Go |
| M3 Local 发布边界 | **Blocked for evidence** | 缺第二 local 项目 |
| M4 热路径分离 | 实现 No-Go until 真实障碍+基线；迁移规则草案已交付（无数值阈值） | 最大 TASK 14 KB、零障碍事件 |
| M5 Slice | **Blocked for evidence** | 缺真实复合任务 |
| M5 Decision edges | **D0 sufficient；D1/D2 当前 No-Go**（D-0004 已含相同条件） | owner review round 2 |
| M6 Owner inbox | 延后 | 0 次真实查找成本事件 |

## 待 owner 执行

1. ~~M2 判断 cell~~ 已完成；结论已按 round 2 口径修正（E2 No-Go / E1 Inconclusive / v0 本周期不实现）。
2. TASK-0005：终验已补记、最终 Gate 已勾选，**待 owner accepted**。
3. TASK-0006：六项 finding 已修复，按"E2 No-Go、E1 未决、v0 本周期不实现"口径**待 owner accepted**。
4. 第二真实 local 项目（解锁 M3、TASK-0004 M2）。
