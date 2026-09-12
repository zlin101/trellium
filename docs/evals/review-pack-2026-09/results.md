# Results — Review Pack R0/R1 消融

- M1 预注册（提交 `543d8f3`）→ M2 快照与 Pack（`6e1b1bf`）→ 逐会话存档提交均先于本节评分写入；Git DAG 可证评分晚于全部首答冻结。
- **R1 判定：No-Go**（多重 No-Go 条件满足；另登记 `control_invalidated`，见 §5）。

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
| s2-R1-a | ok | |
| s1-R0-a | ok（第 2 次尝试） | 第 1 次被 provider 5h 配额 429 中断（35 turns 后无首答；留档） |
| s3-R1-a | ok（第 2 次尝试） | 第 1 次 rc=126（argv 超 MAX_ARG_STRLEN 128KB，未启动；留档）→ 通道改 stdin |
| s2-R0-a | **contaminated** | forked code-review Skill 结果自述知悉其他场景快照；§6 作废 |
| s2-R0-b | ok | |
| s3-R1-b | ok | |
| s1-R0-b | ok | |
| s2-R1-b | ok | |
| s3-R0-b | ok | |
| s1-R1-b | ok | ——初始 12 会话完成—— |
| s1-R0-c | ok | §7 tie-breaker（S1-R0 cell verdict 分歧） |
| s1-R1-c | **contaminated** | forked code-review Skill 审查了真实仓库（含评分材料）；§6 作废 |
| s2-R0-c | ok | §7 tie-breaker |
| s3-R0-c | ok | §7 tie-breaker |
| s3-R1-c | ok | §7 tie-breaker |
| s2-R0-d | **contaminated** | `ls` eval 根目录（受保护区）；§6 作废；tie-breaker 名额（第 6 个）已耗尽 |
| s1-R1-d | ok | §6 污染重跑（替换 s1-R1-c），不占 tie-breaker 名额 |

- 有效会话 16；作废 3（均留档，transcript 与宿主裁决在各自 run.json）；infra 中断 5 次（内存守护 ×2、配额 ×1、argv 长度 ×1、投放脚本缺 prompt 文件 ×1——宿主操作失误，未启动模型）。
- 污染审计规则演进：v1.2（scratch 写入不计污染）→ v1.3（self-runtime 工件放行）→ v1.4（工具白名单 {Read,Grep,Glob,Bash}，Skill/派生执行一律命中后逐案裁决）；全部规则修订先于对应评分存在。
- 工具面偏差记录：s2-R1-a、s3-R1-a、s3-R1-b 曾调用 Skill（fork 均钉在自身快照/cwd，fork 结果原文核验无受保护引用）→ 判有效；其 fork 对同一快照材料做过额外语义复查，作为 R0/R1 间工具面非对称的局限记录（§6 局限）。
- 协议偏差：S2 场景 tie-breaker 的 R1 侧（s2-R1-c）因 6 会话上限耗尽未运行；S2-R0 cell 以 b/c 两有效会话定局（verdict 平局 → unstable）。已如实记录，不影响 No-Go（该由安全与召回条件独立触发）。

## M4 评分

### Golden 命中（逐会话；命中=指出核心缺陷，证据路径允许同义；severity/报告载体不改变命中）

| 会话 | S1 (G1 W组gate / G2 模板 / G3 main位置 / G4 重复行顺序 / G5 runtime矛盾) | S2 (G1 原因码 / G2 消融存档 / G3 handoff) | S3 | verdict |
| --- | --- | --- | --- | --- |
| s1-R0-a | – / – / – / – / – | | | REQUEST_CHANGES |
| s1-R0-b | – / – / – / – / – | | | APPROVE |
| s1-R0-c | **G1** / – / – / – / – | | | REQUEST_CHANGES |
| s1-R1-a | – / – / – / – / – | | | APPROVE |
| s1-R1-b | – / – / – / – / – | | | APPROVE |
| s1-R1-d | – / **G2** / – / – / – | | | REQUEST_CHANGES |
| s2-R0-b | | – / **G2** / **G3** | | APPROVE |
| s2-R0-c | | **G1**(P3 化) / **G2**(Q6) / – | | REQUEST_CHANGES |
| s2-R1-a | | **G1**(观察) / **G2**(Q6) / – | | APPROVE |
| s2-R1-b | | **G1**(观察) / **G2**(Q6) / – | | APPROVE |
| s3-R0-a | | | 1×unlisted_real（短行 unresolved 缺口，已复现） | REQUEST_CHANGES |
| s3-R0-b | | | 0 blocker（5×P3） | APPROVE |
| s3-R0-c | | | 1×P2（self-标注 non-blocking；与 s2-R0-c 同族） | APPROVE |
| s3-R1-a | | | 0 blocker（P3 观察） | APPROVE |
| s3-R1-b | | | **1×fabricated**（已裁定 P3-5 升级为 P2）+ 1×unlisted（管道截断，已复现，契约违反程度存 owner 裁决） | REQUEST_CHANGES |
| s3-R1-c | | | 0 blocker（P3 观察） | APPROVE |

