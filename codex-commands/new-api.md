---
description: 按 runbook 新增或修改 HTTP 接口：契约、分层、生成、测试与文档
argument-hint: <接口变更描述>
---

按 agent-runbook 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/engineering/new-api.md`
   - `runbooks/engineering/server/layering.md`
3. 契约先行：请求、响应、错误码与鉴权写清楚再实现。
4. 生成命令无差异，端到端测试覆盖新增路径。
5. 同一任务回写接口文档。

完成判定：契约与实现一致，生成无差异，端到端测试通过。
