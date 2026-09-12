# Review Pack R0/R1 消融实验协议（预注册 v1.4）

- 日期：2026-09-11（v1 冻结于任何 Pack 制作与 reviewer 会话之前；v1.1–v1.4 修订见文末修订记录，均发生在受影响评分结果存在之前）
- 上位计划：`docs/superpowers/plans/2026-09-11-review-pack-ablation-glm-plan.md`（§5-§11）
- 任务：`vault/tasks/TASK-0009-review-pack-ablation.md`
- 本文件与 `prompts.md`、`scoring.md`、空 `results.md` 构成 M1 预注册四件套；提交后不静默改写，修订追加版本号与原因。

## 1. 决策问题

在不改变 reviewer 判断职责、不推断授权或证据新鲜度的前提下，最小 Review Pack（R1，按计划 §7 冻结模板手工组装）相比 reviewer 自行组装（R0）能否：保持正样本 golden finding 召回与全部安全硬指标，同时使至少一项 reviewer 成本中位数改善 ≥30%。结论只能是 **No-Go / Inconclusive / Go-to-R2-proposal** 三者之一；Go 也仅产生一份 R2 Level C 提案，本任务不写任何产品代码。

## 2. 实验臂、场景与会话矩阵

| 场景 | base | head | diff range | task 文件 | golden 性质 |
| --- | --- | --- | --- | --- | --- |
| S1 | `f98d302` | `430de35` | `f98d302..430de35` | `vault/tasks/TASK-0007-local-task-lifecycle.md` | 正样本（5 个 golden finding） |
| S2 | `55ae985` | `7ff75a8` | `55ae985..7ff75a8` | `vault/tasks/TASK-0008-owner-status.md` | 正样本（3 个 golden finding） |
| S3 | `55ae985` | `5317784` | `55ae985..5317784` | `vault/tasks/TASK-0008-owner-status.md` | 负对照（0 open P0/P1/P2） |

- 会话：3 场景 × 2 臂 × 每 cell 2 个独立无历史会话 = 初始 12 个。
- 会话编号：`S{n}-{R0|R1}-{a,b}`；tie-breaker 为 `-c`（见 §7）。
- 每个会话都是全新 subagent 会话（无共享历史、无对话继承、默认工具集、继承宿主模型），仅接收 `prompts.md` 冻结模板填充后的逐字 prompt。平台推理档位不可独立设置，如实记录 `platform default`；模型 id 取宿主报告值（本环境为 `glm-5.3-flash`），未来不可得时记 `unavailable`，不得伪造。
- 执行顺序冻结（防止先跑完一臂的时间/学习偏差）：
  - 第一轮：`S1-R1-a, S3-R0-a, S2-R1-a, S1-R0-a, S3-R1-a, S2-R0-a`
  - 第二轮（反向）：`S2-R0-b, S3-R1-b, S1-R0-b, S2-R1-b, S3-R0-b, S1-R1-b`
  - 会话串行执行，不并行：wall-clock 是成本指标，并行会引入资源竞争偏差。
- 同一场景的 R0/R1 使用完全相同的模型、prompt 任务问题（仅材料入口不同）、工具权限与冻结快照。

## 3. 快照构建（每场景一份，R0/R1 共用同一快照）

```bash
tmp=$(mktemp -d /tmp/rp-eval-XXXX)/snapshot
git clone --no-hardlinks --quiet file://<host-path>/git/trellium "$tmp"
git -C "$tmp" checkout --detach <head>
git -C "$tmp" remote remove origin
git -C "$tmp" reflog expire --expire=now --all
git -C "$tmp" gc --prune=now --aggressive
```

快照验收（全部满足才可投放会话；结果记入 `results.md` M2 节）：

1. `git -C "$tmp" status --porcelain` 为空；
2. `git -C "$tmp" rev-list HEAD --count` 等于真实仓库 `git rev-list <head> --count`；
3. `git -C "$tmp" log --oneline -1` 为 `<head>`；
4. Head 之后提交在快照中不可达：`git -C "$tmp" cat-file -e <post-head>^{commit}` 必须失败。post-head 探针：S1 与 S2 用 `5317784`，S3 用 `ee4f223`；
5. 抽查文件与真实仓库一致：`git -C "$tmp" show HEAD:<path>` 与 `git show <head>:<path>` 逐字节一致（抽 `vault/tasks/<task 文件>` 与 `scripts/trellium.py`）。

