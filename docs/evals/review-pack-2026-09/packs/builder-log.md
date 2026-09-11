# R1 Pack Builder 成本日志（协议 §9.3）

- Builder：GLM（TASK-0009 实施 agent），2026-09-11。
- 角色：Wizard-of-Oz 手工构建的自动化代行者；构建过程全部命令留痕如下。builder 成本不计入 reviewer 判断成本主指标，只计入端到端成本。

## 输入读取（builder 会话内）

- 上位计划全文、TASK-0009 契约、AGENTS/vault index/runtime/governance、TASK-0007-review.md、TASK-0008-owner-status.md（当前工作树版本，仅用于定位 golden 来源，未进入 Pack 内容）。
- Head 锚点验证读取：5 个 commit 的目标文件片段（git show），用于 scoring.md 锚点核对。
- Pack 内容本身仅来自快照：`git -C <snapshot> show HEAD:<task>`、`git -C <snapshot> diff <base>..<head>` 等。

## 命令与操作计数

- 快照构建：4 次 clone 构建（第 1 次因未删除 refs/heads+tags 导致 Head 后对象可达，判 FAIL 后重建 3 份）+ 五点验收 ×2 轮 + 文件抽查 3 项。
- Pack 构建：3 次完整运行（v1 草稿、v1.1、v1.2 冻结版），每次 <0.06s compute。
- 结构抽查：pack-s1 头部字段、三份尾部字段、Review State 三轮检查。
- 泄漏比对：见下节。

## 输出 bytes

- pack-s1.md = 110041 B；pack-s2.md = 114167 B；pack-s3.md = 210284 B；合计 434,492 B。

## 人工判断次数（对 Pack 内容）

- 内容性判断：0（全部字段由冻结规则机械产出）。
- 规则性判断：3 次（v1→v1.1→v1.2 的 Review State 规则修订，均为通用降噪，修订时点先于任何会话与任何 Pack 提交；理由留痕于 README 修订史）。

## 泄漏检查（宿主侧）

- 方法：三份 Pack 的全部内容来源限定为 Head 快照内容（生成器输入仅快照）；另对每份 Pack grep 该场景 Head 之后的修复 commit 短哈希（S1/S2：`5a622b5 2acf0af fc0cf6d 5317784 ee4f223`；S3：`ee4f223` 及 M0/M1 提交 `b5c3f23 543d8f3`）与 golden 触发词（S2/S3：`STATUS_UNRESOLVED_CODES 删除`、`handoff 条目同步`、S1：`R1-R5`）。
- 结果：宿主 grep 三份全净（S3 pack 中出现的 `fc0cf6d` 属于 S3 diff 范围内部提交，非泄漏）；独立无历史只读检查会话 10 项全 PASS，未发现任何无法追溯到 Head 快照状态的内容。最终结论：无泄漏。

## 耗时

- 单次 Pack 构建 compute：0.057s / 0.05x s（三次运行同量级）。
- 会话级端到端 builder 时间（含快照构建失败重试、规则修订两轮）：从 M2 开始（快照首次构建）到本日志写毕，宿主墙钟约 25 分钟；其中两次规则修订与一次快照重建为返工项，如实计入端到端成本。
