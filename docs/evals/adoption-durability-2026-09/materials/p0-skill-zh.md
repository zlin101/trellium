## 模式选择

编辑前先选择一种模式：

- **新项目初始化**：目标项目为空、可丢弃，或用户明确要求创建新的 Agent-ready 脚手架。
- **既有项目接入**：目标项目已有源码、依赖、测试、构建文件、部署文件、CI 或项目文档。

不确定时，选择既有项目接入。它更安全，因为默认只新增或合并 Agent 协作层。

## 安装与升级（内置脚本优先）

本包自带确定性安装/升级脚本 `assets/trellium.py`，优先使用；Agent 语义迁移在脚本之上叠加。

- 新项目或既有项目接入：`python3 assets/trellium.py adopt <target>`。默认只补缺失文件；已有 `AGENTS.md` 时追加标记区块，不覆盖。语言已明确时重复传入 `--profile go-backend=<root>` / `--profile python-backend=<root>`；只生成一个项目工程规范并由 AGENTS 一跳路由，不自动猜测语言。
- 协议内容更新无需重装本 Skill：任何命令加 `--fetch` 即从 GitHub 拉取最新 tag release 并以该版本的脚本与模板执行（缓存于 `~/.cache/trellium/`，降级会被拒绝）。重装 Skill 仅在 SKILL 工作流或脚本自身变化时需要。
- 已接入项目的升级：
  1. `python3 assets/trellium.py diff <target>`——只读报告：会动什么、绝不动什么、待执行迁移手册。
  2. `python3 assets/trellium.py upgrade <target> --apply`——执行安全子集；冲突生成提案到目标项目 `vault/.upgrade/<version>/`。
  3. Agent 按提案做语义合并（逐条保留项目定制），用户逐条确认。
  4. `python3 assets/trellium.py upgrade <target> --complete`——收尾登记。
- 无版本戳的存量项目（`vault/.agent-init.json` 不存在）先运行 `python3 assets/trellium.py baseline <target>`。
- 校验项目状态：`python3 assets/trellium.py check <target>`（可加 `--format json`）完全只读、确定性，校验最小状态层——Level B/C 任务文件的 `trellium-task-state` 状态块、`vault/index.md` 的 `trellium-policy` 策略块、runtime 任务行与状态块的投影一致性、热文件预算测量、TASK storage 与 Git 实际状态。退出码：有 error 为 `2`；仅 warning 为 `0`（warning 必须显示，不存在无条件 PASS）；操作错误为 `1`。它不自动修复、不写任何文件；没有状态块的历史 TASK 按 unresolved 报告，不猜测状态。新建任务用带状态块的模板，重新激活旧任务时补状态块，不批量迁移历史。 在 `local` 项目中，runtime 行指向的任务文件不存在（fresh clone 或本地丢失）时报 clone-safe warning 且不授予授权；已关闭的 local 任务不得保留 runtime 行。
- 数据保护：runtime、handoff、decisions、tasks 等项目数据对脚本只读，永不被模板替换；数据文件的格式迁移按 `references/protocol-source/init/MIGRATIONS.md` 语义执行，只做内容搬运，不丢事实。
- 版本判断：目标项目 `vault/.agent-init.json` 的 `protocol_version` 低于 `references/protocol-source/init/VERSION` 时提议升级。
- 脚本无法运行时（缺少 python3 等），回退为本 SKILL 的 Agent 驱动流程：按 `references/protocol-source/` 的协议规则手工合并模板与执行迁移，遵守相同的数据保护边界。

## 任务契约

编辑前先说明：

- 目标
- 模式
- 范围和不做范围
- 预计修改的文件
- 授权等级和需要用户确认的事项
- 验收标准
- 验证命令

如果项目已有 `vault/tasks/`，创建或更新任务文件。否则先在工作说明中保留任务契约，等 vault 创建后再写入 `vault/tasks/`。

## 新项目初始化

创建最小可用项目：

1. 添加 Agent 入口文件，例如 `AGENTS.md`；只有有用时才添加工具专属入口文件。
2. 添加必需的 `vault/` 文件。
3. 添加 `skills/agent-task/SKILL.md`。
4. 只有当用户要求具体项目类型时，才添加源码、测试、依赖和 README。
5. 运行最小有意义检查。
6. 在 `vault/runtime.md` 记录当前状态，在 `vault/decisions.md` 记录长期选择。

项目真正需要前，不要添加框架、服务、数据库、CI、部署、LLM SDK 或凭据。

## 既有项目接入

保护既有项目：

1. 先只读扫描：根目录文件、Agent 入口、README/docs、源码结构、依赖文件、测试、构建/部署/CI 文件、既有记忆或决策记录、工作区未提交状态。
2. 先给出接入计划，只列 Agent 协作层修改。
3. 合并既有 Agent 入口规则，不直接覆盖。
4. 创建或合并 `vault/` 文件和 `skills/agent-task/SKILL.md`。
5. 在 `vault/project.md` 记录这是既有项目接入。
6. 在 `vault/runtime.md` 记录接入状态、风险和下一步。

没有用户明确授权时，不要修改业务源码、测试、依赖文件、锁文件、构建文件、部署文件、CI、数据库迁移、环境文件或大段既有文档。