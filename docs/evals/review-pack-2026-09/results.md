# Results — Review Pack R0/R1 消融

- M1 预注册（提交 `543d8f3`）→ M2 快照与 Pack（`6e1b1bf`）→ 逐会话存档提交均先于本节评分写入；Git DAG 可证评分晚于全部首答冻结。
- **R1 正式判定：Inconclusive**（M4.1 修订，owner review 2026-09-13；初版曾判 No-Go，见文末修订记录）。
- **决策含义：R2 本周期不实现、不提案**（由 M4 记录的召回缺口、成本口径与 control_invalidated 共同支撑；产品代码零改动）。

## M2 快照与 Pack 验收（2026-09-11 回填，先于 M3 首个会话提交）

- 快照验收（协议 §3 五项）：三场景全部 PASS——dirty=0；`rev-list HEAD --count` s1=75 / s2=87 / s3=91 与真实仓库一致；tip 即 head；Head 后探针不可达（s1/s2：`5317784` 失败；s3：`ee4f223` 失败）；抽查文件与真实仓库 `git show <head>:` 逐字节一致。快照路径 `/tmp/rp-eval-20260911/{s1,s2,s3}`。
- 首次快照构建失败记录：第 1 次构建未删除 `refs/heads`/`refs/tags`，Head 后对象经 ref 可达（post-hole 探针 FAIL）；修正为删除全部 branch/tag ref 后 prune，复验全过。失败与修复均发生在任何会话之前。
- Pack 字段齐全性与泄漏独立检查：PASS——独立无历史只读会话按 10 项清单逐项核验 3 份 Pack（字段顺序、合同原文逐字节、diff fence 与快照 `git diff` 逐字节、changed names 一致、Verification Boundary 1/7/11 行逐字+后缀、Review State（s1 整份台账逐字节 / s2、s3 none 正确）、Decision Pointers 精确、无自然语言结论/提示、快照 clean、无可追溯性缺口）。宿主侧泄漏 grep（Head 后修复 commit 哈希与 golden 触发词）三份全净。
- Builder 成本日志指针：`packs/builder-log.md`（含 v1→v1.2 Review State 规则修订史，全部发生在任何会话与任何 Pack 提交之前）；生成器存档 `packs/build_packs.py`。

## M3 会话台账

执行顺序：第一轮 `S1-R1-a, S3-R0-a, S2-R1-a, S1-R0-a, S3-R1-a, S2-R0-a`；第二轮反向；随后按 §7 触发的 tie-breaker 与 §6 污染重跑。串行执行，全程无并行。

| 会话 | 状态 | 备注 |
| --- | --- | --- |
| s1-R1-a | ok（第 3 次尝试） | 前 2 次尝试被宿主后台任务内存守护击杀（无首答；`infra-attempts/` 留档）；第 3 次以 setsid 脱离任务树后完成 |
| s3-R0-a | ok | |
| s2-R1-a | **contaminated** | M4.1：v1.4 白名单严格适用（Skill 调用，fork 在空中性 cwd 无受保护接触——原判有效由严格字面规则取代） |
| s1-R0-a | ok（第 2 次尝试） | 第 1 次被 provider 5h 配额 429 中断（35 turns 后无首答；留档） |
| s3-R1-a | **contaminated**（第 2 次尝试） | 第 1 次 rc=126（argv 超 MAX_ARG_STRLEN 128KB，未启动；留档）→ 通道改 stdin；M4.1：Skill 调用触发作废 |
| s2-R0-a | **contaminated** | forked code-review Skill 结果自述知悉其他场景快照；§6 作废 |
| s2-R0-b | ok | |
| s3-R1-b | **contaminated** | M4.1：v1.4 白名单严格适用（Skill 调用）；其两项 P2 随之退出评分，管道截断发现保留于 owner 清单 |
| s1-R0-b | ok | |
| s2-R1-b | ok | |
| s3-R0-b | ok | |
| s1-R1-b | ok | ——初始 12 会话完成—— |
| s1-R0-c | ok | §7 tie-breaker（S1-R0 cell verdict 分歧） |
| s1-R1-c | **contaminated** | forked code-review Skill 审查了真实仓库（含评分材料）；§6 作废 |
| s2-R0-c | **contaminated** | M4.1：漏检的 Skill 调用（fork 钉定 s2 快照）；v1.4 白名单严格适用；其 refused-vault P2 发现由有效会话 s3-R0-c 独立报告并经独立 review 复现，保留于 owner 清单 |
| s3-R0-c | ok | §7 tie-breaker |
| s3-R1-c | ok | §7 tie-breaker |
| s2-R0-d | **contaminated** | `ls` eval 根目录（受保护区）；§6 作废；tie-breaker 名额（第 6 个）已耗尽 |
| s1-R1-d | ok | §6 污染重跑（替换 s1-R1-c），不占 tie-breaker 名额 |

