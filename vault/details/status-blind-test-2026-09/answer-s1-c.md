以下回答仅基于所给输出文本，未读取任何文件或使用任何工具。

**1. 当前 Focus 指向哪个任务？它的状态能否被可信地确定？**

Focus 指向 **TASK-0020**，且被明确标注为 `(unresolved)`。它的状态**不能被可信地确定**：文本给出的 ERROR finding 表明两个来源相互冲突——`vault/runtime.md` 中的 runtime 行称其为 `active`，而 `trellium-task-state` 块称其为 `draft`（reason=TASK_RUNTIME_DRIFT）。文本没有裁决哪个为真。

**2. 处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？**

**没有任何任务处于开放 lifecycle 分类中。** summary 行显示 `0 draft, 0 active, 0 blocked, 0 ready_for_review`，且下方各 lifecycle 分区均为 `(none)`。两个存在的任务（TASK-0020、TASK-0021）都被归入 `unresolved`，即未获得任何 lifecycle 分类。

**3. 已关闭（closed）的任务有几个？**

**0 个**（summary 行明确写着 `0 closed`）。

**4. 哪些任务 unresolved？各自被声称/未被声称了什么？**

- **TASK-0020**（reason=TASK_RUNTIME_DRIFT，ERROR 级，path=`vault/tasks/TASK-0020-drift.md`）：
  - 声称了：存在具体冲突——runtime 行说 active、task-state 块说 draft；任务文件路径存在。
  - 没有声称：哪个来源正确、该任务的真实 lifecycle、任何 authority。
- **TASK-0021**（reason=TASK_RUNTIME_LOCAL_UNRESOLVED，WARNING 级）：
  - 声称了：runtime 指向本地任务 TASK-0021，但其文件不在当前 worktree；给出两种可能解释（fresh clone 中本地任务文件被 ignore 属正常；或文件本地丢失）；给出恢复路径（找回原文件，或在 owner 批准下重建契约）。**明确没有声称 authority**："the runtime summary is an unverified clue and grants no authority"。
  - 没有声称：该任务的真实状态/lifecycle、文件确实丢失（只是可能）。

**5. 哪些任务有 Next Action 可用？**

**没有任何任务列出 Next Action**——输出中根本不包含 Next Action 字段或分区。至于原因，**输出没有明说，无法回答**：文本只能让读者推断"因为两个任务都 unresolved、状态不可信，所以没有可用的 Next Action"，但这是推断，输出本身从未陈述这一因果。要确证原因，还缺一份说明 unresolved 任务为何不产生 Next Action 的文档或输出说明。

```json
{"q1_focus": "TASK-0020（unresolved，active vs draft 冲突，状态不可信）", "q2_open": {"draft": 0, "active": 0, "blocked": 0, "ready_for_review": 0, "note": "两个任务均为 unresolved，未获任何 lifecycle 分类"}, "q3_closed_count": 0, "q4_unresolved": {"TASK-0020": "声称 runtime 行(active)与 task-state 块(draft)冲突；未声称哪个为真、未声称 lifecycle 与 authority", "TASK-0021": "声称 runtime 指向但文件不在 worktree，给出 fresh-clone/丢失两种解释及需 owner 批准的恢复路径；明确声称 runtime summary 为未验证线索、不授予 authority；未声称 lifecycle 或实际状态"}, "q5_next_actions": "无任何任务有 Next Action；输出未明说原因（仅可推断与 unresolved 相关，原因部分无法回答）", "any_unanswerable": true}
```
