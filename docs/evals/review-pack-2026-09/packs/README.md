# R1 Pack 生成规则（冻结 v1.2，M2）

- 依据：上位计划 §7 字段契约；字段顺序固定；缺失写 `none`/`unavailable`。
- 生成器：`build_packs.py`（本目录内存档副本），确定性脚本；同输入重跑逐字节一致。
- 输入仅限：对应冻结快照（`/tmp/rp-eval-20260911/{s1,s2,s3}`）中 Head 提交的内容与其 Git diff。生成器不读取当前工作树、Head 之后历史或任何评分材料。

## 冻结抽取规则（v1.2）

| 字段 | 规则 |
| --- | --- |
| Review Target | 场景常量 + `git status --porcelain` 为空 → clean |
| Canonical Contract | 任务文件 Head 版按标题前缀截取逐字原文：trellium-task-state 块、Objective、In Scope、Out of Scope、Authority、Acceptance Criteria |
| Live Snapshot | `git diff --name-only`、`--stat`、full patch（不截断）、`git ls-files --others` |
| Verification Boundary | 任务文件 `Verification -> Completed:` 逐行原文，每行追加 ` [historical/unverified]` 标记 |
| Review State | 被审任务自己的台账 `vault/tasks/<TASK-ID>-review.md` 在 Head 存在则整份逐字附上；不存在则 open/needs-discussion/wont-fix 三行均写 none |
| Decision Pointers | 任务文件中出现的 `D-[0-9]{4}` 去重，只给 id + `vault/decisions.md` 指针 |
| External Boundary | Out of Scope + Authority 节中匹配冻结关键词（网络 network 外部 external 远端 remote GitHub Release CI push tag 标签）的行去重逐字；无匹配写 unavailable |
| Omissions | 任一规则抽取失败时记录；本次三份均为 none |

## 规则修订史（全部发生在任何会话运行与任何 Pack 提交之前）

- v1（草稿）：Review State 扫描任务文件 + 快照内全部 `*review*.md` 台账的关键词行。缺陷：把决策表行（`| tracked | open，状态一致 |`）、`fail-open` 措辞、其他任务的台账行卷入，且把"无 wont-fix"否定句误归 wont-fix。
- v1.1：收窄为台账文件扫描（消除任务文件噪音，未消除跨台账与否定句问题）。
- v1.2（冻结版）：Review State 只整份逐字附上被审任务自己的台账；无台账写 none。整份拷贝是 open/needs-discussion/wont-fix 子字段的无歧义超集，消除关键词误分类。
- 其余字段规则 v1→v1.2 无变化。

## 构建命令

```bash
python3 packs/build_packs.py   # 输出 packs/pack-s{1,2,3}.md
```

## 验收

- 三份 Pack `Omissions` 均为 none；full patch 与快照内 `git diff <base>..<head>` 逐字节一致（独立检查复核）。
- 泄漏检查：任何 Pack 不得包含该场景 Head 之后的提交、finding 名称或修复描述（宿主比对 + 独立只读检查，结果记 `builder-log.md`）。
