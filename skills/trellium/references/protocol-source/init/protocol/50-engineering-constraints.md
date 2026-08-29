# 50 - 通用工程约束

## 定位

本模块定义 Agent-Native 项目的语言无关工程约束。

项目类型相关细节放入 `init/protocol/profiles/*`。

## 通用约束

- 修改范围必须收敛到任务契约。
- 不做无关重构。
- 没有任务授权时，不引入框架、服务或依赖。
- 不在仓库中保存密钥。
- 不硬编码环境相关配置。
- 单元测试不真实调用外部服务。
- 外部 SDK 使用必须隔离在清晰模块边界内。
- 加入 Agent 功能时，Prompt 和 LLM 行为必须有清晰边界。
- 重要变更必须同步文档和 vault 记忆。

## 配置

配置必须集中管理。

包括：

- 端口；
- URL；
- 路径；
- 模型名称；
- 功能开关；
- 超时时间；
- API Key；
- Token；
- 密码。

敏感信息必须通过环境变量、密钥管理系统或部署平台注入。

## 测试

测试应确定、隔离、可重复。

- mock 或 fake 外部依赖。
- 不依赖开发者本机状态。
- 覆盖确定性的核心逻辑。
- 行为变化时添加或更新聚焦测试。

## 质量入口与提交规范

优先使用仓库已有的统一任务入口（Makefile、Taskfile 或 scripts），本地与 CI 走同一入口。

- 统一入口提供常见目标，如 `test`、`lint`、`format`、`check`；不绕过项目规定的验证脚本。
- 仓库没有统一入口时，按语言 profile 的默认命令执行质量检查。
- 提交前运行质量入口。

提交信息默认遵循 Conventional Commits 风格；仓库已有 gitlint、commitlint 或自有规范时沿用其约定。

- 类型前缀如 `feat`、`fix`、`refactor`、`docs`、`test`、`optimize` 等；仓库可自定义类型列表。
- 标题简明、可检索；不写无意义占位（如 `wip`、`update`）。
- 具体格式以仓库现有约定为准，本协议只提供默认。

## 文档同步

以下内容变化时更新 vault：

- 项目范围；
- 架构；
- API 契约；
- 数据模型；
- Prompt 或 Agent 行为；
- 测试策略；
- 部署方式；
- 依赖；
- 当前任务状态；
- 重要设计决策。

## 记忆目标

- 稳定项目方向：`vault/project.md`。
- 当前状态：`vault/runtime.md`。
- 任务契约和执行记录：`vault/tasks/*`。
- 长期决策：`vault/decisions.md`。
- 交接信息：`vault/handoff.md`。
- 挂起事项：`vault/parked.md`。
- 长上下文：`vault/details/*`。
- 可复用工作流：`skills/*/SKILL.md`。
