---
agent:
  effort: low
---

# Runbook：Worktree 与分支

## 适用场景

- 需要修改代码、文档或配置并隔离工作区。
- 多个任务并行，或需要派发子 agent 执行。
- 只读观察、验证、回查、评审、答疑和检索不创建 worktree；创建前按[Worktree 创建时机](worktree-timing.md)判定。

## 前置读取

- [Worktree 创建时机](worktree-timing.md)

## 规则

- 基线分支为 `develop`，用户明确指定其他分支时除外；项目存在 `.yongchun/worktree-merge-queue.toml` 时以 `project.base_branch` 为准。
- 创建只走 `skills/worktree/worktree-guard/scripts/worktree_create.sh`，不直接执行 `git worktree add`；绕过入口的命令由守卫拒绝。
- worktree 根固定为 `<repo>/.worktrees/<branch 的 / 换成 ->`，该目录必须在 `.gitignore` 中忽略（`/.worktrees/`），否则创建失败。
- 分支前缀白名单为 `feature/`、`fix/`、`claude/`；队列配置存在时以 `project.branch_prefix` 为准，不在脚本外另立前缀。
- 一个任务一个 worktree 与分支；分支名与 `docs/plan/<分支名>/` 计划目录对应。
- 所有子 agent 统一使用主 agent 的 worktree：在主 agent 当前 worktree 目录内执行，不单独创建 worktree，不切换到其他目录或主仓库根目录。
- 子 agent 使用低推理强度（low），模型沿用默认；每个子 agent 只执行一个任务。
- 多个子 agent 并行时，各自只处理自己负责的文件，同一文件不并发写。
- 交付与提交统一由主 agent 在主 worktree 完成。

## 步骤

1. 按[Worktree 创建时机](worktree-timing.md)判定任务需要修改仓库文件。
2. 创建 worktree 与分支，冲突、脏工作区、基线缺失时脚本会拒绝执行：

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/worktree/worktree-guard/scripts/worktree_create.sh" <branch> [base]
```

3. 在 worktree 内完成修改与验证；计划目录见[任务执行与交付](task-delivery.md)。
4. 提交前检查 `git diff`，确认只包含任务范围内的改动。
5. 合并前删除计划目录，再合并到 `develop`。
6. 删除已合并的 worktree 与分支：

```bash
git worktree remove .worktrees/<branch 的 / 换成 -> && git branch -d <branch>
```

## 守卫

`PreToolUse` 钩子把上述规则变成门禁：`git worktree add` 只有在命令包含 `worktree_create.sh` 时放行，`list`、`prune` 放行，`remove`、`move` 等写操作要求路径解析到 `<repo>/.worktrees/` 下。

钩子随插件提供，写在插件的 `hooks/hooks.json`，命令用 `${CLAUDE_PLUGIN_ROOT}` 指向插件安装地址：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/skills/worktree/worktree-guard/scripts/worktree_guard.sh\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

- 插件以 user scope 启用，钩子对所有项目生效，无需改动 `~/.claude/settings.json`；若此前按旧方式在全局 settings 配置过守卫，删除该条，避免重复执行。
- `${CLAUDE_PLUGIN_ROOT}` 由宿主替换为实际插件根：目录源市场指向插件仓库目录，打包安装指向安装副本，两种形态都不用改路径。
- 守卫脚本依赖 `python3` 解析钩子 JSON；`python3` 不可用时放行，不阻塞其他命令。
- 钩子只覆盖 Claude Code 的工具调用，不覆盖 T3 Code 等宿主自己创建的 worktree；这类场景仍按本 runbook 由 agent 调用脚本创建。
- 排障时临时停用只能改插件钩子配置或停用插件，不在脚本里留环境变量开关。

## 验证

- 工作区干净，无未提交改动。
- 分支基于最新 `develop`，合并后无残留 worktree。
- worktree 位于 `<repo>/.worktrees/` 下，`git status` 中没有未忽略的 worktree 目录。
- 计划目录、临时文件与测试专用文件已清理。

## 相关

- [任务计划](../version/plan.md)
