---
name: bugfix
description: "缺陷修复：已确认是不改变产品规则的缺陷，需要完成修复、验证与收尾"
effort: high
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/version/bugfix.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/version/bugfix.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
