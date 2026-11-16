---
name: realtime-frame-sync
description: "实时对战帧同步架构：设计固定 tick、确定性输入广播、需要回放复现的实时对战服务端架构"
effort: xhigh
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/engineering/server/architecture/realtime-frame-sync.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/engineering/server/architecture/realtime-frame-sync.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
