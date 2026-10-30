---
description: 按 runbook 修复已确认的缺陷：定位根因、先写失败用例、最小修复与回归
argument-hint: <缺陷描述>
---

按 agent-runbook 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/version/bugfix.md`
   - `runbooks/problems/troubleshooting.md`
3. 先定位根因，再写失败用例，最后做最小修复。
4. 回归验证覆盖原缺陷路径；失败不得跳过或放宽断言。
5. 同一任务回写文档，提交前检查 `git diff`。

完成判定：失败用例先复现后通过，回归验证通过，`git diff` 只含修复范围。
