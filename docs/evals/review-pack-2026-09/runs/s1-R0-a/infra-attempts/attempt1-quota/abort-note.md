# infra abort — s1-R0-a attempt 1（provider 配额）

- 2026-09-11 16:43 投放，16:57 终止（wall 832.8s，35 turns，34 tool_use）。
- 终止原因：API 429「已达到 5 小时的使用上限」，限额 18:00:38 重置。最后一跳被拒，无首答（最后 assistant 文本即错误串）。
- 处置：归档不计分；限额重置后同槽位重投（相同冻结 prompt）。
