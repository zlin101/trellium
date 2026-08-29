---
name: agent-task
description: 用于执行需要上下文读取、限定范围修改、验证、任务记录或 vault 记忆更新的非琐碎项目任务。
---

# Agent Task Workflow

## Steps

1. 读取 `AGENTS.md`、`vault/index.md`（含速查表）和 `vault/runtime.md`；Level B/C、判定模糊或涉及治理规则时读取 `vault/governance.md`。
2. 按 `vault/index.md` 读取任务特定上下文。
3. 将任务归类为 Level A、Level B 或 Level C。
4. 判断授权等级和是否需要用户确认。
5. 明确目标、范围、不做范围、验收标准和检查。
6. Level B 或 Level C 创建或更新任务文件。
7. 做最小必要修改。
8. 行为变化时添加或更新聚焦测试。
9. 通过任务文件和 `vault/handoff.md` 让长任务可恢复。
10. 运行必要检查。
11. 检查验收门；测试通过不等于完成。
12. 多轮 review 使用 `vault/tasks/TASK-xxxx-review.md` 台账：findings 编号进入、批量处理、批量回写状态（open/fixed/wont-fix/needs-discussion）；收敛后归档进任务文件 Execution Record。
13. 更新 `vault/runtime.md`：只改 Active Tasks 表中对应任务行的状态与下一步，需要时调整 Focus 行；每条一行、单行替换，不重写整段。
14. 长期决策写入 `vault/decisions.md`。
15. 用户挂起任务或决定时，在 `vault/parked.md` 记条目（含重启触发器）；用户重新提起时升回任务文件（Draft）或 `runtime.md`。
16. 记忆更新时检查预算线（runtime ≤ 120 行、Recent Changes ≤ 10 条、handoff ≤ 3 条或 100 行、decisions ≤ 150 行或 8 条、parked ≤ 60 行或 20 条）；超出时把溢出内容迁到正确去向。
17. 任一热文件超出预算线时，执行压缩五阶段：测量→分类→重组→校验→记录。压缩规则：
    - decisions 索引化与任务归档是零信息损失的搬运，可自主执行。
    - 暂停任务降级为 `parked.md` 条目是搬运，可自主执行；parked 清理只出提案。
    - Superseded/Merged/Expired 判定只出提案清单，用户确认前一律保持 Active。
    - 压缩前 `vault/` 必须无未提交变更；压缩形成只含 `vault/` 变更的独立提交；校验失败即恢复。
18. 本次任务中出现用户协作偏好或纠正信号时，按观察记入 `vault/collaboration.md`；重复出现或用户确认后升为偏好。

## Constraints

- 不引入无关依赖或框架。
- 不保存密钥。
- 单元测试不依赖真实外部服务。
- 不静默覆盖用户改动。
- 涉及架构、公开 API、数据模型、安全、隐私、成本、部署、依赖或 Agent 治理时升级。

## Review Before Completion

- 逐条确认验收标准。
- 确认验证输出。
- 确认 vault 记忆已更新。
- 确认没有隐藏高影响变更。
