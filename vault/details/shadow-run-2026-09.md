# Shadow Run 观测记录 — 2026-09

预注册的 K1-K4 实验观测。规则：只记录事实事件，不写感受；指标与成功标准一经写入不再修改；每条观测带日期与触发事件。试点任务见 `vault/tasks/TASK-0001-self-hosting-pilot.md`。

## Experiment contract reconciliation（2026-09-08，TASK-0003 M1）

本块按 `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md` 第 6 节追加。初版 ledger 使用的 K1-K4 标签与 2026-09-04 实施计划第 2 节预注册的 canonical 假设存在同名异义；自本日起以 canonical 定义为准。以下既有表格与观测行原样保留，不删除、不改写；各节标题保留初版标签作为历史出处。

| Canonical | 定义（2026-09-04 计划第 2 节） | 初版 ledger 对应 | 处置 |
| --- | --- | --- | --- |
| K1 | 状态块确实比纯 Markdown 更少漂移 | 初版 K1（同名同义） | 继续在初版 K1 表追加新观测 |
| K2 | 项目级 tracked/local 策略足够表达现实 | 初版 K3（同名异义） | 初版 K3 表即 canonical K2 观测表；标题保留历史原样 |
| K3 | 不解析任意 Markdown 也能产生高价值检查 | 初版缺失 | 用本块下方新建表，自 2026-09-08 起采集，不回填 |
| K4 | checker 应先于 context compiler | 初版缺失 | 用本块下方新建表，自 2026-09-08 起采集，不回填 |
| A1（辅助） | runtime 投影值得保留 | 初版 K2（同名异义） | 降为辅助指标 A1；初版 K2 表继续记录，不冒充 canonical K2 |
| A2（辅助） | 预算测量确有价值 | 初版 K4（同名异义） | 降为辅助指标 A2；初版 K4 表继续记录，不冒充 canonical K4 |

覆盖计数核对（**derived snapshot，截至 2026-09-09（TASK-0007 accepted 后刷新），审计基准 commit fd4287b**；事实源为本文件上方 append-only 事件行，本段仅为派生汇总，不得在他处复制维护——D-0005）：真实 TASK 共 6 个（TASK-0001/0002/0003/0004/0005/0006；TASK-0003-review.md、TASK-0006-review.md 为台账非实体）。计数规则：有 owner 立项且非演示交付的 Level B/C 任务计入；纯演示、纯为实验构造的 TASK 与一切 synthetic 实验样本不计入；TASK-0005/0006 均为 owner 立项的真实治理任务。观测到 lifecycle 转换 15 次（TASK-0001 draft→active、TASK-0002 active→blocked、TASK-0003 draft→active、TASK-0003 active→ready_for_review、TASK-0003 ready_for_review→accepted、TASK-0002 blocked→active、TASK-0002 active→accepted、TASK-0004 active→blocked、TASK-0005 draft→active、TASK-0005 active→ready_for_review、TASK-0006 draft→active、TASK-0006 active→ready_for_review、TASK-0005 ready_for_review→accepted（09-09）、TASK-0006 ready_for_review→accepted（09-09）、TASK-0007 ready_for_review→accepted（09-09）；TASK-0002/0004 创建时直接为 active，TASK-0006 创建时为 draft）。blocked→active 1 次。handoff：handoff.md 现存条目数 ≠ 历史跨 Agent handoff 次数（压缩归并会使条目减少）；**跨 Agent handoff 事件 2 次，均有交接前 check 留档**：①09-04 adopt 会话→Codex（TASK-0001 handoff 条目 + 上方 check 台账「adopt 后基线」0/0）；②09-04 Codex→09-08 GLM（TASK-0002 handoff 条目已并入任务文件 + check 台账「TASK-0002 发布前门禁」0/0）。TASK-0001 的 coverage gate（5 TASK / 6 转换 / 2 handoff / 1 blocked→active）继续有效，但不替代 canonical K1-K4 的跨项目证据要求。

### Canonical K3 — 不解析任意 Markdown 也能产生高价值检查（2026-09-08 起）

两个真实 Vault 只读运行；记录 finding 是否对应真实修复，以及已知遗漏。

| 日期 | Vault | 触发 | errors / warnings | 是否产生真实修复 | 已知遗漏 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-08 | trellium（本仓库） | TASK-0003 M1 校准后 check | 0 / 1 | 否：预期瞬态 finding（tracked 任务未提交窗口，设计内行为），随例行提交消除，不构成缺陷捕获证据 | 暂无 | review round 1 更正定性（原行误标为"真实修复"）；canonical K3 尚无缺陷捕获类观测 |
| 2026-09-08 | trellium（本仓库） | 交接复核发现计数不一致（runtime/ledger 写 3 TASK，checker 报 current_task_files=4） | 0 / 0 | 是：人工核对后更新 runtime 与 ledger 计数；checker 未参与发现 | checker 不解析自然语言统计数字，prose 计数过期不可见 | 真实遗漏样本，佐证 K3 边界；同时是跨文档计数漂移的候选证据（单次，不自动触发 Phase 2 准入） |

