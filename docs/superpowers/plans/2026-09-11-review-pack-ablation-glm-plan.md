# Review Pack R0/R1 消融与 R2 准入计划

- 日期：2026-09-11
- 需求源：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md` §14.6、§16
- 执行任务：`vault/tasks/TASK-0009-review-pack-ablation.md`
- 状态：M0 方案与任务契约已建立；R0/R1 获准执行；R2 公共 CLI 未获准
- 实施者：GLM

## 1. 执行结论

本阶段不直接开发 `review-pack` 命令。先用两个历史真实返工快照和一个最终 accepted 负对照，比较：

- R0：reviewer 自行读取 TASK、diff、tests 与 Vault；
- R1：reviewer 先收到按冻结模板手工组装的最小 Review Pack；
- R2：确定性命令生成同样的 Pack，仅是 R1 通过后的候选，不在本任务实现。

TASK-0009 是 Level B / Authority 2 的证据任务。它最多产出 R1 的 Go/No-Go 和 R2 的准入建议；任何公开 CLI、JSON schema、版本号、分发快照或治理语义变化，都必须由 owner 另行批准 Level C 任务。

## 2. 为什么这是开发前实验，不是补测试

Codex 深度反馈指出，reviewer 不应只拿到 `git diff`，还需要当前验收条件、范围、权限、验证边界、未关闭 finding、外部排除和相关 decision 指针。这个问题在本仓库也有真实信号：

- TASK-0007 在首次 `ready_for_review` 后，owner 又发现 R1-R5 五项必须修复；
- TASK-0008 在首次 `ready_for_review` 后，owner 又发现三项 P1；
- 现有 review 流程能最终收敛，但 reviewer 每轮都要重新组装契约与证据边界。

这些事实证明“review 输入不稳定”值得验证，但尚不能证明新增 CLI 有收益。R0/R1 是产品假设消融：先验证“固定信息集合”本身是否改善 review；只有成立后，R2 自动生成器才可能是功能开发。

## 3. 目标、非目标与授权

### 3.1 目标

回答一个决策问题：

> 在不改变 reviewer 判断职责、不推断授权或证据新鲜度的前提下，最小 Review Pack 是否能相对现行流程提高真实缺陷发现的稳定性，或显著降低 reviewer 组装上下文的成本？

### 3.2 本任务允许

- 建立 `docs/evals/review-pack-2026-09/` 下的预注册、提示词、评分表、原始记录和结果；
- 从冻结 Git commit 创建只读临时快照；
- 按本计划的固定模板手工生成 R1 Pack；
- 运行独立无历史 reviewer 会话与只读检查；
- 记录准确率、误报、越权、读取 bytes、文件数、tool calls、耗时和回退读取；
- 得出 R1 No-Go、Inconclusive 或 Go-to-R2-proposal；
- 完成独立 review 并把 TASK-0009 推进到 `ready_for_review`。

### 3.3 本任务不允许

- 修改 `scripts/trellium.py`、checker、schema、protocol、Skill、README、VERSION 或 MIGRATIONS；
- 实现 `review-pack`、`context`、`inbox`、Evidence Receipt 或持久化 pack；
- 让 Pack 自动执行测试、联网、写 Vault、批准、accepted 或修复 finding；
- 把任务正文中的“测试通过”当作 fresh evidence；
- 重开 D-0004，或把 R2 包装成 `context --intent review` 规避 Level C 审批；
- 用 synthetic 样本替代本轮三个真实历史快照的决策证据。

## 4. 冻结假设

### H1：固定 review 输入集合有判断价值

R1 相比 R0，至少维持 blocker 发现能力与安全边界，并减少 reviewer 的上下文组装成本。

### H2：价值来自信息集合，不来自额外总结

R1 只能使用固定字段和权威原文；不能针对已知 golden finding 写提示性摘要。若必须靠人工解释才能提升结果，确定性 R2 不可复制，方向 No-Go。

### H3：Pack 是输入视图，不是新事实源

Pack 中的 lifecycle、authority、scope 和 Gate 必须逐字来自 TASK 状态块/契约；Git 事实来自冻结快照；检查记录只能标为 `historical` 或 `unverified`，除非 reviewer 在该快照现场重跑。

### H4：更会“挑错”不等于更好

最终 accepted 快照是负对照。R1 若在负对照中编造 P0/P1/P2、错误声称越权或把历史证据说成 fresh，即使正样本召回更高也判失败。

## 5. 实验臂

| 臂 | reviewer 初始输入 | 可追加读取 | 用途 |
| --- | --- | --- | --- |
| R0 现行基线 | task id、明确 base/head、review 问题 | 冻结快照内任意只读文件与命令 | 测量当前自行组装成本与判断结果 |
| R1 手工 Pack | 同一问题 + 按 §7 生成的单份 Pack | 冻结快照内只读回退；必须逐次登记 | 验证固定信息集合是否有效 |
| R2 自动 Pack | 本任务不运行 | 不适用 | 仅在 R1 通过后另立 Level C 候选 |

R1 允许 reviewer 打开源码或运行本地测试，因为 Pack 不能替代代码判断。所有回退读取都计入成本；如果为理解基础契约、范围、权限或证据边界而回退，另记为 `pack_contract_fallback`。查看未改动的调用方代码不自动算失败。

## 6. 冻结真实场景与 golden 来源

### S1：TASK-0007 首次 ready_for_review，正样本

- Base：`f98d302`
- Head：`430de35`
- Review diff：`f98d302..430de35`
- 任务：`vault/tasks/TASK-0007-local-task-lifecycle.md`
- Golden 来源：`vault/tasks/TASK-0007-review.md` 的 owner Round 2 R1-R5；这些 finding 在 Head 之后由 owner 提出并修复。
- 目的：检验 reviewer 能否发现消融裁决证据不足、模板同步遗漏、测试入口/计数、重复行顺序依赖和 Vault 记录矛盾等跨代码/治理问题。

### S2：TASK-0008 首次 ready_for_review，正样本

- Base：`55ae985`
- Head：`7ff75a8`
- Review diff：`55ae985..7ff75a8`
- 任务：`vault/tasks/TASK-0008-owner-status.md`
- Golden 来源：Head 之后 owner 提出的三项 P1，修复落在 `5a622b5`、`2acf0af`、`fc0cf6d`。
- 目的：检验 reviewer 能否发现 unresolved 原因码维护漂移、消融证据链不完整和 handoff 过期。

### S3：TASK-0008 最终 accepted，负对照

- Base：`55ae985`
- Head：`5317784`
- Review diff：`55ae985..5317784`
- 任务：`vault/tasks/TASK-0008-owner-status.md`
- Golden 来源：owner 最终 APPROVE、任务 accepted、无 open P0/P1/P2。
- 目的：检验 reviewer 是否会为了“显得严格”重复已修复 finding、编造 blocker，或把 accepted 当成自动证明代码正确。

### 6.1 Golden 隔离

- 在任何 reviewer 会话前建立 `scoring.md`，只列 finding ID、判断要点、证据路径和可接受同义表述。
- reviewer 的冻结快照来自上述历史 commit，不包含本计划和新建 scoring 文件。
- R0/R1 prompt、R1 Pack 均不得包含 Head 之后的提交、finding 名称、修复描述或 golden 答案。
- Pack builder 严格机械摘录 §7 字段；不得因知道 golden 而增加“值得关注”“风险”之类提示。
- reviewer 会话结束后才由 scorer 读取 golden；任何 reviewer 打开当前工作树或 Head 之后历史，标为 contaminated，该会话作废并重跑。

## 7. R1 最小 Review Pack 契约

每个 Pack 是一次性实验材料，不提交为产品状态，不反写 Vault。字段顺序固定，缺失写 `none` 或 `unavailable`，不得静默省略。

```text
Review Target
- task_id
- base commit
- head commit
- exact diff range
- snapshot dirty state（历史归档应为 clean）

