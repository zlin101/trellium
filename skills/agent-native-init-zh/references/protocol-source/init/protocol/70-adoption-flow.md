# 70 - 既有项目接入流程

## 定位

接入流程用于已经存在的项目。

目标是在不改变既有工程代码、依赖、业务结构和运行逻辑的前提下，引入 Agent-Native 的记忆管理、任务治理和交接机制。

它不是新项目初始化，也不是工程迁移。

一句话定义：

> 接入模式只安装或更新 Agent 协作层，不改业务工程层。

## 适用场景

- 已有项目希望引入 `vault/` 项目记忆系统。
- 已有项目希望引入 `AGENTS.md`、`CLAUDE.md` 等 Agent 入口规则。
- 已有项目希望引入任务契约、授权等级、验收门和 handoff 机制。
- 已有项目希望规范多 Agent 接力，但不调整代码结构。

## 允许修改

默认只允许创建或更新 Agent 协作层文件：

- `AGENTS.md`
- `CLAUDE.md`、`CODEX.md`、`GEMINI.md` 等工具入口文件，按项目需要创建
- `vault/`
- `vault/index.md`
- `vault/project.md`
- `vault/runtime.md`
- `vault/governance.md`
- `vault/decisions.md`
- `vault/handoff.md`
- `vault/tasks/README.md`
- `vault/tasks/.gitkeep`
- `vault/details/*`，仅在已有项目确实需要时创建
- `skills/`
- `skills/agent-task/SKILL.md`

可选修改：

- `README.md` 中添加极短 Agent 协作说明，但必须先说明，并尽量避免打扰原 README 结构。

## 禁止修改

除非用户明确授权，接入模式禁止修改：

- 业务源码目录，例如 `app/`、`src/`、`lib/`、`packages/`
- 测试目录，例如 `tests/`、`spec/`、`__tests__/`
- 依赖文件，例如 `pyproject.toml`、`package.json`、`go.mod`、`Cargo.toml`
- 锁文件，例如 `uv.lock`、`package-lock.json`、`pnpm-lock.yaml`、`Cargo.lock`
- 构建、部署或 CI 配置，例如 `Dockerfile`、`.github/workflows/*`
- 数据库迁移、配置文件或环境文件
- 既有业务文档的大段内容
- 任何真实密钥、Token、密码或凭据

如果接入需要触碰上述文件，必须升级为用户确认事项。

## 接入前扫描

Agent 执行接入前，应只做只读扫描：

1. 查看根目录文件。
2. 查找既有 Agent 入口文件：`AGENTS.md`、`CLAUDE.md`、`CODEX.md`、`GEMINI.md`、`.cursor/rules`。
3. 查找既有项目文档：`README.md`、`docs/`、`CONTRIBUTING.md`。
4. 查找既有记忆或任务目录：`vault/`、`memory/`、`docs/adr/`、`decisions/`。
5. 识别项目类型和技术栈，但不改依赖或代码。
6. 检查工作区是否已有未说明的变更。

扫描后，Agent 应给出接入计划，列出将创建或修改的协作层文件。

## 冲突处理

### 已存在 AGENTS.md

不要直接覆盖。

处理方式：

1. 读取原文件。
2. 保留项目已有规则。
3. 在不削弱原规则的前提下，加入 vault 和 governance 读取规则。
4. 如规则冲突，先指出冲突并请求确认。

### 已存在 CLAUDE.md / CODEX.md / GEMINI.md

保持与 `AGENTS.md` 语义一致。

工具专属说明可以保留，但不得覆盖通用治理规则。

### 已存在 vault/

不要覆盖。

处理方式：

1. 读取现有结构。
2. 缺什么补什么。
3. 已有文件先合并，不直接替换。
4. 对语义冲突的内容请求确认。

### 已存在 docs/adr 或 decisions

不要迁移历史记录。

在 `vault/decisions.md` 中添加指针，说明长期决策还可能存在于原位置。

### 已存在 README.md

默认不修改。

如需要添加 Agent 协作说明，只添加短段落，并避免重写原 README。

## 接入步骤

1. 读取 `init/INIT.md`。
2. 读取 `init/protocol/README.md`。
3. 读取 `init/protocol/10-vault.md`。
4. 读取 `init/protocol/20-governance.md`。
5. 读取 `init/protocol/30-agent-entry.md`。
6. 读取 `init/protocol/40-skills.md`。
7. 执行接入前扫描。
8. 输出接入计划，说明将创建或修改哪些协作层文件。
9. 合并或创建 Agent 入口文件。
10. 合并或创建 `vault/`。
11. 合并或创建 `skills/`。
12. 在 `vault/project.md` 记录“这是既有项目接入，不是新项目初始化”。
13. 在 `vault/runtime.md` 记录接入状态、风险和下一步。
14. 在 `vault/decisions.md` 记录接入决策。
15. 如发生中断或存在未完成事项，更新 `vault/handoff.md`。
16. 运行只读或文档级检查；不要运行会改变工程状态的命令，除非用户授权。

