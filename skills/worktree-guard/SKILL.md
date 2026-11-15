---
name: worktree-guard
description: Use when creating, removing, or validating task worktrees, or when git worktree calls must follow the project's baseline branch, branch prefix, and worktree root rules.
---

# Worktree Guard

## 何时使用

- 为任务创建隔离 worktree，或清理已合并的 worktree 与分支。
- 需要校验 worktree 是否符合基线分支、分支前缀与根目录约定。
- 需要拦截绕过唯一创建入口的 `git worktree` 调用。

创建时机与交付流程不在本文件，按插件根目录的 `runbooks/implementation/worktree.md` 执行，路径相对本文件为 `../../runbooks/implementation/worktree.md`。插件根目录在 Claude Code 为 `${CLAUDE_PLUGIN_ROOT}`，在 Codex 为插件安装目录。

## 唯一创建入口

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/worktree-guard/scripts/worktree_create.sh" <branch> [base] [--root DIR]
```

- `<branch>` 必填，需带前缀：默认白名单 `feature/`、`fix/`、`claude/`；项目存在 `.yongchun/worktree-merge-queue.toml` 时以其 `project.branch_prefix` 为准。
- `[base]` 缺省为该配置的 `project.base_branch`，再缺省为 `develop`。
- worktree 根缺省 `<repo>/.worktrees/<branch 的 / 换成 ->`，且该目录必须已被 `.gitignore` 忽略；`--root` 只用于临时排障。
- 成功时把绝对路径打印到 stdout；工作区不干净、基线不存在、前缀不符、目标已存在、目录未忽略时退出码非 0，不创建任何东西。

清理：

```bash
git worktree remove .worktrees/<branch 的 / 换成 -> && git branch -d <branch>
```

## 守卫

`scripts/worktree_guard.sh` 供 Claude Code 的 `PreToolUse` 钩子调用，从 stdin 读取钩子 JSON：

- `git worktree add`：仅当命令包含 `worktree_create.sh` 时放行，其余一律 `permissionDecision: deny`。
- `git worktree list`、`git worktree prune`：放行。
- `git worktree remove|move|repair|lock|unlock`：命令中的路径必须解析到 `<repo>/.worktrees/` 下，否则拒绝。

全局 `~/.claude/settings.json` 的配置见 `runbooks/implementation/worktree.md` 的「守卫」小节。

## 测试

```bash
python3 -m unittest discover -s skills/worktree-guard/scripts
```
