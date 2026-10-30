# Runbook：Worktree 与分支

## 适用场景

- 需要修改代码、文档或配置并隔离工作区。
- 多个任务并行，或需要派发子 agent 执行。
- 只读观察、验证、回查、评审、答疑和检索不创建 worktree；创建前按[Worktree 创建时机](worktree-timing.md)判定。

## 前置读取

- [Worktree 创建时机](worktree-timing.md)

## 规则

- 基线分支为 `develop`，用户明确指定其他分支时除外。
- 一个任务一个 worktree 与分支；分支名与版本计划目录对应。
- 子 agent 在主 agent 当前 worktree 目录内执行，不单独创建 worktree，不切换到其他目录。
- 多个子 agent 并行时，各自只处理自己负责的文件，同一文件不并发写。
- 交付与提交统一由主 agent 在主 worktree 完成。

## 步骤

1. 按[Worktree 创建时机](worktree-timing.md)判定任务需要修改仓库文件。
2. 从 `develop` 创建 worktree 与分支：`<worktree 命令>`。
3. 在 worktree 内完成修改与验证；计划目录见[任务执行与交付](task-delivery.md)。
4. 提交前检查 `git diff`，确认只包含任务范围内的改动。
5. 合并前删除计划目录，再合并到 `develop`。
6. 删除已合并的 worktree 与分支：`<清理命令>`。

## 验证

- 工作区干净，无未提交改动。
- 分支基于最新 `develop`，合并后无残留 worktree。
- 计划目录、临时文件与测试专用文件已清理。

## 相关

- [任务计划](../version/plan.md)