- 有效会话 12（M4.1 修订：初版曾计 16）；作废 7（含 M4.1 新增的 4 个 Skill 会话，均留档并在 run.json 记录裁决）；infra 中断 5 次（内存守护 ×2、配额 ×1、argv 长度 ×1、投放脚本缺 prompt 文件 ×1——宿主操作失误，未启动模型）。
- 污染审计规则演进：v1.2（scratch 写入不计污染）→ v1.3（self-runtime 工件放行）→ v1.4（工具白名单 {Read,Grep,Glob,Bash}）。**执行缺陷（owner review P1-2）**：v1.4 白名单曾只写入文档未落入审计脚本，且唯一一次全量白名单扫描运行于 s2-R0-c/s3-R0-c/s3-R1-c 完成之前——导致 4 个 Skill 会话漏判有效；owner review 发现后已按字面规则全部作废并重算，`tools/audit_session.py` 已补实现。
- 协议偏差：S2 场景 tie-breaker 的 R1 侧（s2-R1-c）因 6 会话上限耗尽未运行；S2-R0 cell 在初版口径下 1-1 unstable，M4.1 作废后仅剩 1 个有效会话（b）。已如实记录。

## M4 评分

### Golden 命中（M4.1 修订：仅 12 个有效会话计分；命中=指出核心缺陷，证据路径允许同义；severity/报告载体不改变命中）

| 会话 | S1 (G1 W组gate / G2 模板 / G3 main位置 / G4 重复行顺序 / G5 runtime矛盾) | S2 P0/P1 (G1 原因码 / G2 消融存档) | S2 P2 (G3 handoff) | S3 | verdict |
| --- | --- | --- | --- | --- | --- |
| s1-R0-a | – / – / – / – / – | | | | REQUEST_CHANGES |
| s1-R0-b | – / – / – / – / – | | | | APPROVE |
| s1-R0-c | **G1** / – / – / – / – | | | | REQUEST_CHANGES |
| s1-R1-a | – / – / – / – / – | | | | APPROVE |
| s1-R1-b | – / – / – / – / – | | | | APPROVE |
| s1-R1-d | – / **G2** / – / – / – | | | | REQUEST_CHANGES |
| s2-R0-b | | – / **G2** | **G3** | | APPROVE |
| s2-R1-b | | **G1**(观察) / **G2**(Q6) | – | | APPROVE |
| s3-R0-a | | | | 1×unlisted_real（短行 unresolved 缺口，已复现；owner 裁定真实 P1） | REQUEST_CHANGES |
| s3-R0-b | | | | 0 blocker（5×P3） | APPROVE |
| s3-R0-c | | | | 1×P2（refused-vault unresolved:0 同族；self-标注 non-blocking；独立 review 已复现；owner 裁定真实 P1） | APPROVE |
| s3-R1-c | | | | 0 blocker（P3 观察） | APPROVE |

作废会话（7 个，不计分，裁决见各自 run.json 与 M3 台账）：s1-R1-c（Skill 审查真实仓库）、s2-R0-a（跨快照知悉）、s2-R0-c（Skill，其 refused-vault P2 由 s3-R0-c 独立覆盖）、s2-R0-d（`ls` eval 根目录）、s2-R1-a / s3-R1-a / s3-R1-b（Skill，M4.1 严格适用）。作废会话的观察仅供 owner 参考：s2-R0-a 曾观察到 G-S2-1 核心缺陷并给出与 owner 修复同向的 fix direction；s3-R1-b 曾把已裁定 P3-5 升级为 blocker（若计分将构成 fabricated）并独立发现管道截断（owner 裁定真实 P2）。

### 硬指标（M4.1 修订：冻结口径重算，12 有效会话）

