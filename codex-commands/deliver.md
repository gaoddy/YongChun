---
description: 按 runbook 执行任务交付：判断 worktree、写计划、实施、验证、回写与提交
argument-hint: <任务描述>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/implementation/task-delivery.md`
   - `runbooks/implementation/worktree-timing.md`
3. 只改任务范围内的文件，不扩展功能、不顺带重构。
4. 按验证矩阵执行构建、检查与测试；验证失败不得跳过或放宽断言。
5. 同一任务回写文档，提交前检查 `git diff`，合并前删除计划目录。
6. 本仓库另需运行 `python3 scripts/check-runbooks.py`。

完成判定：验证通过，`git diff` 只含任务范围，文档已回写，计划目录已清理。
