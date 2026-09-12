# 宿主投放与计量工具（存档，供第三方复算）

- `mk_prompt.sh`：由冻结模板装配逐字 prompt（占位符替换 + R1 内嵌 Pack）。
- `run_session.sh`：headless CLI 投放（stdin 通道、固定工具面、进程级计时）。
- `finalize_run.py`：transcript 解析 → answer.md / run.json（协议 §5 计量算法的实现）。
- `audit_session.py`：污染审计（v1.4 白名单 + 受保护区分类）。
- 注：`finalize_run.py` 中 `file_opens_task_vault` 的 Bash 归类是判断性口径（见 results.md 计量口径注）；其余指标纯机械。
