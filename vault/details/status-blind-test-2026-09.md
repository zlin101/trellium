# Status Summary S0/S1 盲测 — 索引与评分

TASK-0008 R1/R4 消融的索引文档。原始材料与逐字记录在同级目录 `status-blind-test-2026-09/`：六份实际投放提示词（`prompt-*.md`）、六份未改写的完整首答（`answer-*.md`）、golden 原字节文件（`golden-scenario*.txt`）、S0 材料原字节（`s0-material-scenario1-runtime.md`、`blocks-scenario*.txt`）与会话运行台账（`run-log.md`，含 agentId/tool_uses/时长）。本文件只做真值、评分与结论；更早版本曾把摘要标注为逐字首答，owner review 指出后已更正并以目录原文为准。

预注册：`docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md` §5。评分由实施方（GLM）对照冻结真值做出；每格 n=1，不做统计声称；owner 可按 run-log 复跑。

## 实验控制

- 每个受测会话是全新子代理，无共享历史；提示词明令禁止读取文件与使用工具（run-log 中 `tool_uses: 0` 可复核）。
- S1 臂输入 = 一份手写预期 status 输出（golden）；S0 臂输入 = 现行流程的完整材料（runtime 全文 + 全部任务状态块），提示词声明"材料即全部输入"。
- 场景 1 的 S0 材料 pin 在审计基准 `55ae985`；场景 2/3 为 synthetic fixture，材料全文见 prompt 文件与 `blocks-scenario2.txt`。
- 时序：S1 三会话先于任何 status 实现；S0 三会话于 owner review 后补跑。

## 冻结真值

| 场景 | focus | 开放分类 | closed | unresolved | 可用 Next Action |
| --- | --- | --- | --- | --- | --- |
| 1 当前仓库（@55ae985） | TASK-0008 | active{0001,0008}、blocked{0004} | 5（0002/0003/0005/0006/0007） | 无 | 0001 / 0004 / 0008 |
| 2 混合 fixture | TASK-0013 | draft{0010}、active{0011}、blocked{0012}、ready_for_review{0013} | 2（0014 accepted、0015 superseded） | 无 | 0010–0013 各一条 |
| 3 冲突+缺失 fixture | TASK-0020（不可信） | 无（两个都不可解析） | 0 | 0020 drift、0021 本地缺失 | 无（S1 契约下 unresolved 不给投影） |

## 结果

| 会话 | 输入 | 首答 | 纠正数 | 备注 |
| --- | --- | --- | --- | --- |
| S1-A | golden A（1149 bytes；owner review 时同实现输出 1120 bytes，差异来自 runtime 投影随后续提交演变） | 5/5 正确 | 0 | (resolved) 标记语义未在文本内定义（仍答对） |
| S1-B | golden B（1066 bytes） | 5/5 正确 | 0 | gates/slice 按字面报告，无越权推断 |
| S1-C | golden C（954 bytes） | 5/5 正确 | 0 | "为何无 Next Action"需推断（外观观察，未改契约） |
| S0-A | runtime@55ae985（11039B）+ 8 状态块 | 5/5 正确 | 0 | closed 计数部分依赖本仓库 "Closed …" 书写习惯 |
| S0-B | fixture runtime（624B）+ 6 状态块 | 4 正确 + 1 问需材料外推断 | 0（1 项显式不确定声明） | closed=2 靠"不在 Active Tasks 表即关闭"的推断口径；状态层不携带 open/closed 分类学 |
| S0-C | fixture runtime（496B）+ 1 状态块 | 4 正确 + 1 问过度声称 | 1 | 把缺失文件任务的 Next Action 占位文本当作可用 |

结论（严格限定）：

- S1 臂 3/3 场景五问首答全对、0 纠正、零材料外推断；S0 臂在场景 2/3 出现需外部分类学知识的推断与一次过度声称——S1 的差异不只是 bytes：open/closed 分类学内建与 fail-closed 投影抑制产生了正确性差异。
- bytes guardrail：S1 输出 954–1149 bytes，均远小于 S0-A 材料（11039 bytes）与 S0 基线 `vault/runtime.md`；bytes 仅 guardrail，未做 owner 可用性复核，不声称时间节省。

局限：每格 n=1，中文单语会话，评分者为实现方（非独立第三方）；子代理模型标识未由运行时返回（见 run-log）；S0 材料刻意不含 governance/index 的生命周期语义，用于暴露"现行状态输入不携带 open/closed 分类学"，不代表熟练 owner 的真实表现。
