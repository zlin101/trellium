# 非 Context 优化实验 — 评分规则（仅供 reviewer）

**被测 Agent 禁止读取本文件。** 读到即该 cell 标 `contaminated`，不计入普通准确率样本；如实申报不扣分。同仓库文件无真正保密边界， contamination 如实记录即可。

## M2 golden 答案（与 protocol.md 冻结的 E2 比较规则一致）

| 场景 | golden | 关键理由 |
| --- | --- | --- |
| A 快照未变 | fresh | tracked 树一致、level=PASS |
| B 相关代码变化 | historical | scope 内 scripts/trellium.py 内容已变 |
| C 仅无关文档变化 | **fresh**（scope-aware 正确答案）/ historical（保守全树比较器输出） | 本场景专测 R3：保守规则的假阳性是否误导；agent 若盲从比较器输出 historical 而不核对 scope，记"被误导"，是 E2 相对 E1 的负分项 |
| D 提交后内容等价 | fresh | 比较树内容而非 hash；记录 commit 已不在历史属预期（rebase），不得因此 unresolved |
| 未跟踪文件变化 | fresh | 冻结规则：untracked 不影响 tracked-tree 比较 |
| PARTIAL | historical | level≠PASS，证明力不足以覆盖"已通过"声明 |
| NOT_RUN | unresolved | 无执行结果可考 |
| head 不可解析且树不可比 | unresolved | 无法建立任何等价性 |
| scope 外部系统变化 | fresh（限声明 scope） | excluded 声明生效；freshness 仅覆盖 scope |

评分：与 golden 一致 = 对；不一致 = 错；回答含糊或超出三值 = 错。记录 bytes、工具调用数、耗时、是否读评分材料、owner 纠正次数。

## 判读要点（reviewer 用）

- E0 的预期弱点：自由文本没有 scope/树快照，agent 倾向凭"看起来很近的 commit 号"猜 fresh。
- E1 的预期收益：结构化 scope/level 使"无关文档变化"可被正确判 fresh（若 agent 核对了 scope）。
- E2 的风险面：比较器输出 historical（场景 C）是**设计内假阳性**；agent 盲从即失误——这正是 R3 的 kill criterion 证据。E2 只有在降低总判断成本且不增加误导时才优于 E1。

## 汇总规则

- 每场景每 cell：准确率 + 中位 bytes/耗时；
- Go 强信号：E1（或 E2）相对 E0 中位改善 ≥约 30% 且硬指标零退化（误标 fresh=0、无越权）；
- E1≈E0 → 删除 receipt 方案；E2 不优于 E1 或产生误导 → 保留 E1、E2 标实验性或删除；
- 重复 <3 次的所有结论标 `exploratory`。
