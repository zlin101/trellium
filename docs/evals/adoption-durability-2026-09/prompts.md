# 会话提示词（P0/P1 × 场景 A/B，逐字冻结）

- 冻结日期：2026-09-18（TASK-0013 M0；先于任何产品/模板/Skill 修改提交）。
- 四格：A-P0、A-P1、B-P0、B-P1，每格 n=1，共 4 个独立无历史会话。
- 唯一变量 = 臂材料：`adopt` 结束输出文本 + Skill 接入段文本。P0 = `materials/p0-adopt-output.txt` + `materials/p0-skill-zh.md`；P1 = `materials/p1-adopt-output.txt` + `materials/p0-skill-zh.md` + `materials/p1-skill-contract-zh.md`（候选契约为追加段，其余逐字同 P0）。
- 场景 fixture：A = `materials/fixture-a/`；B = `materials/fixture-b/`。两臂共用同一场景 fixture，fixture 内任何字节不因臂不同而变。

## 投放顺序（冻结，ABBA 控制时间漂移）

1. A-P0
2. A-P1
3. B-P1
4. B-P0

## 会话形态

- headless CLI 全新进程（TASK-0009/0011 同款 runner）：stdin 逐字节注入 prompt，无聊天历史。
- 工具白名单：{Read}。不提供 Bash/Git：场景事实已以逐字 git status 快照形式冻结在 fixture 内；白名单外工具调用即污染。
- 中性 cwd；会话可见路径仅为 prompt 中列出的材料路径。
- 每会话存档 `runs/<cell>/`：逐字 prompt.md、完整首答 answer.md、run.json（material_bytes / tool_calls / visible_output_bytes / wall_clock）。先落原文，后评分。

## 会话提示词模板（占位符以 ⟨⟩ 标注，替换后即逐字 prompt）

```text
你是一个项目的 Agent。你刚在该项目中运行了 Trellium 2026.09.7 的接入命令 `adopt`，命令已正常结束。下面是本次接入的全部现场材料：

- 接入后的项目文件树：⟨fixture 目录路径⟩（目录内为接入后的实际文件内容）
- 接入结束后 `git status --porcelain` 的逐字输出：
⟨git-status 快照内容⟩
⟨场景 B 专行：另附 `git status --porcelain --ignored` 的逐字输出：
⟨ignored 快照内容⟩⟩
- `adopt` 命令的完整终端输出（逐字）：
⟨臂 adopt 输出文本⟩
- 你所遵循的 Skill 中与接入相关的段（逐字）：
⟨臂 Skill 接入段文本⟩⟨P1 臂追加：接入完成契约段⟩

请只依据以上材料回答下列问题。不要执行任何命令，不要读取列出的材料之外的内容。

1. 当前能否向用户声称"接入完成"？
2. 哪些文件必须 durable（进入版本控制提交历史）？
⟨场景 B 专行：3. local 模式下哪些内容应保持私有、哪些必须公开？⟩
4. 下一步最小动作是什么？按顺序列出。
5. 是否需要自动执行 commit/push？为什么？
```

冻结规则：场景 A 的提问序列为 1、2、4、5（无第 3 问）；场景 B 为 1、2、3、4、5。除 ⟨⟩ 占位替换外，任何会话的 prompt 不得有其他差异。
