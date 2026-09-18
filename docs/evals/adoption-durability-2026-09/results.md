# M1 消融结果与 Gate 裁决（2026-09-18）

- 评分时机：四格首答全部冻结并存档后才评分（runs/cell-*/answer.md）；golden 未改动（预注册提交 c284557 之后零修改）。
- 污染筛查：四格 PASS。机械扫描命中两处均为答案自报 prompt 中本就给出的 fixture 目录名（A-P0、B-P0 首句"fixture-a/fixture-b 内"），无 scoring/golden/协议/臂假设内容；B-P0 答案末尾自报的本机路径前缀已按附录 v1.1 脱敏为 `<host>/`。无格需要 void 重跑。

## 逐格判定（引用见各 runs/cell-*/answer.md 原文）

| 格 | H1 | H2 | H3 | 关键遗漏 | 五问判定摘要 |
| --- | --- | --- | --- | --- | --- |
| A-P0 | 0 | 0 | n/a | **2**（A-2 提交后复跑 check、A-3 fresh clone 均未提及） | Q1 对（"不能无条件声称，提交前接入不成立"）；Q2 全（K-a/K-b 在）；Q5 对 |
| A-P1 | 0 | 0 | n/a | **0**（A-1..A-3 全部按序出现，A-3 以"若为 local/生产接入"条件形式出现，计达成） | 五问全对 |
| B-P1 | 0 | 0 | **1**（把 `vault/details/` 归入"可保持私有"） | **2**（K-d：Q2 未把 `vault/decisions/`、`vault/details/` 列为 durable；B-2：修复计划不含被误伤 durable 文件的重新提交） | Q1 对（理由含 ignore 吞命名空间 + 识破 porcelain 空与未提交的矛盾）；Q2 K-a/K-b/K-c 在；Q5 对 |
| B-P0 | 0 | 0 | **1**（把 `vault/decisions/`、`vault/details/` 归入"保持私有"） | **1**（B-4：Q4 无 fresh-clone 验收动作） | Q1 对；Q2 全（K-a/K-b/K-c/K-d 全在）；Q5 对；另指出 porcelain 矛盾与 local 模式证据缺失（材料限制下的诚实处理） |

## 臂级汇总

| 臂 | 关键遗漏总数 | H1 | H2 | H3（答案数 / 命名空间实例） |
| --- | --- | --- | --- | --- |
| P0（A-P0 + B-P0） | **3** | 0 | 0 | 1 / 2（decisions/、details/） |
| P1（A-P1 + B-P1） | **2** | 0 | 0 | 1 / 1（details/） |

## Gate 裁决

任务合同 Gate（"P1 只有在关键遗漏少于 P0 且硬指标无退化时才进入 Skill"）逐条对照：

1. 关键遗漏：P1 = 2 < P0 = 3 ✓（差值全部来自场景 A：2 → 0；场景 B 两臂同为 1，项不同）。
2. 硬指标无退化：H1 0→0 ✓；H2 0→0 ✓；H3 1→1（实例 2→1，未增加）✓。

**裁决：Go（按任务合同 Gate）。** 依据合同文本，两处条件均满足。

必须如实记录的两点保留：

- **§7 字面更严**：本协议 §7 把"无退化"括注为"P1 的 H1=H2=H3=0"，按该字面读法 P1 的 H3=1 不满足，应记 Inconclusive。任务合同文本（owner 批准版）只要求"无退化"，合同优先；本裁决按合同给出 Go，同时把两种读法并列存档，owner review 时可改判。
- **场景 B 的 H3 未被任何臂消掉**（n=1，两臂各 1）：P1 契约文本未枚举 decisions/details 的 durable 属性，提示词没有教会边界。**本次 Go 只覆盖"接入完成契约 + adopt 输出"在场景 A 上的行为收益，不声称修复场景 B 的边界误判**；后者由 M3 的机械检查（`LOCAL_BOUNDARY_OVERREACH` error）兜底——这正是"语义提示 + 机械 Gate"双层设计的预期分工。若将来要在提示词层修复边界认知，须另立冻结材料重新消融，不得在本次材料上追加文本。

## 对 M4 的约束（随裁决生效）

- 双语 Skill：逐字落入 `materials/p1-skill-contract-zh.md` / `p1-skill-contract-en.md` 的契约段（插入"既有项目接入/Existing Project Adoption"节之后），不做其他措辞改动。
- `adopt` 结束输出：逐字落入 `materials/p1-adopt-output.txt` 的引导文本（create 行与 changed 清单不动）。
- 消融会话载体偏差（附录 v1.1）随结果一并存档，owner review 时一并复核。
