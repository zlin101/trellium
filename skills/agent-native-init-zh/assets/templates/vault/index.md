# Vault Index

本文件负责将 Agent 路由到正确项目上下文。不要把它写成项目历史。

## 任务与授权速查表

- Level A 简单任务：低风险、一次会话、1-2 个文件；记 `runtime.md`。
- Level B 追踪任务：多文件、需审计、可能交接；记 `tasks/*`。
- Level C 治理任务：架构、公开 API、数据模型、框架、外部服务、安全、成本、部署或治理规则变化；记 `tasks/*` 和 `decisions.md`，需用户确认。
- 授权等级：0 只读 / 1 局部修改 / 2 限定范围 / 3 需确认 / 4 禁止。
- 判定模糊或涉及治理规则本身：读完整 `governance.md`。

## 默认读取

非琐碎任务读取：

1. `AGENTS.md`
2. `vault/index.md`（含速查表）
3. `vault/runtime.md`

任务为 Level B 或 Level C、判定模糊或涉及治理规则时，追加读取：

- `vault/governance.md`

第一次进入项目：

- `vault/project.md`

中断或恢复任务：

- `vault/handoff.md`

追踪或治理任务：

- `vault/tasks/` 下的活跃任务文件

## 文件职责

- `project.md`：稳定项目目标、范围、边界和阶段。
- `runtime.md`：当前状态、活跃任务、检查、风险和下一步。
- `governance.md`：任务等级、授权、任务契约、验收门、升级和交接。
- `decisions.md`：长期决策索引与（未拆分前的）决策记录；正文拆分后在 `vault/decisions/D-xxxx-*.md`。
- `handoff.md`：中断工作近期交接状态。
- `collaboration.md`：不能覆盖硬规则的软协作偏好。
- `tasks/README.md`：任务文件状态流转和模板。
- `details/*`：可选长上下文，只有重复读取需要时创建。

## 细节路由

- 架构：`vault/details/architecture.md` 和 `vault/decisions.md`。
- 开发工具、依赖、测试或环境：`vault/details/development.md`。
- API 契约：`vault/details/api.md` 和 `vault/decisions.md`。
- Agent、LLM、prompt 或工具行为：`vault/details/agent.md` 和 `vault/decisions.md`。
- 领域知识：`vault/details/domain.md`。
- 协作偏好：`vault/collaboration.md`。

## 更新规则

- 非琐碎任务后更新 `runtime.md`。
- Level B 或 Level C 更新 `tasks/*`。
- 长期决策更新 `decisions.md`。
- 中断或交接时更新 `handoff.md`。
- 将长细节移出 `runtime.md`。
- 更新热文件时检查预算线：runtime ≤ 120 行；handoff ≤ 3 条交接或 100 行；decisions ≤ 150 行或 8 条记录。
- 超出预算线时执行压缩：测量→分类→重组→校验→记录；语义判定（Superseded/Merged/Expired）只提案，用户确认前保持 Active。
