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

覆盖计数核对（截至 2026-09-08 review round 1 后更新，依据本 ledger 与 git 历史，不采信传闻数字）：真实 TASK 共 3 个（TASK-0001/0002/0003）；观测到 lifecycle 转换 4 次（TASK-0001 draft→active、TASK-0002 active→blocked、TASK-0003 draft→active、TASK-0003 active→ready_for_review；TASK-0002 创建时直接为 active，无 draft→active 记录）；handoff.md 现存 3 个条目（TASK-0003/0002/0001）；blocked→active 0 次。TASK-0001 的 coverage gate（5 TASK / 6 转换 / 2 handoff / 1 blocked→active）继续有效，但不替代 canonical K1-K4 的跨项目证据要求。

### Canonical K3 — 不解析任意 Markdown 也能产生高价值检查（2026-09-08 起）

两个真实 Vault 只读运行；记录 finding 是否对应真实修复，以及已知遗漏。

| 日期 | Vault | 触发 | errors / warnings | 是否产生真实修复 | 已知遗漏 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-09-08 | trellium（本仓库） | TASK-0003 M1 校准后 check | 0 / 1 | 否：预期瞬态 finding（tracked 任务未提交窗口，设计内行为），随例行提交消除，不构成缺陷捕获证据 | 暂无 | review round 1 更正定性（原行误标为"真实修复"）；canonical K3 尚无缺陷捕获类观测 |

成功标准：finding 对应真实修复动作。Kill criterion：连续两次真实检查只有无行动价值的 warning，且遗漏已知的状态/storage/预算错误。

### Canonical K4 — checker 应先于 context compiler（2026-09-08 起）

记录 checker 发现数、状态判断耗时、owner 手工打开文件数与上下文选择成本。

| 日期 | 事件 | checker 发现数 | 状态判断耗时 | owner 打开文件数 | 备注 |
| --- | --- | --- | --- | --- | --- |

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

成功标准：不再出现静默状态冲突；每个 TASK 人工修正不超过 1 次。

## K2 — runtime 投影值得保留

| 日期 | 事件 | 单次同步耗时 | check 捕获的相关发现 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-09-04 | 初始建行（TASK-0001 active） | < 30 秒 | 无（人工同步正确） | |
| 2026-09-04 | TASK-0002 active → blocked | 未单独计时 | 无（人工同步正确） | 本行不计入耗时成功样本 |

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
