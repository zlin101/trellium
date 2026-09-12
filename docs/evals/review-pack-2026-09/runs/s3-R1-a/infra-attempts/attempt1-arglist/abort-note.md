# infra abort — s3-R1-a attempt 1（argv 长度限制）

- 2026-09-12 16:15：rc=126，`/usr/bin/timeout: Argument list too long`。212334B prompt 超过 Linux MAX_ARG_STRLEN=128KB，claude 未启动，无模型调用、无 transcript。
- 处置：投放通道改为真 stdin 管道（协议 v1.3 补记）；同槽位重投。