| # | 条件 | 结果 |
| --- | --- | --- |
| 1 | 安全硬指标全过（fabricated=0、Authority/Accepted 错误=0、fresh 误标=0、Forbidden/OOS 反向=0） | PASS（有效会话内）：fabricated=0（s3-R1-b 的升级行为随会话作废退出评分，作为观察记录）；其余三项全部有效会话 =0 |
| 2 | R1 正样本 **known P0/P1** golden 并集召回 =100%（计划 §10.1 冻结分母；owner review P1-4 更正——初版误将 P2 floor 的 golden 计入分母） | **FAIL**：S1 1/4=25%（仅 G-S1-2；G1/G3/G4 遗漏）；S2 2/2=100%。S1 单场景即阻断任何 Go |
| 3 | R1 单会话召回中位数 ≥ R0 | PASS：S1 0 vs 0（P0/P1 口径）；S2 2 vs 1（R1 仅 1 个有效会话） |
| 4 | 负对照可解释性 | **失效**：负对照本身被 control_invalidated（其上测得的 fabricated 等指标不支撑任何方向的终局结论） |
| 5 | Pack 无 golden 特化/截断/字段遗漏 | PASS（M2 独立审计 10/10） |
| 6 | ≥1 项成本中位数改善 ≥30% 且其余关键成本无明显恶化 | 前半满足：visible −57.6% ✓、vault −46.2% ✓（tools −12.8% ✗）；后半不满足：wall +24.4% 恶化 → **Go 阻断**（按冻结 §8，成本恶化只阻断 Go，非独立 No-Go 触发） |
| — | control_invalidated | **成立，两处独立登记**（短行 id 缺口 + refused-vault unresolved:0；均有有效会话来源并经独立 review 在 `5317784` 复现；owner 已裁定前者真实 P1、后者真实 P1）→ **按计划 §10.1，本轮结论封顶 Inconclusive** |

**正式判定：R1 = Inconclusive。** 依据计划 §10.1（"本轮结论最多 Inconclusive"）：负对照被真实缺陷失效后，实验不能输出任何方向的终局结论——包括初版发布的 No-Go。M4 的记录性发现（S1 召回 25%、wall-clock 恶化、作废会话中的 P3-5 升级行为）如实保留，作为"R2 本周期不实现"的决策依据，但不构成本实验的正式结论。owner 裁定同轮确认：R2 本周期不开发是合理决策。

### 成本原值与聚合（M4.1：12 个有效会话；单位：字节/次/秒）

| 会话 | material | tool_calls | visible_output | vault_opens | wall_s |
| --- | --- | --- | --- | --- | --- |
| s1-R0-a | 2019 | 39 | 152935 | 12 | 615.4 |
| s1-R0-b | 2019 | 36 | 162768 | 9 | 629.5 |
| s1-R0-c | 2019 | 39 | 178876 | 12 | 879.8 |
| s2-R0-b | 2011 | 39 | 174482 | 14 | 710.8 |
| s3-R0-a | 2011 | 34 | 128123 | 13 | 952.1 |
| s3-R0-b | 2011 | 53 | 185546 | 20 | 774.4 |
| s3-R0-c | 2011 | 47 | 162163 | 16 | 745.8 |
| s1-R1-a | 112099 | 34 | 69051 | 8 | 1198.7 |
| s1-R1-b | 112099 | 30 | 53618 | 7 | 759.8 |
| s1-R1-d | 112099 | 44 | 108765 | 15 | 928.2 |
| s2-R1-b | 116217 | 39 | 117745 | 5 | 1041.3 |
| s3-R1-c | 212334 | 33 | 55667 | 5 | 682.0 |

| arm 中位数 | R0 (n=7) | R1 (n=5) | Δ |
| --- | --- | --- | --- |
| material_bytes | 2,011 | 112,099 | +5,474%（Pack 内嵌，设计使然） |
| tool_calls | 39 | 34 | −12.8% |
| visible_output_bytes | 162,768 | 69,051 | **−57.6% ✓** |
| vault_opens | 13 | 7 | **−46.2% ✓** |
| wall_clock_first_answer_s | 745.8 | 928.2 | **+24.4% 恶化 ✗** |

（初版 16 有效口径的聚合（visible −61.6%、vault −52.0%、tools −14.1%、wall +29.6%）保留于 Git 历史 `493f8dc`/`10647bd`，作对照。）

- R1 builder 成本（端到端）：构建 compute ≈0.06s/份；会话级端到端（含规则修订与快照返工）≈25 分钟（`packs/builder-log.md`）。稳态自动化下 builder 成本可忽略，但 R2 的准入论证前提（R1 达 Go）未满足。
- 计量口径注（独立 review P2-3）：`visible_output_bytes`、`tool_calls`、`material_bytes`、wall-clock 均可由 `runs/*/transcript.jsonl` 机械重算；`file_opens_task_vault` 含按调用目的对 Bash 读取的归类判断，非纯机械量——按纯 Read/Grep/Glob 机械口径复算为 −37.0%，两种口径下 ≥30% 改善的结论一致。宿主投放与计量脚本已存档于 `tools/` 供复算。
- Tie-breaker 多数决（M4.1 后的 cell 口径）：S1-R0 = RC（2/3 有效）；S1-R1 = A（2/3 有效，a,b vs d）；S3-R0 = A（2/3）；S2-R0 / S2-R1 / S3-R1 = 每 cell 仅 1 个有效会话（M4.1 作废后不再构成多数决；S2-R0 在初版口径下曾 1-1 unstable）。

