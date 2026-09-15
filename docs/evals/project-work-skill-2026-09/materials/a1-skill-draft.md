---
name: trellium-work
description: 本项目的工作入口：执行任何非琐碎任务前，先经此路由到 AGENTS.md 与 vault。
---

# Trellium Work

本项目的工作流入口。规则与事实不在此复制——此文件只负责路由：

1. 先读 `AGENTS.md`（最低安全入口与必读顺序）。
2. 按 `AGENTS.md` 指引读取 `vault/index.md` 与 `vault/runtime.md`；Level B/C 或判定模糊时加读 `vault/governance.md`。
3. 任务契约、状态块、handoff、decisions 一律以 `vault/` 内文件为准。
4. 机械操作（adopt/upgrade/check/status）用用户级 `trellium`/`trellium-zh` Skill，不在本 Skill 范围内。

离开本项目目录后，本 Skill 不应再被触发或发现。
