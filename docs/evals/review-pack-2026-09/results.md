# Results — Review Pack R0/R1 消融（空模板，预注册）

- 本文件在 M1 预注册时创建，**除 M2 快照/Pack 验收记录外全部留空**；M3 会话、M4 评分与结论按协议回填。
- 预注册时序由 Git DAG 证明：本文件所在提交早于任何 `packs/`、`runs/` 内容。

## M2 快照与 Pack 验收（2026-09-11 回填，先于 M3 首个会话提交）

- 快照验收（协议 §3 五项）：三场景全部 PASS——dirty=0；`rev-list HEAD --count` s1=75 / s2=87 / s3=91 与真实仓库一致；tip 即 head；Head 后探针不可达（s1/s2：`5317784` 失败；s3：`ee4f223` 失败）；抽查文件与真实仓库 `git show <head>:` 逐字节一致。快照路径 `/tmp/rp-eval-20260911/{s1,s2,s3}`。
- 首次快照构建失败记录：第 1 次构建未删除 `refs/heads`/`refs/tags`，Head 后对象经 ref 可达（post-hole 探针 FAIL）；修正为删除全部 branch/tag ref 后 prune，复验全过。失败与修复均发生在任何会话之前。
- Pack 字段齐全性与泄漏独立检查：PASS——独立无历史只读会话按 10 项清单逐项核验 3 份 Pack（字段顺序、合同原文逐字节、diff fence 与快照 `git diff` 逐字节、changed names 一致、Verification Boundary 1/7/11 行逐字+后缀、Review State（s1 整份台账逐字节 / s2、s3 none 正确）、Decision Pointers 精确、无自然语言结论/提示、快照 clean、无可追溯性缺口）。宿主侧泄漏 grep（Head 后修复 commit 哈希与 golden 触发词）三份全净。
- Builder 成本日志指针：`packs/builder-log.md`（含 v1→v1.2 Review State 规则修订史，全部发生在任何会话与任何 Pack 提交之前）；生成器存档 `packs/build_packs.py`。

## M3 会话台账（运行时回填）

| 会话 | 场景 | 臂 | 状态(ok/contaminated) | 备注 |
| --- | --- | --- | --- | --- |
| （12+ 行，逐会话回填） | | | | |

## M4 评分（首答冻结后回填）

- 逐会话 golden 命中与安全硬指标：待回填。
- 正样本召回（场景 × 臂，原值 + 中位数）：待回填。
- 负对照 fabricated/unlisted_real 判定：待回填。
- 成本原值与 arm 中位数（bytes / 文件打开 / tool calls / 正确首答耗时 / pack_contract_fallback / builder 与端到端）：待回填。
- Tie-breaker 触发记录：待回填。

## 结论（M4 回填）

- R1 判定（严格三选一）：待回填。
- Gate 逐条推导（可重算）：待回填。
- R2 建议（仅当 Go）：待回填。

## 偏差与协议修订记录

- 无（v1 冻结于 2026-09-11，先于任何 Pack 与会话）。