## 结论

- **R1 正式判定：Inconclusive**（M4.1 修订；初版 No-Go 违反计划 §10.1 的封顶规则，owner review 2026-09-13 更正）。
- Gate 逐条推导见上表，可由 `runs/*/answer.md`、`runs/*/run.json` 与 `scoring.md` 完全重算（独立 review 已机械复核一轮；M4.1 重算待下轮复核抽查）。
- **R2 本周期不实现、不提交提案。** 支撑该决策的记录性发现（非正式结论）：Review Pack 显著降低 reviewer 的可见读取量与 vault 文件打开数（上下文组装效率真实改善），但 S1 场景 known-P0/P1 召回仅 25%（G1/G3/G4 遗漏，且命中项与 R0 互不相同），wall-clock 中位数恶化 24.4%，作废会话中还观察到 P3-5 升级为 blocker 的过报行为；负对照被两处真实缺陷失效（control_invalidated 双登记），实验无法给出任何方向的终局结论。
- 实验附带产出（供 owner 裁决，均不经 Gate）：见 §5。

## 实验附带缺陷清单（owner 裁决项）

1. **`status` 短行 id 缺口**（s3-R0-a 发现，scorer 独立复现；独立 review 复核确认）：malformed 短行引用的缺失任务不进 `unresolved`（`TASK_RUNTIME_INVALID` 无 task_id），违反 AC"malformed…全部 fail-closed"与 MIGRATIONS/README"无法解析的任务显式列入 unresolved"。→ **control_invalidated 登记（第一处）**。**owner 裁定（2026-09-13）：真实 P1。**
2. **refused-vault `unresolved: 0`**（s2-R0-c 以 P2 发现，s3-R0-c 独立以 P2 报告同一缺陷族；独立 review 在 `5317784` 现场复现）：`vault/` 或 `vault/tasks` 被符号链接拒绝枚举时，`summary.unresolved` 输出 0（全零摘要），仅 `SYMLINK_INPUT` 错误可见——"unresolved: 0" 是对从未读取内容的机器可读"无未解决项"断言，违反 AC"全部 fail-closed"与 plan §5.4 kill criterion"对 closed/unresolved 任务产生任何 fail-open 表述"；缓解项：exit 2 仍发出。→ **control_invalidated 登记（第二处）**。**owner 裁定（2026-09-13）：真实 P1。**
3. **管道截断**（s3-R1-b 发现，scorer 复现；s2-R0-c 作为 P3 独立观察到同一现象）：Next Action 含 `|` 时投影静默截断且 exit 0 无 finding。**owner 裁定（2026-09-13）：真实 P2。**
4. **同 id 不可读副本**（s3-R1-b 以 P2 重报）：即任务内已记录的 P3-5。**owner 裁定（2026-09-13）：维持既有 P3，不作为本轮 blocker**（本会话已作废，升级行为不再计入 Gate）。
5. **S1 场景 five 项 owner findings 中 4 项（G1/G3/G4/G5）双臂有效会话仅 1 次命中**（G1，R0-c）；G3（unittest.main 位置）、G4（重复行顺序依赖）、G5（runtime 矛盾行）双臂全部遗漏——review 输入形状不是该样本上 review 深度的约束瓶颈。

### 正样本场景非 golden blocker 主张分类（协议 §9.3，独立 review P1-3 补全）

- `unlisted_real`（有证据、可复现，owner 未记录；已入上文清单或供 owner 裁决）：s1-R0-b P2-1（M5 验收标准在必须满足它的范围内被就地改写——reviewer 与独立 review 均在 base↔head 逐字验证）；s1-R0-b P2-2（malformed 行 local 模式 warning vs tracked error 的不对称，fixture 实证）；s1-R0-b P2-3 / s1-R0-a F-3 / s1-R0-c F-2 / s1-R1-b P2-1 / s1-R1-d F-B（台账 F3 的"124"不可复现，静态计数证明 87/136 才是真实值）；s1-R0-a F-2 / s1-R0-b P2-3 / s1-R0-c F-1 / s1-R1-d F-C（M6 "CI 全绿" `[x]` 无 run id 留痕）；s2-R0-c P2（refused-vault，见清单第 2 项）；s2-R0-a 的 P3 观察集（会话已作废，不作评分依据，仅存档）。
- `false_positive`：0（所有上报 blocker 均有可定位证据与机制说明，无误读快照或凭空主张）。