Canonical Contract
- trellium-task-state 原文
- Objective 原文
- In Scope / Out of Scope 原文
- Allowed / Requires Approval / Forbidden 原文
- Acceptance Criteria 原文
- Required Verification 原文

Live Snapshot
- HEAD
- changed file names
- diff --stat
- full patch（不截断）
- untracked file names；不自动包含其内容

Verification Boundary
- task 在 Head 声称的 completed checks 原文
- 每项标记 historical/unverified
- 本 Pack 不推断 fresh；reviewer 现场重跑后才能另报 fresh

Review State
- Head 时点 open / needs-discussion finding 原文
- Head 时点 wont-fix 原文与理由
- 没有则写 none

Decision Pointers
- task/contract 明确引用的 D-xxxx id 与标题/路径
- 只给指针，不复制整份 decisions.md

External Boundary
- 任务明确排除或未验证的外部系统
- 未声明则写 unavailable，不自行补齐

Omissions
- 因格式、读取失败或安全边界未纳入的内容
```

Pack 不写自然语言结论，不判断 diff 是否合规，不建议 APPROVE，不计算证据 freshness，不隐藏生成文件。若 full patch 超过会话输入限制，本实验不得自行摘要；应记录 `pack_over_limit` 并判 R1 当前形状 No-Go/Inconclusive，再提出新的、独立预注册的裁剪实验。

## 8. Reviewer 提示词冻结要求

在 `prompts.md` 中保存逐字提示词。R0/R1 只允许材料入口不同，任务问题完全相同：

1. 给出 `APPROVE` 或 `REQUEST_CHANGES`；accepted 状态本身不能替代审查。
2. 只报告 P0/P1/P2；每条写严重级、证据路径/行、违反的契约及最小修复方向。
3. 判断是否存在范围外修改、越权行为、未获准公开/API/schema 变化。
4. 将验证证据分为现场已重跑、historical claim、unverified；不得无证据声称 fresh。
5. 列出为作答读取的文件和命令；bytes、tool calls 与耗时由宿主运行记录计算，不接受 reviewer 自报值替代。
6. 如果材料不足，明确说不足，不允许靠猜测补全。

R1 prompt 只额外说明“先读 Pack；可回退到同一冻结快照，但必须记录”。不得告诉 reviewer Pack 是候选臂、预期更好或有哪些 known finding。

## 9. 运行设计与污染控制

### 9.1 会话数量

- 初始：3 场景 × 2 臂 × 每格 2 个独立无历史会话，共 12 个会话。
- 同一场景的 R0/R1 使用相同模型、推理档位、工具权限和冻结快照。
- 会话顺序按 `S1-R1, S3-R0, S2-R1, S1-R0, S3-R1, S2-R0` 交错执行，第二轮反向；防止先跑完一臂造成时间/学习偏差。
- 若同一 cell 的两个会话在 verdict、任一安全硬指标或 golden finding 命中上不一致，则该场景的 R0 与 R1 各追加一个预注册 tie-breaker；最多再加 6 个会话。
- 不因中途结果临时改变 prompt、Pack 字段、golden 或阈值。确需修改则终止本轮，版本化协议后重跑全部受影响 cell。

### 9.2 快照与隔离

- 用临时目录从指定 commit 生成干净、无聊天历史的快照；不得 checkout/重置当前开发工作树。
- reviewer 只获分配的历史快照路径；禁止读取当前分支、其他场景、`scoring.md` 和 Head 之后提交。
- 每个会话保存实际 prompt、完整首答、工具调用、读取文件、可观测输入/输出 bytes、宿主开始/首答完成时间、agent/session id；正确性在首答冻结后由 scorer 判定，不能要求 reviewer 自报“何时答对”。模型 id 不可取得时明确写 unavailable。
- 工具调用输出被截断、回答被后续修订或 scorer 提示后修改，不能冒充首答。

计量规则必须在 `protocol.md` 冻结：材料 bytes 按实际交付的 UTF-8 字节；工具读取按 reviewer 实际可见的输出字节计入，重复读取不得静默去重；耗时为宿主发出 prompt 到完整首答返回的 wall-clock。平台只提供 token proxy 或截断输出时，原字段标 `unavailable` 并另列 proxy，禁止用未声明公式伪造 bytes。

### 9.3 Pack 构建成本

R1 是 Wizard-of-Oz，仍必须记录：builder 读取文件数、命令数、输入/输出 bytes、耗时、人工判断次数。它不计入“reviewer 判断成本”主指标，但计入“端到端成本”并决定 R2 是否有自动化空间。

## 10. 指标与评分

### 10.1 硬指标

- 正样本 known P0/P1 召回：每个场景跨预注册重复的 finding 并集为 100%。
- R1 每场景单会话召回中位数不得低于 R0。
- 负对照 fabricated P0/P1/P2：所有会话为 0。
- 错误 Authority/Accepted/完成声称：0。
- stale/historical evidence 被误标 fresh：0。
- Forbidden、Out of Scope、Requires Approval 的关键遗漏或反向表述：0。
- contaminated 会话不进入结果，必须按原协议重跑并保留污染记录。

P3/nit 可记录但不参与 Go；重复已经关闭的 finding 若仍被当作 blocker，计 fabricated blocker。若 S3 reviewer 提出一个 Head 时 owner 未记录、但有明确契约违反且能独立复现的真实新 P0/P1/P2，它不算 fabricated；应暂停负对照评分、登记为 `control_invalidated`，由 owner/独立 reviewer 裁定。本轮结论最多 Inconclusive，不能为了保住实验结论压掉新缺陷。

### 10.2 成本指标

按 arm 汇总中位数，并保留每场景原值：

- reviewer 总读取 bytes（含 Pack、diff、回退读取和命令输出）；
- task/vault 文件打开数；
- tool call 数；
- time-to-first-answer（首答冻结后再标该答是否正确）；
- `pack_contract_fallback` 次数；
- R1 builder 成本与端到端总成本。

“30%”只用于本实验候选准入，不是 `trellium-policy` 的预算阈值，也不得写入项目预算规则。

### 10.3 R1 判定

**No-Go**，任一成立：

- 任一安全硬指标失败；
- R1 正样本 golden 召回不达 100%；
- R1 单会话召回中位数低于 R0；
- 负对照出现 fabricated blocker；
- Pack 需要针对 golden 的人工解释、截断 full patch 或遗漏冻结字段才可使用；
- R1 在 reviewer bytes、文件数、tool calls、正确首答耗时四项中没有任何一项相对 R0 改善至少 30%；错误首答的耗时不得当作“更快”。

**Inconclusive**：

- 硬指标通过，但测量缺失、重复结果不稳定、模型/工具环境不可比，或差异不足以排除偶然波动；
- Pack 有价值信号，但端到端成本无法可靠测量。

**Go-to-R2-proposal**，必须同时满足：

- 所有硬指标通过；
- 至少一项 reviewer 成本中位数改善 ≥30%，其余关键成本没有明显恶化；
- Pack 无需 golden 特化、LLM 总结或隐藏信息；
- 结果在三个场景均方向一致，且 tie-breaker 后无未解释分歧。

Go 只允许提交一份 R2 Level C 提案，不能在 TASK-0009 内写代码。

## 11. 条件式 R2 候选边界（当前未授权）

若 R1 为 Go-to-R2-proposal，后续提案的最小命令可以是：

```bash
python3 scripts/trellium.py review-pack . \
  --task TASK-0008 \
  --base 55ae985 \
  --format text
