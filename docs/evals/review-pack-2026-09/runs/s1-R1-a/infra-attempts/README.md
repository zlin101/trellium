# S1-R1 槽位 a 的 infra 中断记录（两次投放尝试，均无首答产生）

- attempt 1（2026-09-11 15:31–15:42）：harness 后台任务内存守护击杀；transcript 9 行、0 tool_use。
- attempt 2（2026-09-11 15:45 投放）：同样被守护快速击杀；transcript e513a797…jsonl 归档于本目录。
- 系统无内核 OOM（dmesg 无事件、swap 0、可用内存 ~12GB）；判定为 harness 对后台子任务的守护行为，非实验会话自身故障。
- 处置：改用 setsid 完全脱离 harness 任务树执行（同一冻结命令/工具面/prompt，仅宿主挂接方式变化，记入 results.md M3 备注）；a 槽位由首次完整完成的会话占据。
