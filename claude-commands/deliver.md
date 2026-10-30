---
description: 按 runbook 执行任务交付：判断 worktree、写计划、实施、验证、回写与提交
argument-hint: <任务描述>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/implementation/task-delivery.md
@${CLAUDE_PLUGIN_ROOT}/runbooks/implementation/worktree-timing.md

按上述 runbook 执行以下任务：

$ARGUMENTS

执行要求：
1. 先判断任务是否修改仓库文件；只读任务直接执行，不建 worktree。
2. 需要修改时从 `develop` 建 worktree 与分支，计划写到 `output/plans/<分支名>/`；项目有版本目录时写到 `docs/versions/<版本>/plans/<分支名>/`。
3. 只改任务范围内的文件，不扩展功能、不顺带重构。
4. 按验证矩阵执行构建、检查与测试；失败不得跳过或放宽断言。
5. 同一任务回写文档，提交前检查 `git diff`，合并前删除计划目录。

完成判定：验证矩阵通过、`git diff` 只含任务范围、文档已回写、计划目录已清理；本仓库另需 `python3 scripts/check-runbooks.py` 退出 0。
