# TASK-0009 - Review Ledger

## Round 1（独立 Agent review，2026-09-12）

审查人：独立无历史 reviewer 会话（只读，可访问真实仓库与评分材料），按七个维度审计：预注册时序（Git DAG）、原始材料完整性、污染裁决、算术、结论-vs-冻结 Gate、范围合规、R2 越权。

### 结论（七维核查）

- 预注册 DAG "airtight"：M1 `543d8f3`（空 results 模板）→ M2 `6e1b1bf`（首个 Pack）→ 首个会话存档 `eb11c39`；scoring/prompts 自 M1 未动；全部协议修订先于唯一评分提交 M4 `493f8dc`；12 份初始 prompt 与归档逐字节一致，cell 内 md5 一致，Pack 与 prompt 内嵌逐字节一致。
- 原始材料可重算：20 个 run 目录 material_bytes == prompt.md 实际大小；19 个会话的 tool_calls / visible_output_bytes 从 transcript **精确**重算；answer.md == 末条 assistant 消息。
- 污染裁决均有据；三个作废会话未泄入任何评分表。
- No-Go "mechanically correct and over-determined"：reviewer 本人在 `5317784` 复现两处 unlisted_real（短行 unresolved 缺口、管道截断）；确认 fabricated-blocker 定性（P3-5 为 owner 已裁定的 discretion 项）；稳健性——剔除 S3 臂或作废全部 Skill 会话仍 No-Go。
- 范围合规：M1 之后 protected 路径（scripts/init/skills/README/VERSION/MIGRATIONS/AGENTS）零改动；无 R2 越权。

### Findings

- P1-1 · fixed · results.md material_bytes R1 中位数误发布为 114,158/+5,478%（实为两值均值）；正确值 116,217/+5,679% · 已更正
- P1-2 · fixed · s2-R0-c × G-S2-1 误计命中且脚注引证张冠李戴（"fix direction" 实出自 s2-R0-a；s2-R0-c 原文为 "investigated and rejected"）· 翻判为 miss，脚注重写，Gate 条件 3 更正为 S2 2 vs 1.5（仍 PASS）
- P1-3 · fixed · 四项非 golden blocker 主张未按 §9.3 分类；refused-vault `unresolved: 0`（reviewer 在 5317784 复现）构成**第二处** control_invalidated 但未登记 · 新增分类节（unlisted_real / false_positive=0），清单增补，control_invalidated 双登记
- P1-4 · fixed · 协议 v1.4 声称"全部裁决记录于 run.json"但 s2-R0-a 文件仍为 clean、s2-R1-a/s3-R1-a 无裁决块、s3-R1-b 裁决未覆盖其 Skill 使用、results.md 工具面描述不精确 · 七个 run.json 补全 host_adjudication，results.md 改写
- P2-1 · fixed · 三个 run.json 审计曾就地改写未留版本痕 · 补 reaudit_note（含历史出处）
- P2-2 · fixed · 成本恶化被表述为独立 No-Go 触发（冻结 §8 下只阻断 Go）· 措辞更正 + 稳健性注（S3 臂剔除后条件 2 单独成立）
- P2-3 · fixed · file_opens_task_vault 非纯机械量未声明 · 计量口径注（机械口径 −37.0%，两口径结论一致）+ 宿主工具存档 `tools/`
- P2-4 · fixed · s2-R1-c 未运行的 tie-breaker 偏差与 staged prompt 残留 · 已在偏差节记录
- P2-5 · partially fixed · protocol 标题升 v1.4、s2-R0-d 暴露范围补全、scratch_write 计数注记；model_id 注记与 reaudit_note 字符串修正在 round 2 后处理

### 结论（Round 1）

REQUEST_CHANGES（4×P1 + 5×P2；全部为记录准确性问题，数据与裁决本身被确认 robust）。

## Round 2（同一独立 reviewer 复核，2026-09-12）

复核对象：修复提交 `10647bd`。

- P1-1..P1-4 全部 RESOLVED 并逐项对照原始证据验证（含 reviewer 自行重算中位数、复核翻判引用、复现 refused-vault）。
- P2-1/2/3/5 处理到位；遗留三个非阻断字符串错误（reaudit_note 中 s1-R0-a 命中描述有误、b824b25/f71addf 引用差一个 `^`）与 model_id 注记缺失。
- 修复提交本身合规：仅触及 eval 目录；七个 run.json 无任何计量字段变化（仅审计字段）；无 transcript/answer/prompt 被改；vault 门禁 0/0。

### 结论（Round 2）

**APPROVE**——R1 **No-Go** 裁决 confirmed and over-determined；遗留三项字符串级修正并入 M5 finalize 提交（不阻断）。

## 收尾记录

- Round-2 遗留三项已在 finalize 提交修正：s1-R0-a reaudit_note 描述更正为"自身会话 tool-results 分页文件（v1.3 放行）"；两处历史引用去掉误加的 `^`；19 个 run.json 的 model_id 补齐 v1.1 规定的 `[1m] inherited + unrecognized_model warning` 注记；稳健性注措辞精确化（S3 剔除后由条件 2 单独支撑）。
- 任务按计划停在 `ready_for_review`，等 owner 验收；R2 未实现、未提案。
