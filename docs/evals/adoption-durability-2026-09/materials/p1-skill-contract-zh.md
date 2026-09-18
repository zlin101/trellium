# P1 候选：接入完成契约（中文 Skill 插入段 — 实验材料，非实现）

拟插入位置：`skills/trellium-zh/SKILL.md` 的「既有项目接入」节之后。

---

## 接入完成契约

`adopt` 只做机械安装；"接入完成"要求以下全部成立，缺一不可：

1. 语义配置已完成：按真实项目事实选择模式与 storage，合并既有 Agent 入口，不覆盖用户内容。
2. 协作核心已持久化：`AGENTS.md`、`vault/` 全部必需文件、`skills/agent-task/SKILL.md` 与版本戳已提交进版本控制历史（进入 Git `HEAD`）。adopt 与 Agent 都不得自动 `git add`、commit、push——提交动作由用户执行或经用户明确授权。
3. 提交后复跑 `trellium.py check <target>` 为 0 error：核心路径未提交时 check 报 `CORE_STORAGE_UNCOMMITTED`，被 ignore 规则误伤时报 `CORE_STORAGE_IGNORED`，两者都是 error。
4. local/生产接入的最终验收是 fresh clone 后复跑 check 同样通过。fresh clone 是一次性验收动作，不进入日常 check。
5. 接入状态与风险已记入 `vault/runtime.md`。

文件已生成 ≠ 接入已完成。协作核心未提交前，不得向用户声称接入完成。
