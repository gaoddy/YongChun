---
description: 按 runbook 执行 UI 设计、改版与实现：方向确认、分册细化、共享层与验证
argument-hint: <UI 任务描述>
---

按 agent-runbook 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/product/ui/ui-design.md`
   - `runbooks/product/ui/README.md`
3. 先确认方向方案，再细化到分册；共享组件与 tokens 只改一处。
4. 验证覆盖浅色、深色与目标尺寸。

完成判定：方向已确认，实现与设计系统一致，多主题与多尺寸验证通过。
