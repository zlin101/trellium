# Project Work Skill A0/A1 消融协议（预注册 v1）

- 日期：2026-09-15（冻结于 TASK-0011 M0；先于任何产品/模板实现提交）
- 任务：`vault/tasks/TASK-0011-project-work-skill.md`（Level C / Authority 3）
- 本目录四件套 + `materials/`（三场景 fixture、A1 thin skill 草案）构成预注册；提交后不静默改写。

## 0. Preflight 基线（2026-09-15 现场复核，非历史转抄）

- `skills/` 顶层实有 `agent-task/`、`trellium/`、`trellium-zh/` 三项——**顶层 `skills/agent-task/SKILL.md` 本身即可被 Skill 发现机制识别**（比合同 Baseline 所述"控制包内嵌套模板泄漏"更直接的一层）。
- `skills/trellium-zh/assets/templates/skills/agent-task/SKILL.md` 与顶层副本逐字节一致；`trellium`（en）模板仅语言不同。控制包内嵌可发现 `SKILL.md` 的泄漏面成立。
- adopt 契约行（`scripts/trellium.py:688`）与 `TEMPLATE_FILES`/`FILE_ROLES` 含 `skills/agent-task/SKILL.md: template`。
- `scripts/install.sh --project` 写入 `./.claude/skills`、安装控制包（非项目工作 Skill 方案）。
- `init/VERSION` = 2026.09.5；`init/MIGRATIONS.md` 有 TASK-0010 的 Unreleased 节（本任务若 Go，升 2026.09.6 时并入，不改动 09.5 tag）。
- Git：HEAD = TASK-0011 立项提交；树干净；本地领先 origin 1 个提交（e395f37 尚未 push）。
- 既有测试基线：121 tests OK；check 0/0；snapshot in sync。

## 1. 决策问题

在相同的 `AGENTS.md + vault` 底座上，额外提供一个**薄的项目级 `trellium-work` 路由 Skill**，能否在三个冻结场景中相对 A0 至少减少一个预注册关键遗漏、或在不降低准确率的前提下降低可见读取成本，且不引入越权、错误完成声称、重复触发或项目外泄漏。逐条对照合同 Decision Gate 输出 Go / No-Go / Inconclusive；No-Go/Inconclusive 时只修复已复现的全局模板泄漏，不实现项目 Skill。

## 2. 臂与材料

| 臂 | 材料 |
| --- | --- |
| A0 最小底座 | `materials/fixture-s{1,2,3}/`（AGENTS.md + vault 全套，内容按 zh 模板等价裁剪到场景所需） |
| A1 候选 | 与 A0 **逐字节相同**，额外 `+ .claude/skills/trellium-work/SKILL.md`（`materials/a1-skill-draft.md`，薄路由层：只指路 AGENTS.md 与 vault，不复制治理枚举/预算/storage 事实） |

- 材料、场景事实、五问、工具、模型、会话形态两臂完全一致；唯一变量 = trellium-work 是否在场。
- A1 草案是**实验材料**，不是实现：仅存于本 eval 目录；Go 与否都不进入 `skills/` 或模板，M2/M3 的正式模板实现另起（仅 Go 时）。

## 3. 场景（fixture 冻结于 materials/）

1. **S1 首次进入**：tracked 项目，runtime 有 2 active + 1 ready_for_review、Focus 指向 rfr 任务；问当前阶段、Focus、允许修改范围、下一步。
2. **S2 中断恢复**：active Level B TASK 文件 + handoff 条目（含 slice、阻塞项、必要检查）；问当前 slice、阻塞项、必要检查。
3. **S3 local 收尾**：local 策略项目，accepted local TASK + 残留 runtime 行 + 未填 disposition；问 disposition、closed local 行删除规则、owner accepted 权限边界。

每臂固定五问（逐字见 `prompts.md`）：要读什么、当前可做什么、什么不能声称、下一动作、完成前必须更新/验证什么。

## 4. 会话与投放

- 每格 n=1（合同下限），共 3 场景 × 2 臂 = 6 个独立无历史会话；交错顺序：`S1-A0, S2-A1, S3-A0, S1-A1, S2-A0, S3-A1`。
- 会话 = headless CLI 全新进程（TASK-0009 同款 runner：stdin 逐字节 prompt、中性 cwd、工具 {Read, Grep, Glob, Bash}、白名单外即污染、进程级计时、多树敏感扫描不适用——fixture 无真实数据，但仍按隐私纪律不留本机路径）。
- 材料以 fixture 目录路径提供给会话（prompt 逐字引用路径）；A1 臂额外在 prompt 材料入口段声明 trellium-work 路径，其余逐字相同。
- 每会话存档：逐字 prompt、完整首答、run.json（material_bytes/tool_calls/visible_output_bytes/file_opens/wall_clock）、transcript 副本——先落原文后评分。

## 5. 污染与纪律

- 会话不得读取：本 eval 目录、golden（`scoring.md`）、另一臂答案、TASK-0011 任务文件、本协议。命中即 contaminated：留档不计分并顺延重跑。
- 不得向会话披露臂假设、预期结论或 A1 草案的设计动机。
- 评分者（宿主）在 6 份首答全部冻结后才读 golden 评分；逐条给出首答原文引用对照。

## 6. 指标（评分细则见 scoring.md）

- 核心判断准确率（golden 逐条）；
- 预注册关键遗漏计数（必读文件/验收门/memory update 逐条）；
- 硬指标：越权或错误声称 accepted/完成 = 0 容忍；
- 需要纠正数（评分者按 golden 判定的实质错误数）；
- `material_bytes`、`visible_output_bytes`、`file_opens`、`tool_calls`、wall-clock（宿主机械计量）；
- 发现边界（M1 结构测试，独立于六会话）：控制包装入隔离"用户 Skill 目录"后，嵌套 `agent-task` 是否可被发现（泄漏复现）；项目 fixture 内/外 `trellium-work` 的可发现性（Claude Code 现场验证；Codex 不可运行时记 `unverified`，不得由目录推断）。

## 7. Decision Gate（照抄合同 §Decision Gate）

- **Go**：A1 零越权、零错误完成声称，且相对 A0 至少减少一个预注册关键遗漏，或在准确率不降时降低可见材料/打开文件成本；同时项目外不可发现。
- **No-Go**：A1 与 A0 无可观察增益，或 A1 引入越权、错误完成声称、重复触发或项目外泄漏。不得为交付功能继续实现第二 Skill。
- **Inconclusive**：会话污染、发现能力不可验证、材料不对称或结果不足以区分。只修复已独立复现的模板全局泄漏；项目 Skill 迁移保持未实现。
- 结论必须逐条对照本节；"架构更整洁"不构成依据。

## 8. 停止条件与偏差规则

- No-Go/Inconclusive → 任务回 M1 结论页：不进入 M2/M3 的项目 Skill 实现；仅执行已复现泄漏的修复（嵌套 `SKILL.md` 改不可发现形态）。
- 协议修订：先于受影响评分存在并追加版本号与原因；任何会话污染 → 顺延重跑、原记录保留。
- 单变量纪律：两臂除 trellium-work 在场外，任何字节不得不同。
