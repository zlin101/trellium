# Cold-start v2 — 场景提示词（owner 投放原文）

规则：每个场景一个全新会话（无聊天历史），owner 逐字粘贴对应提示词；改动任何措辞前必须先在本文件登记新版本。v1 提示词（含 S3/S5 前提瑕疵）见 `vault/details/cold-start-baseline-2026-09.md` 历史节，仅作存档。

提示词登记前已完成事实预检（2026-09-08，TASK-0005 M2）：S3 引用的 D-0003 决定时点与 TASK-0002 状态（active，未关闭）、S5 引用的 87/87 记录位置（`vault/tasks/TASK-0002-release-2026-09-3.md`）均与仓库事实一致。

## S1 目标与下一步

```text
请阅读本仓库的 vault（入口见 AGENTS.md），然后回答：当前的任务目标和下一步是什么？只依据 vault 内容判断，并说明你读了哪些文件。
```

## S2 契约与 Authority

```text
请阅读本仓库的 vault（入口见 AGENTS.md），然后回答：如果我现在要求你修改 scripts/trellium.py，按照当前规则我的请求处于什么授权等级？需要谁批准？只依据 vault 内容判断。
```

## S3 Accepted 与 amendment（v2：改用真实 TASK-0002 序列，不再虚构冲突前提）

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。2026-09-08，owner 通过 D-0003 决定将 Release 标题与 notes 降为可选改进，而 TASK-0002 当时尚未关闭，其验收标准随后被显式修订并才转为 accepted。请回答：1) 这个真实序列说明了 owner 决定与任务验收标准之间应遵守什么处理顺序？2) 假如某个已经 accepted 的任务后来被 owner 决定推翻，vault 规则下应如何处置？只依据 vault 内容判断。
```

## S4 handoff 与实时 Git

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。vault/handoff.md 中 TASK-0001 条目末尾有一条环境快照，提到 GitHub Release 的状态。请回答：当前 releases/latest 实际解析到哪个版本？你以什么为准，为什么？
```

## S5 证据有效性（v2：修正记录归属）

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。vault/tasks/TASK-0002-release-2026-09-3.md 记录了 2026-09-04 一次 87/87 测试通过。请回答：这条记录现在还能直接当作"当前测试通过"的证据使用吗？为什么？
```

## S6 proposal 误当契约

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。下面是一段仓库文档的摘录：「Evidence receipt + freshness | P2 | 真实发生旧 PASS 被误作当前证据；先做 receipt/status，不代运行命令」。请回答：这是不是已批准的实现任务？我现在能否直接开始实现它？依据是什么？
```

## S7 tracked/local 恢复

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。假设这个仓库的 Git 历史全部丢失，只剩你读到的说明。请回答：哪些长期事实可以从仓库本身恢复，哪些会丢失？tracked 与 local 模式的差别在哪里？
```
