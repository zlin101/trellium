# Trellium Agent-Native 下一周期执行计划（GLM）

> 本文是交给 GLM 的执行任务书。先完成交付收尾与试点校准，再用真实证据决定是否进入 context manifest；不得把后续候选自动视为已授权实现。

- 日期：2026-09-08
- 状态：Ready for owner handoff
- 输入：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md`
- 前序计划：`docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md`
- 当前协议版本：`2026.09.3`
- 当前阶段：Phase 1 实现已落地，发布与 shadow 验证未闭环

## 1. 目标

本周期只解决四件事：

1. 发布现有 `2026.09.3` tag 对应的 GitHub Release，关闭 latest release 落后问题；
2. 校准 TASK-0001 的 K1-K4 实验契约，停止使用同名但不同义的指标；
3. 把现有只读 `trellium.py check` 接入本仓库 CI，使 self-hosting 的结构漂移在合并前可见；
4. 继续收集真实 shadow 证据，形成是否进入最小 context manifest 的 Go / No-Go 结论。

本周期不直接实现 context compiler、evidence receipt、runtime generator、owner inbox 或新的状态 schema。

当前一次 GLM 执行的交付边界是完成 M0-M3，并把 M4 恢复为可持续记录的 active 状态；不得等待或制造未来样本来宣称整个 shadow 周期结束。

## 2. 已验证基线

执行前先现场复核，不直接相信本文快照。2026-09-08 的已知基线是：

- 分支：`develop`，与 `origin/develop` 一致，工作树 clean；
- `init/VERSION`：`2026.09.3`；
- tag `2026.09.3` 指向 `97d5506`；
- GitHub latest release 仍是 `2026.09.2`；`2026.09.3` Release 不存在；
- `python3 scripts/trellium.py check . --format json`：0 error / 0 warning；
- `python3 scripts/sync-skills.py --check`：两套 Skill snapshot in sync；
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`：87/87 PASS；
- 当前有 2 个 TASK：TASK-0001 active，TASK-0002 blocked；
- 当前 policy 为 `task_storage: tracked`，暂不配置预算阈值，只记录 measurement。

若任一基线已变化，先记录差异及影响，再决定是否继续；不得为了匹配本文修改现实。

## 3. 任务等级与授权边界

本执行计划包含 Agent 治理、CI 和外部 Release，整体按 Level C / Authority 3 管理。GLM 开始实现前必须创建新的治理任务文件，例如：

```text
vault/tasks/TASK-0003-agent-native-next-cycle.md
```

TASK-0003 负责 M1、M3 和 M4；TASK-0002 继续单独负责 M2 Release，不把两个任务的 lifecycle 合并。

### Allowed

- 在既有 tag 上创建同名 GitHub Release；
- 更新 TASK-0001、TASK-0002、TASK-0003 及其 runtime/handoff 投影；
- 以 append-only 方式校准 shadow ledger，不删除既有事实条目；
- 修改 `.github/workflows/skill-sync.yml`，加入本仓库只读检查并覆盖 `develop`；
- 补全与本周期直接相关的项目说明和验证记录；
- 增加聚焦测试，但仅在生产脚本行为实际改变时需要。

### Requires owner confirmation

- 接受本计划作为实施契约；
- 确认第 6 节的 K1-K4 对齐方案；
- 修改 CI 触发范围或权限；
- 创建 GitHub Release；现有 TASK-0002 已记录过一次授权，执行者仍须确认该授权未被新指令撤销；
- 进入第 9 节的 context manifest 实现任务。

### Forbidden

- 移动、覆盖、删除或重建 `2026.09.2` / `2026.09.3` tag；
- 为完成试点指标创建虚假 TASK、虚假 transition、虚假 handoff 或虚假阅读障碍；
- 回写或改写已有 shadow 观测行来制造一致性；
- 修改 `trellium-task-state` schema v1 的既有字段语义；
- 自动批准 Gate、自动写 Accepted、自动运行 TASK 文本中的命令；
- 引入第三方依赖、网络服务、数据库、daemon、RAG、权限 DSL 或锁服务；
- 在本周期顺手实现 context/evidence/runtime generator。

## 4. 全局执行纪律

