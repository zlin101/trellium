# Decisions

长期决策记录。当前任务进展放 `vault/runtime.md` 或 `vault/tasks/*`。

每条决策标注状态：`Active`、`Superseded by D-xxxx`、`Merged into D-xxxx` 或 `Expired`。默认 `Active`。

超过 150 行或 8 条完整记录时索引化：本文件变纯索引（每条 1-2 行），正文迁入 `vault/decisions/D-xxxx-slug.md`。ID 顺序分配。

## 决策索引

- D-0001 · Canonical K1-K4 实验契约 · Active · shadow 观测以 2026-09-04 计划第 2 节为唯一定义，旧标签映射为 A1/A2/canonical K2，历史不改写 · 2026-09-08
- D-0002 · Self-hosting vault check 进入 CI 门禁 · Active · PR 与 main/develop push 运行只读 check；写权限仅限 PR self-heal job，push 任务严格只读 · 2026-09-08
- D-0003 · Release 元数据降为可选改进 · Active · Release 验收 Gate = 既有 tag 正确、非 draft/prerelease、`releases/latest` 解析正确；标题与 notes 不阻塞 · 2026-09-08
- D-0004 · Context 功能 No-Go · Active · M4/`trellium.py context` 未授权不实现；AGENTS.md→vault 必读路径为默认；重开仅限 D-0004 三条件 · 2026-09-08

## D-0001 - Canonical K1-K4 实验契约（2026-09-08）

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

## D-0002 - Self-hosting vault check 进入 CI 门禁（2026-09-08）

Status: Active

### Decision

`.github/workflows/skill-sync.yml` 在 PR 与 push（`main`、`develop`）上运行只读 `python3 scripts/trellium.py check . --format json`；checker error（exit 2）使 job 失败，warning 保持既有 exit-0 语义。权限按事件最小化：写权限（`contents: write`、`pull-requests: write`）仅存在于 PR 专用 `sync` job（self-heal 所需）；push 专用 `gate` job 无 job 级权限提升，只继承 workflow 级 `contents: read`。CI 不修改 `vault/`。

### Rationale

本仓库以 tracked 模式自托管 Trellium，vault 结构漂移应在合并前机械可见；同时分支 push 不需要任何写 token，单一 job 携带写权限属于不必要的暴露面。

### Alternatives

- 独立新 workflow：被否，最小修改原则，避免第二套触发面。
- 单一 job 承载 PR 与 push：被否（review round 1 R1），`permissions` 只能按 job 声明，单 job 无法让 push 事件摆脱写权限。
- warning 也使 job 失败：被否，擅自加严会改变 checker 既有退出码语义。

### Impact

向 `develop` 或 `main` 推送前先在本地跑同一命令；CI 报 error 时修 vault 结构，而不是放松门禁；后续改 workflow 时保持"push 路径零写权限"不变。

## D-0003 - GitHub Release 元数据降为可选改进（2026-09-08）

Status: Active

### Background

2026.09.3 Release 已发布且 `releases/latest` 解析正确，但 API 返回 `name=""`、`body=""`；TASK-0002 原契约把标题与 notes 列为验收 Gate，形成唯一残余缺口。

### Decision

Owner 于「09.3 Post-release Validation」方案 M0 决定：Release 验收 Gate 为——指向既有正确 tag、非 draft、非 prerelease、`releases/latest` 解析到该版本；标题与 notes 降为可选改进，不再阻塞任务关闭。

### Rationale

`install.sh --fetch` 等所有机器路径只依赖 tag 与 latest 解析；标题/notes 仅影响人类阅读体验。为可选的人类体验阻塞治理闭环，摩擦大于收益。

### Alternatives

- 阻塞等待 owner 在 UI 补齐元数据：被否，收益不抵摩擦；事实仍记录在 TASK-0002 的 Optional 条目中，随时可补。

### Impact

后续 Release 类任务的验收不再把元数据当 Gate；引用本决策时注意其适用边界——发布对象本身缺失或 tag 错误仍是不折不扣的失败。

## D-0004 - Context 功能 No-Go 与重开条件（2026-09-08）

Status: Active

### Background

「09.3 Post-release Validation」M1 冷启动基线（S1-S7，7 个独立新会话）结果：判断准确率 7/7、越权 0、错误声称 accepted 0、过期证据误用 0、owner 纠正 0，每场景读取 5-16 个文件。M3 三条件中条件 1（≥2 次可复现判断失败）不成立、条件 2（读取成本持续明显）未被证实、条件 3（手工 manifest A/B ≥30% 降本）未测试；M2 无第二项目。Agent 建议 No-Go。

### Decision

Owner 于 2026-09-08 采纳 No-Go：当前不进入 M4，不立项、不实现 `trellium.py context`；暂不补做手工 Manifest A/B；AGENTS.md → vault 必读路径继续作为默认方案。Context 评估重开仅限：

1. 真实工作累计出现至少两次可复现的契约、授权或证据边界误判；
2. 持续记录到明显的读取成本，并补齐 bytes/耗时数据；
3. Owner 明确批准手工 A/B，且结果证明成本降低至少约 30%，同时没有准确率、越权和验收判断退化。

### Rationale

开发新功能的举证责任未满足：M1 未显示任何判断失败；读取成本有界且在协议设计内工作。M1 的评分污染（3/7 场景读到评分 key）与 bytes/耗时数据缺失限制结论强度，但不构成 Go 证据。M2 第二项目试点继续用于验证 K1-K4，但不阻塞本决策。

### Alternatives

- 立即实现 context 命令：被否，无失败或成本证据支撑。
- 立即补做手工 A/B：被否，owner 判定暂无必要；条件 3 保留为重开路径之一。

### Impact

任何 Agent 不得在无新任务契约的情况下实现 context/evidence 类功能；以本决策为"不实现"依据时，须同时检查三条重开条件是否已被真实证据触发。重开证据（误判事件、成本记录）必须先登记在 vault 观测文件中，不得口头声称。
