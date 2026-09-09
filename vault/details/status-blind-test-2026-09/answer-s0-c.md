1. **当前 Focus 指向哪个任务？它的状态能否被可信地确定？**
   Focus 指向 **TASK-0020**。其状态存在两个互相冲突的来源：任务文件 `trellium-task-state` 状态块给出 `lifecycle: "draft"`，而 runtime.md 的 Active Tasks 表给出 `Status: active`。状态块本身可以解析，因此"任务文件声称 draft"这一点是确定的；但两个来源不一致（漂移），项目层面的单一可信状态无法确定。若以任务文件状态块为生命周期权威，则其 lifecycle 为 draft，runtime.md 的 active 记录已过期。

2. **处于开放状态的任务有哪些？各自的 lifecycle 分类是什么？**
   按 runtime.md，开放任务有两个：TASK-0020 和 TASK-0021（表中均标 active）。lifecycle 分类：
   - TASK-0020：`draft`（来自其状态块，与 runtime.md 的 active 冲突）。
   - TASK-0021：**无法回答**——本地不存在 TASK-0021 的任务文件，也就没有状态块，其 lifecycle 无法解析。材料只能支持"runtime.md 将其列为 active"这一声称。

3. **已关闭（closed）的任务有几个？**
   在给定材料范围内可确认为 **0 个**：唯一的任务文件状态块是 draft，runtime.md 中两个任务均标记 active，没有任何 closed 记录。（该结论仅对材料范围成立；材料即全部输入。）

4. **有哪些任务的状态无法解析（unresolved）或存在疑问？声称了什么、没有声称什么？**
   - **TASK-0021：unresolved。** 声称：runtime.md 将其列为 active 并给出 Next Action，但本地无任务文件、无状态块，其 lifecycle 未知。未声称：它的真实生命周期、它是否真的处于开放状态、甚至该任务是否实际存在。
   - **TASK-0020：状态可解析但存在疑问（漂移）。** 声称：状态块为 draft，runtime.md 为 active，二者冲突。未声称：哪个来源正确（除非额外假定状态块权威），也未声称该任务的实际进度。

5. **哪些任务有 Next Action 可用？**
   两个任务在 runtime.md 中都有 Next Action 记录：TASK-0020 为 "Next action for the drifted task."，TASK-0021 为 "Next action for the missing local task."。需要说明：这些只是 runtime.md 表中的占位式文本，其是否真实可执行无法凭材料验证；尤其 TASK-0021 的 Next Action 挂在一个缺少本地任务文件的条目下，其有效性存疑，但"存在 Next Action 记录"这一点成立。因此不存在"都无法确定"的情形。

```json
{"q1_focus": "TASK-0020", "q2_open": {"TASK-0020": "draft（状态块；runtime.md 称 active，存在漂移）", "TASK-0021": "无法回答（无任务文件，lifecycle 不可解析；runtime.md 称 active）"}, "q3_closed_count": 0, "q4_unresolved": {"TASK-0021": "unresolved：无任务文件，lifecycle 未知", "TASK-0020": "drift：状态块 draft 与 runtime.md active 冲突"}, "q5_next_actions": "两者均有：TASK-0020 'Next action for the drifted task.'；TASK-0021 'Next action for the missing local task.'（均为 runtime.md 占位文本，TASK-0021 的有效性存疑）", "any_unanswerable": true}
```