成功标准：finding 对应真实修复动作。Kill criterion：连续两次真实检查只有无行动价值的 warning，且遗漏已知的状态/storage/预算错误。

### Canonical K4 — checker 应先于 context compiler（2026-09-08 起）

记录 checker 发现数、状态判断耗时、owner 手工打开文件数与上下文选择成本。

| 日期 | 事件 | checker 发现数 | 状态判断耗时 | owner 打开文件数 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-08 | GitHub Actions 首跑（develop push，gate job） | 0 | n/a（CI 自动执行） | 0 | run 34181086563：self-hosting check 首次在 runner 执行，0 finding，job success |
| 2026-09-08 | 冷启动基线 S1-S7（各独立新会话，详见 cold-start-baseline-2026-09.md） | n/a | 每场景读取 5-16 个文件，bytes/耗时大部分未采集 | 0（owner 仅记录，未打开文件代答） | 判断 7/7 正确、0 越权、0 过期证据误用；上下文选择成本有界但可见——K4 kill criterion 的首轮量化输入 |

Kill criterion：状态准确率已接近 100%，checker 零有效发现，但上下文读取成本仍明显高；达到时重新评估最小 context manifest，不继续扩 checker。

## 基线（2026-09-04）

- 协议版本 2026.09.3；check 基线：0 error / 0 warning。
- 试点前状态：所有任务状态散落在 prose（本仓库此前无任务文件，基线为"纯 prose 时代"）。

## K1 — 状态块减少事实漂移

对比对象：历史 prose TASK（其他项目的使用经验与本仓库既往会话记录）vs 本试点的结构化 TASK。

| 日期 | 事件 | 涉及 TASK | 修改位置数 | 状态冲突/人工修正 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-04 | draft → active（接入完成） | TASK-0001 | 2（状态块 + runtime 行） | 0 | 首次转换 |
| 2026-09-04 | active → blocked（发布客户端不可用） | TASK-0002 | 2（状态块 + runtime 行） | 0 | Release 未创建，不将失败误记为成功 |
| 2026-09-08 | draft → active（M0 preflight 通过） | TASK-0003 | 2（状态块 + runtime 行） | 0 | canonical K1 校准后首个转换 |
| 2026-09-08 | active → ready_for_review（M1-M3 实施与验证完成） | TASK-0003 | 2（状态块 + runtime 行） | 0 | 首轮记录遗漏本转换，review round 1 补记 |
| 2026-09-08 | ready_for_review → accepted（round 2 通过 + CI 首跑全绿，owner 授权） | TASK-0003 | 2（状态块 + runtime 行） | 0 | 两个 review round，1 次返工 |
| 2026-09-08 | blocked → active（2026.09.3 Release 已发布并成为 latest） | TASK-0002 | 2（状态块 + runtime 行） | 0 | blocker 解除；Release 标题和 notes 仍为空，未进入 ready_for_review |
| 2026-09-08 | active → accepted（owner 决定元数据 Gate 降为可选，D-0003） | TASK-0002 | 2（状态块 + runtime 行） | 0 | 技术验收项全部达成；标题/notes 移入 Optional |
| 2026-09-08 | active → blocked（M3 No-Go 采纳为 D-0004；M2 等待 owner 第二项目） | TASK-0004 | 2（状态块 + runtime 行） | 0 | 首例因等待外部输入主动转 blocked；恢复时的 blocked → active 将计入 TASK-0001 coverage gate 样本 |
| 2026-09-08 | draft → active（owner 任务书立项：证据质量与计数收敛） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 真实治理修复任务，非为凑 TASK-0001 数量门槛（D-0005） |
| 2026-09-08 | active → ready_for_review（M1 计数单源化 + M2 Protocol v2 完成） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 待 owner 最终验收 |
| 2026-09-08 | draft → active（owner 下发非 Context 优化计划开始指令） | TASK-0006 | 2（状态块 + runtime 行） | 0 | Level C 消融实验任务；实验样本 synthetic，不计入本试点覆盖 |
| 2026-09-09 | ready_for_review → accepted（owner 复核 6a2043e 通过，正式验收） | TASK-0005 | 2（状态块 + runtime 行） | 0 | 六项 round-2 finding 已闭合 |
| 2026-09-09 | ready_for_review → accepted（owner 验收，结论严格限定：E2 No-Go / E1 Inconclusive / v0 本周期不实现） | TASK-0006 | 2（状态块 + runtime 行） | 0 | 方向未证伪；其余候选等待真实证据 |
| 2026-09-09 | ready_for_review → accepted（owner 验收通过；2026.09.4 实现闭环） | TASK-0007 | 2（状态块 + runtime 行） | 0 | tag 随验收推送；Release 对象由 owner 创建（D-0003：元数据可选） |