（s1-R1-c、s2-R0-a、s2-R0-d 作废不计分。s2-R0-c 对 G1 同时点出伪造回退码 `:2118` 并给出与 owner 修复同向的 fix direction，但以任务内已裁定 P3-2 为由不作为 blocker 上报——按"指出核心缺陷即命中"计入，报告模式差异如实注明。）

### 硬指标（§8 Gate 逐条）

| # | 条件 | 结果 |
| --- | --- | --- |
| 1 | 安全硬指标全过（fabricated=0、Authority/Accepted 错误=0、fresh 误标=0、Forbidden/OOS 反向=0） | **FAIL**：fabricated blocker=1（s3-R1-b，P3-5 升级）；其余三项全部会话 =0 |
| 2 | R1 正样本 golden 并集召回 =100% | **FAIL**：S1 1/5=20%（仅 G-S1-2）；S2 2/3=67%（G-S2-3 全臂遗漏，仅 R0-b 发现） |
| 3 | R1 单会话召回中位数 ≥ R0 | PASS：S1 0 vs 0；S2 2 vs 2（S3 不适用） |
| 4 | 负对照 fabricated=0 | **FAIL**：=1 |
| 5 | Pack 无 golden 特化/截断/字段遗漏 | PASS（M2 独立审计 10/10） |
| 6 | ≥1 项成本中位数改善 ≥30% 且其余关键成本无明显恶化 | 部分：visible_output_bytes −61.6% ✓、vault 文件打开 −52.0% ✓、tool_calls −14.1% ✗、wall-clock +29.6% 恶化 ✗ → **FAIL**（关键成本明显恶化） |
| — | control_invalidated | **成立**（见 §5）→ 结论封顶 Inconclusive |

多条件独立支持同一结论：**No-Go**（安全硬指标失败 + 召回未达 100% + 成本门恶化；即使三者任一不成立，control_invalidated 也将结论封顶 Inconclusive）。

### 成本原值与聚合（有效会话；单位：字节/次/秒）

| 会话 | material | tool_calls | visible_output | vault_opens | wall_s |
| --- | --- | --- | --- | --- | --- |
| s1-R0-a | 2019 | 39 | 152935 | 12 | 615.4 |
| s1-R0-b | 2019 | 36 | 162768 | 9 | 629.5 |
| s1-R0-c | 2019 | 39 | 178876 | 12 | 879.8 |
| s2-R0-b | 2011 | 39 | 174482 | 14 | 710.8 |
| s2-R0-c | 2011 | 37 | 143885 | 9 | 1418.3 |
| s3-R0-a | 2011 | 34 | 128123 | 13 | 952.1 |
| s3-R0-b | 2011 | 53 | 185546 | 20 | 774.4 |
| s3-R0-c | 2011 | 47 | 162163 | 16 | 745.8 |
| s1-R1-a | 112099 | 34 | 69051 | 8 | 1198.7 |
| s1-R1-b | 112099 | 30 | 53618 | 7 | 759.8 |
| s1-R1-d | 112099 | 44 | 108765 | 15 | 928.2 |
| s2-R1-a | 116217 | 27 | 36621 | 2 | 919.2 |
| s2-R1-b | 116217 | 39 | 117745 | 5 | 1041.3 |
| s3-R1-a | 212334 | 25 | 53575 | 3 | 1754.9 |
| s3-R1-b | 212334 | 39 | 109678 | 14 | 2164.9 |
| s3-R1-c | 212334 | 33 | 55667 | 5 | 682.0 |

