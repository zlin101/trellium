# Status Summary S0/S1 盲测原始记录 — 2026-09

TASK-0008 R1/R4 消融的完整原始材料（owner review round 后补齐 S0 臂）。预注册见 `docs/superpowers/plans/2026-09-09-2026-09-5-codex-feedback-audit-and-status-plan.md` §5；本文件只存事实：材料、提示词、逐字首答、评分与纠正数。评分由实施方（GLM）对照冻结真值做出，未做统计声称；owner 可按本文件材料复跑。

## 实验控制

- 每个受测会话是一个全新子代理，无共享历史；提示词明令禁止读取文件与使用工具（各首答中 `tool_uses: 0` 可复核）。
- S1 臂输入 = 一份手写预期 status 输出（golden）；S0 臂输入 = 现行流程的完整材料（`vault/runtime.md` 全文 + 全部任务文件状态块），提示词明确声明"材料即全部输入"。
- 场景 1 的 S0 材料 pin 在审计基准 `55ae985`（runtime 11039 bytes + 8 个状态块，可用 `git show 55ae985:...` 复取）；场景 2/3 的 fixture 材料全文附下。
- 评分口径：逐问 对照冻结真值，记录 首答正确 / 需材料外推断 / 过度声称，纠正数 = 首答中必须撤回的错误声称数。

## 冻结真值

| 场景 | focus | 开放分类 | closed | unresolved | 可用 Next Action |
| --- | --- | --- | --- | --- | --- |
| 1 当前仓库（@55ae985） | TASK-0008 | active{0001,0008}、blocked{0004} | 5（0002/0003/0005/0006/0007） | 无 | 0001 / 0004 / 0008 |
| 2 混合 fixture | TASK-0013 | draft{0010}、active{0011}、blocked{0012}、ready_for_review{0013} | 2（0014 accepted、0015 superseded） | 无 | 0010–0013 各一条 |
| 3 冲突+缺失 fixture | TASK-0020（不可信） | 无（两个都不可解析） | 0 | 0020 drift、0021 本地缺失 | 无（S1 契约下 unresolved 不给投影） |

## 提示词模板（两臂同构）

S1 臂："你是一个没有任何历史上下文的评审员。下面是一份工具输出的完整文本。规则：只能依据这份文本回答问题，绝对不要读取任何文件、目录或使用任何搜索工具。如果仅凭该文本无法回答某个问题，必须明确写'无法回答'，并说明还缺什么信息。——（golden 全文）——五问：1 当前 Focus 是哪个（哪些）任务？2 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？3 已关闭（closed）的任务有几个？4 有哪些任务的状态无法解析（unresolved）？输出对它们声称了什么、没有声称什么？5 哪些任务有 Next Action 可用？分别是什么？（场景 3 的第 1/5 问措辞略有调整，见各首答原文）最后用一行 JSON 概括。"

S0 臂："你是一个没有任何历史上下文的评审员，正在模拟现行工作流：人工阅读 vault/runtime.md 全文与各任务文件的 trellium-task-state 状态块，手工编译项目状态。规则：只能依据下面给出的材料回答……材料就是全部输入。同五问。"

## S1 臂输入（手写 golden，逐字）

### Golden A（场景 1，1149 bytes；owner review 时同实现输出为 1120 bytes，差异来自 runtime 投影文本随后续提交演变）

```
trellium status: /home/liam/git/trellium
focus: TASK-0008 (resolved)
summary: 0 draft, 2 active, 1 blocked, 0 ready_for_review, 5 closed, 0 unresolved
draft: (none)
active (2):
  TASK-0001 authority=2 path=vault/tasks/TASK-0001-self-hosting-pilot.md
    objective: Run the self-hosting pilot and collect K1-K4 shadow evidence.
    next: Next Agent continues pilot work; log transitions in `vault/details/shadow-run-2026-09.md`.
  TASK-0008 authority=3 path=vault/tasks/TASK-0008-owner-status.md
    objective: Ship one 2026.09.5 feature from the Codex feedback audit: deterministic read-only status summary.
    next: Plan/red-team/preregistration frozen; GLM runs the handwritten-output five-question test, then M1-M5 only if it passes.
blocked (1):
  TASK-0004 authority=2 path=vault/tasks/TASK-0004-post-release-validation.md
    objective: Post-release validation: cold-start baseline, second-project pilot, Context Go/No-Go.
    next: M3 No-Go adopted as D-0004; resumes (blocked -> active) when the owner provides a second real project in local mode.
ready_for_review: (none)
unresolved: (none)
findings: none
result: 0 error(s), 0 warning(s)
```

### Golden B（场景 2，1066 bytes）

