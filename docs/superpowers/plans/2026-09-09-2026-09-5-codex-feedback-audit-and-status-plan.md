# 2026.09.5 Codex 反馈剩余功能审计与 Status 开发计划

- 日期：2026-09-09
- 需求源：`Vault-Agent-Native-使用评估与优化建议-2026-09-03.md`
- 目标版本：`2026.09.5`
- 状态：审计与文档 review 完成；唯一开发候选已选定，实验契约冻结；实现待 GLM

## 1. 目标与边界

本轮不再以“继续完善 Vault 治理”为交付目标，而是将 Codex 长期深度使用反馈重新映射到 2026.09.4 现状，得到一份剩余产品机会清单，然后只选一个已有真实痛点、不需要新架构的能力进入开发。

证据分层：

- A：Codex 深度使用现场（63 TASK、43–52 KB 默认读取、50–80 KB 长 TASK）。
- B：Trellium 本仓库或 owner 真实使用事件。
- C：受控消融实验。
- D：推测或长期设想，不足以直接生产化。

不做：同时启动多个功能；为了版本号扩张 schema/CLI；用 synthetic 样本替代真实痛点；重开 D-0004 Context No-Go；自动授权、自动 accepted 或修改 Vault。

## 2. 2026.09.4 已有能力（从剩余清单删除）

| Codex 反馈 | 当前实现 | 结论 |
| --- | --- | --- |
| TASK 小型机器状态块 | `trellium-task-state` schema v1 | 已解决 |
| 项目 policy 单一 owner | `trellium-policy` | 已解决 |
| 只读确定性 checker | `trellium.py check` + CI | 已解决 |
| runtime 状态漂移 | TASK 状态块为 owner，checker 校验投影 | 已解决核心问题 |
| handoff 复制实时 Git 事实 | 现场读 Git，handoff 只存历史快照 | 已解决 |
| UTF-8 bytes/line/entry 测量 | check 始终报告 measurements | 已解决测量层 |
| tracked/local 归属 | 全局 `task_storage` + Git 实际状态校验 | 已解决 |
| local fresh-clone 误报 | 09.4 clone-safe warning / closed-local error | 已解决 |
| local TASK 发布边界 | Accepted 前 Durable Knowledge Disposition | 已解决最小人工 Gate |

## 3. 剩余功能清单

| 排名 | 机会/问题 | 证据 | 影响 | 工作量/风险 | 本轮处置 |
| --- | --- | --- | --- | --- | --- |
| 1 | **Deterministic status summary**：owner 要从 runtime/TASK 中手工汇总“现在到哪、哪些待 review、哪些 blocked” | A：反馈 §12.5/§14.5；B：owner 在 09.3–09.4 期间反复询问当前进度/status | 高；直接减少人和 Agent 重复汇总 | 低；复用现有 schema，只读 | **Go with experiments：2026.09.5 唯一开发候选** |
| 2 | Current Contract / historical journal 热冷分离 | A：50–80 KB TASK；当前契约与历史混存 | 高 | 中；涉及迁移与历史完整性 | 延后；先用可获得的真实长 TASK 重放 H0/H1/H2 |
| 3 | 确定性 review pack | A：reviewer 需要契约、diff、finding、evidence 边界 | 中高 | 中；容易演化为 Context 子集 | 延后；status 证明派生视图价值后再评估 |
| 4 | Slice-native TASK state | A：多 amendment 复合状态歧义；当前只有 `current_slice` | 高（复杂任务） | 高；schema 变更、迁移风险 | Blocked；等 ≥2 个真实复合任务 |
| 5 | Byte budget 可配置执行 | A：line-only 在 119 行/35 KB 失真；当前仅测量 bytes | 中 | 低中；错误阈值会制造噪声 | 延后；先有真实阅读障碍与分布再冻结阈值 |
| 6 | Evidence Receipt / freshness | A：旧 PASS 时效问题；C：E2 准确率退化，E1 成本未测 | 高 | 高；假失效会误导 Agent | E2 No-Go；E1 Inconclusive；本轮不实现 |
| 7 | Fact type（normative/proposal/observation/derived/journal） | A：proposal 与当前真相可被混用 | 中 | 中高；可能增加写入税和伪权威 | 延后；需要真实误用事件 |
| 8 | runtime 自动生成 | A：能降低写放大 | 中高 | 高；隐私泄漏/生成 diff/第二 owner | 延后；先保持 checker 对照 |
| 9 | Decision edges / `reconsider_when` 结构化 | B：D-0004 自然语言条件已被正确使用 | 低中 | 中；会复制现有正文 | 当前 No-Go（D0 sufficient） |
| 10 | Context compiler | 冷启动 7/7 正确，无可复现判断失败 | 潜在高 | 高 | **D-0004 No-Go，不重开** |
| 11 | worktree metadata / write-set / explain / RAG / daemon / Web UI | D 或 trigger-only | 不确定 | 高 | 不进路线图；只按真实事件触发 |

