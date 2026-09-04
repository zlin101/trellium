# Migrations 迁移手册

本文件是升级机制的数据保护手册：每次协议模板变更，逐条写清旧内容的去向，供执行升级的 Agent 读取。当前版本号见 `init/VERSION`；升级机制与保护边界见 `init/protocol/70-adoption-flow.md`。

条目格式：

- `Added` / `Removed` / `Breaking` / `Auto`：模板与文件层面的机械变化，由 `trellium.py diff` 报告、`upgrade --apply` 执行；
- `Agent migration`：需要 Agent 语义执行、用户确认的迁移动作。数据文件（runtime、handoff、decisions 等）的格式迁移一律属于此类：只做内容搬运，不丢事实，不做"判断不重要然后丢弃"。

## 2026.09.3 — check 状态唯一性与必需文件修复

- Added: `trellium.py check` 新增三类 error 发现：跨任务文件重复 `task_id`（`TASK_ID_DUPLICATE`）、runtime Active Tasks 表重复行（`TASK_RUNTIME_DUPLICATE`）、未关闭任务（draft/active/blocked/ready_for_review）在 runtime 中没有任何 Active Tasks 投影行（`TASK_PROJECTION_MISSING`）。
- Added: 必需文件检查扩展到 `vault/project.md`、`vault/governance.md`、`vault/tasks/README.md`（缺失报 `REQUIRED_FILE_MISSING` warning），与 `10-vault.md` 必备文件清单一致。
- Removed: 计划文档中未实现的 `max_bytes` 未来配置承诺。check 行为不变：预算只有显式配置的阈值会被执行。
- Auto: 无模板变更；`upgrade --apply` 仅刷新版本指针。

## 2026.09.2 — 任务状态块、项目策略块与只读 check

- Added: Level B/C 任务文件标题之后新增 `trellium-task-state` 状态块（schema v1：`schema_version`、`task_id`、`level`、`authority_level`、`lifecycle` 必填；`current_slice`、`gates` 可选），是 lifecycle、authority_level、当前 slice 与 Gate 结果的唯一 owner。新建或重新激活任务时添加；历史 TASK 不批量迁移，`check` 对缺失块报 legacy warning、不推断状态。`TASK-*-review.md` 台账与 `tasks/archive/` 不需要状态块。
- Breaking: 任务 lifecycle 统一为 `draft | active | blocked | ready_for_review | accepted | superseded`。`runtime.md` TASK 行改用同一枚举并成为状态块的派生投影；`paused`、`waiting-review` 不再是 TASK 状态，暂停且暂不推进的工作降级为 `parked.md` 条目。
- Breaking: 任务模板删除独立可编辑的 `## Status` 段与 Authority `Level:` 副本；Authority 正文只保留 Allowed、Requires Approval、Forbidden。
- Added: `vault/index.md` 新增 `trellium-policy` 策略块（schema v1）：`task_storage`（`tracked | local`）与可选 `budgets`，是项目预算与 TASK storage 的唯一配置来源；本协议其他位置的预算数字降级为初始化默认值。策略块缺失时 `check` 报 `POLICY_MISSING` warning，不套用隐藏默认值。
- Breaking: `handoff.md` 不再把 Workspace State（分支、HEAD、脏文件）当权威记录；每条交接改为 Objective、Completed、In Progress、Failed Attempts、Blockers、Next Best Action、Files To Read First，实时 Git 事实恢复时现场读取，只可另存一条带观察时间、明确非权威的环境快照。
- Agent migration: `runtime.md`、`handoff.md` 是 protected data，升级不替换；由 Agent 按上述规则以小 diff 方式人工同步，不丢事实。既有项目的 `task_storage` 由 owner 决定（新接入项目默认 `tracked`），工具不自动选择、不修改 `.gitignore`、不自动 untrack。
- Added: `trellium.py check <target>`（`--format json` 可选）：只读确定性校验——状态块/策略块结构与枚举、task_id 与文件名一致、runtime 投影漂移、预算测量与显式阈值、TASK storage 与 Git 实际状态。发现 error 退出 `2`，warning 不改变退出码；全程不写文件、不自动修复。

## 2026.09.1 — 一行安装器与工具修订

- Added: `scripts/install.sh` 一行安装/升级 Skill 包——`curl -fsSL https://raw.githubusercontent.com/zlin101/trellium/develop/scripts/install.sh | sh`。支持 `--lang en|zh`（默认 en）、`--agent codex|claude|all`（默认自动探测 `$CODEX_HOME`/`~/.codex` → codex，`~/.claude` → claude）、`--version`、`--dir`、`--project`（装到当前项目 `.claude/skills`）、`--source`。经 `releases/latest` 重定向解析最新版本（无 API 速率限制）；原地替换，重复执行即升级。
- Auto: 工具变更，无模板变化。`upgrade --apply` 在无文件变更时会把版本戳的 `protocol_version` 刷新到当前版本，避免纯工具版本的版本指针滞后。

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