```
trellium status: /tmp/fixture-mixed
focus: TASK-0013 (resolved)
summary: 1 draft, 1 active, 1 blocked, 1 ready_for_review, 2 closed, 0 unresolved
draft (1):
  TASK-0010 authority=1 path=vault/tasks/TASK-0010-draft.md
    objective: Draft the onboarding guide rewrite.
    next: Split the outline into reviewable sections.
active (1):
  TASK-0011 authority=2 slice=M2 gates: design=passed, launch=not_authorized path=vault/tasks/TASK-0011-active.md
    objective: Migrate the exporter to the stable writer API.
    next: Run the characterization suite after the slice lands.
blocked (1):
  TASK-0012 authority=2 gates: vendor=blocked path=vault/tasks/TASK-0012-blocked.md
    objective: Cut the 3.2 release once the vendor fix lands.
    next: Blocked on the vendor patch; revisit after upstream merges.
ready_for_review (1):
  TASK-0013 authority=3 path=vault/tasks/TASK-0013-ready.md
    objective: Land the retention policy documentation.
    next: Owner review of the documented retention rules.
unresolved: (none)
findings: none
result: 0 error(s), 0 warning(s)
```

### Golden C（场景 3，954 bytes）

```
trellium status: /tmp/fixture-conflict-local
focus: TASK-0020 (unresolved)
summary: 0 draft, 0 active, 0 blocked, 0 ready_for_review, 0 closed, 2 unresolved
draft: (none)
active: (none)
blocked: (none)
ready_for_review: (none)
unresolved (2):
  TASK-0020 reason=TASK_RUNTIME_DRIFT path=vault/tasks/TASK-0020-drift.md
  TASK-0021 reason=TASK_RUNTIME_LOCAL_UNRESOLVED
findings (2):
  ERROR   TASK_RUNTIME_DRIFT vault/runtime.md [TASK-0020]: runtime row for TASK-0020 says 'active' but the trellium-task-state block says 'draft'
  WARNING TASK_RUNTIME_LOCAL_UNRESOLVED vault/runtime.md [TASK-0021]: runtime points to local task TASK-0021, but its file is not in this worktree: this is expected in a fresh clone (local task files are ignored) or the file may have been lost locally; recover the original task file or rebuild the contract with owner approval; the runtime summary is an unverified clue and grants no authority
result: 1 error(s), 1 warning(s)
```

## S0 臂输入

- 场景 1：`git show 55ae985:vault/runtime.md`（11039 bytes）+ 8 个状态块（同 commit；TASK-0008 块当时为 active）。
- 场景 2 runtime 全文：

```
# Runtime Context

## Focus

- TASK-0013

## Active Tasks

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0010 | Draft the onboarding guide rewrite. | draft | Split the outline into reviewable sections. |
| TASK-0011 | Migrate the exporter to the stable writer API. | active | Run the characterization suite after the slice lands. |
| TASK-0012 | Cut the 3.2 release once the vendor fix lands. | blocked | Blocked on the vendor patch; revisit after upstream merges. |
| TASK-0013 | Land the retention policy documentation. | ready_for_review | Owner review of the documented retention rules. |
```

场景 2 状态块 = 6 个 `trellium-task-state` JSON（0010 draft/authority 1；0011 active/2 + slice M2 + gates design=passed、launch=not_authorized；0012 blocked/2 + gates vendor=blocked；0013 ready_for_review/C/3；0014 accepted/B/2；0015 superseded/B/2）。

- 场景 3 runtime 全文 + 唯一状态块：

```
# Runtime Context

## Focus

- TASK-0020

## Active Tasks

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0020 | Objective for the drifted task. | active | Next action for the drifted task. |
| TASK-0021 | Objective for the missing local task. | active | Next action for the missing local task. |
```

```
<!-- trellium-task-state
{
  "schema_version": 1,
  "task_id": "TASK-0020",
  "level": "B",
  "authority_level": 2,
  "lifecycle": "draft"
}
-->
```

## 逐字首答与评分

### S1-A（场景 1）— 5/5 正确，0 纠正

首答要点（逐字 JSON）：`{"q1_focus": "TASK-0008 (resolved)", "q2_open": {"TASK-0001": "active", "TASK-0008": "active", "TASK-0004": "blocked"}, "q3_closed_count": 5, "q4_unresolved": [], "q5_next_actions": {"TASK-0001": "...", "TASK-0008": "...", "TASK-0004": "..."}, "any_unanswerable": false}`。评审员备注：(resolved) 标记语义未在文本中定义（仍答对）；closed 5 个仅计数未列明细（设计内）。

### S1-B（场景 2）— 5/5 正确，0 纠正

首答要点：focus 0013；四开放任务分类全对；closed 2；unresolved 无；四个 Next Action 全对，且 gates/slice 按字面原值报告、不做超字面推断。备注：材料未定义"开放"，评审员按"非 closed 非 unresolved"理解并注明（答案仍全对）。

### S1-C（场景 3）— 5/5 正确，0 纠正

首答要点：focus TASK-0020 状态不可信（active vs draft 冲突）；无任何开放分类；closed 0；两个 unresolved 的声称/不声称完全正确（含 "grants no authority"）；无 Next Action。备注：评审员指出"为何无 Next Action"需推断（输出未陈述原因）——已记为外观观察，未改契约。

### S0-A（场景 1）— 5/5 正确，0 纠正

