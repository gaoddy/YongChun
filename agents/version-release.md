---
name: version-release
description: "版本发布：版本收尾后执行正式发版，完成合并 `main`、打 tag、发布产物与发版后核对"
effort: xhigh
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/delivery/version-release.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/delivery/version-release.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
