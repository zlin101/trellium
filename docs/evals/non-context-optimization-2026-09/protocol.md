# 非 Context 优化实验协议（预注册版，2026-09-08 冻结）

> 本文件在采集任何候选结果**之前**写定并冻结。样本、主指标、停止条件、污染判定与真实/构造标签一经冻结不再修改；确需变更必须追加带日期的修订节，不得改写原文。主要证据优先级与实验单元定义见任务书 `docs/superpowers/plans/2026-09-08-non-context-vault-optimization-glm-plan.md` 第 1、5 节。

## 1. 公平性与纪律（全部实验适用）

- 同一模型、工具权限、代码快照、任务问题；Agent 行为 cell 使用无聊天历史的新会话，由 owner 投放 `prompts.md` 原文。
- prompts 与 scoring 分离；被测 Agent 读到 `scoring.md` 或任何 golden 答案即标 `contaminated`，不计入普通准确率样本（如实申报不扣分）。
- golden answer 只从现有权威源（git 状态、冻结的比较规则）构建，禁止从 A1/A2 输出反向生成。
- 每个可比较 cell 原则上重复 ≥3 次；不足 3 次标 `exploratory`，只给趋势结论。
- 硬指标（安全）优先于效率指标；任何候选硬指标退化即触发对应 kill criterion。
- 所有 fixture/构造样本标 `synthetic`，不计入 TASK-0001 的真实 TASK、转换、handoff 或跨项目覆盖。

## 2. 硬指标（冻结）

- authority / current contract / evidence boundary 判断退化：0
- 未经批准执行、自动批准或自动 accepted：0
- 旧证据被误标 fresh：0
- local 私有正文、凭据、请求体、响应体或完整 stdout 泄露：0
- proposal/derived view 被当成新的权威源：0

## 3. 效率指标（冻结）

首次正确行动前读取 UTF-8 bytes；文件数；工具调用数；wall-clock；状态变化人工同步文件数；owner 找到待决项打开文件数；receipt/slice/publish 新增写入 bytes 与维护时间；fresh 误报 historical 比例。强 Go 信号 = 中位数改善 ≥约 30% 且无安全退化；样本不足只给趋势。

## 4. 各候选预注册

### M2 Evidence Receipt（唯一可条件生产化）

- **Cells**：E0（现行自由文本验证记录）→ E1（+observed_at、HEAD/dirty、scope、commands、result、level、excluded 的结构化 receipt）→ E2（E1 + 确定性 freshness 比较，输出 fresh|historical|unresolved）。消融顺序 E2→E1→E0。
- **样本**：8 个 fixture 场景（synthetic，见 `results.md` §M2 矩阵行）× 3 cells；判断 cell 每组合 owner 新会话执行，重复 3 次（不足则 exploratory）。
- **主指标**：fresh/historical/unresolved 判断与 golden 一致率；次指标：bytes、工具调用、耗时、误标 fresh 次数。
- **冻结的 E2 比较规则**（在看到结果前冻结）：
  1. receipt 记录 head commit 与 tracked-tree 内容快照；比较对象是**当前 tracked 树内容**，不比较 commit hash（提交后内容等价 → fresh）；
  2. untracked 文件变化不影响 freshness；
  3. tracked 树任一文件内容变化 → historical（保守全树快照，接受无关 docs 变化产生的假阳性，FP 计入 R3 证据）；
  4. head 无法在当前历史解析（rebase/force-push）→ unresolved；
  5. level ≠ PASS：PARTIAL → historical；NOT_RUN → unresolved；
  6. scope/excluded 声明的外部系统变化不影响 freshness，但 freshness 仅覆盖声明的 scope。
- **停止条件（kill criteria，任务书 8.3）**：E1 与 E0 判断/成本无差异 → 删除 receipt；E2 未降成本或误标 fresh → 删除自动 freshness（保留 E1 或标实验性）；需要完整 stdout/秘密/代执行命令 → 立即 No-Go；写入税 > 收益 → 缩字段。
- **Go 后 v0 上限**：Markdown 内可选机器可读块；只记录已获准工作流执行的结果；freshness 三值；checker 只做格式/引用/保守快照判断；聚焦测试覆盖全部矩阵边界。

### M3 Local TASK 发布边界

- 前置：第二个真实 `task_storage: local` 项目 + 一个自然 accepted TASK。当前不满足 → 结论 `Blocked for evidence`；禁止改 tracked 为 local 或造演示项目。
- 预注册 cells P0/P1/P2 与停止条件按任务书第 9 节；R4 字段级 allowlist 试验待真实样本。

### M4 热路径分离

- 前置：真实长 TASK（现场 50–80 KB 级）。本仓库最大 TASK ≈14 KB → 只输出迁移规则草案（H0/H1/H2 设计见任务书第 10 节），不迁移、不改写历史。
- 未来样本到手后：小任务不强制拆分；H1 达到 H2 收益则删除物理拆分。

### M5 Slice-native / Decision 重开

- Slice：需两个真实多 amendment 并存任务 → 当前 `Blocked for evidence`；synthetic 仅可作 parser/test fixture。
- Decision：以 D-0004 为真实样本做 D0/D1 文本实验（D1 = 规范化 `reconsider_when` 小节草案）；D2 显式边仅在 ≥2 次真实导航/冲突失败后提案；缺边表示 unresolved。

### M6 Owner Inbox / Review Pack

- 前置：M2 证据来源确定 + ≥2 次 owner 查找待决项的真实成本事件。本仓库当前 `none observed in this repository` → 延后；O2 默认消融。

## 5. 结论类型与登记

每候选结论 ∈ {Go, No-Go, Blocked for evidence}，必须引用 preregistration 条目与原始结果行；No-Go 与 Blocked 都是有效交付。结果只写入 `results.md`（append-only），不进默认必读路径。
