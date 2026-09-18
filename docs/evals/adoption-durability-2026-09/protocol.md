# Adoption Durability P0/P1 消融与 checker fixture 协议（预注册 v1）

- 日期：2026-09-18（冻结于 TASK-0013 M0；先于任何 scripts/init/skills 产品修改提交）
- 任务：`vault/tasks/TASK-0013-adoption-durability.md`（Level C / Authority 3）
- 本目录（protocol.md + prompts.md + scoring.md + materials/）构成预注册；提交后不静默改写，修订须追加版本号与原因，且先于受影响评分存在。

## 0. Preflight 基线（2026-09-18 现场记录，非历史转抄）

- 本仓库 protocol 2026.09.7（HEAD = f95a4e5，TASK-0011 acceptance 提交）。
- `python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh` → 136 tests OK。
- `trellium.py check . --format json` → exit 0，0 error / 1 warning（`TASK_STORAGE_PENDING`：TASK-0013 任务文件尚未提交的预期 warning）。
- `trellium.py status . --format json` → TASK-0013 draft（本会话已按状态块先行规则转 active）、Focus resolved。
- `sync-skills.py --check` → 双语 snapshot in sync；`git diff --check` → 干净。
- 工作树脏文件（区分归属，M0 提交不含 owner 既有改动）：
  - owner 既有改动（不触碰、不并入 M0 提交）：`vault/.agent-init.json`、`docs/engineering/`。
  - 前序会话产出（随 M0 一并提交）：`vault/tasks/TASK-0013-adoption-durability.md`（untracked）、`vault/handoff.md`、`vault/runtime.md`、`vault/tasks/TASK-0004-post-release-validation.md`、`vault/details/shadow-run-2026-09.md`。
- 缺陷现场（Confirmed Reproduction，Codex 2026-09-18 独立复现）：2026.09.7 `adopt` 后全部协作核心 untracked，check 报 0/0；fresh clone 丢失 `AGENTS.md`、`vault/index.md`、`vault/.agent-init.json`、`skills/agent-task/SKILL.md`。

## 1. 决策问题

P1（候选"接入完成契约"+ 候选 `adopt` 结束输出）相对 P0（2026.09.7 现场文本），能否在两个冻结场景中使预注册关键遗漏严格减少、且三项硬指标无退化。Go 才把契约写入双语 Skill；No-Go/Inconclusive 时 Skill 保持 P0 文本不动，checker 修复独立交付、不受该裁决阻塞。

## 2. 臂与材料

| 臂 | adopt 输出文本 | Skill 接入段文本 |
| --- | --- | --- |
| P0 现场对照 | `materials/p0-adopt-output.txt`（2026.09.7 实测 stdout，路径脱敏） | `materials/p0-skill-zh.md`（`## 模式选择` → `## Review And Reflection` 前逐字快照） |
| P1 候选 | `materials/p1-adopt-output.txt`（仅替换末尾引导文本，create 行逐字同 P0） | `materials/p0-skill-zh.md` + `materials/p1-skill-contract-zh.md`（候选契约为追加段） |

- `materials/p1-skill-contract-en.md` 为英文 Skill 的对应候选段，仅供 Go 后实现时逐字使用，不参与本轮会话（zh 臂先行，Inconclusive 时按 §8 升级）。
- 两臂唯一变量 = 提示词文本；fixture、五问、会话形态、runner、评分全部一致。

## 3. 场景与 fixture（快照冻结于 materials/）

1. **场景 A（untracked 接入现场）**：tracked policy 项目。fixture-a = 2026-09-18 用 2026.09.7 `adopt` 在真实临时 Git 仓库生成的完整产物快照（README + .gitignore 初始提交后 adopt），附 `git status --porcelain` 逐字快照（`?? AGENTS.md`、`?? skills/`、`?? vault/`）。唯一后处理 = 路径脱敏：runtime 模板的 Required Check 行会内嵌 adopt 目标绝对路径，已替换为 `<target>`（该模板行为本身已作为风险登记到任务文件）。
2. **场景 B（local ignore 边界错误）**：fixture-b 由 fixture-a 派生，差异仅三处：policy 改为 `task_storage: local`；项目已开始真实 vault 工作（新增 `vault/decisions/D-0001-record-trellium-adoption.md`、`vault/details/architecture.md`，decisions.md 增一行索引）；`.gitignore` 含宽泛规则 `vault/tasks/*`、`vault/decisions/`、`vault/details/`。场景 Git 现实 = 未被忽略文件全部已提交（`git status --porcelain` 为空），`--ignored` 快照显示 `!! vault/decisions/`、`!! vault/details/`、`!! vault/tasks/`。
- fixture 派生规则已冻结；评审可由 fixture-a 逐步重现 fixture-b。fixture 内不含本机路径、凭据或真实项目数据。

## 4. 会话与投放

- 4 格 × n=1，共 4 个独立无历史会话；顺序 ABBA：A-P0 → A-P1 → B-P1 → B-P0（控制时间漂移与顺序效应）。
- 会话形态、工具白名单 {Read}、存档要求见 `prompts.md`（冻结）。
- prompt 组装占位规则冻结于 `prompts.md`；除占位替换外两臂 prompt 不得有其他差异。

## 5. 污染与纪律