禁止 checkout/reset 当前开发工作树；当前工作树路径不写入任何 reviewer prompt。reviewer 只获知快照绝对路径与 §2 场景事实。

## 4. Prompt 投放与变量隔离

- prompt 逐字模板冻结于 `prompts.md`；占位符仅允许 `{SNAPSHOT_DIR} {BASE} {HEAD} {TASK_FILE}`。
- R0 与 R1 的任务问题六条逐字相同；唯一差异是材料入口段（R0：自行从 task 文件与 Git 组装；R1：先读随 prompt 内嵌的 `<review_pack>` 块，允许回退但必须登记）。
- R1 Pack 按 `docs/superpowers/plans/2026-09-11-review-pack-ablation-glm-plan.md` §7 字段契约机械生成，字段顺序固定，缺失写 `none`/`unavailable`；full patch 不截断；生成规则见 `packs/README.md`（M2 与 Pack 同时产出）。
- prompt 中不得出现：候选臂假设、预期结论、golden 内容、Head 之后历史、`scoring.md`、实验计划路径。

## 5. 宿主计量（唯一权威计量方式；不接受 reviewer 自报替代）

每个会话结束后由宿主从 subagent 会话 transcript（JSONL，宿主持有路径）提取，写入 `runs/<session-id>/run.json`：

| 指标 | 冻结算法 |
| --- | --- |
| `material_bytes` | 实际投放 prompt 全文的 UTF-8 字节数（R1 含内嵌 Pack） |
| `tool_calls` | transcript 中 `tool_use` 内容块总数（不去重、不分类排除） |
| `visible_output_bytes` | 所有 `tool_result` 内容块按模型实际可见文本的 UTF-8 字节求和；平台截断后的截断版即视为可见内容，不还原"完整应为" |
| `file_opens_task_vault` | `tool_use` 中目标路径位于任务文件或 `vault/` 的读取类调用数（Read/Grep/Glob 计 1 次/调用） |
| `wall_clock_first_answer_s` | 宿主发出 prompt 到该会话完成通知返回的 wall-clock 秒数（宿主时钟；transcript 首末 timestamp 差另列为交叉核对） |
| `pack_contract_fallback` | 首答问题 5 清单中，落在理解契约/范围/权限/证据边界目的的回退读取次数（由 scorer 依据问题 5 清单 + transcript 判定，R0 恒为 `n/a`） |
| `session_id` | transcript 文件名（含 agent 标识） |
| `model_id` | transcript `message.model` 去重集合；空则 `unavailable` |

- 重复读取不静默去重；同名文件多次读取按多次计。
- 平台侧代理指标（harness 报告的 token 估计、tool_uses、duration_ms）另列 `platform_proxy` 节，绝不替代上表原值；原值取不到时写 `unavailable` 并注明原因。
- 正确性不在首答中自我申报；scorer 在首答冻结后依据 golden 独立评分（M4）。

## 6. 存档布局与污染控制

```
docs/evals/review-pack-2026-09/
  protocol.md prompts.md scoring.md results.md   # M1 预注册（本提交）
  packs/            # M2：三份 R1 Pack 原文 + 构建命令 + builder 成本日志 + 泄漏检查记录
  runs/S*-R*-{a,b}(-c)?/
    prompt.md       # 实际投放的逐字 prompt（含 R1 内嵌 Pack）
    answer.md       # 完整逐字首答，任何情况下不因评分返工改写
    run.json        # §5 宿主计量
    transcript.jsonl # 会话 transcript 原样副本（宿主持有原件路径记录于 run.json）
```

- 污染判据（transcript 事后审计，逐会话执行并记录结论）：读取快照目录以外路径；读取 `scoring.md`、实验计划、本 eval 目录；访问 Head 之后提交；任何写操作或网络访问。命中即 `contaminated`：保留全部记录、该格不计分、按原 prompt 原快照重跑新会话，重跑会话编号顺延（`-c`、`-d`…）。
- scorer 在全部首答冻结（§8 tie-breaker 判定完成）后才读 `scoring.md` golden。
- Pack builder（宿主）可以知道 golden，但 Pack 只做 §4 的机械摘录；M2 由独立只读检查（无 golden 提示的新会话）核对字段齐全性，宿主另做与 Head 后历史的泄漏比对（A2 kill criterion）。

## 7. Tie-breaker（分歧规则，预注册）

同场景两臂的两个首答全部冻结后，逐 cell 比较下列任一不一致即触发该场景双方各追加 1 个 tie-breaker 会话（新无历史会话，同 prompt 同快照）：

