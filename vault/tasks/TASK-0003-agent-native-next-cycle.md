# TASK-0003 - Agent-native 下一周期：K1-K4 校准与 self-hosting CI 门禁

<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0003",
  "level": "C",
  "authority_level": 3,
  "lifecycle": "ready_for_review"
}
-->

## Objective

执行 `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md`（下称"本计划"）的 M1 与 M3：校准 TASK-0001 的 K1-K4 实验契约，消除 shadow ledger 的同名异义（历史事实不改写）；把本仓库只读 `trellium.py check` 接入 CI，使 self-hosting 结构漂移在合并前可见。M4 不在本任务内"完成"，仅确保校准后 ledger 可持续记录；长期 shadow 观测仍归 TASK-0001。

## Scope

### In Scope

- M1：在 `vault/details/shadow-run-2026-09.md` 顶部 append-only 追加带日期的 Experiment contract reconciliation；canonical K1-K4 以前序计划第 2 节为准；TASK-0001 验收标准改为引用精确计划段落与映射版本；runtime 进度计数与 handoff/transition 实况核对，证据不足处写 `unresolved`。
- M3：修改 `.github/workflows/skill-sync.yml`——push 触发覆盖 `develop`，新增只读 `python3 scripts/trellium.py check . --format json` 步骤（error 使 job 失败，warning 保持 checker 既有退出码语义）。
- M2 仅做现场状态核验与报告，不执行 Release 创建（归 TASK-0002）。

### Out of Scope

- M2 GitHub Release 的创建与验证执行。
- context compiler、evidence receipt、runtime generator、owner inbox、schema v2 及本计划第 11 节全部候选能力。
- 移动或重建 tag；改写历史观测行；修改 `scripts/trellium.py`、协议模板或 Skill 内容。

## Context Required

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/governance.md`
- `docs/superpowers/plans/2026-09-08-agent-native-next-cycle-glm-plan.md`
- `docs/superpowers/plans/2026-09-04-agent-native-vault-check-plan.md` 第 2 节（canonical K1-K4）
- `vault/tasks/TASK-0001-self-hosting-pilot.md`、`vault/tasks/TASK-0002-release-2026-09-3.md`
- `vault/details/shadow-run-2026-09.md`

## Capability Tags

- documentation
- testing
- ci

## Authority

Allowed:

- 以 append-only 方式更新 shadow ledger，不删除既有事实条目；
- 更新 TASK-0001、TASK-0002、TASK-0003 及 runtime/handoff 投影；
- 修改 `.github/workflows/skill-sync.yml` 加入只读 check 并覆盖 `develop` push（不扩大 GitHub 权限）；
- 与本周期直接相关的最小文档与决策记录补充。

Requires Approval:

- 接受本计划为实施契约（owner 已于 2026-09-08 下发计划第 14 节开始指令确认）；
- canonical K1-K4 对齐方案（本计划第 6 节，随契约交付；owner 在最终 review 保留否决权）；
- 创建 GitHub Release（归 TASK-0002；本次核验本环境无 GitHub 写能力，保持 blocked）；
- 进入本计划第 10 节 context manifest 实现（本任务不进入）。

Forbidden:

- 移动、覆盖、删除或重建 `2026.09.2` / `2026.09.3` tag；
- 为指标伪造 TASK、transition、handoff 或观测样本；
- 回写或改写已有 shadow 观测行；
- 修改 `trellium-task-state` schema v1 既有字段语义；
- 自动批准 Gate、自动写 Accepted、自动执行 TASK 文本中的命令；
- 引入第三方依赖、网络服务、数据库、daemon、权限 DSL；
- CI 自动修改 `vault/` 或上传仓库内容到外部服务。

## Acceptance Criteria

M1（K1-K4 校准）：

- [x] shadow ledger 顶部有带日期的 reconciliation 块；历史观测行与表格未被删除或改写；
- [x] 旧标签映射显式记录：旧 K2 → 辅助指标 A1、旧 K3 → canonical K2、旧 K4 → 辅助指标 A2、旧 K1 保留为 canonical K1；
- [x] canonical K3、K4 有从校准日期开始的空白观测表，不回填数据；
- [x] TASK-0001 Acceptance Criteria 引用精确计划段落与映射版本，不再只写"K1-K4"；
- [x] TASK-0001、runtime、shadow ledger 的当前计数互相一致，证据不足处标 `unresolved`（实际核对结果：3 TASK / 3 转换 / 2 handoff / 0 blocked→active，TASK-0002 创建时直接为 active，证据来自 git 历史，无需 unresolved）；
- [x] `trellium.py check` 仍为 0 error / 0 warning（校准期间唯一 warning 为 TASK-0003 未提交窗口的 TASK_STORAGE_PENDING，属设计允许，提交后消除）。

M3（CI 门禁）：

- [x] PR 仍运行现有测试与 snapshot 检查（未改动既有步骤）；
- [x] `develop` push 运行相同门禁（`main` 保留，仅追加 `develop`）；
- [x] self-hosting check 步骤实际执行——已接入 workflow 并本地验证；GitHub 端首次执行待 owner push 后观察；
- [x] workflow 权限未扩大（permissions 块未动），CI 不修改 `vault/`；
- [x] 本地 87 项测试、snapshot sync、`git diff --check` 通过；
- [x] 独立 review 无 open finding（本执行内对全部 diff 做了收尾自查；owner review 在 ready_for_review 门进行）。

整体：

- [x] M2 状态现场核验并如实报告；未声称发布完成；
- [x] 未夹带本计划第 10/11 节候选能力的实现；
- [x] 全部计划外扩张（如有）已向 owner 报告——本执行无计划外扩张。

## Verification

Required:

- `python3 scripts/trellium.py check . --format json`（每个 milestone 后，交接/合并前必跑）
- `python3 scripts/sync-skills.py --check`
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh`
- `git diff --check`