1. 先读 `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、活跃 TASK、shadow ledger、本计划和前序计划。
2. 每个 milestone 前后运行 `git status --short`，保留用户既有修改。
3. 状态变化先改 TASK 的 `trellium-task-state`，再同步 runtime 对应行。
4. 外部 GitHub 事实必须现场验证；历史 handoff 只能作为线索。
5. 每个 milestone 独立 review；有 open finding 不进入下一 milestone。
6. 不把 test PASS 等同于用户 Accepted。
7. 所有计划外扩张停止并向 owner 报告。

## 5. M0 — Preflight 与任务建立

### 操作

运行：

```bash
git status --short --branch
git log --oneline --decorate -10
git tag --list --sort=-creatordate
python3 scripts/trellium.py check . --format json
python3 scripts/sync-skills.py --check
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
```

只读查询 GitHub：

```text
GET /repos/zlin101/trellium/releases/latest
GET /repos/zlin101/trellium/releases/tags/2026.09.3
```

然后创建 TASK-0003，正文必须包含本计划路径、明确 scope/out-of-scope、Authority、Acceptance Criteria、Verification 和 Memory Updates。

### 验收

- [ ] 记录实时分支、工作树、版本、tag 和 Release 状态；
- [ ] 87 项测试、snapshot sync 和 vault check 的真实结果已记录；
- [ ] 用户改动未被覆盖；
- [ ] TASK-0003 与 runtime 投影一致；
- [ ] 若基线失败，任务进入 blocked，而不是修改旧测试掩盖问题。

## 6. M1 — 校准 K1-K4 实验契约

### 已知问题

前序实施计划预注册的是：

| ID | Canonical hypothesis |
| --- | --- |
| K1 | 状态块是否减少状态推导和漂移 |
| K2 | 项目级 `tracked | local` 是否足够表达 TASK storage |
| K3 | 不解析任意 Markdown 的最小 checker 是否产生高价值发现 |
| K4 | checker 是否应先于 context manifest/compiler |

当前 `vault/details/shadow-run-2026-09.md` 使用的是：

| Existing label | Existing meaning | Recommended disposition |
| --- | --- | --- |
| K1 | 状态块减少事实漂移 | 保留为 canonical K1 |
| K2 | runtime 投影值得保留 | 改列为辅助指标 A1，不冒充 canonical K2 |
| K3 | tracked/local 足够表达存储策略 | 映射为 canonical K2 |
| K4 | 预算阈值确有价值 | 改列为辅助指标 A2，不冒充 canonical K4 |

### 修改原则

- 以前序计划第 2 节为 canonical K1-K4，除非 owner 明确选择另一版本；
- 不删除、不改写旧表格和观测行；
- 在 shadow ledger 顶部追加带日期的 `Experiment contract reconciliation`；
- 显式说明旧标签到 canonical/auxiliary 的映射；
- 新增 canonical K3、K4 的观测表，从校准日期开始采集，不回填不存在的数据；
- TASK-0001 Acceptance Criteria 改为引用精确计划段落和映射版本，避免只写“K1-K4”；
- runtime Current Progress 与实际 handoff/transition 数重新核对，但证据不充分时写 `unresolved`，不猜数字。

### K1-K4 最低证据

沿用前序计划，不因当前样本不足降低标准：

- K1：两个真实项目、至少 10 次状态变化；记录修改位置数与漂移；
- K2：至少一个 tracked 项目和一个 local 项目；列出合法例外；
- K3：两个真实 Vault 的检查结果；记录 finding 是否导致真实修复，以及已知遗漏；
- K4：记录状态判断耗时、owner 打开文件数、上下文选择成本；达到 kill criterion 才重新评估 context manifest。

TASK-0001 原有“5 个 TASK / 6 次 transition / 2 次 handoff / 1 次 blocked → active”可保留为 self-hosting coverage gate，但不能替代前序计划的跨项目证据。

### 验收

- [ ] owner 确认 canonical K1-K4；
- [ ] 历史观测未被删除或改写；
- [ ] 同名异义已消除；
- [ ] canonical K3/K4 有明确的空白或新观测入口；
- [ ] TASK-0001、runtime、shadow ledger 对当前计数不再互相矛盾；
- [ ] `trellium.py check` 仍为 0 error / 0 warning。

## 7. M2 — 发布并关闭 2026.09.3

本 milestone 按既有 TASK-0002 执行，不创建或移动 tag。

### 操作

1. 验证 `2026.09.3` 仍指向 `97d5506`，且 `init/VERSION` 为 `2026.09.3`。
2. 使用 GitHub UI、已连接的 GitHub 工具或经 owner 明确提供的安全凭据创建 Release。
3. Release 必须：tag 为 `2026.09.3`、非 draft、非 prerelease；标题和 notes 与该版本一致。
4. 验证 tag-specific Release API 成功，`releases/latest` 解析到 `2026.09.3`。
5. blocker 解除时 TASK-0002 `blocked -> active`；全部技术验收通过后进入 `ready_for_review`。
6. 只有 owner 明确验收后才进入 `accepted`。
7. 同步 TASK-0002、runtime、handoff 和 shadow ledger；把本次转换计入真实观测。

### 失败处理

- 没有 GitHub 写能力时保持 `blocked`，输出精确 UI 操作和 Release 内容；
- API 失败时记录 HTTP 状态和非敏感错误摘要，不保存 token 或请求头；
- latest 仍非 2026.09.3 时不得声称发布完成。

### 验收

- [ ] tag 未移动；
- [ ] Release 存在且属性正确；
- [ ] latest 为 `2026.09.3`；
- [ ] 安装/`--fetch` 路径不再停留在 2026.09.2；
- [ ] TASK-0002 状态和 runtime 投影一致；
- [ ] 外部验证证据包含时间、命令/API、结果与排除项。

## 8. M3 — Self-hosting CI 门禁

### 目标

让结构漂移检查在 PR 和 `develop` push 上运行。当前 workflow 会运行单元测试和 snapshot sync，但 push 只覆盖 `main`，且没有执行仓库自身的 `trellium.py check`。

### 修改范围

- `.github/workflows/skill-sync.yml`
- 必要的最小文档或 TASK 记录

不得在同一 milestone 加入自动发布、自动修复 Vault、自动提交任务状态或新的 workflow 框架。

### 期望行为

- 保留现有 PR 行为和 snapshot self-heal；
- push 分支至少覆盖实际默认开发分支 `develop`；是否继续保留 `main` 由 owner 决定；
- 增加只读步骤：

```bash
python3 scripts/trellium.py check . --format json
```

- checker error 使 job 失败；warning 按 checker 既有退出码语义展示，不擅自改成 error；
- 不增加 GitHub 权限；不把仓库内容上传到外部服务；
- CI 不自动修改 `vault/`。

### 验收

- [ ] PR 仍运行现有测试与 snapshot 检查；
- [ ] `develop` push 运行相同门禁；
- [ ] self-hosting check 实际执行；
- [ ] workflow 权限未扩大；
- [ ] 本地 87 项测试和 snapshot sync 继续通过；
- [ ] `git diff --check` 通过；
- [ ] 独立 review 无 open finding。

## 9. M4 — 完成 shadow 证据，不制造样本

GLM 不能在一次执行中“完成”本 milestone，除非真实工作自然满足全部条件。

每次真实任务只追加：

- task/lifecycle 变化；
- 状态块和 runtime 投影的修改位置数；
- checker finding、是否产生真实修复；
- tracked/local storage 的实际结果；
- 读取文件、bytes、状态判断耗时和 owner 打开文件数；
- handoff 前的 check 结果；
- 阅读障碍或旧证据误用事件；没有就明确记 `none observed`，不推测。

TASK-0001 只有同时满足自身 coverage gate 和 canonical K1-K4 证据要求，且完成五问复盘，才可进入 `ready_for_review`。

## 10. Phase 2 准入：最小 context manifest

### Go 条件

只有满足以下任一条件，GLM 才能起草新的 Level C 实施任务；本计划不直接授予实现权：

1. canonical K4 kill criterion 成立：结构状态判断准确且 checker 缺少有效发现，但上下文选择成本仍显著；或
2. 两个真实项目重复出现“新 Agent 无法在有界读取内确定 objective/current contract/authority/next action/evidence boundary”；或
3. 至少两次可复现的跨文档权威或契约漂移，且不能通过更小的文档修正消除。

当前已观察到一次 K1-K4 同名异义，可作为候选证据，但单次事件不足以自动进入实现。

### 候选最小范围

若 owner 批准，优先实现：

```text
python3 scripts/trellium.py context <target> --task TASK-xxxx --intent implement|review|handoff --format json
```

第一版只输出 manifest，不拼接大型 Markdown 正文：

- 必读源及原因；
- 源的权威类型（normative/proposal/observation/derived/journal）；
- 当前 task、slice、lifecycle、authority、gates；
- Allowed / Requires Approval / Forbidden 的来源位置；
- 实时 Git/worktree 事实；
- unresolved/legacy 和被省略资料；
- 输入文件、UTF-8 bytes 和可重放 receipt。

硬边界：只读、确定性、标准库、无 LLM、无网络、stdout 默认、不执行文档命令、不生成持久状态、不启发式猜授权。

## 11. 后续候选及重新进入条件

| Candidate | Priority | Re-entry condition |
| --- | --- | --- |
| Evidence receipt + freshness | P2 | 真实发生旧 PASS 被误作当前证据；先做 receipt/status，不代运行命令 |
| Owner inbox / review pack | P2 | 真实任务开始使用 gates，owner 查找待决项重复出现明显成本 |
| Accepted local TASK publish boundary | P2 | local 项目出现跨 clone 无法恢复长期约束的事件 |
| Runtime generated section | P3 | 两个项目稳定使用 state v1，且人工投影连续发生漂移 |
| Slice history/schema v2 | P3 | 至少两个真实多-slice TASK 无法由 `current_slice` + current contract 表达 |
| Byte thresholds | P3 | measurement 记录到明确阅读障碍后再定，不按直觉冻结 |
| Release automation | Separate task | 再次出现漏建/错建 Release，或 owner 明确要求自动发布 |
| Fact types / explicit decision edges / explain | P3 | proposal 被误作规范、决策边反复解析失败等可复现事件 |
| Worktree metadata / advisory write-set | Trigger-only | 多 Agent 或多 worktree 发生可复现覆盖事件 |

继续排除：RAG、向量数据库、知识图谱、daemon、分布式锁、完整权限 DSL、自动批准、全量历史迁移。

## 12. 最终验证

每个实际代码/CI milestone 完成后运行：

```bash
python3 scripts/trellium.py check . --format json
python3 scripts/sync-skills.py --check
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
git diff --check
git status --short --branch
```

若没有修改生产脚本，不为“增加测试数”而修改测试。若修改了协议源或 Skill 内容，必须运行 sync 并审查中英文语义一致性。

## 13. 完成定义

### 当前 GLM 执行完成

- M0-M3 的适用验收项逐条记录；
- TASK-0002 完成或因缺少 GitHub 写能力保持真实 blocked；
- TASK-0003 对已完成实施进入 `ready_for_review`，M4 长期观测仍由 TASK-0001 保持 active；
- 不等待、不伪造未来真实任务样本。

### 整个下一周期完成

整个周期只有满足以下条件才能声称完成：

- `2026.09.3` Release 已发布并成为 latest；
- TASK-0002 已经技术验收并由 owner Accepted；
- canonical K1-K4 与 shadow ledger 的同名异义已解决，历史事实未被改写；
- TASK-0001 的当前计数、runtime 和 handoff 已现场核对；
- CI 在 PR 与 `develop` push 上运行 self-hosting check，权限未扩大；
- 所有本地检查通过，或失败被如实记录并使任务 blocked；
- TASK、runtime、handoff、shadow ledger 等记忆同步；
- context/evidence/runtime generator 等后续能力未被夹带实现；
- context manifest 是否进入下一周期有清晰的 Go / No-Go 结论和证据。

## 14. 给 GLM 的开始指令

Owner 可将下面这段与本文路径一起交给 GLM：

```text
请按 docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md 执行。
先完成 Required Reading、M0 preflight，并创建 TASK-0003；逐 milestone 执行和验收。
不要把本文后续候选视为自动授权。发现基线变化、用户改动、K1-K4 解释冲突、GitHub 权限不足或 CI 权限扩大时停止并报告。
每个 milestone 后运行计划指定检查，更新任务状态块、runtime 和必要 handoff，最终给出逐条验收结果、真实命令输出摘要、未完成项和高影响变更。
```
