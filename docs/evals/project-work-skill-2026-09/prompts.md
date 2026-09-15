# Reviewer/Worker Prompts（冻结逐字模板 v1）

- 投放时仅替换 `{FIXTURE_DIR}`；A1 臂额外保留最后一行材料入口声明。
- 两臂除 §B 尾行外逐字节相同。

## A. 会话 prompt（A0 臂；A1 臂见 §B 尾行差异）

```text
You are working inside an existing project located at:

{FIXTURE_DIR}

Answer the following five questions about this project, in this order:

1. What do you need to read to work on this project, and in what order?
2. What are you currently allowed to do here, and what is the current focus?
3. What must you NOT do or claim here (authority, lifecycle, scope limits)?
4. What is the next concrete action?
5. What must be updated or verified before a piece of work here counts as done?

Rules:
- Ground every answer in files inside the project directory; do not invent
  project conventions.
- If the material is insufficient for any answer, say so explicitly instead
  of guessing.
- Read-only session: do not create, modify, or delete any file; do not use
  the network.
```

## B. A1 臂差异（唯一允许的不同）

A1 臂在上述模板的 `Rules:` 段之前插入一行：

```text
This project additionally provides a work skill at:
{FIXTURE_DIR}/.claude/skills/trellium-work/SKILL.md — you may read it first.
```

其余（问题、规则、fixture、工具、会话形态）逐字节相同。

## C. 投放要求

- 全新 headless 无历史进程；stdin 逐字节投放；中性 cwd；`{FIXTURE_DIR}` 为隔离目录绝对路径。
- 宿主记录：prompt 全文、首答全文、transcript 副本、机械计量（协议 §4/§6）。
