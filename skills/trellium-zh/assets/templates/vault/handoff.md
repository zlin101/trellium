# Handoff

只用于近期中断或转交工作，最多保留 3 条交接。不要当作永久日志。
每条交接以任务编号命名；无任务编号时用 SESSION。更早的交接在压缩时按任务编号归并进对应任务文件。

分支、HEAD、脏文件在恢复时通过 Git 现场读取；不要把实时 Git 状态当权威记录。可选保留一条带观察时间、明确标注为历史观察的环境快照。

## TASK-0001 - 2026-01-01

- Objective: 替换为目标。
- Completed: 替换为已完成工作。
- In progress: 替换为进行中工作。
- Failed attempts: 替换为失败尝试和原因。
- Blockers: 替换为阻塞项，没有则写 none。
- Next best action: 替换为下一步最佳行动。
- Files to read first: 替换为行动前先读取的文件。
- Environment snapshot（可选，观察于 2026-01-01 14:00，历史快照）: 替换或删除本行。
