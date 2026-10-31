---
name: sse
description: "SSE 接口：设计或调整 Server-Sent Events 接口的事件格式、重连补发、心跳与连接限制"
effort: high
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/engineering/server/api/sse.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/engineering/server/api/sse.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
