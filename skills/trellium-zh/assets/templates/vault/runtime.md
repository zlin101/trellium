# Runtime Context

## Current Phase

替换为当前阶段。

## Focus

- TASK-0001

## Active Tasks

每行一个并行任务；本表只存指针，正文放 `vault/tasks/<task-id>.md`。

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-0001 | 替换为一句话目标。 | active | 替换为下一步动作。 |

状态取值：draft | active | blocked | ready_for_review | accepted | superseded。有任务文件的 TASK，此行状态是 `trellium-task-state` 状态块的派生投影：先改状态块，再改此行。Focus 只表示当前注意力，不等于 lifecycle；更新状态时只改对应行。暂停且暂不推进的任务降级为 `vault/parked.md` 条目。

## Current Progress

- 替换为简短当前状态（对应 Focus 任务）。

## Constraints

- 保持本文件短小。
- 将长执行历史移到 `vault/tasks/*`。
- 暂停且暂不推进的任务降级为 `vault/parked.md` 条目。
- 不保存密钥。

## Recent Changes

- 替换为近期相关变化。

最多保留 10 条；更早的条目在压缩时并入任务文件执行历史。

## Known Risks

- 替换为已知风险。

## Required Checks

```bash
replace-with-project-check
```

## Next Steps

- 替换为下一步。