## 接入验收

接入完成必须满足：

- 未修改业务源码。
- 未修改依赖和锁文件。
- 未修改测试、构建、部署或 CI 配置。
- Agent 入口文件会路由到 `vault/index.md` 和 `vault/runtime.md`，并在 Level B 或 Level C、判定模糊或涉及治理规则时路由到 `vault/governance.md`。
- `vault/` 必备文件存在。
- `vault/governance.md` 定义任务等级、授权等级、任务契约、验收门和接力规则。
- `skills/agent-task/SKILL.md` 存在。
- `vault/runtime.md` 明确记录接入完成状态。
- `vault/decisions.md` 记录接入模式决策。
- 所有冲突和未完成事项已记录或请求确认。

## 协作层升级

接入之后，协议源仍会演进。升级的目标是：协议文件跟进新版，项目数据零损失，项目发展路线不中断。

### 文件两分法

升级器把协作层文件分成两类，写入权限不同：

| 类 | 文件 | 升级权限 |
| --- | --- | --- |
| 项目数据 | `runtime.md`、`handoff.md`、`decisions.md`、`decisions/`、`tasks/*`、`project.md`、`collaboration.md`、`details/*` | 只读。写入范围是硬编码白名单，数据文件不在其中，不依赖 Agent 自觉 |
| 协议文件 | `governance.md`、`index.md`、`tasks/README.md`、`skills/agent-task/`、`AGENTS.md` | 可写。本地未改的跟进上游；本地改过且上游也改过的出冲突提案 |

`vault/.agent-init.json` 是升级器的版本戳：记录每个文件上次安装时的内容 hash，用于区分"项目自己改的"和"上游旧模板"。`AGENTS.md` 有两种形态：从模板整文件创建的按整文件对比；追加到用户已有文件的，只管理 marker 标记区域。

### 铁律

1. 数据文件永不被模板替换。数据文件需要换格式时，按 `init/MIGRATIONS.md` 的迁移手册做内容搬运：同一批事实、新排版，Agent 提案、用户确认，不允许"判断不重要然后丢弃"。
2. 协议文件的本地修改永不静默丢弃：本地未改 → 跟进上游；仅本地改 → 保留；双方都改 → 冲突提案，由 Agent 语义合并、用户确认。语义合并后的文件标记为 observed，此后上游再变也只出提案，不自动替换。
3. 先报告后执行：`diff` 只读；`upgrade` 默认 dry-run，`--apply` 只执行安全子集。
4. 升级逐文件可选：`--only` / `--skip` 允许部分采纳；跳过的文件下轮再补。
5. 目标为 git 仓库时，待触碰文件必须无未提交变更（`--allow-dirty` 显式覆盖）；非 git 目标先备份到 `.agent-init-backup/`。升级产出独立提交，可随时 `git revert`。

### 升级轮次

1. `python3 scripts/agent-init.py diff <target>`：只读报告（apply / conflict / add / keep / protected）与待执行迁移手册。
2. `python3 scripts/agent-init.py upgrade <target> --apply`：执行安全子集（pristine 替换、新增、删除）；冲突生成提案到 `vault/.upgrade/<version>/`，含上游新版本与 upstream→local 差异。
3. Agent 按提案合并 → 用户逐个确认。
4. `python3 scripts/agent-init.py upgrade <target> --complete`：登记合并结果，收尾版本。中断安全：pending 状态持久在版本戳中，重跑 `diff` 可见卡点。

### 存量项目接入

版本戳出现之前接入的项目，先运行 `python3 scripts/agent-init.py baseline <target>` 补记版本戳（unversioned 信任级）：以当前本地内容为基线，此后上游变更一律出提案、不自动替换；首轮升级完成后恢复完整分级。

### 发布侧约束

每次修改协议模板：若新增或删除下发的模板文件，同步更新 `scripts/agent-init.py` 的 `FILE_ROLES`；在 `init/MIGRATIONS.md` 追加条目并按需更新 `init/VERSION`。

## 接入模式的授权

接入模式默认属于 Authority 2。

如果需要修改 README 的短说明，仍可视为 Authority 2，但必须提前说明。

如果需要修改源码、依赖、测试、构建、部署或 CI，必须升级为 Authority 3，并取得用户确认。

## 接入输出建议

Agent 完成接入后，应向用户报告：

- 创建或修改了哪些协作层文件；
- 明确没有触碰哪些工程代码或配置；
- 发现了哪些既有规则或冲突；
- 后续 Agent 应从哪些文件开始读取；
- 是否存在需要用户确认的剩余事项。