## 4. 唯一选择：确定性 Status Summary

选择的是问题，不是预设的大方案：

> 当状态块已经存在时，owner 仍需反复让 Agent 手工重读 runtime/TASK，才能知道当前焦点、进行中、待 review、blocked 和 unresolved 项。

最小解法是在现有单文件标准库 CLI 中增加一个只读命令：

```bash
python3 scripts/trellium.py status .
python3 scripts/trellium.py status . --format json
```

它只编译现有真相，不新增事实源。它是 status summary，**不是完整 owner approval inbox**；现有 schema 不能可靠推断“谁必须批准什么”，本轮不为此扩 schema。

来源边界：

- TASK 状态块持有 lifecycle/authority/current_slice/gates。
- runtime 只提供 Focus、一句 objective 和 Next Action 投影。
- `ready_for_review`、`blocked`、`active`、`draft` 分类显示；`accepted/superseded` 只进计数，不进默认行动清单。
- 开放 Gate 只显示原值，不推断“需 owner 批准”。
- missing/legacy/invalid/local-only 指针显式 `unresolved`，不推断 Authority，不 fail-open。
- 输出带源路径；不写 Vault，不运行 TASK 内命令，不访问网络。

实现应先运行并复用现有 check 解析结果，不复制一套宽松 parser。有 error 时仍可输出可确定的部分，但必须把相关任务放入 `unresolved`、保留 finding，并以 `2` 退出；仅 warning 时退出 `0`；目标/参数操作错误退出 `1`。这只是 `status` 自身契约，不改 `check` 的既有输出和退出码。

JSON v1 的最小形状冻结为（字段可为空数组，不可省略后让调用方猜）：

```json
{
  "schema_version": 1,
  "target": "/absolute/target",
  "focus": [{"task_id": "TASK-0008", "resolved": true}],
  "summary": {"draft": 0, "active": 2, "blocked": 1, "ready_for_review": 0, "closed": 5, "unresolved": 0},
  "tasks": {
    "ready_for_review": [],
    "blocked": [],
    "active": [],
    "draft": [],
    "unresolved": []
  },
  "findings": []
}
```

每个 resolved task 项只允许：`task_id`、`lifecycle`、`authority_level`、可选 `current_slice`、`gates`、`task_path`，以及明确命名的 `runtime_projection`（`objective`/`next_action`）。`runtime_projection` 不存在时不从 TASK 自然语言猜。unresolved 项的 `lifecycle`/`authority_level` 必须为 `null` 或不出现，不得从 runtime 行填充。

## 5. 消融预注册（实现前冻结）

### 5.1 对照组

- S0（现行）：读 `vault/runtime.md` + 打开任务文件，人工编译 owner 状态。
- S1（候选）：只读 `trellium.py status` 输出。
- 只实现 S1；不同时做 inbox 文件、context pack 或 runtime generator。

### 5.2 冻结场景

1. 当前自托管仓库：Focus=TASK-0008；TASK-0001/TASK-0008 active；TASK-0004 blocked；其余 closed 不进行动列表。
2. synthetic 混合 fixture：draft / active / blocked / ready_for_review / accepted / superseded 各一个，带 current_slice 与 Gate。
3. runtime lifecycle 与 TASK 块冲突：报 unresolved/error，不按 runtime 授权。
4. local fresh clone missing open TASK：保留 clone-safe warning，不创造 lifecycle/authority。
5. malformed/duplicate/symlink 输入：复用 `check` 的 fail-closed 结果。
6. 只读性：命令前后目标文件快照完全一致。

