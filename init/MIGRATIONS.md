# Migrations 迁移手册

本文件是升级机制的数据保护手册：每次协议模板变更，逐条写清旧内容的去向，供执行升级的 Agent 读取。当前版本号见 `init/VERSION`；升级机制与保护边界见 `init/protocol/70-adoption-flow.md`。

条目格式：

- `Added` / `Removed` / `Breaking` / `Auto`：模板与文件层面的机械变化，由 `agent-init.py diff` 报告、`upgrade --apply` 执行；
- `Agent migration`：需要 Agent 语义执行、用户确认的迁移动作。数据文件（runtime、handoff、decisions 等）的格式迁移一律属于此类：只做内容搬运，不丢事实，不做"判断不重要然后丢弃"。

## 2026.08.0 — 初始版本化发布

- 确立热文件预算线与五阶段压缩（vault compaction）为基线能力。
- Added: 升级机制本身——`agent-init.py baseline|diff|upgrade` 与 `vault/.agent-init.json` 版本戳；升级器对项目数据只读，协议文件本地修改永不静默丢弃。
- Agent migration: 本版本之前接入、尚无版本戳的项目，先运行 `python3 scripts/agent-init.py baseline <target>` 补记版本戳（unversioned 信任级，首次升级全部走提案）。
- Auto: 此后每次模板变更由 `diff` 报告；`upgrade --apply` 只替换未被项目修改过的协议文件，冲突生成提案到 `vault/.upgrade/<version>/`。
