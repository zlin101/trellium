# Trellium 2026.09.4：Local TASK 生命周期闭环与 Clone-safe 投影（GLM 实施契约）

> 本文可直接交给 GLM 执行。Owner 已批准本方向；GLM 收到本文及“开始执行”指令后，按 M0 建立 Level C 任务并实施。本文纠正一个关键误解：local TASK 本来就是不进入仓库的私有工作日志，不应被重新包装成需要发布的项目资产。

- 日期：2026-09-09
- 状态：Owner 已批准方案；等待 GLM 执行
- 主要输入：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md` 第 12.6、14.8 节
- 当前基线：Trellium `2026.09.3`，develop 与 origin 在交付本计划前一致，既有门禁全绿
- 目标版本：`2026.09.4`（完成实现与迁移文档后更新版本号；本任务不创建 tag 或 Release）
- 任务等级：Level C / Authority 3（改变 Agent 治理规则与 checker 行为）
- 任务编号：GLM 在 M0 现场选择下一个可用编号，不在本文预占
- 预期交接改动：本文为 untracked 新文件，`vault/runtime.md`、`vault/collaboration.md` 为 modified；三者均是 Codex 本轮方案交接产物，GLM 须先审阅后保留并纳入 M0 提交，不得当作未知漂移覆盖

## 0. 执行前 Review 已关闭

2026-09-09 的最终 review 曾给出 `REQUEST_CHANGES`，本版已逐项修复：

- R1：基线与终验测试模块更正为真实存在的 `scripts.test_install_sh`；
- R2：Durable Knowledge Disposition 只阻塞 `accepted`，不阻止错误任务立即 `superseded`；
- R3：若 W1/W2 进入模板，tracked 模式使用 `not_applicable`，local 模式禁止该值，避免伪 `pending`；
- R4：分发同步面补齐 runtime/governance/index/handoff 模板、顶层 Skill 与 agent-task Skill；
- R5：把概念删减改成可执行的流程消融与 checker characterization，先证明最小层确有必要；
- R6：显式登记 GLM 入场时预期看到的三项未提交交接改动。

该 review 只关闭方案缺陷，不替代实施后的独立代码 review。

## 1. 先统一设计含义

原始设计的职责边界是：

| 信息 | 位置 | 生命周期与用途 |
| --- | --- | --- |
| 当前任务契约、实施流水、review、失败尝试、详细证据 | ignored local TASK / review / archive | 当前工作区私有工作日志；不要求跨 clone 恢复，不进入 Git |
| 当前注意力和开放任务摘要 | `vault/runtime.md` | 热路径投影；只保留最少摘要，不复制私有流水 |
| 中断接力信息 | `vault/handoff.md` | 临时叙事；恢复后压缩或删除 |
| 会约束未来实现的事实 | `vault/decisions.md`、`vault/project.md`、`vault/details/*` 或公开契约文档 | tracked 的项目真相；未来 clone 必须可恢复 |
| 分支、HEAD、diff、dirty files | Git / worktree 现场 | 动态事实，读取时实时获取，不写成长期权威 prose |

“TASK 内容被内化进 Vault”只意味着：任务关闭前，把未来仍需遵守的最小结论蒸馏到对应权威文件。它不意味着复制 TASK 全文、review 流水或执行日志。没有长期结论的任务允许明确记录 `none`，关闭后不留下额外项目记忆。

现有 09.3 已经实现了 local storage 的基本边界：local TASK 不得 tracked/staged，Accepted 结论应蒸馏到公开位置，工具不自动修改 `.gitignore` 或 untrack。此次只补齐两个缺口：

1. Accepted 前没有显式的“长期知识处置”检查点，容易让 Agent 忘记判断是否需要蒸馏；
2. fresh clone 中被忽略的 local TASK 必然不存在，但 checker 当前仍把 `runtime.md` 指向它判成普通缺失 error，没有表达 local 模式的真实证据边界。

## 2. 目标与非目标

### 2.1 目标

- 保留 local TASK 的私有、临时、低仓库负担属性；
- 让 local 任务进入 `accepted` 前显式处置长期知识；任务需要 `superseded` 时可立即废止，未处置知识由替代任务承接；
- 关闭 local 任务后清理 `runtime.md` 和 `handoff.md` 的热路径残留；
- 让 fresh clone 能区分“私有任务文件按策略不可见”与“tracked 任务文件真的丢失”；
- missing local TASK 时 fail closed：checker 可以 warning，但 Agent 不得据 runtime 摘要自行恢复授权或开始实现；
- 保持 `task_storage=tracked` 的现有严格校验完全不变。

### 2.2 明确不做

- 不上传、提交、自动发布或完整归档 local TASK；
- 不新增 publish generator、owner inbox、Context、RAG、数据库、daemon 或 Web UI；
- 不从自然语言自动提取“长期事实”，不让 LLM 或 checker 替 Owner 判断什么值得发布；
- 不新增公开 CLI 子命令；
- 不修改 `trellium-task-state` schema v1，也不新增 machine-readable memory receipt；
- 不自动改 `.gitignore`、不自动 `git rm --cached`、不自动迁移历史 TASK；
- 不修改 CI 权限、依赖、公开 API、tag 或 Release；
- 不把第二项目变成进入实现的前置测试。第二项目用于后续真实验证，不用于重新证明 local TASK 是否应该存在。

## 3. 决策表：必须先冻结再编码

M0 后，GLM 先把以下表复制到任务文件，并以测试名称一一对应。任何实现若改变表中结论，必须停下向 Owner 报告，不能自行扩大语义。

| Policy | TASK 文件 | runtime 行 | 预期结果 |
| --- | --- | --- | --- |
| tracked | open，状态一致 | 存在 | PASS，维持 09.3 行为 |
| tracked | 不存在 | 存在 | `TASK_RUNTIME_MISSING` error，维持 09.3 行为 |
| local | open，状态一致 | 存在 | PASS |
| local | open | 不存在 | `TASK_PROJECTION_MISSING` error；同一工作区必须维护开放任务投影 |
| local | 不存在 | open 行存在 | `TASK_RUNTIME_LOCAL_UNRESOLVED` warning；说明私有契约在本 clone 不可验证，不能据此获得授权 |
| local | accepted/superseded | 行不存在 | PASS；关闭任务不占 runtime 热路径 |
| local | accepted/superseded | 行存在 | `TASK_RUNTIME_CLOSED_LOCAL` error；要求关闭后清理投影 |
| local | 不存在 | accepted/superseded 行存在 | 同上，仍为 `TASK_RUNTIME_CLOSED_LOCAL` error，不因文件不可见而放过 stale row |
| local | 任意 TASK/review/archive 被 tracked 或 staged | 任意 | 沿用现有 `TASK_STORAGE_MISMATCH` error |
| policy 缺失或非法 | 任意 | 任意 | 保持现有兼容行为；不得暗中套用 local 语义 |

补充规则：

- `Focus` 指向不存在的 local TASK 时，同一 TASK 最多产生一条 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning，不因 Focus 与表格重复报警；
- runtime status 非法、重复行、已存在 TASK 的状态漂移，继续使用原有 error；local 模式不能降低这些约束；
- warning 的退出码继续遵守现有契约：只有 warning 时为 0，但输出必须可见；
- `runtime.md` 的 open-task 摘要不是任务契约，不授予 Authority。fresh clone 要继续该任务，必须取得原 local TASK，或由 Owner 批准后重建新的本地任务契约；不得从摘要推断 Allowed / Forbidden。

## 4. 反思、红队与消融结论

### 4.1 承重假设与最低成本防线

| 假设/失败模式 | 影响 | 发生可能 | 最低成本防线 | Kill criterion |
| --- | --- | --- | --- | --- |
| missing local TASK 可能是正常 fresh clone，也可能是误删 | 高 | 中 | warning 同时写明两种原因、恢复动作与不授予权限 | 若实现只能静默忽略或把缺失断言为正常 fresh clone，则停止 |
| runtime 摘要可能泄露私有过程 | 高 | 中 | 只允许 task id、短目标、lifecycle、下一动作；协议禁止复制日志、请求体、响应体、凭据 | 若功能要求复制 TASK 正文才能工作，则停止 |
| 人工蒸馏可能被漏做 | 中 | 中 | Accepted review gate 增加明确处置项；独立 review 核验 | 单次遗漏不升级 schema；真实重复遗漏达到 2 次后再提机器校验 |
| 清理 closed row 可能被误认为删除历史 | 中 | 中 | 文档明确：历史在 local journal/Git，长期约束在 canonical Vault，runtime 只服务当前态 | 若关闭后仍需靠 runtime 找长期事实，说明蒸馏未完成，不保留 stale row 掩盖问题 |
| local 分支可能意外弱化 tracked 校验 | 高 | 低 | 旧 tracked case 全量回归，策略分支显式传入 | 任一 tracked 基线从 error 降为 warning 即 No-Go |
| 自动发布会制造重复事实源 | 高 | 中 | 本周期禁止 generator、proposal 文件与自动写入 | 若需要新派生文件才能闭环，则回退到人工 gate |

### 4.2 预注册消融：先证明最小层必要

Owner 批准的是问题方向，不是要求每个候选必须上线。GLM 在修改正式模板和 checker 前，先在任务 Execution Record 冻结并执行以下两组小实验；临时 fixture 标 `synthetic`，不进入 TASK-0001 的真实覆盖计数，也不新建长期 eval 目录。

#### W 组：Accepted 知识处置流程

使用相同的三个短任务案例（产生长期约束、无长期约束、错误契约需要立即 supersede），分别交给无历史 reviewer 判断能否关闭、应更新哪里：

| Cell | 唯一变量 |
| --- | --- |
| W0 | 09.3 现有 `Memory Updates` 通用提示 |
| W1 | 只在现有 `Memory Updates` 增加一条明确的 disposition 行 |
| W2 | 新增独立 `Durable Knowledge Disposition` 段 |

顺序为 W2 → W1 → W0；每个 cell 独立会话，只接收对应任务片段，不允许读取本文、实验任务或 scoring；读到任一评分材料即标 `contaminated` 并重跑。记录首答、判断正确性、是否错误阻塞 supersede、输入 UTF-8 bytes 和 reviewer 纠正数。

Gate：

- W0 是 baseline；单轮 synthetic tie 不能反证长期深度反馈，只能把增量收益记为 Inconclusive；只有新的真实长期证据证明现有提示没有遗漏时，流程增强才 No-Go；
- W1 与 W2 判断相同则选择 W1，删除独立段；
- 只有 W2 修复了 W1 的真实漏判且没有错误阻塞 supersede，才采用独立段；
- 任一方案要求复制 TASK 正文或新增状态 owner，立即 No-Go。

#### C 组：Checker characterization

用同一组临时仓库 fixture 记录三层结果：

| Cell | 唯一变量 |
| --- | --- |
| C0 | 09.3 当前 checker |
| C1 | 仅修改协议，checker 不变 |
| C2 | 协议 + 最小 local-aware projection 分支 |

至少覆盖 fresh clone 的 open local 指针、closed local stale row、tracked dangling pointer。C0 必须在改代码前保存真实 code/severity/exit；C1 用来证明仅改文档是否仍会机械误报；C2 才运行第 8 节的完整回归。

Gate：

- 若 C0/C1 已不误阻断 fresh clone，C2 No-Go；
- C2 必须把 missing open local 从 generic error 收敛为带恢复边界的 warning，同时保持 closed-local error 和 tracked error；
- 任一 tracked finding 降级、missing local 被静默忽略、或 warning 诱导 reviewer 直接继续任务，C2 No-Go；
- 若最小实现无法通过 Gate，结论为 Blocked，不得恢复自动发布、JSON receipt、新 CLI 或自动 Git 操作。

以下扩展在实验前即删除，不进入 cell：自动扫描 TASK/publish proposal、`trellium-task-memory` schema、新存储层、自动 `.gitignore`/untrack。它们增加新的事实源或破坏原始边界，没有必要用实现成本再次证明。

## 5. M0 — Preflight 与任务建立

1. 读取 `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`、`vault/handoff.md`、本文、源反馈第 12.6/14.8 节和活跃任务文件。
2. 现场检查 branch、HEAD、origin、dirty state、`init/VERSION`；不相信本文中的动态快照。
3. 运行并记录基线：
   - `python3 scripts/trellium.py check . --format json`
   - `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
   - `python3 scripts/sync-skills.py --check`
   - `git diff --check`
4. 创建下一个可用的 Level C / Authority 3 TASK，并把第 3 节真值表写入验收标准。任务本身按本仓库 `tracked` policy 管理；不要借机把本仓库切为 local。
5. 在 `vault/decisions.md` 记录一条真实决策：local TASK 是私有工作日志，只有长期约束被蒸馏；runtime 的 missing-local warning 不授予恢复权限；tracked 行为保持严格。
6. 预期存在三项交接改动：本计划、`vault/runtime.md`、`vault/collaboration.md`。逐项审阅后保留并纳入 M0 提交；除此之外的 dirty 文件才按未知用户改动报告，不覆盖。
7. 在任何正式实现前完成第 4.2 节预注册与 C0/W0 基线记录，不能看过实现结果后改 Gate。

Owner 将本文交给 GLM 并说“开始执行”，即授权 M0–M6 范围内的 Level C 修改、正常提交、push develop 和观察既有 CI；不授权创建 tag、Release 或把任务自行标为 accepted。

## 6. M1 — 协议与模板：补齐关闭语义

修改 canonical 协议与下发模板，使下列规则在中文、英文使用路径中表达一致：

### 6.1 Durable Knowledge Disposition

按 W 组 Gate 选择载体，不预设必须新增独立段。默认候选 W1 是在现有 `Memory Updates` 中增加一行：

```md
- Durable knowledge disposition (required before `accepted` when `task_storage=local`): not_applicable | pending | none — <reason> | distilled — <canonical destinations>
```

只有 W2 明确优于 W1 时，才改用同字段的独立 `## Durable Knowledge Disposition` 段；W0 胜出则不改模板，只收紧现有协议文字。

语义：

- `not_applicable`：仅用于 tracked 任务；local 任务禁止使用；
- `pending`：local 任务不能进入 `ready_for_review` 或 `accepted`；
- `none`：任务没有会约束未来 clone 的新事实，写一句理由；
- `distilled`：只列 canonical 目标文件，长期事实的唯一正式正文在那些文件中，不在此段复制第二份；
- local 任务最迟在进入 `ready_for_review` 前由执行者填写、reviewer 核验；tracked 任务默认 `not_applicable`，仍可主动记录 `none`/`distilled`；
- 规则只作用于新关闭、重新打开后再关闭的任务，不要求批量回填历史任务。

第一版不让 checker 解析这些值。机器无法可靠判断“有没有长期事实”；这里是 review gate，不是新的真相源。若未来出现至少 2 次真实遗漏，再单独提案是否加入结构化检查。

### 6.2 关闭后的热路径清理

- local TASK 进入 `accepted` 前先完成长期知识处置；
- 错误、过期或不安全的任务契约可以立即进入 `superseded`，不得被 disposition 阻塞；转换时记录替代任务或废止原因，尚未处置的长期事实作为显式 next action 交给替代任务或 Owner；
- lifecycle 状态块改为 `accepted`/`superseded` 后删除 `runtime.md` 对应行；若 Focus 指向该任务，转向真实开放任务或清空；
- 删除或压缩 `handoff.md` 对应条目；稳定结论必须先落入 canonical 文件；
- local TASK/review/archive 是否在本机保留或归档由 Owner 的本地策略决定，Trellium 不自动删除；
- tracked 模式继续允许 runtime 保留 closed 行，避免本版本无关的 breaking change。

### 6.3 Fresh clone 行为

- runtime 可保留 local open TASK 的一行最小摘要，帮助人知道存在未完成工作；
- fresh clone 看不到 ignored TASK 时，摘要只能表示“有未验证的工作线索”，不能成为任务契约或授权源；
- Agent 必须向 Owner 获取原任务文件，或获得批准后重建任务契约，才能继续修改；
- 不得把 TASK 正文复制进 runtime/handoff 来绕过 local 边界。

协议与分发面（只在相关语义出现处做最小修改）：

- `init/protocol/10-vault.md`
- `init/protocol/20-governance.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/80-execution-patterns.md`
- 两套 `skills/*/assets/templates/vault/{index,governance,runtime,handoff,tasks/README}.md`
- 两套 `skills/*/assets/templates/skills/agent-task/SKILL.md`
- `skills/trellium/SKILL.md`、`skills/trellium-zh/SKILL.md`
- 两套精简 `references/protocol-model.md` 与 `references/templates-guide.md`
- 当前自托管实例的 `vault/index.md`、`vault/governance.md`、`vault/tasks/README.md`（只做与新规则对应的小 diff，不覆盖项目定制）

不要直接编辑 `skills/*/references/protocol-source/`；它们由同步脚本生成。若没有新增/删除下发文件，`FILE_ROLES` 不应变化。

## 7. M2 — Checker：只补 local-aware projection

### 7.1 实现边界

- 将已解析的 policy 显式传给 `check_runtime_projection`，不要在函数内部重新读取或猜默认值；
- 只有 policy 合法且 `task_storage == "local"` 时启用 local 分支；
- 对 open runtime 行/Focus 指向的 missing local TASK，产生一次去重后的 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning；
- warning message 必须同时说明：TASK 在当前 worktree 不存在，原因可能是正常 fresh clone 或本地文件意外丢失；恢复前应寻找原工作区/备份或取得 Owner 批准后重建契约；runtime summary 不授予 Authority；
- 对 local closed row，无论 TASK 文件是否存在，产生 `TASK_RUNTIME_CLOSED_LOCAL` error；
- 已存在的 open local TASK 缺少 runtime 行，继续由 `TASK_PROJECTION_MISSING` 报 error；
- malformed lifecycle、duplicate row、task id mismatch、状态漂移、storage tracked/staged 错误保持现状；
- tracked 或 policy 缺失路径保持 09.3 行为，包括 missing pointer 的 `TASK_RUNTIME_MISSING` error。

### 7.2 不允许的捷径

- 不以 `vault/tasks/` 整体缺失为由跳过 projection check；
- 不把所有 `TASK_RUNTIME_MISSING` 全局降级；
- 不根据 `.gitignore` 猜 policy；
- 不把 runtime row 升格为 lifecycle owner；
- 不自动创建 TASK、删 runtime 行或写修复文件；`check` 必须继续只读、确定性。

## 8. M3 — 聚焦测试与回归

在 `scripts/test_trellium.py` 增加至少以下离线测试，名称与第 3 节决策表对应：

1. local open TASK + matching runtime：0 finding；
2. local open TASK + no row：`TASK_PROJECTION_MISSING` error；
3. local open row + missing TASK：单个 `TASK_RUNTIME_LOCAL_UNRESOLVED` warning、exit 0、没有 `TASK_RUNTIME_MISSING`；断言 message 同时包含 fresh-clone/possible-loss、恢复动作与 no-authority 三层含义；
4. 同一 missing TASK 同时出现在 row 与 Focus：warning 去重；
5. local accepted TASK + row：`TASK_RUNTIME_CLOSED_LOCAL` error；
6. local accepted row + missing TASK：同一 closed-local error；
7. local closed TASK + no row：通过；accepted 与 superseded 至少各覆盖一次；
8. local TASK/review/archive 被 tracked 或 staged：既有 storage error 不退化；
9. tracked row + missing TASK：仍是 `TASK_RUNTIME_MISSING` error；
10. policy 缺失：保持既有 warning/严格 projection 语义，不套 local 分支；
11. invalid status、duplicate row、state drift：原有 error 不变；
12. JSON 与 text renderer 都包含新 code、severity、task_id，warning 不改变退出码。

不得在单元测试中调用网络或真实 GitHub。fixture 中的 synthetic TASK 不计入 TASK-0001 的真实覆盖。

## 9. M4 — 版本、迁移与用户文档

1. 把 `init/VERSION` 更新为 `2026.09.4`。
2. 在 `init/MIGRATIONS.md` 顶部追加 2026.09.4 条目：
   - Added：local Accepted 前的人工 Durable Knowledge Disposition；按 W 组真实结论写明采用现有提示、单行提示或独立段，不虚构未采用的载体；
   - Added：missing open local TASK 的 clone-safe warning；
   - Breaking（仅 local hot path）：closed local TASK 不应继续留在 runtime；
   - Agent migration：不批量回填历史 TASK；升级现有 local 项目时，人工审查并清理 runtime 中 closed 行，不删除 local TASK，不自动修改 Git；superseded 转换不受 disposition 阻塞；
   - Auto：只更新未定制模板和版本戳；protected data 仍不自动改写。
3. 更新 `README.md`、`README.en.md` 的 local storage/check 说明和 finding code；中英文语义必须一致。
4. 按第 6.3 节清单逐项人工同步中英文模板、顶层 Skill、agent-task Skill 和精简 references；尤其核对 runtime 模板与 checker 文档。不要假装同步脚本能翻译语义。
5. 运行 `python3 scripts/sync-skills.py` 生成两套 protocol-source 与 `assets/trellium.py` 快照，再用 `--check` 验证。
6. 本任务不打 `2026.09.4` tag、不创建 Release。待 Owner accepted 后另行发布。

## 10. M5 — 自托管检查与独立 Review

本仓库自身使用 tracked mode，不能把它伪装成第二个 local 项目。local 行为由单元 fixture 验证；之后再由真实第二项目做外部验证。

实现者完成后建立 `TASK-xxxx-review.md`，由独立 Agent/会话按下列问题审查：

- 是否保留了“local TASK 不进仓库”的原始设计，而非新增发布系统；
- Durable Knowledge Disposition 是否只是人工 gate，没有成为第二份长期事实；
- W0/W1/W2 是否按冻结顺序执行，最终载体是否遵守“同效取小”；tracked 是否有明确 `not_applicable`，superseded 是否仍可立即执行；
- missing local warning 是否清楚地 fail closed for authority；
- closed local row 是否稳定报错且给出可执行修复；
- tracked 和 policy-missing 旧行为是否零退化；
- checker 是否仍然只读、确定性、标准库；
- 是否无自动 `.gitignore`、untrack、TASK 删除、tag、Release、CI 权限改动；
- migrations、中文、英文、分发快照是否一致；
- 是否遗漏凭据/隐私边界。

所有 `open`/`needs-discussion` finding 收敛前不得进入 `ready_for_review`。GLM 不得自行标 `accepted`。

## 11. M6 — 终验、提交与交付

必须记录真实结果，不预写测试数量：

```bash
python3 scripts/trellium.py check . --format json
python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh
python3 scripts/sync-skills.py --check
git diff --check
git status --short
```

交付要求：

- 分 milestone 做聚焦提交；提交信息能区分协议、checker/tests、迁移/分发和 review 修复；
- push develop 后观察既有 CI，记录 run id 与真实结果；
- 更新任务文件、runtime、decisions 和必要 handoff；
- lifecycle 最多推进到 `ready_for_review`；
- 向 Owner 报告新 finding code、兼容边界、迁移动作、测试结果、CI 结果和未完成项；
- 工作树干净、与 origin 一致后交付；若不能做到，逐项列出原因，不宣称完成。

## 12. 验收标准

- [ ] local TASK 仍保持 ignored/untracked；实现没有 publish generator 或自动知识提取；
- [ ] TASK 模板和治理协议明确区分 private journal、published truth、runtime/handoff、live Git；
- [ ] W0/W1/W2 有冻结材料、首答和 Gate 结论；同效时选择更小载体，tracked 路径不残留伪 `pending`；
- [ ] 新 accepted 的 local TASK 完成人工 Durable Knowledge Disposition，历史任务无需批量回填；superseded 可立即执行并把未处置事项显式转交；
- [ ] local closed row 从 runtime 清理，handoff 同步压缩；tracked 模式不受此清理规则影响；
- [ ] C0/C1/C2 characterization 记录真实 code/severity/exit，证明 checker 代码层相对 protocol-only 层的必要性；
- [ ] 第 3 节全部 checker 真值表有聚焦测试并通过；
- [ ] missing open local TASK 只产生可见 warning，且文案覆盖正常 fresh clone、本地误删可能、恢复动作和 runtime 不授予权限；
- [ ] tracked missing TASK 仍为 error，所有既有严格校验无退化；
- [ ] `trellium-task-state` schema、公开 CLI、依赖、CI 权限未改变；
- [ ] `2026.09.4` migration、双语文档、runtime/governance/index/handoff/task 模板、两类 Skill 和分发快照同步；
- [ ] 独立 review 无 open finding，终验和 push 后 CI 全绿；
- [ ] 任务停在 `ready_for_review`，由 Owner 决定 accepted 与后续 Release。

## 13. 后续真实验证（不阻塞本任务实现）

第二个真实 local 项目接入后，用一项自然发生的 Level B/C 工作验证：

1. 任务进行中时，本工作区 TASK 可验证、runtime 投影一致；
2. 另一个 fresh clone 只看到 open 摘要，checker 报 local-unresolved warning，Agent 不越权继续；
3. 原工作区完成任务，填写 `none` 或 `distilled`，再进入 accepted；
4. runtime/handoff 清除 closed 任务；
5. fresh clone 只靠 canonical Vault 和 Git 能恢复长期约束，不需要 TASK 流水。

该试点用于发现边缘行为和积累跨项目证据，不得把本任务已批准的设计重新降级为“先造测试再决定要不要做”。若出现真实重复遗漏，再立新任务评估 machine-readable disposition；本周期不提前建设。
