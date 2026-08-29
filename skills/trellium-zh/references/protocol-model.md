# Trellium 协议模型

## 目的

Trellium 为软件项目添加持久的协作层。它不是业务框架、角色层级、CI 系统或 LLM 运行时。

核心原则：

> Agent 不按身份获得信任，而是按任务契约获得授权，并且只有通过验收门才能关闭工作。

## 分层

- 入口层：`AGENTS.md`、`CLAUDE.md`、`CODEX.md`、`GEMINI.md` 或类似项目级 Agent 指令。
- 上下文层：`vault/index.md`、`vault/project.md`、`vault/runtime.md` 和可选 `vault/details/*`。
- 治理层：`vault/governance.md` 和 `vault/tasks/*`。
- 决策层：`vault/decisions.md`。
- 交接层：`vault/handoff.md`。
- 工作流层：`skills/*/SKILL.md`。
- Profile 层：只有项目类型明确时才加入语言或框架默认值。

## 必需 Vault 文件

除非目标项目已有等价文件并需要合并，否则创建：

```text
vault/
  index.md
  project.md
  runtime.md
  governance.md
  decisions.md
  handoff.md
  parked.md
  collaboration.md
  tasks/
    README.md
    .gitkeep
```

## 记忆分层与压缩

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；预算线内；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md`、`parked.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新 |
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增 |

预算线：runtime ≤ 120 行（Recent Changes ≤ 10 条）；handoff ≤ 3 条交接或 100 行；decisions ≤ 150 行或 8 条记录；parked ≤ 60 行或 20 条；tasks（不含 archive）≤ 40 个文件。

压缩五阶段：测量→分类→重组→校验→记录。非语义操作（搬运、索引、标注 Active、暂停任务降级为 parked 条目）Agent 自主执行；语义判定（Superseded by D-xxxx / Merged into D-xxxx / Expired、parked 清理）只提案，用户批量确认，未确认保持 Active。压缩是只含 `vault/` 变更的独立提交。

决策索引化：decisions.md 变纯索引，正文入 `vault/decisions/D-xxxx-slug.md`。索引原则：增长进目录，读取走索引。

读路径分级：默认读 `index.md`（含速查表）+ `runtime.md`；Level B/C、判定模糊或涉及治理规则时读完整 `governance.md`。

## 文件职责

- `vault/index.md`：上下文读取和记忆更新路由表。
- `vault/project.md`：稳定项目目标、范围、边界和当前阶段。
- `vault/runtime.md`：短当前状态、活跃任务指针表（Focus 行 + Active Tasks 每行一任务）、检查、风险和下一步。支持多任务并行，状态变化只改对应行。
- `vault/governance.md`：任务等级、授权等级、任务契约、验收门、升级规则和 handoff。
- `vault/decisions.md`：决策索引与生命周期记录（Active / Superseded / Merged / Expired）；正文拆分后在 `vault/decisions/*`。
- `vault/handoff.md`：中断或恢复工作时的近期交接上下文；每条交接以任务编号命名，最多 3 条。
- `vault/parked.md`：用户挂起事项冷索引；仅被提及时读取，不进默认读取路径；与 runtime 双向流动（挂起降级、提及升回）。
- `vault/collaboration.md`：不能覆盖硬治理的软协作偏好。
- `vault/tasks/*`：追踪或治理任务的契约、执行记录、验证和关闭说明。
- `skills/*`：可复用 Agent 工作流。

## 任务等级

- Level A，简单任务：低风险，通常一次会话完成，一到两个文件，不影响架构、API、依赖或数据模型。记录在 `vault/runtime.md`。
- Level B，追踪任务：多文件、需要审计、需要设计加文档/测试/验证，或可能需要交接。记录在 `vault/tasks/TASK-xxxx-short-title.md`。
- Level C，治理任务：改变架构、公开 API、数据模型、框架、外部服务、安全、隐私、成本、部署或 Agent 治理。记录在任务文件和 `vault/decisions.md`；通常需要用户确认。

## 授权等级

- Authority 0：只读分析。
- Authority 1：低风险局部修改。
- Authority 2：说明边界和检查后的限定范围修改。
- Authority 3：高影响工作需要批准。
- Authority 4：禁止事项，包括保存密钥、伪造验证、未授权破坏性命令和静默覆盖用户改动。

## 任务契约字段

追踪任务和治理任务应包含：

- Objective
- Scope and out of scope
- Context required
- Capability tags
- Authority level
- Allowed changes
- Requires approval
- Forbidden changes
- Acceptance criteria
- Required verification
- Required memory updates
- Handoff requirement

## 验收门

不要在满足以下条件前关闭工作：

1. 逐条检查验收标准。
2. 运行必要验证，并记录结果。
3. 适用时同步代码、测试、文档和 vault 记忆。
4. 更新 `vault/runtime.md`。
5. 在 `vault/decisions.md` 记录长期决策。
6. 在任务文件或 `vault/handoff.md` 记录未完成工作或风险。
7. 没有隐藏的高影响变更。

测试通过不等于完成。

## 执行模式

- Plan first：编辑前明确目标、边界、验收、验证、文件和不做范围。
- Context grounded：先读本地项目上下文，再应用通用建议。
- Checkpointable：通过任务文件、runtime 和 handoff 让长任务可恢复。
- Human signal：架构、成本、安全、隐私、部署和模糊产品取舍交还用户判断。
- Review ledger：多轮 review 用 `TASK-xxxx-review.md` 台账批量收敛，每轮一次写入替代消息往返；收敛后归档进任务文件。
- Workflow compounding：重复稳定工作流沉淀为聚焦 skill，而不是扩写入口文件。

## 既有项目接入边界

接入模式默认只新增或合并 Agent 协作文件。

默认允许：

- Agent 入口文件
- `vault/`
- `skills/`
- 极短 README 协作说明，但要先说明意图

没有用户明确授权时禁止：

- 业务源码
- 测试
- 依赖和锁文件
- 构建、部署或 CI 文件
- 数据库迁移
- 环境文件
- 大段既有文档重写
- 密钥或凭据

## 协作画像

`vault/collaboration.md` 记录稳定协作偏好和观察模式。它是软画像，不是硬规则。它不能覆盖用户当前指令、Agent 入口文件、治理、任务契约、决策、安全、权限、测试、成本或部署约束。
