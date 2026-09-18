以下回答仅基于你给出的现场材料（fixture-b 树的描述、两段 git status 输出、adopt 逐字输出、Skill 接入相关段落），未执行任何命令、未读取其他内容。

## 1. 当前能否声称"接入完成"

**不能声称完整意义上的"接入完成"，只能说"脚本的 adopt 步骤已正常结束"。** 依据：

- Skill 明确"Agent 语义迁移在脚本之上叠加"。脚本只完成了文件落盘（changed: 11）；而"既有项目接入"清单中属于 Agent 的语义步骤没有完成证据：
  - 在 `vault/project.md` 记录"这是既有项目接入"；
  - 在 `vault/runtime.md` 记录接入状态、风险和下一步；
  - 若已有 `vault/tasks/`（本次已由脚本创建 README.md，说明目录已存在），创建或更新任务文件承接任务契约；
  - 合并既有 Agent 入口规则——而输出是 `create <target>/AGENTS.md`（新建语义），如果项目此前已有入口文件，需核对既有规则是否被保留而非覆盖。
- 验收未做：未运行 `check`（只读校验策略块、状态块、runtime 投影一致性、热文件预算、TASK storage 与 Git 实际状态）。
- 存在一个未决的 durable 性疑点（见下），必须由用户裁决后才能说"可交付"。

另有一处需要向用户如实点出的矛盾：脚本报告 changed: 11，但 `git status --porcelain` 为空，而 `--ignored` 只列出 `vault/decisions/`、`vault/details/`、`vault/tasks/`。这只有两种自洽解释：这 11 个文件已被跟踪且内容与 HEAD 一致（幂等重放/已提交），或该 porcelain 并非在接入目标根目录执行。无论哪种，"已写入"不等于"已固化"，需要 check 与 git 层面确认。

## 2. 哪些文件必须 durable

判据：fresh clone 后必须能恢复协作规则与项目状态、且是脚本声明"对脚本只读、永不被模板替换"的项目数据。

必须 durable：
- 协作层全部 11 个文件：`AGENTS.md`、`vault/index.md`、`vault/governance.md`、`vault/decisions.md`、`vault/handoff.md`、`vault/parked.md`、`vault/collaboration.md`、`vault/project.md`、`vault/runtime.md`、`vault/tasks/README.md`、`skills/agent-task/SKILL.md`；
- 记忆数据目录 `vault/tasks/`（任务文件及其 `trellium-task-state` 状态块）、`vault/decisions/`、`vault/details/`——check 的校验项"TASK storage 与 Git 实际状态""runtime 任务行与状态块投影一致性"意味着任务与状态必须与 Git 一致；
- `vault/.agent-init.json`（协议版本戳，升级判断与 baseline 判断的唯一依据；本次 create 列表中没有它，需确认其存在且被跟踪）。

不必 durable：脚本缓存 `~/.cache/trellium/`、Skill 包自带的脚本与模板等可再生产物。

## 3. local 模式下的私有 / 公开边界

- 保持私有（可被忽略）：`vault/tasks/` 任务明细、`vault/decisions/`、`vault/details/`——即只在本机有意义的工作明细。代价是 fresh clone 后这些文件缺失：runtime 行指向的任务文件不存在时报 clone-safe warning，**且不授予授权**；因此已关闭的 local 任务不得保留 runtime 行。
- 仍必须公开（入库）：入口与策略层——`AGENTS.md`、`skills/agent-task/SKILL.md`、`vault/index.md`（含 trellium-policy 策略块）、`governance.md`、`decisions.md`（长期决定）、`handoff.md`、`parked.md`、`collaboration.md`、`project.md`、`runtime.md`、`.agent-init.json`。标准是"别人 clone 后能读懂规则与当前状态"。
- 当前 `--ignored` 输出显示三个数据目录已被忽略，这与 local 模式一致；**但材料中没有本项目选择 local 模式的任何证据**，这一模式归属必须向用户确认。若项目意图是共享/durable，则当前忽略规则就是接入缺陷，`vault/tasks/README.md` 虽已创建也永远不会入库。

## 4. 下一步最小动作（按顺序）

1. 按脚本 next 指示读取 `AGENTS.md`、`vault/index.md`、`vault/runtime.md`（Level B/C 工作前再读 `vault/golenance.md` 全文，应为 `governance.md`）。
2. 向用户报告：adopt 正常结束、11 个文件、按数据保护边界未触碰项目数据；同时报告唯一疑点（三个数据目录被忽略 + porcelain 为空），请用户裁决项目模式是 local 还是共享/durable。
3. 若为共享/durable：经用户明确授权后修改忽略规则，把 `vault/decisions/`、`vault/details/`、`vault/tasks/`（含 README.md）纳入版本控制——改动忽略规则触及版本控制行为，不属于可自动执行的范围。
4. 运行 `python3 trellium.py check <target>`（完全只读，可加 `--format json`）确认最小状态层、TASK storage 与 Git 状态一致；warning 必须如实显示，不存在无条件 PASS。
5. 完成 Agent 语义收尾：`vault/project.md` 写明既有项目接入、`vault/runtime.md` 写接入状态/风险/下一步、长期选择（含模式与忽略策略的决定）写入 `vault/decisions.md`，并把任务契约落成 `vault/tasks/` 下的任务文件。
6. 用户确认提交范围后，一次性提交 durable 文件。

## 5. 是否需要自动执行 commit/push

**不需要，也不应自动执行。**

- 材料中没有任何一步授予 commit/push 授权：脚本输出只到 "changed: 11" 和 next 指示为止；Skill 的授权边界始终是"没有用户明确授权不修改……"与升级流程"用户逐条确认"，版本控制操作同样落在用户授权之内。
- 当前存在一个必须由用户决策的分叉（local 还是 durable）。在分叉解决前自动 commit，会把有疑点的状态固化进历史；若之后判定数据目录应入库，还需补改 ignore、补 add，产生返工。
- 实际上当前 porcelain 为空，说明已跟踪文件层此刻没有待提交内容；真正待决的是被忽略目录的入库策略，这只能由用户裁定。
- push 影响共享远端，风险高于 commit，更不应在验收（check 通过、语义记录完成）之前自动进行。正确姿势是：报告事实 + 列出待决项 + 请示，而不是替用户提交。

（核对对象目录：<host>/docs/evals/adoption-durability-2026-09/materials/fixture-b）
