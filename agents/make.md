---
name: make
description: "Make 构建入口：需要构建、测试、静态检查、生成或启动本地环境时，优先使用仓库的 `make` 入口，不手写等效命令"
effort: low
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/implementation/make.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/implementation/make.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
