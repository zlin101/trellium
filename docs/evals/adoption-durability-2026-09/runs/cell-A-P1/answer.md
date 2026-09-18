以下回答仅依据本次接入的现场材料（adopt 输出、`git status --porcelain`、Skill 接入相关段落），未执行任何命令。

## 1. 当前能否声称"接入完成"？

**不能。** 材料中多处明确排除：

- adopt 输出明示 `not durable yet: none of the generated files is committed to Git ... generated does not mean adopted`。
- `git status --porcelain` 显示 `?? AGENTS.md`、`?? skills/`、`?? vault/` —— 全部为未跟踪（untracked），核心不在 Git HEAD 中。
- Skill 接入完成契约要求五项缺一不可：语义配置完成、核心已进 HEAD、提交后 `check` 0 error、（local/生产）fresh clone 复验通过、状态已记入 `vault/runtime.md`。当前一项都未验证成立。
- Skill 原文："文件已生成 ≠ 接入已完成。协作核心未提交前，不得向用户声称接入完成。"

当前状态只能表述为："`adopt` 机械安装已完成（11 个文件已生成），接入尚未完成"。

## 2. 哪些文件必须 durable（进入版本控制提交历史）？

按 adopt 输出第 2 步与 Skill 完成契约第 2 条，核心持久化集合为：

- `AGENTS.md`
- `vault/` 全部必需文件（本次生成的 `index.md`、`governance.md`、`decisions.md`、`handoff.md`、`parked.md`、`collaboration.md`、`project.md`、`runtime.md`、`tasks/README.md`）
- `skills/agent-task/SKILL.md`
- 版本戳 `vault/.agent-init.json`

注意一点：`vault/.agent-init.json` 不在终端打印的 `changed: 11` 清单中，但 adopt 第 2 步和 Skill 契约都把它列入必须提交的集合；由于 `git status` 显示整个 `vault/` 目录未跟踪，按目录提交会自然包含它，需确认它确实随 `vault/` 入库，不被遗漏。

## 4. 下一步最小动作（按顺序）

1. 与用户一起复查生成文件并完成语义配置：模式选择（新项目初始化 vs 既有项目接入）、TASK storage 决策、合并既有 Agent 入口（不覆盖用户内容）。
2. 将接入状态与风险记入 `vault/runtime.md`（完成契约第 5 条要求）。
3. 将核心（`AGENTS.md`、`vault/`、`skills/agent-task/SKILL.md`、`vault/.agent-init.json`）提交进 Git。
4. 提交后复跑 `python3 trellium.py check <target>`，以 0 error 为接入完成的判据（核心在 HEAD 且未被 ignore，否则报 `CORE_STORAGE_UNCOMMITTED` / `CORE_STORAGE_IGNORED`，均为 error）。
5. 若为 local/生产接入：对仓库 fresh clone 复跑 `check`，同样通过才算最终验收（一次性动作，不进入日常 check）。

后续升级检查用 `python3 trellium.py diff <target>`，不属于本次完成流程。

## 5. 是否需要自动执行 commit/push？

**不需要，且不允许自动执行。** 依据：

- adopt 输出："adopt never runs git add/commit/push - commits stay under the user's control"。
- Skill 契约："adopt 与 Agent 都不得自动 `git add`、commit、push——提交动作由用户执行或经用户明确授权。"

因此提交必须由用户本人执行，或经用户对该次提交的明确授权后进行；不能以"完成接入"为由代为 commit/push。