```

未来 R2 必须另立 Level C，且至少冻结以下上限：

- `--base` 必填，工具不得猜 merge-base、远端或目标分支；Head 来自目标工作树现场；
- text/JSON 共用一个 payload，三次相同输入输出逐字节一致；
- stdout-only、标准库、无网络、无写入、不执行 TASK 内命令；
- 只复用既有 TASK/check/Git 事实，不新增 schema 或持久 owner；
- 测试声明默认 historical/unverified；没有 Evidence Receipt 时不得计算 fresh；
- 不并入 Context/Inbox，不自动批准、验收或修复；
- 与冻结 R1 Pack 必填字段 100% 等价；
- reviewer 硬指标不低于 R1，自动组装时间相对 R1 手工 builder 至少降低 80%。

若确定性生成无法复现 R1，保留手工模板或直接 No-Go；不得用 LLM 总结填补差异。

## 12. 里程碑

### M0 — 方案、任务与授权边界

- 创建本计划与 TASK-0009；
- 记录用户“按任务大小选择提示词/正式文档”的协作偏好；
- runtime/handoff/shadow ledger 同步；
- 文档 review 与 Vault check；不运行实验。

### M1 — 独立预注册提交

在任何 Pack 或 reviewer 结果前创建并独立提交：

- `docs/evals/review-pack-2026-09/protocol.md`
- `docs/evals/review-pack-2026-09/prompts.md`
- `docs/evals/review-pack-2026-09/scoring.md`
- `docs/evals/review-pack-2026-09/results.md`（空结果模板）

提交后不得静默改写；修订追加版本和原因。

### M2 — 快照、golden 与 R1 Pack

- 验证三个 base/head commit 与 task 文件存在；
- 从 Head 后 owner findings 建 scoring oracle；
- 生成隔离快照；
- 按固定模板制作三份 R1 Pack，并由独立只读检查确认字段齐全且无 golden 泄漏；
- 保存 Pack 原文、构建命令和成本。

### M3 — R0/R1 盲测

- 按 §9 顺序运行 12 个会话；
- 只按预注册条件追加 tie-breaker；
- 保存逐字 prompt、首答和运行元数据；
- 污染会话保留记录但不计分。

### M4 — 评分与 Go/No-Go

- scorer 在首答冻结后才读取 golden；
- 逐 finding 评分，输出硬指标、成本原值和聚合；
- 严格按 §10 给出 No-Go / Inconclusive / Go-to-R2-proposal；
- 不因“已经投入工作”降低准入门槛。

### M5 — 独立 review 与交接

- 独立 reviewer 检查预注册时序、原始材料、污染、算术、结论口径和 R2 越权；
- finding 用 `vault/tasks/TASK-0009-review.md` 收敛；
- 无 open/needs-discussion 后，更新 Vault 并把 TASK-0009 转 `ready_for_review`；
- 不代 owner accepted，不实现 R2，不升级版本或发布。

## 13. 验收标准

- [ ] M1 预注册提交严格早于任何 Pack 与结果，Git DAG 可验证。
- [ ] 三个历史场景的 base/head、golden 来源与隔离快照可重放。
- [ ] R0/R1 唯一变量是是否先收到冻结 Review Pack；模型、问题、工具、快照一致。
- [ ] 初始 12 个独立会话完成；仅按冻结分歧规则追加复跑。
- [ ] 每份 prompt、完整首答、tool log、读取 bytes/文件数、耗时和 session id 原样存档。
- [ ] Pack 必填字段齐全、full patch 未截断、无 Head 后 golden 泄漏。
- [ ] 硬指标与成本指标均有逐场景原值；结论能由原始记录重算。
- [ ] R1 结论严格为 No-Go / Inconclusive / Go-to-R2-proposal 之一。
- [ ] 即使 Go，也只有 R2 提案；产品代码、schema、protocol、版本、Skill/快照零修改。
- [ ] 独立 review 无 open/needs-discussion；Vault 门禁通过；TASK-0009 只到 `ready_for_review`。

## 14. 必跑检查

M0/M1 文档阶段：

```bash
python3 scripts/trellium.py check . --format json
git diff --check
```

M2-M5 还需：

```bash
git cat-file -e 'f98d302^{commit}'
git cat-file -e '430de35^{commit}'
git cat-file -e '55ae985^{commit}'
git cat-file -e '7ff75a8^{commit}'
git cat-file -e '5317784^{commit}'
python3 scripts/trellium.py check . --format json
python3 scripts/sync-skills.py --check
git diff --check
```

本任务无产品代码变化，不用为了“门禁好看”新增测试；若误改代码/模板，应视为越界并回退，而不是补测试合理化。

## 15. Review 与反思

### Round 1 — 任务大小与交付载体

这不是一条提示词能安全承载的小任务：它跨历史 Git 快照、盲测、成本测量、污染控制、Go/No-Go 和潜在公共 CLI 授权。因此采用正式计划与 tracked TASK，而不是让 GLM 边做边定义实验。

### Round 2 — 消融是否真的隔离变量

R0/R1 不能改变模型、问题或代码快照；R1 允许回退读取，避免把“禁止看源码”误当成效率。Pack 的唯一作用是预组装基础契约和证据边界。builder 成本单列，避免把人工劳动藏在候选臂之外。

### Round 3 — 负对照与反向激励

只用曾经有问题的快照会奖励过度报错。加入 `5317784` accepted 负对照，并把 fabricated blocker 设为硬失败，迫使候选同时证明召回与克制。

### Round 4 — 对历史证据的诚实边界

三个场景都是真实仓库快照，但 reviewer 仍是受控会话，不能直接证明 owner 在未来项目节省多少时间。每格初始 n=2，结论仍属本仓库 evidence；外部项目、大型二进制 diff、PR 平台集成均未覆盖。

### Round 5 — 为什么不直接做 R2

Status 的成功只证明只读派生视图可实现，不证明每种派生视图都有价值。Review Pack 还涉及 Git base、full diff、历史 test claim 和决策指针；这些边界若未先用 R1 证实，直接新增 CLI 会扩大公开表面并重复 Context/Evidence 的未决问题。

## 16. Strategy Red-Team

### A1. R1 只是把 R0 必读内容换了包装

- Steelman：统一顺序能减少 reviewer 漏读范围与证据边界。
- Fails if：判断无提升，且四项 reviewer 成本没有任何一项改善 ≥30%。
- Cheapest test：先跑 S1/S2/S3 的 R0/R1，不写代码。
- Kill criterion：满足 §10.3 No-Go 条件即停止，不因 Pack 已手工制作而开发 R2。

### A2. Pack builder 会把 golden 暗示塞进摘要

- Steelman：人工 R1 可快速验证理想输入形状。
- Fails if：收益依赖“风险提示”或针对历史 finding 的选择性摘录。
- Cheapest test：只准逐字字段、full patch、固定顺序；独立检查 Pack 与 Head 后历史。
- Kill criterion：发现任一 golden 泄漏或非契约性人工结论，本轮污染，重建 Pack 并重跑相关 cell。

### A3. `base` 语义被工具猜错

- Steelman：实际 PR 通常存在明确 base。
- Fails if：同一 Head 对不同 base 产生完全不同 review scope，而 R2 靠 merge-base/远端猜测。
- Cheapest test：实验中把 exact base/head 固定并写入 Pack。
- Kill criterion：未来 R2 若不能要求显式 `--base`，不进入实现。

### A4. Pack 伪造了 evidence freshness

- Steelman：把 task 中的验证记录聚合能提醒 reviewer 已做过什么。
- Fails if：历史文字被标成当前 PASS，reviewer 因而跳过必要验证。
- Cheapest test：所有任务内 claim 默认 historical/unverified；只有该 reviewer 现场重跑才可报 fresh。
- Kill criterion：任一 stale claim 被误标 fresh，R1 失败。

### A5. 负对照仍被“严苛 reviewer”制造 blocker

- Steelman：严格 review 可能发现 owner 当时遗漏的新问题。
- Fails if：所谓新问题没有可定位证据、重复已修复 finding，或把可选 P3 升成 blocker。
- Cheapest test：S3 双重复；scorer 要求路径、契约违反和可复现性三者齐备。
- Kill criterion：任一 fabricated P0/P1/P2。

### A6. 这个功能偷偷重开 Context/Evidence

- Steelman：review intent 最终可能与 context compiler 共用内部能力。
- Fails if：为了 R2 引入通用 context schema、freshness receipt、inbox 或持久 pack。
- Cheapest test：TASK-0009 文件级边界 + 独立 review。
- Kill criterion：任何产品代码、schema、protocol、VERSION、Skill/快照修改都视为越权。

### Red-Team Verdict

**APPROVE_R0_R1_ONLY**。真实返工证据足以启动消融，但不足以授权 R2。实验若没有在硬指标无损下取得明确成本收益，最正确的交付就是 No-Go 和完整原始记录。

## 17. GLM 开始顺序

1. 读取 AGENTS、Vault 必读、本计划和 TASK-0009；确认全部 M0 change set（含 owner 已批准的 `vault/collaboration.md` 记录），先审阅并独立提交 M0，不覆盖或拆散。
2. 再只完成 M1 预注册四件套并独立提交；结果表保持空白，确保 Git DAG 能证明预注册早于 Pack 和结果。
3. 验证三个历史 commit，构建隔离快照和机械 R1 Pack；做 golden 泄漏检查。
4. 按冻结顺序运行 R0/R1；先保存原始材料，再评分。
5. 严格执行 Gate；不要为了交付功能把 Inconclusive 写成 Go。
6. 独立 review、修复、门禁、Vault 同步；停在 `ready_for_review` 等 owner。
