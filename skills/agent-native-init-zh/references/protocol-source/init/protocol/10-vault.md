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
| 治理文件 | `governance.md`、`collaboration.md` | 事件驱动更新；压缩只出提案 |
| 结构文件 | `index.md`、`project.md`、`tasks/README.md` | 极少更新；压缩不可直接修改 |
| 归档区 | `tasks/*`、`decisions/`、`details/*` | 只增；压缩内容的去向 |

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
- 活跃任务或任务指针；
- 当前进展；
- 没有任务文件时的验收标准；
- 当前约束；
- 最近变化；
- 已知风险；
- 必须运行的检查；
- 下一步建议。

长内容迁移到 `tasks/*`、`decisions.md` 或 `details/*`。

### governance.md

任务授权、追踪、验收、升级和多 Agent 接力规则。

非琐碎任务前必须读取。

### decisions.md

长期有效决策。

当架构、技术栈、API 契约、数据模型、依赖、项目范围或 Agent 协作规则变化时更新。

每条决策标注生命周期状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。超过 150 行或 8 条完整记录时索引化：`decisions.md` 变纯索引，正文迁入 `vault/decisions/D-xxxx-slug.md`，默认只读索引。

### handoff.md

任务中断、模型切换、工具切换或多 Agent 接力时的最近交接上下文。

只保留最近 1-3 次关键交接。稳定结论迁移到 `decisions.md`；当前状态迁移到 `runtime.md`；执行历史迁移到任务文件。

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

## 更新规则

- 非琐碎任务完成后更新 `runtime.md`。
- 追踪任务或治理任务更新 `tasks/*`。
- 产生长期结论时更新 `decisions.md`。
- 任务中断或转交时更新 `handoff.md`。
- `runtime.md` 膨胀时，将细节迁移到对应目标文件。
- 更新热文件时检查预算线；超出时按 `15-vault-compaction.md` 执行压缩。
- 压缩语义判定只提案，由用户确认；未确认的决策保持 `Active`。