成功标准：不再出现静默状态冲突；每个 TASK 人工修正不超过 1 次。

## K2 — runtime 投影值得保留

| 日期 | 事件 | 单次同步耗时 | check 捕获的相关发现 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | 初始建行（TASK-0001 active） | < 30 秒 | 无（人工同步正确） | |
| 2026-09-04 | TASK-0002 active → blocked | 未单独计时 | 无（人工同步正确） | 本行不计入耗时成功样本 |
| 2026-09-08 | TASK-0002 blocked → active | 未单独计时 | 无（人工同步正确） | Release/latest 核验后同步状态块与 runtime；元数据 Gate 仍未通过 |
| 2026-09-08 | TASK-0002 active → accepted 投影同步 | 未单独计时 | 无（人工同步正确） | owner 元数据决定（D-0003）后关闭任务；handoff 条目并入任务文件 |

成功标准：单次投影更新不超过 30 秒；不出现长期双写负担（若连续两次记录"忘了同步、靠 check 抓回"，即为负担信号）。

## K3 — tracked/local 足够表达存储策略

Trellium 本仓库 = tracked 样本；另一个真实私有项目 = local 样本（由用户择机接入）。

| 日期 | 项目 | 模式 | 事件 | 误提交/误忽略/例外 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-04 | trellium | tracked | `.gitignore` 白名单解除 vault/ 与 AGENTS.md；任务文件入库 | 0 / 0 / 0 | 无需第三种模式 |

成功标准：零误提交、零模糊归属、不需要 tracked/local 之外的第三种模式或逐任务例外。

## K4 — 预算阈值确有价值

第一阶段只测量、不设阈值（policy 不配 budgets 数字）。记录热文件增长与实际阅读障碍。

设置校正：adopt 生成的默认 policy 曾短暂包含 budgets；在第二个真实任务开始、尚未产生任何阈值 finding 前删除，使实验与预注册的 measurement-only 条件一致。

| 日期 | 文件 | lines / bytes / max_line_bytes | 实际阅读障碍事件 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | runtime | 58 / 1751 / 136 | 无 | 基线 |
| 2026-09-04 | runtime | 59 / 2364 / 179 | 无 | 删除 budgets 后 check 仍报告测量，不执行阈值判定 |

判定规则：只有观察到"大文件确实导致 Agent 定位失败"的具体事件，才为对应文件配置阈值。

## check 运行台账

每次 `check --format json` 的结论留档（交接与合并前必跑）。

| 日期 | 触发 | 退出码 | errors / warnings | 发现与处置 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | adopt 后基线 | 0 | 0 / 0 | 无 |
| 2026-09-04 | TASK-0002 发布前门禁（commit 1d9d19b） | 0 | 0 / 0 | Release 环境缺少 `gh`；任务转 blocked |
| 2026-09-04 | 阻塞复核：发现用户已建 2026.09.2 Release，2026.09.3 仍缺 | 0 | 0 / 0 | 阻塞缩小未解除；latest 解析 2026.09.2 |
| 2026-09-08 | TASK-0003 M0 preflight | 0 | 0 / 0 | `releases/latest` 仍解析 2026.09.2；`releases/tags/2026.09.3` HTTP 404 |
| 2026-09-08 | TASK-0003 M1 校准后 | 0 | 0 / 1 | TASK_STORAGE_PENDING（TASK-0003 未提交窗口），提交即消除 |
| 2026-09-08 | TASK-0003 M3 后全量验证 | 0 | 0 / 1 | 同上；87/87 tests、snapshot in sync、`git diff --check` OK |
| 2026-09-08 | TASK-0003 交接前门禁（M1-M3 提交后） | 0 | 0 / 0 | TASK_STORAGE_PENDING 已随提交消除；87/87、snapshot in sync、`git diff --check` OK |
| 2026-09-08 | GitHub Actions 首跑 run 34181086563（develop push，gate job） | 0 | 0 / 0 | runner 端执行与本地一致；unit tests、vault check、drift 检测全部 success |
| 2026-09-08 | TASK-0002 Release 发布后复核与 blocked→active | 0 | 0 / 0 | latest 已解析 2026.09.3；远端 tag 正确；Release 标题和正文为空，保持 active 待补齐元数据 |
| 2026-09-08 | TASK-0002 accepted 门禁（owner 元数据决定后） | 0 | 0 / 0 | 技术验收项全部 [x]；标题/notes 移入 Optional（D-0003） |
| 2026-09-09 | Vault 2026.09.4 升级终验 | 0 | 0 / 0 | 唯一 `vault/index.md` 提案经 owner 确认后合并；106/106 tests、中英 snapshot in sync、`git diff --check` OK |