### 5.3 指标

硬指标：

- 行动分类准确率 100%。
- accepted/superseded 误进行动清单 = 0。
- unresolved 误声称 lifecycle/authority = 0。
- 命令写入文件 = 0。
- 现有 `check` finding/severity/exit 不变。
- 对每个冻结场景，只看 S1 能 100% 回答 Focus、开放 TASK 分类、closed 计数、unresolved 边界和可得 Next Action 五个问题。

效率 guardrail：

- 在当前仓库，S1 文本输出 bytes 必须严格小于 `vault/runtime.md` bytes；不为此牺牲任一硬指标。
- JSON 输出为稳定 schema v1，内容与文本输出同源。
- bytes 只是 guardrail，不单独证明人类成本降低；未有 owner 可用性复核前，不声称“减少了多少时间”。

### 5.4 Kill criteria

任一条成立即停止 09.5 生产化：

- 必须新增 TASK schema 或第二份持久状态才能实现。
- 对 closed/unresolved 任务产生任何 fail-open 表述。
- 为了状态命令改变现有 `check` 语义或退出码。
- 命令依赖 LLM、网络、第三方库或写入 Vault。
- S1 在硬指标不降的前提下，输出不比 runtime 基线更小。
- S1 仍需要 owner/Agent 再打开 runtime 才能回答上述五个状态问题。

## 6. 实现上限

允许：

- `scripts/trellium.py`：复用现有 parser/check 数据，新增 `status` 子命令与 text/JSON renderer。
- `scripts/test_trellium.py`：聚焦混合状态、冲突、local missing、只读性和输出 schema。
- `init/VERSION`、`init/MIGRATIONS.md`、中英 README、Skill/reference 和同步快照：仅在消融 Gate 全过后更新到 2026.09.5。
- 自托管 Vault：TASK-0008、runtime、collaboration、shadow check 记录的最小同步。

禁止：

- `context`、`evidence`、`review-pack`、自动 inbox 文件、runtime 生成器。
- schema v2、slice 数组、fact-type 标签、byte 阈值、decision edge。
- 自动修复、自动批准、自动 accepted、执行 TASK 中命令。
- 为此新增依赖、服务、数据库、网络访问或遥测。

## 7. 里程碑

- M0：本审计、TASK-0008 与 S0/S1 预注册独立提交，先于代码。
- M1：记录 S0 当前仓库 golden 与 runtime bytes；不改代码。
- M2：实现最小 `status` + 聚焦测试。
- M3：运行 S1 对照与全量门禁；Kill criterion 命中则回退实现。
- M4：Gate 通过后补齐 2026.09.5 版本、migration、双语文档和 Skill 快照。
- M5：独立 review；无 open finding 后进入 `ready_for_review`，不代 owner accepted，不创建 tag/Release。

## 8. 验收标准

- [ ] 预注册先于代码的 Git 时序可验证。
- [ ] 剩余功能清单对每项标注已解决/No-Go/Inconclusive/Blocked/Deferred/Go，不重开 D-0004。
- [ ] `status` 只读，不新增 schema/依赖/网络/持久视图。
- [ ] 六个冻结场景全部通过，硬指标无损，S1 bytes < runtime bytes。
- [ ] 现有 106 项测试零退化，snapshot in sync，check 0 error / 0 warning，`git diff --check` 通过。
- [ ] 双语文档与 2026.09.5 migration 只描述已实现行为。
- [ ] 独立 review 无 open finding；TASK-0008 停在 `ready_for_review`。

## 9. Review 与反思

### Round 1 — 需求消融

- 删除已交付的 state/policy/check/projection/local 边界，避免重复开发。
- 不因 Codex 把 Context 称为长期核心就绕过 D-0004；决策依据是已完成实验。
- Evidence Receipt、slice、hot/cold 虽有 A 级问题证据，但它们的当前实现假设风险更高，不与 status 并行。

### Round 2 — 最小性

- 不创建 `approvals.md`或持久 inbox，因为它会变成新状态 owner。
- 不把 blocked/pending Gate 自动翻译成“owner 必须批准”，避免越权推理。
- 不为 status 改状态块；如现有数据不足，则按 Kill criterion 终止，不扩 schema。

