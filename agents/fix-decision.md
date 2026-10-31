---
name: fix-decision
description: "修复决策：排查已确认根因，需要决定修在哪一层、改哪一端、修到什么程度"
effort: xhigh
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/problems/fix-decision.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/problems/fix-decision.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
