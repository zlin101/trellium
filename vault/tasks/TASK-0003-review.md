# TASK-0003 - Review Ledger

## Findings

- R1 · fixed · develop push 任务继承 job 级 `contents: write` / `pull-requests: write`，违反最小权限 · workflow 拆分为 `sync`（仅 PR，写权限仅此处）与 `gate`（仅 push，继承 workflow 级 `contents: read`）
- R2 · fixed · TASK-0003 active → ready_for_review 转换未补观测，transition/handoff 计数过期 · K1 表补记转换行；reconciliation 更新为 4 转换 / 3 个 handoff 条目；runtime 进度行同步
- R3 · fixed · "GitHub 端 CI 已实际执行"与"独立 review 无 finding"提前勾选 · 两项回退为未勾选；独立 review 首轮即本轮，结论 REQUEST_CHANGES
- R4 · fixed · runtime Known Risks 保留已解决的 K1-K4 标签漂移风险 · 移除并替换为当前风险（CI runner 首跑未验证；Release 阻塞持续）
- R5 · fixed · TASK_STORAGE_PENDING 被误定性为"已证明的缺陷修复" · K3 观测行更正为预期瞬态 finding（设计内未提交窗口），不作为 canonical K3 证据；任务记录中的相应推断同步作废
- R6 · fixed · decisions.md 残留模板示例索引，真实决策无编号 · 删除示例行；决策编号 D-0001/D-0002 并建立真实索引；D-0002 正文同步 least-privilege 结构

## Round 2026-09-08（owner review，REQUEST_CHANGES）

- 6 项 finding 全部接受并修复；无 wont-fix、无 needs-discussion。
- 验证：workflow YAML 解析确认 `gate`（push）无 job 级写权限、`sync`（PR）保留 self-heal 写权限；`trellium.py check . --format json` 0 error / 0 warning（提交后终验）；87/87 tests；snapshot in sync；`git diff --check` 通过。
- 待 round 2：owner 复核本台账与修复提交；GitHub 端 CI 首跑仍待 push 后观察。
