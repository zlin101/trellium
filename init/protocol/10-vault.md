# 10 - Vault 项目记忆系统

## 定位

`vault/` 是项目记忆系统。它的目标不是保存所有文档，而是让 Agent 在正确时机读取正确上下文。

## 索引原则

增长进目录，读取走索引。任何会增长的内容（决策、任务、细节），正文进目录按需读取；索引层保证默认读取路径永远短。

`index.md` 是路由中枢，保持纯路由、不存状态；活跃任务指针唯一存在于 `runtime.md`。新增记忆类型一律按此模式扩展。

## 记忆分层

| 层 | 文件 | 生命周期 |
| --- | --- | --- |
| 热文件 | `runtime.md`、`handoff.md`、`decisions.md` | 高频更新；有预算线；压缩对象 |
| 治理文件 | `governance.md`、`collaboration.md`、`parked.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/<task-id>.md`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

预算线、压缩流程与安全边界见 `15-vault-compaction.md`。

## 必备结构

```text
vault/
├── index.md
├── project.md
├── runtime.md
├── governance.md
├── decisions.md
├── decisions/            # 首次压缩时创建：决策正文
├── handoff.md
├── parked.md
├── tasks/
│   ├── README.md
│   ├── .gitkeep
│   └── archive/          # 里程碑归档时创建
└── details/
    ├── architecture.md
    ├── development.md
    ├── api.md
    ├── agent.md
    └── domain.md
```

必备文件：

- `vault/index.md`
- `vault/project.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions.md`
- `vault/handoff.md`
- `vault/parked.md`
- `vault/tasks/README.md`

同一主题的长内容被重复读取或迁移 2 次以上时创建 `vault/details/<topic>.md`。

## 文件职责

### index.md

vault 上下文路由表。

它定义：

- 默认读取路径；
- 何时读取 project、runtime、governance、decisions、handoff、任务文件或 details；
- 各类记忆的更新规则。

### project.md

稳定项目方向。

读取场景：

- Agent 第一次进入项目；
- 项目方向或范围不清楚；
- 任务可能引入模块、框架、服务或新边界。

不要在这里记录当前任务进展或交接流水。

### runtime.md

当前项目运行态。

任何非琐碎任务前都要读取。保持短小，建议 50-120 行。超过 120 行即触发压缩（见 `15-vault-compaction.md`）。

它应包含：

- 当前阶段；
- 活跃任务指针表：`Focus` 行指向当前主线任务，`Active Tasks` 表每行一个并行任务（任务编号、一句话目标、状态、下一步），支持多任务并行；
- 当前进展（对应 Focus 任务）；
- 没有任务文件时的验收标准；
- 当前约束；
- 最近变化；
- 已知风险；
- 必须运行的检查；
- 下一步建议。

任务状态取值：`active`、`paused`、`waiting-review`。状态变化只改对应行，不重写全表。暂停且暂不推进的任务降级为 `parked.md` 条目。

长内容迁移到 `tasks/*`、`decisions.md`、`parked.md` 或 `details/*`。

### governance.md

任务授权、追踪、验收、升级和多 Agent 接力规则。

非琐碎任务前必须读取。

### decisions.md

长期有效决策。

当架构、技术栈、API 契约、数据模型、依赖、项目范围或 Agent 协作规则变化时更新。

每条决策标注生命周期状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。超过 150 行或 8 条完整记录时索引化：`decisions.md` 变纯索引，正文迁入 `vault/decisions/D-xxxx-slug.md`，默认只读索引。

### handoff.md

任务中断、模型切换、工具切换或多 Agent 接力时的最近交接上下文。

只保留最近 1-3 次关键交接，每条以任务编号命名（无任务编号时用 SESSION）。稳定结论迁移到 `decisions.md`；当前状态迁移到 `runtime.md`；执行历史按任务编号归并进对应任务文件。

### parked.md

用户挂起事项的冷索引：挂起不遗忘，提及才读取，不进入默认读取路径。

条目格式：`P-xxxx · 类型(task/decision/question) · 标题 · 一句话上下文 · 重启触发器 · 日期`。有任务文件的记 `TASK-xxxx` 指针，没有的记 2-4 行上下文。

生命周期与 `runtime.md` 双向流动：任务被用户挂起时记入；用户重新提起时升回任务文件（Draft）或 `runtime.md`。Agent 不得删除条目；压缩清理只出提案，由用户确认。

### tasks/

追踪任务和治理任务的任务契约与执行记录。

简单的一次性任务可以留在 `runtime.md`。

### details/

按路由读取的长上下文：

- `details/architecture.md`：架构、模块、数据流和边界。
- `details/development.md`：工具、命令、依赖、CI/CD 和环境。
- `details/api.md`：API 设计和契约。
- `details/agent.md`：Agent、LLM、Prompt 和工具行为。
- `details/domain.md`：领域术语和规则。

## 默认读取路径

非琐碎任务：

```text
AGENTS.md
vault/index.md    # 含任务等级与授权速查表
vault/runtime.md
```

满足任一条件时追加读取完整 `vault/governance.md`：

- 任务为 Level B 或 Level C；
- 任务等级或授权判定模糊；
- 任务涉及治理规则本身。

第一次进入项目追加读取：

```text
vault/project.md
```

接手交接任务追加读取：

```text
vault/handoff.md
```

追踪任务或治理任务追加读取：

```text
vault/tasks/<task-id>.md
```

用户提到挂起、搁置或暂停的事项时追加读取：

```text
vault/parked.md
```

## 更新规则

- 非琐碎任务完成后更新 `runtime.md`（Active Tasks 表中对应任务行）。
- 追踪任务或治理任务更新 `tasks/*`。
- 产生长期结论时更新 `decisions.md`。
- 任务中断或转交时更新 `handoff.md`。
- 用户挂起任务或决定时记入 `parked.md`；重新提起时升回。
- `runtime.md` 膨胀时，将细节迁移到对应目标文件。
- 更新热文件时检查预算线；超出时按 `15-vault-compaction.md` 执行压缩。
- 压缩语义判定只提案，由用户确认；未确认的决策保持 `Active`。
