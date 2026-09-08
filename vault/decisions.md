# Decisions

长期决策记录。当前任务进展放 `vault/runtime.md` 或 `vault/tasks/*`。

每条决策标注状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。默认 `Active`。

超过 150 行或 8 条完整记录时索引化：本文件变纯索引（每条 1-2 行），正文迁入 `vault/decisions/D-xxxx-slug.md`。ID 顺序分配。

## 决策索引（索引化后使用）

- D-0001 · 决策标题 · Active · 一句话实质 · 2026-01-01

## 2026-09-08 - Canonical K1-K4 实验契约

Status: Active

### Background

shadow ledger 初版使用的 K1-K4 标签与 2026-09-04 实施计划第 2 节预注册的假设存在同名异义（初版 K2/K3/K4 与 canonical K2/K3/K4 含义不同），继续混用会使试点结论不可比。

### Decision

以 2026-09-04 计划第 2 节为 canonical K1-K4 唯一定义；初版 K2（runtime 投影）与初版 K4（预算阈值）降为辅助指标 A1/A2，初版 K3（tracked/local）改称 canonical K2；历史观测行不删除、不改写。映射记录见 `vault/details/shadow-run-2026-09.md` 顶部 2026-09-08 reconciliation 块。

### Rationale

跨项目证据要求（两个真实项目、至少 10 次状态变化）挂在 canonical 假设上；不消除同名异义，K3/K4 的证据永远无法积累，kill criterion 无法评估。

### Alternatives

- 保留初版标签并改写计划定义：被否，预注册指标不容事后修改。
- 删除初版表格重建：被否，违反 append-only 与"不改写历史观测"。

### Impact

后续 Agent 记录 shadow 观测时必须按 canonical 定义选表；引用"K1-K4"时须落到具体计划段落，不得只写缩写。

## 2026-09-08 - Self-hosting vault check 进入 CI 门禁

Status: Active

### Decision

`.github/workflows/skill-sync.yml` 在 PR 与 push（`main`、`develop`）上运行只读 `python3 scripts/trellium.py check . --format json`；checker error（exit 2）使 job 失败，warning 保持既有 exit-0 语义；不扩大 GitHub 权限，CI 不修改 `vault/`。

### Rationale

本仓库以 tracked 模式自托管 Trellium，vault 结构漂移应在合并前机械可见，而不是等下一次人工交接才发现。

### Alternatives

- 独立新 workflow：被否，最小修改原则，避免第二套触发面。
- warning 也使 job 失败：被否，擅自加严会改变 checker 既有退出码语义。

### Impact

向 `develop` 或 `main` 推送前先在本地跑同一命令；CI 报 error 时修 vault 结构，而不是放松门禁。
