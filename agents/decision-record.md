---
name: decision-record
description: "决策记录：需要记录一项今后不应被重新推翻的决策：架构形态、技术选型、边界划分、有意的偏离常规做法，或已否决的需求与方案"
effort: high
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/version/decision-record.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/version/decision-record.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
