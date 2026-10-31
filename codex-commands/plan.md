---
description: 按 runbook 编写任务计划：阶段顺序、任务拆分与文件边界
argument-hint: <版本或任务范围>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/version/plan.md`
   - `runbooks/docs/structure/version-docs-structure.md`
3. 阶段顺序固定：产品确认、技术确认、任务拆分，前一阶段未确认不进入下一阶段。
4. 每个任务写清输入、产出、文件边界与验证方式；并行任务不得写同一文件。

完成判定：计划文件结构正确，任务可独立验证，文件边界清晰。
