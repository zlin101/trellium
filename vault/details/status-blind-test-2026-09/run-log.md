# S0/S1 盲测运行台账

六个受测会话的运行标识与元数据。全部会话由实施会话（ZCode session `sess_9e641c30-a18a-43f6-a598-dc7e034d8704`，2026-09-09）以全新子代理派出；`tool_uses` 为运行时返回的实际工具调用数（0 = 未读任何文件、未使用搜索）。子代理运行时未返回独立模型标识；宿主会话模型为 `builtin:bigmodel-coding-plan/GLM-5.3-Flash`。会话转录由本地 ZCode 会话存储保留；本目录的 prompt/answer 文件是投放与回收的逐字文本。

| 会话 | 臂/场景 | agentId | subagent_tokens | tool_uses | duration_ms | 投放文件 | 首答文件 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | S1 / 场景 1 | `agent_42a9cb7d-bb24-4842-a855-0d26ca2de1a0` | 10929 | 0 | 47811 | `prompt-s1-a.md` | `answer-s1-a.md` |
| 2 | S1 / 场景 2 | `agent_5569f7a4-31b1-45ac-be6a-1c578099d2eb` | 13984 | 0 | 122578 | `prompt-s1-b.md` | `answer-s1-b.md` |
| 3 | S1 / 场景 3 | `agent_c742da6d-8fba-4022-8841-6d29cf2d8bb8` | 11967 | 0 | 74342 | `prompt-s1-c.md` | `answer-s1-c.md` |
| 4 | S0 / 场景 1 | `agent_a7107a77-7688-4169-a14c-731b095175a7` | 12947 | 0 | 63090 | `prompt-s0-a.md` | `answer-s0-a.md` |
| 5 | S0 / 场景 2 | `agent_c8f96f29-4670-44f7-a1c9-4a5b1dfa9c46` | 17926 | 0 | 220573 | `prompt-s0-b.md` | `answer-s0-b.md` |
| 6 | S0 / 场景 3 | `agent_72e3b159-f5b8-4f5c-8cfa-8f827ee81e4e` | 11368 | 0 | 56243 | `prompt-s0-c.md` | `answer-s0-c.md` |

污染控制：

- 六个会话互相独立、与实施会话无共享历史（每次为全新子代理上下文）。
- 提示词明令禁止读文件/用工具；运行元数据 `tool_uses: 0` 与各首答自述一致。
- S1 臂输入为 golden 原字节文件（`golden-scenario*.txt`）；S0 场景 1 材料为 `git show 55ae985:vault/runtime.md` 的原字节（`s0-material-scenario1-runtime.md`，11039 bytes）+ `blocks-scenario1.txt`；场景 2/3 材料内嵌于 `prompt-s0-b.md`/`prompt-s0-c.md`，状态块另存 `blocks-scenario2.txt`。
- 时序：S1 三会话先于任何 status 代码（parser 于其后实现，见任务文件执行记录）；S0 三会话于 owner review 后补跑，代码已存在但受测会话未接触任何实现信息。
- 评分：由实施方对照冻结真值（见上级索引文档）做出；每会话首答原文即 answer 文件，未做任何改写。

评分汇总（逐问依据见 answer 文件与索引文档）：

| 会话 | 首答 | 纠正数 | 说明 |
| --- | --- | --- | --- |
| S1-A | 5/5 正确 | 0 | 备注 (resolved) 语义未定义 |
| S1-B | 5/5 正确 | 0 | |
| S1-C | 5/5 正确 | 0 | 备注"为何无 Next Action"需推断 |
| S0-A | 5/5 正确 | 0 | closed 计数依赖本仓库 runtime 行书写习惯 |
| S0-B | 4 正确 + 1 问需材料外推断 | 0 | closed=2 为推断口径，评审员显式声明 |
| S0-C | 4 正确 + 1 问过度声称 | 1 | 把缺失文件任务的 Next Action 记录当作可用 |
