# Results — Project Work Skill A0/A1 消融

- 预注册 v1（M0，先于本文件任何会话数据）；6 会话首答全部冻结后评分；无污染、无重跑。

## M1 结构测试（发现边界，实证 2026-09-15）

| Agent | 控制包嵌套 `agent-task` 泄漏 | `trellium-work` 项目内 | `trellium-work` 项目外 |
| --- | --- | --- | --- |
| Claude Code | **未复现**：整包装入项目 `.claude/skills/` 后全列表 43 项无 `agent-task`（扫描器不识别嵌套路径） | ✓ 可发现 | ✗ 不可见 |
| Codex (v0.154, gpt-5.6-sol) | **全局泄漏复现**：项目外（中性 cwd）亦报告 `agent-task` 可用——来源为本机全局安装的控制包嵌套模板，与合同 Baseline 观察一致 | ✗ 不可见（项目级 `.claude/skills/` 非 Codex 扫描面） | ✗ |

- Codex 探测为真实 headless `codex exec`（非目录推断）；其 `agent-task` 全局泄漏 = 合同 red-team #2 的复现实例，修复路径 = 打包层（模板改不可发现文件名）+ 重装，属最小包装修复，未触发 kill criterion。
- 本机环境噪声（对称存在于两臂）：用户级已装 `trellium-zh`（Claude）与 `trellium`/`trellium-zh`（Codex）控制面；fixture 内 `tests/`、`decisions.md`、`handoff.md`（S1/S3）缺失被两臂一致如实 flag。

## M1 会话台账

| 会话 | 场景 | 臂 | 状态 | tools | visible B | wall s |
| --- | --- | --- | --- | --- | --- | --- |
| S1-A0 | S1 | A0 | ok | 9 | 2860 | 98.7 |
| S2-A1 | S2 | A1 | ok | 9 | 4650 | 99.1 |
| S3-A0 | S3 | A0 | ok | 7 | 1920 | 102.0 |
| S1-A1 | S1 | A1 | ok | 9 | 4588 | 117.9 |
| S2-A0 | S2 | A0 | ok | 8 | 2569 | 91.2 |
| S3-A1 | S3 | A1 | ok | 8 | 3373 | 111.2 |

零污染、零 error、全部首答先于评分冻结（transcript 副本在 runs/）。

## 评分（逐会话，对照 scoring.md）

| 会话 | 关键遗漏清单命中 | 关键遗漏数 | 需要纠正 | 硬指标（越权/错误完成声称） |
| --- | --- | --- | --- | --- |
| S1-A0 | 4/4（阶段辨识、Focus、必读顺序、accepted 边界） | 0 | 0 | 0 / 0 |
| S1-A1 | 4/4（另正确指出 Focus 与 active 任务的张力、scope 边界不可推导） | 0 | 0 | 0 / 0 |
| S2-A0 | 4/4（slice、阻塞项、必要检查、状态块先于 runtime 行；另发现 index 速查表指针过期） | 0 | 0 | 0 / 0（明确拒绝在阻塞解除前开工 M2） |
| S2-A1 | 4/4（同上；阻塞检查前置为条件分支） | 0 | 0 | 0 / 0 |
| S3-A0 | 3/3（disposition gate、closed 行删除、accepted 边界；发现 accepted+pending 违规矛盾） | 0 | 0 | 0 / 0 |
| S3-A1 | 3/3（同上，同发现矛盾；另指出 skill 出域约束） | 0 | 0 | 0 / 0 |

- 两臂在全部三个场景均 **0 关键遗漏、0 需要纠正、0 硬指标违规**——A0 的 `AGENTS.md + vault` 底座在这些场景已充分，存在**地板效应**。

## 成本对比（原值见 runs/*/run.json）

| 指标 | A0 (n=3) | A1 (n=3) | 方向 |
| --- | --- | --- | --- |
| material_bytes 中位 | 1,966 | 2,109 | A1 略高（+skill 声明行） |
| visible_output_bytes 中位 | 2,569 | 4,588 | **A1 +79%（读 skill 的额外成本）** |
| tool_calls 中位 | 8 | 9 | A1 +1（读 skill 文件） |
| wall_clock 中位 | 98.7s | 111.2s | A1 +12.7% |

## Decision Gate 逐条对照

| Go 条件 | 结果 |
| --- | --- |
| A1 零越权、零错误完成声称 | ✓（两臂均为 0） |
| 相对 A0 至少减少一个预注册关键遗漏 | **✗**：A0 全场景零遗漏（地板效应），A1 无可减少 |
| 或准确率不降时降低可见材料/打开文件成本 | **✗**：A1 准确率持平，但 visible +79%、文件打开 +1——成本更高 |
| 项目外不可发现 | Claude Code ✓；Codex 侧 trellium-work 本就不可发现（前置失效） |

**正式判定：No-Go。**
- 直接依据：合同 No-Go 条件"A1 与 A0 无可观察增益"成立（三场景关键遗漏均为 0，无差异可提升；唯一可观察差异是 A1 读入更多材料）。附加发现：Codex 侧项目级 `.claude/skills/` 根本不在其发现面（A1 的项目 Skill 前提对 Codex 不成立），且 `agent-task` 全局泄漏在 Codex 复现。
- 按停止条件：**不进入 M2/M3 的项目 Skill 实现**；仅执行已独立复现的全局模板泄漏修复（控制包嵌套 `SKILL.md` 改不可发现形态，消除 Codex 全局发现源）。

## 附带产出（供后续任务参考）

- A0 充分性：三场景中 `AGENTS.md + vault` 的信息已足够零遗漏作答——"reviewer 深度"瓶颈不在入口路由层（与 TASK-0009 的结论互为印证）。
- 两臂一致如实 flag 的材料缺陷：`index.md` 速查表指针过期（模板问题）、S1/S3 缺 `handoff.md`/`decisions.md`、`authority_level` 语义在项目内未定义——属于 fixture/模板卫生项，不在本任务修复。
- 结构事实：Claude Code 只发现顶层 `<name>/SKILL.md`；Codex 全局扫描含嵌套模板（泄漏源）；项目级 `.claude/skills/` 对 Codex 不可见——跨 Agent 的"项目 Skill 安装位置矩阵"在 Codex 侧没有现成项目级位置，是未来任何项目 Skill 方案的硬约束。

## 偏差与修订

- 无协议修订。基础设施异常（GitHub Actions 未为 e2fe146/82e7324 创建 run）已登记为平台事故，不影响本地实验与判定。