逐字 JSON：`{"q1_focus": "TASK-0008", "q2_open": {"TASK-0001": "active", "TASK-0004": "blocked", "TASK-0008": "active"}, "q3_closed_count": 5, "q4_unresolved": "none — 8/8 任务均有状态块且与表格 Status 一致；不声称已核验任务正文或材料外无其他任务", "q5_next_actions": {"TASK-0001": "继续 pilot 工作并在 vault/details/shadow-run-2026-09.md 记录转换", "TASK-0004": "owner 提供第二个真实项目后恢复（条件性）", "TASK-0008": "GLM 执行 handwritten-output 五问测试，通过后进入 M1-M5", "TASK-0002/0003/0005/0006/0007": "仅关闭记录，无后续动作"}, "any_unanswerable": false}`。评分：全对；closed=5 的依据包含 Next Action 单元格中的 "Closed 2026-09-08/09" 字样——该线索是本仓库 runtime 行的书写习惯，不是协议保证（见 S0-B 对照）。

### S0-B（场景 2）— 4 问正确 + 1 问需材料外推断，0 纠正（1 项不确定声明）

逐字 JSON：`{"q1_focus": "TASK-0013", "q2_open": {"TASK-0010": "draft", "TASK-0011": "active", "TASK-0012": "blocked", "TASK-0013": "ready_for_review", "_caveat": "文本未定义 open，此处为非 closed 非 unresolved 的四个任务"}, "q3_closed_count": 2, "q4_unresolved": "无解析失败；6 个状态块均可解析，仅 TASK-0014/0015 的 closed 归类依赖材料未定义的 lifecycle 分类学", "q5_next_actions": {...四个全对...}, "any_unanswerable": true}`。评分：Q3 答案 "2" 正确，但评审员明确声明"严格意义上无法仅凭材料回答……closed=2 是推断口径，不是材料的直接陈述"——现行状态层确实没有任何位置定义 accepted/superseded 即 closed；S1 的 summary 行把该分类学内建（对照差异 1）。

### S0-C（场景 3）— 4 问正确 + 1 问过度声称，1 纠正

逐字 JSON：`{"q1_focus": "TASK-0020（unresolved，active vs draft 冲突，状态不可信）", "q2_open": {"draft": 0, "active": 0, "blocked": 0, "ready_for_review": 0, "note": "两个任务均为 unresolved，未获任何 lifecycle 分类"}, "q3_closed_count": 0, "q4_unresolved": {"TASK-0020": "声称 runtime 行(active)与 task-state 块(draft)冲突；未声称哪个为真、未声称 lifecycle 与 authority", "TASK-0021": "声称 runtime 指向但文件不在 worktree……明确声称 runtime summary 为未验证线索、不授予 authority；未声称 lifecycle 或实际状态"}, "q5_next_actions": "无任何任务有 Next Action；输出未明说原因（仅可推断与 unresolved 相关，原因部分无法回答）", "any_unanswerable": true}`。

注意：以上 JSON 的 q2/q4 是评审员正文正确结论的概括；其正文第 5 问首答原文为："两个任务在 runtime.md 中都有 Next Action 记录：TASK-0020 为 'Next action for the drifted task.'，TASK-0021 为 'Next action for the missing local task.'……'存在 Next Action 记录'这一点成立"。评分：Q5 首答把缺失文件任务（TASK-0021）的 runtime 占位文本列为"有 Next Action 记录"，对"哪些任务有 Next Action 可用"构成过度声称（真值：无可信 Next Action）——记 1 次纠正；评审员正文其余判断（含 drift 不裁决、TASK-0021 不可解析）全部正确。S1 golden C 对同一问结构性输出"无"，未给不可信投影（对照差异 2）。

## 结果汇总

| 会话 | 输入 bytes | 五问首答 | 纠正数 | 备注 |
| --- | --- | --- | --- | --- |
| S1-A | 1149 | 5/5 | 0 | |
| S1-B | 1066 | 5/5 | 0 | |
| S1-C | 954 | 5/5 | 0 | |
| S0-A | ≈12530（runtime 11039 + 8 块） | 5/5 | 0 | closed 计数依赖本仓库书写习惯线索 |
| S0-B | ≈1810（runtime 624 + 6 块 1187） | 4 正确 + 1 需材料外推断 | 0（1 项显式不确定声明） | 状态层无 open/closed 分类学定义 |
| S0-C | ≈712（runtime 496 + 1 块 216） | 4 正确 + 1 过度声称 | 1 | 把缺失文件任务的 Next Action 记录当作可用 |

结论（严格限定）：六会话全部一次作答、零工具使用；S1 臂 3/3 场景五问全对、0 纠正、零材料外推断；S0 臂正确性依赖阅读量更大的材料与读者自身补全分类学/冲突裁决，场景 3 出现 1 次过度声称。bytes 对照（S1 954–1149 vs S0-A 材料 11039+）满足 guardrail 方向；bytes 只是 guardrail，未做 owner 可用性复核，不声称时间节省。

局限：每格 n=1，中文单语会话，评分者为实现方（非独立第三方）；S0 材料刻意不含 governance/index 中的生命周期语义，用于暴露"现行状态输入本身不携带 open/closed 分类学"这一事实，不代表熟练 owner 的真实表现。
