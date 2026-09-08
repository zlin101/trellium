# Trellium 非 Context 优化：证据、发布边界与热路径实验计划（GLM）

> 本文是交给 GLM 的分阶段执行任务书。主要证据来自 Codex 深度使用评估，而不是仅依据当前仓库的短期冷启动结果。每项候选必须先做消融实验，再决定实施、缩减或放弃；No-Go 是有效交付。

- 日期：2026-09-08
- 状态：Ready for owner handoff；尚未授权实现
- 主要输入：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md`
- 当前协议版本：`2026.09.3`
- 当前约束：D-0004 Context No-Go 继续有效；本计划不实现或变相实现 Context Compiler
- 预期任务：owner 明确下发“按本文开始执行”后，GLM 建立新的 Level C / Authority 3 任务；建议使用下一个现场可用 TASK 编号

## 1. 反思：为什么需要重新立项

前一轮决策把 7 个冷启动场景的 7/7 结果赋予了过高权重。该结果能证明当前必读路径在一个小型、自托管、tracked 仓库中可以正确工作，但不能反证深度使用评估中已经出现的结构性摩擦：

- 深度评估来自约 63 个 TASK、43–52 KB 默认读取路径、多个 50–80 KB 大任务、过期 handoff 和 tracked/local 混合等长期现场；
- 当前冷启动样本只有一个仓库、每个场景一次，其中 3 个场景读取过评分材料，且 bytes/耗时未完整采集；
- 7/7 主要测“最终判断是否正确”，没有充分测量 Agent 为排除旧契约、旧 PASS、旧 slice 和重复状态所做的隐形推导；
- 当前 Trellium TASK 最大约 14 KB，不能代表深度评估里 50–80 KB 长任务的热路径成本；
- “暂不做 Context”只是否定一个解决方案，不等于证据时效、local 发布边界和历史膨胀问题不存在。

因此，本计划采用以下证据优先级：

1. 多任务长期使用中的真实缺陷和重复摩擦；
2. 当前仓库及第二真实项目的可重放观测；
3. 受控实验；
4. 单次主观感受或纯演示结果。

受控构造可以验证正确性，但不能单独证明生产收益。任何构造样本必须标 `synthetic`，不得计入 TASK-0001 的真实 TASK、转换、handoff 或跨项目覆盖。

## 2. 已完成能力与剩余问题

09.3 已经完成以下基础能力，不得重复建设：

- TASK 的小型机器可读状态块与项目 policy block；
- lifecycle、Authority、tracked/local 的规范化；
- 只读、确定性的 `trellium.py check` 和 CI 门禁；
- UTF-8 bytes 测量；
- runtime 投影校验、handoff 的 live Git 边界；
- 覆盖计数的单一事实源（D-0005）。

本计划只评估六个非 Context 候选：

1. Evidence Receipt 与证据新鲜度；
2. accepted local TASK 的显式发布边界；
3. 当前契约与历史 journal 的热路径分离；
4. 复杂 amendment TASK 的 slice-native 状态；
5. 高价值决策的重开条件与显式关系；
6. 只读 owner inbox / review pack 派生视图。

其中 1 是当前唯一允许在本计划内进入生产实现的优先候选；2–6 先实验，是否生产化分别过 Gate，不捆绑交付。

## 3. 目标、非目标与成功定义

### 3.1 目标

- 让 PASS/PARTIAL/NOT_RUN 能回答“针对哪版代码、什么范围、什么环境、排除了什么”；
- 让 local TASK 的私有过程不泄露，同时让未来 clone 能恢复必要的长期契约；
- 让 Agent 不读旧 review/执行流水也能确定当前契约；
- 让复杂任务的当前 slice、授权和 Gate 不再挤进一个自然语言状态句；
- 让被否决或冻结的长期决策具有可判断的重开条件；
- 降低 owner 查找待批准、待验收和证据失效事项的成本。

### 3.2 硬指标

任何候选都不得以效率换安全。以下指标优先于 bytes、时间和工具调用数：

- authority / current contract / evidence boundary 判断退化：0；
- 未经批准执行、自动批准或自动 accepted：0；
- 旧证据被误标为 fresh：0；
- local 私有正文、凭据、请求体、响应体或完整 stdout 泄露：0；
- proposal/derived view 被当成新的权威源：0。

### 3.3 效率指标

- 首次正确行动前读取的 UTF-8 bytes；
- 文件数、工具调用数和 wall-clock 时间；
- 状态变化时人工同步的文件数；
- owner 找到待决项需要打开的文件数；
- receipt / slice / publish proposal 的新增写入 bytes 与维护时间；
- fresh 被误报 historical 的比例。

数值目标必须在 baseline 后冻结。除硬指标外，默认采用“中位数改善至少约 30%，且没有安全退化”作为强 Go 信号；样本太少时只给趋势结论，不伪造统计显著性。

### 3.4 明确不做

- `trellium.py context`、持久 context pack 或替代 AGENTS.md 必读路径；
- RAG、embedding、知识图谱、数据库、daemon、Web UI；
- 新全局 lifecycle、完整权限 DSL、自动审批、自动 accepted；
- 从 TASK 文本提取并自动执行 shell 命令；
- 保存完整 stdout、真实请求/响应、凭据或私有 URL；
- 批量迁移历史 TASK、强制每个 TASK 拆目录；
- 自动提交生成结果、自动发布 local TASK；
- worktree lock、lease 或多 Agent 分布式协调；
- 借本计划修改版本、tag、Release、CI 权限或业务代码。

## 4. 授权与执行纪律

Owner 把本文交给 GLM 并明确“开始执行”，只授权：

- M0–M2 的基线、实验和满足 Gate 后的最小 Evidence Receipt v0；
- M3–M6 的只读实验、文档提案和 Go/No-Go 结论；
- 为本任务更新必要的 `docs/`、`vault/`、`scripts/trellium.py`、聚焦测试、init 模板和同步快照，但生产代码修改仅限 M2 的 Evidence Receipt v0；
- 正常提交、推送 develop 并观察由该 push 触发的既有 CI。

以下动作仍需 owner 二次批准：

- M3–M6 任一候选进入生产 schema、checker 或 CLI；
- 改变 `trellium-task-state` schema_version 或既有字段语义；
- 新增公开 CLI 子命令；
- 改变 tracked/local 策略、自动生成 runtime 或修改治理规则；
- 发布新版本或创建 Release。

执行纪律：

1. 每个 milestone 前现场读取 `AGENTS.md`、Vault 必读文件、本计划、源评估和相关活跃 TASK；不相信本文中的动态 Git 快照。
2. M0 创建一个 Level C 任务。任务自身是 owner 立项的真实治理任务；实验 fixture、临时任务和模拟转换明确排除在覆盖计数之外。
3. 每个候选独立提交、独立 review；前一个候选的 open finding 未关闭，不进入生产化。
4. 状态变化先改 TASK 状态块，再同步 runtime；实验数据 append-only，错误记录只能追加更正说明。
5. 不静默覆盖用户改动；发现基线漂移先记录影响。
6. GLM 不得自行把任务推进到 accepted；最多进入 ready_for_review。

## 5. 统一实验协议

### 5.1 实验单元

对每个候选至少设置：

- `A0 Baseline`：09.3 当前行为；
- `A1 Minimal`：只加入最小信息或流程；
- `A2 Expanded`：加入候选的机械能力。

消融顺序必须是 A2 → A1 → A0。若 A1 已达到同等结果，删除 A2；若 A0 已达到同等结果且成本无明显差异，整个候选 No-Go。

### 5.2 公平性

- 同一模型、工具权限、代码快照和任务问题进行比较；
- 每个 Agent 行为 cell 使用无聊天历史的新会话，顺序随机或交叉平衡；
- prompts 与 scoring 分离，被测 Agent 读到 scoring 即标 `contaminated`；
- golden answer 只从现有权威源构建，不能从 A1/A2 的输出反向生成；
- 记录模型、日期、HEAD、dirty state、输入文件、bytes、调用数、耗时和首答原文；
- 每个可比较 cell 原则上至少重复 3 次；做不到就标探索性结果；
- owner 纠正次数按首答后实际纠正记录，不让主会话代替 owner；
- synthetic case 只用于边界正确性和回归测试，不作为真实收益证明。

### 5.3 三类结论

- `Go`：硬指标全通过，且最小候选相对 baseline 有明确收益；
- `No-Go`：baseline 已足够、收益不足、写入税更高或风险不可接受；
- `Blocked for evidence`：缺少第二 local 项目、长 TASK 或真实复杂 amendment，不能用构造样本替代。

## 6. M0 — Preflight、任务建立与预注册

### 操作

1. 现场核验分支、HEAD、工作树、版本、活跃任务和既有决策。
2. 完成 TASK-0005 当前状态复核；不得替 owner 自动 accepted，也不得把它的未决 review 偷渡进新任务。
3. 创建新的 Level C / Authority 3 TASK，引用本文并写清 Allowed / Requires Approval / Forbidden。
4. 新建冷路径实验目录，例如：

   ```text
   docs/evals/non-context-optimization-2026-09/
   ├── protocol.md
   ├── prompts.md
   ├── scoring.md
   └── results.md
   ```

   `scoring.md` 对被测 Agent 禁读；结果不得写进默认必读路径。
5. 预注册每个实验的样本、主指标、停止条件、污染判定和真实/构造标签，再采集结果。

### 验收

- [ ] 未把 7/7 冷启动结果解释为对深度使用反馈的反证；
- [ ] TASK/runtime 投影一致，实验样本不污染 TASK-0001 覆盖计数；
- [ ] prompts/scoring 隔离；
- [ ] 在看到候选结果前冻结 Gate；
- [ ] preflight 与基线差异已记录。

## 7. M1 — 当前能力与问题基线

建立一张“已解决 / 部分解决 / 未解决 / 当前无证据”的矩阵。至少复核：

- state/policy block、checker、bytes、tracked/local、runtime、handoff 是否已经覆盖源评估的 Phase 1；
- 当前所有 TASK/runtime/decision 文件的 bytes 和默认读取 bytes；
- 自 09.3 起旧 PASS 误用、重复状态、owner 查找、local 发布丢失、复杂 slice 歧义的真实事件；
- 哪些证据来自深度使用项目，哪些只来自 Trellium 自托管；二者不得混写成同一总体。

不得为了让候选成立制造事件。当前没有事件时写 `none observed in this repository`，同时保留深度评估中的外部现场结论。

### Gate

- [ ] 每个候选都有明确问题证据和证据来源等级；
- [ ] 当前仓库的小规模限制已写明；
- [ ] 已被 09.3 解决的能力从后续实现范围删除；
- [ ] 没有先冻结新的全局阈值。

## 8. M2 — Evidence Receipt 与新鲜度（第一优先）

### 8.1 要验证的假设

> 结构化 receipt 加上确定性快照比较，比自由文本 PASS 更可靠、更快地判断证据是否仍覆盖当前工作树，且不会形成新的执行器或泄密面。

### 8.2 消融 cells

| Cell | 内容 | 用于回答 |
| --- | --- | --- |
| E0 | 当前自由文本验证记录 | baseline 能否正确识别旧 PASS |
| E1 | 仅增加 observed_at、HEAD/dirty、scope、commands、result、level、excluded | 结构化 provenance 本身是否足够 |
| E2 | E1 + 确定性 freshness 比较，输出 fresh/historical/unresolved | 自动比较是否比人工判断额外有价值 |

至少覆盖：快照未变、相关代码变化、无关文档变化、未跟踪文件变化、提交后内容等价、无法解析旧 commit、PARTIAL/NOT_RUN 和明确排除外部系统。

### 8.3 Kill criteria

- E1 与 E0 判断和成本无差异：删除 receipt 方案；
- E2 未降低判断成本，或把旧证据误标 fresh：删除自动 freshness；
- 保守整树指纹因无关变化产生的 historical 假阳性不可接受：不得直接升级 scoped dependency fingerprint；先保留 E1 或把 E2 标实验性；
- receipt 需要保存完整 stdout、环境秘密或执行任意文档命令：立即 No-Go；
- 写入和维护成本抵消收益：缩减字段，不增加数据库或新服务。

### 8.4 Go 后的 v0 上限

- Markdown 内一个小型、可选、机器可读 receipt；不创建 evidence 数据库；
- 只记录已经由当前获准工作流执行的结果，不代运行命令；
- freshness 只标 `fresh | historical | unresolved`，不删除证据、不自动判任务 PASS/FAIL、不要求自动重跑；
- checker 只做格式、引用和保守快照判断；legacy 证据报告 unresolved，不猜；
- 最小聚焦测试覆盖所有实验边界；模板/skill/snapshot 仅按既有同步机制更新。

### 验收

- [ ] A0/A1/A2 原始记录和污染状态齐全；
- [ ] 旧证据误标 fresh = 0；
- [ ] receipt 不授予执行权限；
- [ ] 无 stdout/请求/响应/凭据入库；
- [ ] 独立 review 无 open finding；
- [ ] 若 Go，生产实现没有超出 v0 上限；若 No-Go，代码零改动并保留结论。

## 9. M3 — Local TASK 发布边界

### 前置条件

必须有第二个真实 `task_storage: local` 项目和一个自然完成的 accepted TASK。没有则结论只能是 `Blocked for evidence`；不得把 Trellium tracked 项目改成 local 或创建演示项目满足条件。

### 消融 cells

| Cell | 内容 |
| --- | --- |
| P0 | 当前流程：由 Agent 自行判断是否蒸馏长期事实 |
| P1 | accepted 时只提出一个固定问题：“是否产生未来 clone 必须知道的持久事实？” |
| P2 | P1 + 生成最小 published-truth 提案，owner 审阅后写入 decision/权威文档 |

用新 clone 验证：指定的长期事实能否恢复、私有过程是否泄露、proposal 是否被误作已发布事实、owner 修改提案的成本。

### 消融与停止条件

- P1 与 P2 同样可靠：只保留固定问题和文档流程，不开发生成器；
- P0 已能稳定恢复且没有 owner 查找成本：候选 No-Go；
- 任何私有 journal、失败尝试、review 流水或敏感内容进入 tracked 输出：立即停止；
- 发布动作必须由人审核，不能由 accepted 自动触发提交。

### 本计划交付边界

只提交实验记录、最小契约提案和 Go/No-Go；生产化需 owner 二次批准。

## 10. M4 — 当前契约与历史 journal 分离

### 前置条件

至少有一个真实任务达到可观察的热路径成本。当前 Trellium 最大 TASK 约 14 KB，只能提供小任务对照，不能替代源评估中的 50–80 KB 长任务。若拿不到长任务，只输出迁移规则草案，不修改现有 TASK。

### 消融 cells

| Cell | 内容 |
| --- | --- |
| H0 | 当前单文件布局 |
| H1 | 不拆文件，只把 Current Contract / Acceptance / Next Action 固定到顶部 |
| H2 | H1 + 仅将旧 review、旧 evidence 和执行流水移入链接的冷 journal/evidence 文件 |

同时测试两类问题：回答当前应做什么，以及追溯一次历史 finding。H2 不能用“找不到历史”换取热路径变短。

### 消融与停止条件

- H1 已达到 H2 的读取收益：删除物理拆分；
- 当前问题读取成本没有明显下降，或历史追溯准确率下降：No-Go；
- 小任务不强制拆目录；只对超过现场测量阈值且确有障碍的任务适用；
- 不批量迁移，不改写历史语义，移动后保留可验证链接。

### 本计划交付边界

只做临时副本/fixture 的对照和规则提案；生产迁移需 owner 二次批准。

## 11. M5 — Slice-native 状态与决策重开条件

### 11.1 Slice-native 消融

前置条件：至少两个真实任务同时存在多个 amendment/slice，且各 slice 的 lifecycle、Gate 或授权不同。仅有顺序历史、不同时并存的普通任务不算。

| Cell | 内容 |
| --- | --- |
| S0 | 当前任务级 lifecycle + prose |
| S1 | 仅增加可选 `current_slice`，其他信息仍在当前契约 |
| S2 | S1 + 可选 `slices[]`，每项复用现有 lifecycle 和任务 Gate |

- S1 已消除歧义：删除 `slices[]`；
- S2 不能显著降低“旧 slice accepted 被误套到新 slice”的错误：No-Go；
- 小任务出现额外必填字段或新全局 lifecycle：设计失败；
- 无真实复杂任务时保持 `Blocked for evidence`，synthetic 只做 parser/test fixture。

### 11.2 Decision 消融

以 D-0004 等已有重开条件的决策为真实样本：

| Cell | 内容 |
| --- | --- |
| D0 | 当前自然语言 Background/Decision/Impact |
| D1 | 仅增加规范化 `reconsider_when` 小节 |
| D2 | D1 + `affects`、`supersedes`、`implemented_by` 显式边 |

- 若 D1 足以稳定回答“何时重开”，不增加机器字段；
- 只有至少两次真实决策导航/冲突失败，D2 才能进入生产提案；
- 缺边必须表示 unresolved 并回退索引读取，不能解释为“没有相关契约”；
- 类型或边不能赋予文档权威，权威仍由 governance、owner 和任务状态决定。

### 本计划交付边界

只提交实验结果和最小 schema/文档约定提案；任何 state schema 或 decision 结构变化需 owner 二次批准。

## 12. M6 — Owner Inbox / Review Pack（只读派生视图）

此候选不实现 Context，也不增加持久状态文件。它必须直接读取现有权威状态；如果需要先复制一份索引或状态缓存，方案失败。

### 前置条件

- M2 已确定证据新鲜度的最小来源；
- 至少记录两次 owner/reviewer 为查找待批准、待验收、外部阻塞或 stale evidence 打开多个文件的真实成本事件。

### 消融 cells

| Cell | 内容 |
| --- | --- |
| O0 | 当前 runtime + TASK 手工查找 |
| O1 | 一次性只读 owner/review 报告原型，stdout 输出并带源文件/字段 |
| O2 | 拆分 inbox、review、explain 等多个命令或持久文件 |

O2 默认被消融：CLI 面和状态 owner 都会膨胀。只有 O1 无法表达两个明确不同的使用场景时才重新评估。

### Kill criteria

- 没有重复 owner 查找成本：延后；
- 输出不带来源、擅自总结授权或把 derived 当 normative：立即停止；
- O1 未减少 owner 打开的文件数/时间，或遗漏任一待决项：No-Go；
- 需要 Context Compiler、数据库或持久缓存才能工作：超出本计划。

### 本计划交付边界

只提交 stdout 原型/fixture、评估记录和 Go/No-Go；公开 CLI 需 owner 二次批准。

## 13. Red-Team：承重假设与最便宜测试

按“错误影响 × 可能错误 × 测试便宜程度”排序：

### R1：深度使用问题能迁移到 Trellium/其他项目

- **Claim：** 长期现场问题不是 Iris 单项目特例。
- **Fails if：** 第二真实项目和后续真实任务长期没有证据误用、发布丢失、slice 歧义或热路径成本。
- **本周证据：** 完成 M1 来源分层；取得第二 local 项目时按同一指标观测。
- **Kill criterion：** 只有 synthetic 能复现，两个真实项目均无事件且无成本改善。
- **Cheapest test：** 不写代码，先审计现有事件与一个真实 local accepted 任务。

### R2：结构化 metadata 会减少而不是增加写放大

- **Claim：** receipt/slice/edge 省下的推导成本大于新增维护税。
- **Fails if：** 每次状态或验证需要更多同步文件，且 Agent/owner 判断没有变快或变准。
- **本周证据：** 对每个 cell 记录新增 bytes、编辑位置数和维护时间。
- **Kill criterion：** A1/A2 成本高于 baseline 且硬指标无改善。
- **Cheapest test：** 先在临时 fixture 手写最小块，不先改 parser。

### R3：保守 freshness 足够有用

- **Claim：** 简单 HEAD/worktree 快照能阻止旧 PASS 误用，假阳性仍可接受。
- **Fails if：** 无关文档变化频繁把证据标 historical，导致持续无意义复核。
- **本周证据：** M2 的相关/无关/未跟踪变化矩阵。
- **Kill criterion：** 误标 fresh 任一次，或 historical 假阳性使 E2 不优于 E1。
- **Cheapest test：** 纯函数/fixture 比较，不执行真实测试命令。

### R4：发布边界不会变成隐私外泄器

- **Claim：** 最小提案能恢复长期约束而不复制 private journal。
- **Fails if：** proposal 需要读取/输出大量任务正文，或人不能可靠删去私密过程。
- **本周证据：** 一个真实 local accepted TASK 的字段级 allowlist 试验。
- **Kill criterion：** 任一私有事实进入 tracked proposal，或没有真实 local 项目可验证。
- **Cheapest test：** P1 固定问题，先不做生成器。

### R5：更复杂的 slice/派生视图真的必要

- **Claim：** 现有 lifecycle + prose 无法以较低成本表达复杂任务和 owner 待决项。
- **Fails if：** `current_slice` 或现有 runtime 已能稳定回答，且没有重复误判/查找事件。
- **本周证据：** 搜索真实复合状态和 owner 查找事件；不制造任务。
- **Kill criterion：** 缺少两个真实样本，或 S1/O0 与扩展方案等效。
- **Cheapest test：** 文本原型与新会话判断，不改 schema/CLI。

## 14. 综合决策矩阵

| Candidate | 当前证据 | 依赖 | 默认处置 |
| --- | --- | --- | --- |
| Evidence Receipt/freshness | 深度评估明确；当前仓库只验证过人工识别 | 无第二项目硬依赖 | 立即实验；唯一可条件生产化项 |
| Local publish boundary | 深度评估明确；当前仓库为 tracked | 第二真实 local 项目 | Blocked for evidence |
| Hot-path journal split | 深度评估有 50–80 KB 现场；当前仓库任务较小 | 真实长 TASK | 实验/提案，不迁移 |
| Slice-native state | 深度评估有复杂 TASK 现场；当前仓库样本不足 | 两个真实复合任务 | Blocked for evidence |
| Decision reopen/edges | D-0004 已证明 prose 重开条件可用 | 重复导航失败才需要 edges | 先试 D1；默认不扩 schema |
| Owner/review derived view | 深度评估有 owner 成本陈述 | evidence source + 两次真实成本事件 | 只读原型，默认不扩 CLI |

不能把六项合并成一个总分后全部 Go。每项独立决策；最小 cell 优先。

## 15. 提交、验证与 review

### 每个实现性提交必跑

```bash
python3 scripts/trellium.py check . --format json
python3 scripts/sync-skills.py --check
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
git diff --check
git status --short --branch
```

如果 tests 数量变化，按现场数量报告，不继续复制“87/87”。实验/文档-only milestone 至少运行 check、sync check、相关测试和 `git diff --check`；不得伪造未运行检查。

### Review 门

每个 milestone review 必须检查：

- 是否把 proposal/experiment 写成 approved behavior；
- 是否新增第二事实源；
- 是否扩大 CLI、依赖、权限或数据收集；
- 是否用 synthetic 代替真实收益证据；
- 是否改变 D-0004；
- 是否遗漏反例、污染样本或失败 cell；
- 是否可以进一步消融到更小方案。

finding 使用独立 review ledger。存在 `open` 或 `needs-discussion` 时不进入下一生产 milestone；`wont-fix` 必须交 owner 裁决。

## 16. 最终交付

GLM 最终应交付：

1. 一个可恢复的 Level C TASK 和完整 execution record；
2. M0–M6 的逐项 `Go | No-Go | Blocked for evidence` 表；
3. 每个实验的 preregistration、原始结果、污染标记和计算方法；
4. 若 M2 Go：最小 Evidence Receipt v0、聚焦测试、模板/snapshot 同步和迁移说明；
5. M3–M6 仅提交 owner 可审阅的生产化提案，不越过二次批准门；
6. 独立 review 及所有 finding 处置；
7. vault/runtime/handoff/decisions 的必要更新；只有 owner 作出长期选择时才写 decision；
8. 明确列出未验证边界、第二项目依赖和下一项最便宜实验。

任务完成代码与实验后只能进入 `ready_for_review`。Owner 可分别接受：

- Evidence Receipt v0；
- 各候选的 Go/No-Go 结论；
- 是否批准下一生产阶段。

不得用“CI 绿”替代 owner acceptance。

## 17. 给 GLM 的开始指令

Owner 可将本文连同下面一句发送给 GLM：

> 按 `docs/superpowers/plans/2026-09-08-non-context-vault-optimization-glm-plan.md` 开始执行。先现场复核并建立 Level C 任务；严格按预注册、单变量消融和停止条件推进。M2 只有实验 Go 后才能实现最小 Evidence Receipt v0；M3–M6 只做实验与提案，任何生产化需再次申请。Context 继续 No-Go，不得制造项目、TASK、转换或实验结果。
