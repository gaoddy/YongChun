---
name: explanation
description: "解释与讲解：需要向特定受众解释代码、概念、报错或方案，如用户说「ELI5」「解释一下」「讲给老板听」「让我妈也能听懂」，或直接点名受众"
effort: high
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/docs/explanation.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/docs/explanation.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