审计结论：**Deterministic Status Summary 是 2026.09.5 唯一 Go-with-experiments 项；其余保持已有结论或等待证据。**

## 10. Strategy Red-Team（文档 review）

### Top Kill-Assumptions（按影响 × 可能性 × 低成本可验证性排序）

#### R1. 反复询问 status 代表可复用产品痛点

- Steelman：这与 Codex 深度反馈的 owner decision-queue 问题同向，且在 Trellium 自托管期间真实重复。
- Fails if：这些询问只是会话习惯，而非状态获取成本；S1 不能独立回答五个冻结问题。
- Evidence to get：当前仓库 + 两个状态 fixture 的 S0/S1 盲测，保存首答和纠正数。
- Kill criterion：任一场景需要再打开 runtime/TASK 才能答对基本状态问题。
- Cheapest test：实现前先手写一份预期 status 输出，让一个无历史会话只看该输出回答五问；失败则先修契约，不写 parser。

#### R2. 现有 state + runtime 足以安全编译 status

- Steelman：lifecycle/authority 已有严格 TASK owner，runtime 已是受 check 约束的投影。
- Fails if：实现必须解析任意 TASK 自然语言，或将 runtime objective/next action 误当 Authority。
- Evidence to get：针对 drift、missing local、duplicate、legacy 和 symlink 运行 characterization，核对输出的 null/unresolved 边界。
- Kill criterion：出现任一个由 runtime 填充的未验证 lifecycle/authority。
- Cheapest test：先复用 `run_vault_checks` 产出 finding，在一个 local-missing fixture 上确认 status 不猜状态。

#### R3. 新增公开 CLI 比现有 `check --format json` + runtime 更小

- Steelman：`check` 的职责是 finding，强行把 owner 视图塞入 check 会污染稳定 schema。
- Fails if：`status` 只是重排 runtime，没有排除 closed 噪声或没有显式 unresolved。
- Evidence to get：对比 status 与 runtime bytes、行数和五问覆盖，并确认 `check` 输出逐字节/结构不变。
- Kill criterion：无法在不改 check schema/语义的前提下产生更短且信息完整的视图。
- Cheapest test：只实现 renderer 的纯函数原型，用冻结 dict 输入测试；未过不接文件系统。

#### R4. bytes 变小就代表 owner 成本降低

- Steelman：更短的稳定输出至少降低每次传入 Agent 的基础上下文。
- Fails if：输出虽短，但遗漏 Next Action/边界，或 owner 仍需追问解释。
- Evidence to get：五问准确率与 owner review；bytes 只记 guardrail。
- Kill criterion：任一硬指标下降，即使 bytes 显著减少也停止。
- Cheapest test：对同一 golden 用完整 runtime 与候选输出分别首答，先比正确性再比 bytes。

#### R5. status 能顺便变成 owner inbox

- Steelman：ready_for_review 确实通常对应 owner review。
- Fails if：blocked/pending/not_authorized 被统一翻译为“需 owner 行动”，导致误授权或噪声。
- Evidence to get：输出 golden 仅使用 lifecycle 原值和明确标签，禁止推断 actor。
- Kill criterion：任一非 `ready_for_review` 状态被声称为 owner 必须批准。
- Cheapest test：一个 blocked + pending gate + not_authorized gate 的 fixture 快照断言。

### What's Well-Reasoned

- 候选直接对应 A+B 证据，不是凭空增加 CLI。
- 现有状态块和 checker 使只读派生成为可能，不需要数据库、LLM 或 schema v2。
- 单功能、先预注册、有 kill criteria，且 D-0004 与 Evidence 结论未被重开。

### What I Couldn't Assess

- 无法直接访问当初 63 TASK 的深度现场，因此 status 在大项目的输出规模仍需真实复核。
- 没有 owner 的定量 time-to-answer 基线；本轮不声称时间节省百分比。
- 当前 TASK 大多没有 gates/current_slice，因此这两个字段的价值只能做兼容性验证，不能声称生产收益。

### Red-Team Verdict

**APPROVE_WITH_EXPERIMENTS**。GLM 可以开始 M1/M2，但必须先做最便宜的手写输出五问测试；如 R1/R2/R5 任一 kill criterion 命中，将 TASK-0008 转 `superseded` 或 No-Go 收尾，不扩 schema。
