# 09.3 Post-release Validation：自托管试点闭环与 Context Go/No-Go

> 阶段任务书。主线是"证明 09.3 的实际价值并减少治理摩擦"，而不是立即扩大功能面。只有冷启动对照实验明确证明上下文读取是主要成本，才进入最小 Context Manifest。

- 日期：2026-09-08
- 状态：Owner 已批准（owner 直接下发本方案文本作为执行指令）
- 输入：`docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md`（前周期，已全部闭环）
- 当前协议版本：`2026.09.3`
- 任务映射：M1-M3 归 `vault/tasks/TASK-0004-post-release-validation.md`（Level B）；M4 仅在 Go 后另立 Level C 任务，本阶段不实现

## 0. 已验证基线（2026-09-08 现场）

- 2026.09.3 Release 已发布：tag 正确（`97d5506`）、非 draft、非 prerelease；`releases/latest` 解析到 `2026.09.3`（两个独立会话现场核验一致）；
- Release 标题与正文为空——owner 决定降为可选改进（D-0003），不作为任何 Gate；
- TASK-0002 已 accepted；TASK-0001（shadow 试点）active；TASK-0003（上一周期）accepted；
- CI：PR 与 `main`/`develop` push 运行只读 self-hosting check，权限最小化（D-0002），develop push 首跑全绿；
- canonical K1-K4 契约已校准（D-0001）；coverage 计数：3 TASK / 7 转换 / 1 blocked→active。

## M0：正式关闭 09.3 ✅（本计划下发前已完成）

- 按 owner 结论，2026.09.3 Release 视为完成；标题和 notes 降为可选改进（D-0003）；
- TASK-0002 推进至 accepted（Codex 完成 blocked → active 与现场核验；GLM 完成元数据降级与 accepted）；
- Codex 留下的 4 个未提交 vault 状态文件已由 GLM 审阅（全部为规范记录，无覆盖）并随本次提交入库；
- 推送后在 GitHub Actions 确认全绿。

## M1：建立冷启动基线

选择 5–7 个真实场景，让**没有聊天历史的新 Agent** 判断（协议见 `vault/details/cold-start-baseline-2026-09.md`）：

- 当前任务目标和下一步；
- 当前有效契约和 Authority；
- 旧 Accepted 与新 amendment 的关系；
- handoff 与实时 Git 冲突时相信谁；
- 代码变化后旧测试证据是否仍有效；
- proposal 是否会被误当成已批准契约；
- tracked/local 项目是否能恢复长期事实。

只记录这些指标：

- 五个核心问题的判断准确率；
- 错误声称 accepted/完成的次数；
- 越权次数；
- 读取文件数、字节数、工具调用数和耗时；
- 过期证据误用次数；
- 需要你纠正 Agent 的次数。

不开发服务、数据库或遥测系统。

## M2：完成第二个真实项目试点

这是当前证据最大的缺口：

- 找一个真实项目以 local 模式接入；
- 不制造演示 TASK；
- 让真实工作自然产生状态转换、handoff 和 checker 结果；
- 使 K1-K4 至少覆盖两个项目、累计 10 次状态变化；
- 完成 TASK-0001 的五问复盘。

如果暂时没有第二个项目，就如实保持未满足，不伪造数据。

## M3：Context 功能的 Go/No-Go 决策

只有出现以下任一证据才进入实现：

1. 至少两次可复现的契约、Authority 或 evidence boundary 判断失败；
2. Agent 能判断正确，但每次需要打开大量文件，读取成本持续明显；
3. 手工制作的临时 manifest 能在不降低准确率的情况下，减少至少约 30% 的读取或操作成本。

No-Go 也是有效结论：如果当前必读路径已经准确、快速，就不开发 Context Compiler。

## M4：只有 Go 后才做最小 Context 命令

第一版收缩为：

```bash
python3 scripts/trellium.py context <target> \
  --task TASK-xxxx \
  --intent implement|review|handoff \
  --format json
```

只输出：

- 必读文件及原因；
- TASK 的结构化状态、lifecycle、Authority level 和 Gates；
- Allowed / Requires Approval / Forbidden 所在位置，不擅自总结或改写；
- 实时 Git/工作树事实；
- legacy、unresolved 和省略内容；
- 输入文件、字节数及可重放摘要。

严格边界：

- 只读、确定性、标准库；
- 不联网、不调用 LLM；
- 不生成持久 context pack；
- 不解析自然语言来猜授权；
- 不自动执行文档命令；
- 不自动批准或写 accepted；
- 暂不替代 AGENTS.md 必读流程。

## 本阶段明确不做

evidence freshness；owner inbox / review pack；runtime 自动生成；schema v2 / slice history；Release 自动化；RAG、知识图谱、数据库、daemon；自动审批与自动验收。

## 执行纪律

1. 每个 milestone 前后 `git status --short`，保留用户既有修改（本周期已实践一次：Codex 的 4 文件改动全部审阅后保留）。
2. 冷启动场景必须用无聊天历史的新会话跑；主会话 Agent 不得代答。
3. 不制造场景数据；M2 无第二个项目时如实记录未满足。
4. M3 结论必须引用 M1/M2 的具体记录行；M4 前必须另立 Level C 任务并获 owner 批准。

## 最终结论（owner 原文）

> 下一阶段主线应当是"证明 09.3 的实际价值并减少治理摩擦"，而不是立即扩大功能面。只有冷启动对照实验明确证明上下文读取是主要成本，才进入最小 Context Manifest。