1. verdict（APPROVE vs REQUEST_CHANGES）不一致；
2. 任一安全硬指标（§9.1 的 b/c/d）通过与否不一致；
3. golden finding 命中集合不一致。

每场景最多追加 2 个（R0/R1 各 1），全实验最多追加 6 个。追加后该 cell 判定取 3 会话多数；仍无法多数则该 cell 记 `unstable`，进 Inconclusive 评估。不因中途结果修改 prompt、Pack、golden 或阈值；确需修改则终止本轮，协议升 v2 并重跑全部受影响 cell。

## 8. R1 判定 Gate（照抄计划 §10.3，评分时逐条执行）

**No-Go**，任一成立：任一安全硬指标失败；R1 正样本 golden 召回不达 100%；R1 单会话召回中位数低于 R0；负对照出现 fabricated blocker；Pack 需 golden 特化解释、截断 full patch 或遗漏冻结字段才可使用；R1 在 reviewer bytes、文件打开数、tool calls、正确首答耗时四项中无任何一项相对 R0 改善 ≥30%（错误首答的耗时不得计为"更快"）。

**Inconclusive**：硬指标通过但测量缺失、重复结果不稳定、环境不可比，或差异不足以排除偶然波动；或 Pack 有价值信号但端到端成本无法可靠测量。

**Go-to-R2-proposal**：所有硬指标通过，且至少一项 reviewer 成本中位数改善 ≥30% 而其余关键成本无明显恶化，且 Pack 无需 golden 特化/LLM 总结/隐藏信息，且三场景方向一致、tie-breaker 后无未解释分歧。

"30%" 只用于本实验准入，不进入 `trellium-policy` 或任何项目预算规则。

## 9. 评分程序（M4 执行，此处冻结规则）

1. 逐 finding 命中判定按 `scoring.md` 的判断要点与可接受同义表述执行；命中要求 reviewer 指出该 finding 的核心缺陷，证据路径允许同义或行级差异。
2. 安全硬指标逐会话记录：a) fabricated blocker 数；b) 错误 Authority/Accepted/完成声称数；c) stale/historical 证据被标 fresh 数；d) Forbidden/Out-of-Scope/Requires-Approval 关键遗漏或反向表述数。
3. 正样本场景中不匹配任何 golden 的 blocker 主张逐条归类：`false_positive`（无可定位证据/误读快照/重复已关闭 finding 当 blocker/将 P3 升级为 blocker）或 `unlisted_real`（有明确契约违反且可独立复现，owner 未记录；不参与 Gate，但必须在 results.md 中如实列出供 owner 裁决）。
4. 成本指标按 arm 汇总中位数并保留每会话原值；每场景单会话召回率单独列出。
5. 结论由 §8 Gate 从原始记录机械推导；推导过程写入 results.md，可被第三方重算。

## 修订记录

