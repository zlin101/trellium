# TASK-0015 - Claude Code 入口统一到 AGENTS.md

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0015",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

移除协议对项目级 `CLAUDE.md` 的现行要求，统一由 `AGENTS.md` 承载 Claude Code 与其他兼容 Agent 的项目指令。

## Scope

### In Scope

- 删除现行协议、流程与分发参考中对独立 `CLAUDE.md` 的生成、同步和接入描述。
- 明确 Claude Code 使用 `AGENTS.md`；保留 Claude Code Skill 安装支持。
- 同步双语协议快照、迁移说明和项目记忆。

### Out of Scope

- 改动历史评估 transcript 或其他逐字证据。
- 删除 Claude Code 的 Skill 安装支持。
- 修改 owner 排除文件、业务代码、依赖、CI、push、tag 或 release。

## Context Required

- `AGENTS.md`
- `vault/index.md`
- `vault/runtime.md`
- `vault/governance.md`
- `init/protocol/30-agent-entry.md`
- `init/protocol/60-initialization-flow.md`
- `init/protocol/70-adoption-flow.md`

## Capability Tags

- agent-governance
- documentation
- distribution-sync

## Authority

Allowed:

- Owner 明确授权删除 `CLAUDE.md` 约定并同步相关描述。

Requires Approval:

- commit、push、tag、release 或删除 Claude Code Skill 安装支持。

Forbidden:

- 改写历史证据或触碰 owner 排除文件。

## Acceptance Criteria

- [x] 现行协议不再要求生成或同步 `CLAUDE.md`。
- [x] 明确 Claude Code 读取 `AGENTS.md`，其他工具专属兼容入口仍按需保留。
- [x] Claude Code Skill 安装说明保持不变。
- [x] 双语 snapshots、whitespace 与相关测试通过。

## Verification

Required:

- `rg -n 'CLAUDE\.md'`（排除历史证据与 Vault 记录后，只允许迁移记录和“不再创建”的否定说明）
- `python3 scripts/sync-skills.py --check`
- `python3 -m unittest scripts.test_sync_skills scripts.test_install_sh`
- `git diff --check`

## Required Memory Updates

- `vault/runtime.md`
- `vault/decisions.md`
- Durable knowledge disposition: not_applicable（tracked task）

## Handoff Requirement

若中断，记录尚未同步的 canonical/derived 文件；不得以修改历史 transcript 消除搜索命中。

## Execution Record

### 2026-09-20 - Agent: Codex — 实施与验收

Changes made:

- 确认仓库根目录与 HEAD 均不存在 `CLAUDE.md`，因此无需删除实体文件；删除的是初始化、接入和协议模型中对独立入口的正向约定。
- `AGENTS.md` 成为 Claude Code 的共享项目入口；`CODEX.md`、`GEMINI.md` 等仅在目标工具仍明确需要时作为兼容入口。
- 保留 README 中 Claude Code 用户级 Skill 安装说明；历史 eval transcript 和 owner 排除文件未改。
- canonical protocol、双语 concise references、生成 snapshots、MIGRATIONS 与 D-0009 同步。

Checks run:

- 非历史范围搜索：`CLAUDE.md` 只剩“不得再创建”的兼容说明与迁移记录，无生成/同步清单命中。
- `python3 scripts/sync-skills.py --check` → in sync。
- `python3 -m unittest scripts.test_sync_skills scripts.test_install_sh` → 11/11 OK。
- `git diff --check` → clean。

Review and reflection:

- Round 1 coverage：新建、接入、入口协议、模块索引、双语分发参考全部改为 `AGENTS.md` 单入口。
- Round 2 minimality：未删除 Claude Code Skill 安装能力，未改脚本行为、业务代码、历史证据或 owner 文件。
- 无剩余阻断；任务进入 `ready_for_review`，未执行 commit/push/tag/release。