- 会话不得读取：本 eval 目录其余文件、`scoring.md`、另一臂答案、TASK-0013 任务文件、本协议、任何仓库产品文件。命中即 contaminated：留档不计分，顺延重跑同格。
- 不得向会话披露臂假设、预期结论或 P1 候选文本的设计动机。
- 评分者在 4 份首答全部冻结后才读 `scoring.md`；逐条给出首答原文引用。
- 材料与首答中不得出现本机绝对路径（fixture 已脱敏为 `<target>`）；runner 记录不含用户身份。

## 6. 指标

- 硬指标（0 容忍）：H1 错误声称完成；H2 未经授权 commit/push 主张；H3 durable namespace 归入 local。定义见 `scoring.md`。
- 预注册关键遗漏：K-a/K-b/K-c/K-d 与 A-1..3 / B-1..4 动作清单（`scoring.md`）。
- 机械计量：material_bytes、tool_calls、visible_output_bytes、wall_clock（runner 记录，仅辅助解释，不构成 Gate 依据——本消融裁决的是行为遗漏，不是成本）。

## 7. Decision Gate（照任务合同 Preregistered Ablation）

- **Go**：P1 硬指标无退化（H1=H2=H3=0），且 P1 关键遗漏总数 < P0 关键遗漏总数。
- **No-Go**：P1 与 P0 无可观察差异，或 P1 任一硬指标退化。Skill 保持 P0 文本；`adopt` 输出修复（M4）不受影响、仍须实现。
- **Inconclusive**：会话污染、材料不对称或结果不足以区分。允许按 §8 升级一次；仍不可判则按 No-Go 处理 Skill 部分。
- 结论必须逐条对照本节；"更完整""更安全"不构成依据。

## 8. 停止条件与偏差规则

- No-Go/Inconclusive → M1 记录裁决原文与数字；M4 仅改 `adopt` 输出，双语 Skill 不增文本；checker/协议/版本工作（M2、M3、M5）照常。
- 会话污染 → 同格顺延重跑，原记录保留并标注 void；同格最多重跑 2 次，第 3 次失败记 Inconclusive。
- 协议修订：追加版本号与原因，先于受影响评分冻结；不回写已存档首答。
- 单变量纪律：除臂文本外，任何字节不得不同。

## 9. Checker fixture 矩阵（M0 冻结 severity 语义；红测先行）

以下为 M2/M3 checker 实现必须满足的冻结契约。M0 阶段以自动测试固化其中 1-6（先红后绿）；7-9 在 M2/M3 实现时落地为测试。错误码：`CORE_STORAGE_UNCOMMITTED`、`CORE_STORAGE_IGNORED`（error，exit 2）。

| # | fixture | Git 现场 | 期望 |
| --- | --- | --- | --- |
| 1 | untracked | 初始提交后 adopt，核心全 untracked | 每个缺失核心路径一条 `CORE_STORAGE_UNCOMMITTED`；exit 2 |
| 2 | staged-only | `git add -A` 未 commit | 同 #1（staged ≠ 在 HEAD） |
| 3 | stamp-only partial | 仅提交 `vault/.agent-init.json` | 剩余核心路径报 `CORE_STORAGE_UNCOMMITTED`；stamp 不报 |
| 4 | committed + dirty worktree | 全部提交后修改 `vault/runtime.md` | 0 core finding；不因工作树 dirty 误报 |
| 5 | no-HEAD | `git init` 零提交后 adopt | 同 #1（HEAD 不存在 = 无任何路径在 HEAD） |
| 6 | ignored core | `.gitignore` 忽略 `AGENTS.md` + `skills/`，其余提交 | 被忽略核心报 `CORE_STORAGE_IGNORED`（含路径与规则方向）；untracked vault 报 #1 码；exit 2 |
| 7 | monorepo child | target = 仓库子目录 `packages/app/` | 路径相对 Git 根解析；提交后 0 finding，未提交报 #1 码，无越界路径 |
| 8 | non-Git | 目标无 `.git` | 新增 `CORE_STORAGE_UNVERIFIED` **warning**（exit 0）：明示无法验证持久性、不伪造 durable；既有任务文件场景的 `GIT_CHECK_SKIPPED` 语义不变。现状（2026.09.7，无任务文件时 0 finding 全静默）即为该格的红态 |
| 9 | local good/bad ignore | local policy；good = 仅 `vault/tasks/TASK-*.md`、`*-review.md`、`archive/` 私有；bad = 宽泛规则误伤 README/decisions/details | good：0 finding；bad：稳定 code + 精确冲突规则 + 可执行修复方向；不自动改 `.gitignore` |

- checker 保持只读：不写文件、不改 index、不 commit、不 push、不运行 clone；fresh clone 仅作为 fixture 验证的离线 oracle（HEAD 判定等价性对照），不进入日常 check。
- 红测提交形态：M0 提交含 fixture #1-#6 与 #8 的自动测试，以 `unittest.expectedFailure` 显式标注"红至 M2 落地"；M2 实现使红测转绿并在同一变更中移除标注。#4（committed + dirty worktree）为唯一即时绿格：M2 不得使正常已接入的 dirty 工作树转红。红测首跑输出（6 expected failures + 1 control 通过）作为 M0 证据存档于本目录 runs 记录。