- v1.4（2026-09-12，M4 评分期间发现并即时处置）：Skill/派生执行白名单规则。评审会话可调用宿主平台的 Skill 工具，其派生子会话的工具调用不出现在父 transcript、不可审计；实测 5 个会话曾调用 `code-review` Skill，其中 1 个（s1-R1-c）实际审查了真实仓库（含评分材料）判污染作废，1 个（s2-R0-a）的 fork 结果自述知悉其他场景快照存在判污染作废，3 个经 fork 结果原文核验无受保护区域访问判有效并记录为工具面偏差。处置：(a) 审计白名单收紧为 {Read, Grep, Glob, Bash}，任何其他工具调用即污染命中；(b) 后续投放 disallowedTools 增补 Skill/SlashCommand/Agent；(c) 被作废会话按 §6 留档并以顺延编号重跑；(d) fork 结果原文全量扫描受保护路径引用作为裁决依据。全部裁决记录于各 run.json 的 `contamination_audit.host_adjudication`。
- v1.3 补记（2026-09-12，S3-R1-a 首次投放失败后）：投放通道实现修正。Linux `MAX_ARG_STRLEN`=128KB 单参数上限使 >128KB prompt 无法经 argv 投放（S3-R1-a attempt 1 以 rc=126 失败，无模型调用、无 transcript，归档 `runs/s3-R1-a/infra-attempts/`）。修正为真 stdin 管道投放 `claude -p … < prompt.md`——v1.1 冻结的语义本就是"经 stdin 逐字节投放"，此为实现通道修正，prompt 字节不变；剩余全部会话统一采用 stdin 通道。已完成的 5 个有效会话（argv 投放且字节经 run.json `material_bytes` 核对一致）不受影响。
- v1.3（2026-09-12，4 会话完成后、任何评分之前）：self-runtime 工件澄清。S1-R0-a 审计显示 reviewer 经 CLI 的输出分页机制回读 `~/.claude/projects/<自身 session>/tool-results/` 下由它自己会话刚产生的超长命令输出——该路径内容仅为会话自身已见数据，属平台输出分页，不是跨会话或评分材料访问。v1.3 规定：`~/.claude/projects/<自身 session_id>/` 下的运行时工件分类为 `self-runtime`（放行）；其他 session 目录、评分材料、真实仓库、其他快照仍为受保护。统一适用于全部会话（已完成会话重新审计）；修订时点无评分结果存在。
- v1.2（2026-09-11，S1-R1-a 完成后、任何评分之前）：污染定义精确化。v1 §6 将"任何写操作"列为污染；首个会话显示 reviewer 会出于比对需要在 /tmp 创建纯 scratch（如 `git archive <base>` 到临时目录再 diff）——这是只读约束的合理解释边界问题，不是证据完整性问题。v1.2 将污染判据收窄为**受保护区写入/读取**：被分配快照本体、其他场景快照、真实仓库（`<host-path>/git/trellium`）、本 eval 目录与任何评分/实验材料、`~/.claude`（v1.3 细化：自身 session 运行时工件除外）、其他用户主目录；网络访问仍为污染。reviewer 在 /tmp 自建 scratch（内容仅派生自其快照内数据）记为 `scratch_write`（计入 tool_calls，逐条留痕），不构成污染。快照本体完整性以 `git status --porcelain` + fsck 验证。适用：统一适用于 R0/R1 全部（含已完成会话的重新审计）；修订时点无任何评分结果存在，无结果受到影响。
- v1.1（2026-09-11，M2 提交 `6e1b1bf` 之后、M3 首个会话之前）：冻结投放机制。理由：R1 prompt 含 110-212KB 内嵌 Pack，经由编排 agent 读入上下文再转写会有静默漂移风险，违反"逐字投放"。修订内容：
  1. 每个实验会话 = 一个 headless `claude -p` 全新进程（无历史、无共享上下文）；prompt 文件经 stdin 逐字节投放（`claude -p "$(cat prompt.md)" < /dev/null`），不经过编排 agent 转写；
  2. 进程 cwd 为中性目录 `/tmp/claude-headless-neutral`（无 CLAUDE.md/AGENTS.md/vault），避免向 reviewer 注入项目级指令；平台级默认（用户 settings、插件前导）对 R0/R1 对称存在，如实记录；
  3. 工具面固定：`--allowedTools Read Grep Glob Bash`，`--disallowedTools Write Edit NotebookEdit WebFetch WebSearch Task TodoWrite`；写操作由 prompt 禁止 + transcript 事后审计执行（与 v1 的"默认工具集 + 审计"执行姿态等价）；
  4. `--max-turns 128`（12 会话相同已知上限；触发上限的会话如实记录并按 §8 Inconclusive 评估）；
  5. 模型：继承宿主配置（harness 报告 `glm-5.3-flash[1m]`；CLI result JSON 的 model 字段为 null、stderr 有 `unrecognized_model` 警告——该警告对全部会话相同，如实记录，model_id 记为 `glm-5.3-flash[1m] (inherited; client-side unrecognized_model warning)`；
  6. `wall_clock_first_answer_s` 改为进程级 wall-clock（宿主在 claude 进程前后的 epoch 差），比 v1 的"完成通知返回"更精确；`session_id` = CLI 返回的 session uuid；transcript 位于 `~/.claude/projects/<cwd-slug>/<session_id>.jsonl`，原样拷贝进 `runs/<sid>/transcript.jsonl`；
  7. `platform_proxy` 记录 result JSON 的 usage（input/output/cache tokens）、duration_ms、num_turns、total_cost_usd、is_error。
- 其余条款（会话矩阵、顺序、快照、计量算法、tie-breaker、Gate、评分程序）自 v1 冻结。宿主编排备注（非协议变量）：前两次投放尝试被宿主 harness 的后台任务内存守护击杀（系统无内核 OOM），改用 setsid 脱离任务树执行同一冻结命令；两次尝试均无首答产生，归档于 `runs/s1-R1-a/infra-attempts/`。