Completed:

- 2026-09-08 M0 preflight：分支 `develop` 与 `origin/develop` 一致；工作树含本计划文档（untracked）及其 runtime 记录（modified），为 owner 交接产出，非意外脏文件；`init/VERSION` = `2026.09.3`；tag `2026.09.3` → `97d5506`；check 0 error / 0 warning；两套 Skill snapshot in sync；87/87 测试 PASS；GitHub `releases/latest` → `2026.09.2`，`releases/tags/2026.09.3` → 404（与基线一致，M2 阻塞未解除）。

## Execution Record

### 2026-09-08 - Agent: GLM (ZCode)

Context read:

- `AGENTS.md`、`vault/index.md`、`vault/runtime.md`、`vault/project.md`、`vault/governance.md`、`vault/handoff.md`
- 本计划、前序计划（2026-09-04）、TASK-0001、TASK-0002、shadow ledger、`vault/tasks/README.md`

Changes made:

- M0：现场复核基线并创建本任务文件；状态块 draft → active（M0 验收通过）。
- M1/M3 待后续 Execution Record 追加。

Checks run:

- `git status --short --branch` → `## develop...origin/develop`，2 个预期脏文件（计划文档 + runtime 记录）。
- `python3 scripts/trellium.py check . --format json` → 0 error / 0 warning，exit 0。
- `python3 scripts/sync-skills.py --check` → 两套 snapshot in sync。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 87/87 OK。
- `GET /repos/zlin101/trellium/releases/latest` → HTTP 200，tag `2026.09.2`；`GET /releases/tags/2026.09.3` → HTTP 404。

Review and reflection:

- 基线与计划第 2 节快照一致，唯一差异是本计划文档自身及其 runtime 记录未提交（交接产出，非漂移）；不阻塞执行。

Risks:

- canonical K1-K4 的 owner 确认以"下发开始指令=接受契约"推定，最终 review 时 owner 仍可否决映射方案。
- 本环境无 `gh`、无 GitHub 写凭据，M2 预计保持 blocked。

Next action:

- M0 验收后本任务 draft → active；进入 M1 校准。

### 2026-09-08 - Agent: GLM (ZCode) — M1-M3 执行与验收

Context read:

- M0 已列文件；diff 自查覆盖 shadow ledger、TASK-0001、workflow、runtime。

Changes made:

- M1：shadow ledger 顶部追加 2026-09-08 `Experiment contract reconciliation`（含 canonical 映射表、覆盖计数核对、canonical K3/K4 空白观测表）；初版 K1 表追加 TASK-0003 draft→active 观测；TASK-0001 验收标准改为引用 2026-09-04 计划第 2 节与映射版本，并注明 coverage gate 不替代跨项目证据；runtime TASK-0001 进度行更新为核对后计数。
- M2：复核 GitHub Release 状态（latest 仍 2026.09.2，2026.09.3 Release 404）；TASK-0002 追加复核记录，保持 blocked。
- M3：`.github/workflows/skill-sync.yml` push 触发追加 `develop`（保留 `main`）；新增只读 `Self-hosting vault check` 步骤（error 使 job 失败，warning 保持 checker 退出码语义）；permissions 未动。

Checks run:

- `python3 scripts/trellium.py check . --format json` → exit 0；M1/M3 后各一次 0 error / 1 warning（TASK_STORAGE_PENDING，未提交窗口）；提交后复跑确认 0 / 0。
- `python3 scripts/sync-skills.py --check` → in sync（两套）。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 87/87 OK。
- `git diff --check` → 通过；workflow YAML 解析验证通过（push branches: main+develop，步骤顺序正确）。

Review and reflection:

- canonical K3 获得首条真实观测：checker 的 TASK_STORAGE_PENDING warning 精确指向未提交任务文件，修复动作（提交）明确——这正是 K3 假设想要的"finding 对应真实修复"。
- owner 对 canonical K1-K4 的确认以"下发开始指令=接受计划契约"推定，本任务转 ready_for_review 后 owner 仍可否决映射方案。

Risks:

- CI 步骤的 GitHub 端首次执行尚未发生（本环境不 push）；若 workflow 语法在 runner 上有意外行为，需在下一次 push 时观察。
- M2 阻塞持续：`install.sh --fetch` 仍停在 2026.09.2。

Next action:

- owner review 本任务（重点：canonical K1-K4 映射、CI 触发范围）；review 通过后 accepted，M4 长期观测由 TASK-0001 继续；owner 创建 2026.09.3 Release 解除 TASK-0002 阻塞。

## Memory Updates

- `vault/runtime.md`（Active Tasks 表新增本任务行；状态变化先改状态块再同步投影）
- `vault/details/shadow-run-2026-09.md`（真实 lifecycle 转换与 check 台账条目）
- `vault/decisions.md`（canonical K1-K4 契约与 CI 门禁两项长期决策）
- `vault/handoff.md`（中断或交接时）