## 偏差与协议修订记录

- 协议 v1.1（投放机制）、v1.2（scratch 写入）、v1.3（self-runtime 工件 + stdin 通道）、v1.4（Skill 白名单）——全部先于受影响评分存在，理由与影响见 protocol.md 修订记录。
- **M4.1 修订（owner review 2026-09-13；本节即为预注册修订说明）**：
  1. 正式判定 No-Go → **Inconclusive**（初版违反计划 §10.1"control_invalidated 后本轮结论最多 Inconclusive"的封顶规则）；
  2. 召回率改用冻结的 known P0/P1 分母（S1 1/4=25%，S2 2/2=100%；初版 20%/67% 误含 P2 floor golden）；
  3. 按 v1.4 字面规则新作废 4 个 Skill 会话（s2-R0-c、s2-R1-a、s3-R1-a、s3-R1-b——初版白名单扫描先于这些会话完成，审计脚本未实现白名单），有效会话 16 → 12，全部聚合重算；
  4. 负对照相关指标（含 fabricated 计数）标注为不可解释，不再作为任何方向的终局依据；
  5. owner 对四项 status 缺陷的 severity 裁定（P1/P1/P2/维持 P3）写入清单。
  修订原因：owner 对冻结规则的解释权与执行完整性要求；修订不触碰任何 transcript/answer/prompt/pack 原始材料。
- 宿主操作失误两次：s2-R0-d 首次投放前未装配 prompt 文件（脚本瞬时失败，无模型调用）；v1.4 白名单只写文档未落入审计脚本且全量扫描时点过早（即 M4.1 起因）。如实记录。
- 局限：有效会话 n=7/5（作废后）属探索性证据；单仓库三个场景；S2 两 cell 与 S3-R1 cell 仅剩 1 个有效会话、S1-R0/R1 各 3/3-1；wall-clock 受 Pack 内嵌体积影响显著；`visible_output_bytes` 的 R1 优势部分来自 Pack 替代了原本必要的自行读取，其对判断质量的净效应在本实验中无法与召回缺口分离。

## push 前隐私与历史处理（owner 已裁决方案 B；执行待最终批准）

- 现状（owner review P1-3，已核实）：本 eval 目录的 19 份 transcript.jsonl 与 run.json 含宿主绝对路径、session UUID、`total_cost_usd` 等本机元数据；s2-R1-a 的 fork 输出枚举了 <host-path> 下无关仓库名；未发现任何凭据/Token。
- **owner 裁决（2026-09-13）：方案 B**——`git filter-repo` 脱敏未推送历史；A（原样 push）因仓库已有公开安装路径被否决，C（剥离 transcript）因损失审计证据被否决。**执行门槛：owner 明确回复"批准执行 B"后方可执行。**
- B 的前置准备状态：
  1. ✅ 原始归档已保留：`~/trellium-eval-raw-archive-20260913/`（16MB，167 文件）+ `SHA256SUMS-original.txt`（manifest 根哈希 `9f89536e…d783`）；仓库内不留该归档。
  2. ✅ 范围更正：未推送提交为 **24 个**（`origin/develop..HEAD`，初版误报 23）。
  3. ⏳ `git filter-repo` 未安装（owner 指出）；执行日前需 `pip install --user git-filter-repo` 或等价单文件安装。
  4. 冻结的脱敏映射（B 执行时逐条应用，映射表随仓库提交供复核）：宿主绝对路径 `<host-path>/...` → `<host-path>`；session UUID → `<session-uuid>`；`total_cost_usd` 数值 → 移除字段（保留 duration/bytes）；无关仓库名枚举（s2-R1-a fork 文本）→ `<redacted-local-repos>`；`/tmp/claude-1002/...` 与 `/tmp/rp-eval-20260911/` 保留（非个人路径，且为复算所需）。
  5. 执行后验证：对 `origin/develop..HEAD` 全历史（非仅最终文件）重跑同一敏感模式扫描，结果须为 0 命中；任何含原始元数据的备份引用（refs/original、filter-repo 自带 backup）不得 push，本地验证后删除。
  6. 脱敏后逐字节重算性说明：metric 字段（bytes/次数/秒）不受影响；transcript 内路径类上下文降为占位符，README 需声明该映射。
- 在 owner 回复"批准执行 B"前：**不 push、不重写历史**。
