# Migrations 迁移手册

本文件是升级机制的数据保护手册：每次协议模板变更，逐条写清旧内容的去向，供执行升级的 Agent 读取。当前版本号见 `init/VERSION`；升级机制与保护边界见 `init/protocol/70-adoption-flow.md`。

条目格式：

- `Added` / `Removed` / `Breaking` / `Auto`：模板与文件层面的机械变化，由 `trellium.py diff` 报告、`upgrade --apply` 执行；
- `Agent migration`：需要 Agent 语义执行、用户确认的迁移动作。数据文件（runtime、handoff、decisions 等）的格式迁移一律属于此类：只做内容搬运，不丢事实，不做"判断不重要然后丢弃"。

## 2026.09.0 — 多任务运行态与挂起区

- Added: `vault/parked.md`（data 角色；`adopt` 与 `upgrade --apply` 会在文件缺失时自动创建，已存在则跳过）。
- Breaking: `vault/runtime.md` 模板 `Active Task` 小节改为 `Focus` 行 + `Active Tasks` 指针表（每行一个并行任务：任务编号、一句话目标、状态、下一步）。
- Breaking: `vault/handoff.md` 模板改为条目式，每条交接以任务编号命名（无任务编号时用 SESSION）。
- Agent migration: 已有定制的 `runtime.md` 是项目数据，永不模板替换——把现有 Active Task 内容改写为指针表一行，`Focus` 指向该任务；`Current Progress` 条目逐条保留或按压缩规则分流；不丢任何事实。向用户提案后执行。
- Agent migration: 已有定制的 `handoff.md` 同理——把现有快照内容改写为一条以任务编号命名的交接条目；无任务编号的用 SESSION。
- Added: review 台账——`vault/tasks/TASK-xxxx-review.md`（运行时创建，不由 adopt 下发）；80 号模块新增 Review Ledger 执行模式；`tasks/README.md` 模板含台账格式。
- Breaking: runtime 的 Recent Changes 上限 10 条，超出走压缩分流；热文件更新纪律成文（每条一行、单行替换、不重写整段）。
- Added: `trellium.py --fetch`——从 GitHub 拉取最新 tag release 并以该版本的脚本与模板执行；协议内容更新无需重装 Skill 包。各命令支持 `--templates <dir>` 覆盖模板目录。
- Auto: `vault/index.md`、`vault/tasks/README.md`（如未变）、`skills/agent-task/SKILL.md`（如未变）按升级分级格自动刷新；定制过的 `index.md` 走提案合并 parked 路由条目。

## 2026.08.0 — 初始版本化发布

- 确立热文件预算线与五阶段压缩（vault compaction）为基线能力。
- Added: 升级机制本身——`trellium.py baseline|diff|upgrade` 与 `vault/.agent-init.json` 版本戳；升级器对项目数据只读，协议文件本地修改永不静默丢弃。
- Agent migration: 本版本之前接入、尚无版本戳的项目，先运行 `python3 trellium.py baseline <target>` 补记版本戳（unversioned 信任级，首次升级全部走提案）。
- Auto: 此后每次模板变更由 `diff` 报告；`upgrade --apply` 只替换未被项目修改过的协议文件，冲突生成提案到 `vault/.upgrade/<version>/`。
