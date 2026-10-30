---
description: 按 runbook 修复已确认的缺陷：定位根因、先写失败用例、最小修复与回归
argument-hint: <缺陷描述>
---

@runbooks/version/bugfix.md
@runbooks/problems/troubleshooting.md

按上述 runbook 修复以下缺陷：

$ARGUMENTS

执行要求：
1. 先确认缺陷不改变产品规则与对外行为；会改变的走需求变动。
2. 稳定复现并确认根因；根因未确认不开始改代码。
3. 先写失败用例，再实施最小修复。
4. 一次只修一个根因；同一根因的多处症状一并修，不同根因分开验证。
5. 修复完成后回写 `docs/` 并删除缺陷目录。

完成判定：失败用例修复前失败、修复后通过；回归点全部通过；改动范围与修复决策一致。
