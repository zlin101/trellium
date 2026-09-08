# 非 Context 优化实验 — 判断 cell 提示词（owner 投放原文）

规则：每个 cell 一个全新会话（无聊天历史），owner 逐字粘贴；被测 Agent 读到 `scoring.md` 即标 `contaminated`。当前仅 M2 Evidence Receipt 具备实验条件；M3-M6 前置未满足（见 `results.md`）。所有场景材料为 **synthetic**，只测判断正确性，不证明生产收益。

## M2 判断 cell 基础提示词（E0/E1/E2 通用）

```text
请阅读本仓库的 vault（入口见 AGENTS.md）。下面是某次验证工作留下的记录，以及当前工作树状态的事实清单。请判断：这份记录是否仍可作为"当前代码树已通过这些验证"的证据？只能回答 fresh / historical / unresolved 之一，并用不超过三句话说明理由。你可以使用 git 只读命令核实。
```

随后按 cell 粘贴对应材料（见下）。E2 cell 在材料末尾额外附"自动比较器输出"。

## 场景与材料（synthetic）

四类可判定场景各配 E0/E1/E2 材料。E0 为现行自由文本风格；E1 为结构化 receipt 草案（`schema_version: 0` 表示实验稿，非授权 schema）；E2 = E1 + 比较器输出。

### 场景 A：快照未变

- 事实清单：`HEAD = 9f1c2ab；git status 干净；tracked 树与记录时完全一致。`
- E0 材料：`验证于 commit 9f1c2ab：unittest 87/87 通过，vault check 0/0。一切正常。`
- E1 材料：
  ```html
  <!-- trellium-evidence-receipt
  {
    "schema_version": 0,
    "observed_at": "2026-09-08T10:00:00Z",
    "head": "9f1c2ab",
    "tracked_tree": "t1",
    "worktree": "clean",
    "scope": ["scripts/", "init/", "vault/"],
    "excluded": ["external CI", "GitHub Releases"],
    "commands": ["python3 -m unittest scripts.test_trellium scripts.test_sync_skills scripts.test_install_sh"],
    "result": "PASS",
    "level": "PASS"
  }
  -->
  ```
- E2 材料：E1 + `comparator: tracked tree t1 == current t1 → fresh`

### 场景 B：相关代码已变化

- 事实清单：`记录基于 commit 4a7b1c0；此后 scripts/trellium.py 被修改（改动未提交，工作树 dirty）。`
- E0 材料：`验证于 commit 4a7b1c0：unittest 87/87 通过。`
- E1 材料：同结构，`head: 4a7b1c0, tracked_tree: t2, scope: ["scripts/"], level: PASS`。
- E2 材料：E1 + `comparator: tracked tree t2 != current → historical（scripts/trellium.py 内容变化）`

### 场景 C：仅无关文档变化

- 事实清单：`记录基于 commit 7c8d9e0；此后仅 docs/notes.md 增加了一段笔记，scripts/ 与 init/ 未变。`
- E0 材料：`验证于 commit 7c8d9e0：unittest 87/87 通过，vault check 0/0。`
- E1 材料：`head: 7c8d9e0, tracked_tree: t3, scope: ["scripts/"], level: PASS`。
- E2 材料：E1 + `comparator: tracked tree t3 != current（docs/notes.md 变化）→ historical`

### 场景 D：提交后内容等价

- 事实清单：`记录基于 commit aa11bb2；当前 HEAD = cc33dd4（记录后有过一次空内容变动的 rebase），tracked 树内容与记录时逐字节一致。`
- E0 材料：`验证于 commit aa11bb2：unittest 87/87 通过。`
- E1 材料：`head: aa11bb2, tracked_tree: t4, scope: ["scripts/", "init/"], level: PASS`。
- E2 材料：E1 + `comparator: head aa11bb2 不在当前历史；tracked tree t4 == current t4 → fresh（树等价）`

（其余边界——untracked 变化、PARTIAL/NOT_RUN、head 不可解析、scope 外部系统——的 golden 与比较器行为见 `scoring.md`；如需扩展 cell 再登记。）

## 投放顺序

消融比较按 E2 → E1 → E0 交叉平衡（同场景优先连续跑完三个 cell 的不同会话），每 cell 至少 1 次；不足 3 次重复时结果标 `exploratory`。
