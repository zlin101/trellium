# TASK-0007 - Review Ledger

## Round 1（独立 Agent review，2026-09-09）

审查人：独立 GLM 会话（只读），对照 `docs/superpowers/plans/2026-09-09-local-task-lifecycle-glm-plan.md` 第 10 节十问与提交 2a17e53..c09cab2。

### 十问结论

全部通过：原始 local 设计保留（无发布系统）；disposition 仅为人工 gate（checker 不解析、非第二事实源）；W0/W1/W2 按冻结顺序执行且同效取小（tracked `not_applicable`、superseded 不受阻）；missing local warning 三层文案齐备且 fail closed；closed local row 稳定报错含可执行修复；tracked/policy-missing 旧行为零退化（测试纯新增）；checker 仍只读、确定性、标准库；无 .gitignore/untrack/tag/Release/CI 权限改动；MIGRATIONS、双语、分发快照一致（sync --check in sync）；无凭据/隐私问题。自查：136 tests OK（当时含重复执行，见 R3）、check 0/0、sync in sync、diff-check clean。

### Findings

- F1 · fixed · W 组原始证据（首答原文、材料 bytes、纠正数）未按预注册归档 · 已补入 `vault/details/task-0007-w-group-records.md`（9 份逐字首答 + 材料 bytes + 纠正数 0 + Gate 裁决）
- F2 · fixed · "C0/预注册先于实现"的提交级证据 · owner round-2 复核裁认：f98d302（预注册+M0）在 Git DAG 中先于全部实现提交，顺序有提交级证据；仅 C0 的实际运行时刻无独立提交，但其结果与旧代码行为完全吻合且可重放（重放脚本见下方 Round 2 附录）· 流程规则保留：今后预注册与基线记录先于实现独立提交
- F3 · fixed · 基线测试数记录为 87/87，reviewer 实测 bf3f84b 为 124 · 根因查明：`LocalProjectionTest(VaultCheckTest)` 继承重跑了全部 37 个父类测试，且`unittest` 计数含该重复——87 是 TASK-0007 起点时的真实三模块合计（76+5+6），124 是继承重跑后的虚增值 · 已重构为 `VaultCheckMixin` 消除继承重跑，真实口径：基线 87（76+5+6）→ 现全量 99（88+5+6，含新增 12 项聚焦测试），既有测试零退化

### 结论（Round 1）

R1 已修复；F3 已修复；F2 经 owner round-2 裁认转为 fixed（见下）。

## Round 2（owner review，REQUEST_CHANGES，2026-09-09）

- R1 · fixed · W 组裁决违反冻结 Gate（Case3 n=1、归档不全即声称 W1≡W2）· 仅 Case3 复跑：W1/W2 各 3 个独立会话，完整存档输入/scoring/首答/session id（`vault/details/task-0007-w-group-records.md` Case3 复跑节）；复跑结果两载体核心判断无差异、W2 0/3 提及废止类终态 → 按冻结 Gate 保留 W1，实测裁决非事后解释
- R2 · fixed · 下发模板未完整同步（zh/en governance、两套 index、两套 handoff 缺 local 语义；sync --check 不校验人工模板）· 六套模板全部补齐；新增 `LocalTemplateSemanticsTest` rendered-content 测试（6 项断言防再漏）
- R3 · fixed · `unittest.main()` 位于 LocalProjectionTest 之前，直接运行文件漏掉新增测试 · 已移至文件末尾；修正后直接运行 95 项、三模块 106 项（含 R4 顺序测试追加后的最终口径）
- R4 · fixed · duplicate row 的 freshness/closed 分类依赖行顺序 · 重复 TASK 现只报 `TASK_RUNTIME_DUPLICATE`、跳过 freshness/closed 推断（scripts/trellium.py resolve 入口）；正反顺序测试通过（均仅 DUPLICATE）
- R5 · fixed · runtime Recent Changes 新旧矛盾行；F2 状态非标准 · 矛盾行已改写为当前事实；F2 经 owner 裁认（DAG 顺序 + C0 可重放）转 fixed，重放脚本如下

### Round 2 附录：C0 重放脚本

```bash
# 以任意 <commit>=bf3f84b^ 之前的 09.3 checker 重放（或当前 checker 观察 C2 行为）
# fixture：local policy + runtime 指向不存在的 open TASK（TASK-9001），无任务文件
d=$(mktemp -d); mkdir -p $d/vault/tasks
cat > $d/vault/index.md <<'P'
# Vault Index

<!-- trellium-policy
{
  "schema_version": 1,
  "task_storage": "local"
}
-->
P
cat > $d/vault/runtime.md <<'R'
# Runtime Context

## Focus

- TASK-9001

## Active Tasks

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| TASK-9001 | do thing | active | next |
R
python3 scripts/trellium.py check $d --format json; echo "exit=$?"
# 09.3 预期（C0）：TASK_RUNTIME_MISSING error ×2（row+focus），exit 2
# 2026.09.4 预期（C2）：TASK_RUNTIME_LOCAL_UNRESOLVED warning ×1（去重），exit 0
```

### 结论（Round 2）

R1-R5 全部修复；W 组 Case3 复跑后裁决不变（保留 W1 单行）。等待增量 review 与 owner accepted。