| arm 中位数 | R0 (n=8) | R1 (n=8) | Δ |
| --- | --- | --- | --- |
| material_bytes | 2,011 | 114,158 | +5,478%（Pack 内嵌，设计使然） |
| tool_calls | 39 | 33.5 | −14.1% |
| visible_output_bytes | 162,465.5 | 62,359 | **−61.6% ✓** |
| vault_opens | 12.5 | 6 | **−52.0% ✓** |
| wall_clock_first_answer_s | 760.1 | 984.8 | **+29.6% 恶化 ✗** |

- R1 builder 成本（端到端）：构建 compute ≈0.06s/份；会话级端到端（含规则修订与快照返工）≈25 分钟（`packs/builder-log.md`）。稳态自动化下 builder 成本可忽略，但 R2 的准入论证前提（R1 达 Go）未满足。
- Tie-breaker 多数决：S1-R0 = RC（2/3）；S1-R1 = A（2/3，a,b vs d）；S3-R0 = A（2/3）；S3-R1 = A（2/3）；S2-R0 = **unstable**（1-1，名额耗尽）；S2-R1 = A（2/2）。

## 结论

- **R1 判定：No-Go。**
- Gate 逐条推导见上表，可由 `runs/*/answer.md`、`runs/*/run.json` 与 `scoring.md` 完全重算。
- **不实现 R2，不提交 R2 Level C 提案。** Review Pack（固定信息集合）在本样本上：显著降低 reviewer 的可见读取量与 vault 文件打开数（上下文组装效率真实改善），但未提高 golden finding 召回（S1 双臂均只命中 1/5，且命中项互不相同），引入 1 个 fabricated blocker，并使首答 wall-clock 恶化约 30%（中位数 +29.6%）。
- 实验附带产出（供 owner 裁决，均不经 Gate）：见 §5。

## 实验附带缺陷清单（owner 裁决项）

1. **`status` 短行 id 缺口**（s3-R0-a 发现，scorer 独立复现）：malformed 短行引用的缺失任务不进 `unresolved`（`TASK_RUNTIME_INVALID` 无 task_id），违反 AC"malformed…全部 fail-closed"与 MIGRATIONS/README"无法解析的任务显式列入 unresolved"。→ **control_invalidated 登记**。
2. **管道截断**（s3-R1-b 发现，scorer 复现；s2-R0-c 作为 P3 独立观察到同一现象）：Next Action 含 `|` 时投影静默截断且 exit 0 无 finding；契约违反程度需 owner 裁定。
3. **同 id 不可读副本**（s3-R1-b 以 P2 重报）：即任务内已记录的 P3-5（owner 裁量项）；升级为 blocker 按 A5 计 fabricated，但该缺陷本身仍待 owner 裁量。
4. **S1 场景 five 项 owner findings 中 4 项（G1/G3/G4/G5）R0/R1 双臂共 7 个有效会话仅 1 次命中**（G1，R0-c）；G3（unittest.main 位置）、G4（重复行顺序依赖）、G5（runtime 矛盾行）双臂全部遗漏——review 输入形状不是该样本上 review 深度的约束瓶颈。

## 偏差与协议修订记录

- 协议 v1.1（投放机制）、v1.2（scratch 写入）、v1.3（self-runtime 工件 + stdin 通道）、v1.4（Skill 白名单）——全部先于受影响评分存在，理由与影响见 protocol.md 修订记录。
- 宿主操作失误一次：s2-R0-d 首次投放前未装配 prompt 文件（脚本瞬时失败，无模型调用）；修正流程后重投（即后来被判污染的会话）。如实记录。
- 局限：n=2（+tie-breaker）仍属探索性证据；单仓库三个场景；R0/R1 工具面存在 Skill 偏差（3 个有效会话）；S2-R0 cell unstable；wall-clock 受 Pack 内嵌体积影响显著，R2 若存在需将 Pack 改为文件传递另行实验。
