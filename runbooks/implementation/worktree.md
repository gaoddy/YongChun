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
- 开工后在首次回复中用一行说明当前 worktree 的绝对路径与分支；路径与分支不符时先纠正再动手，不在主仓库或其他 worktree 中修改。
- 创建只走 `skills/worktree/worktree-guard/scripts/worktree_create.sh`，不直接执行 `git worktree add`；绕过入口的命令由守卫拒绝。
- worktree 根固定为 `<repo>/.worktrees/<branch 的 / 换成 ->`，该目录必须在 `.gitignore` 中忽略（`/.worktrees/`），否则创建失败。
- 本仓库同时是 Claude Code 插件的本地目录市场来源，市场同步按插件根目录整目录复制，`.worktrees/` 会被一起复制进插件缓存；刷新后由 `scripts/clean-plugin-cache.sh` 清理，见[版本发布](../delivery/version-release.md#本仓库插件发版)。worktree 仍只放在根目录 `.worktrees/` 下。
- 分支前缀白名单为 `feature/`、`fix/`、`claude/`；队列配置存在时以 `project.branch_prefix` 为准，不在脚本外另立前缀。
- 一个任务一个 worktree 与分支；分支名与 `docs/plan/<分支名>/` 计划目录对应。
- 所有子 agent 统一使用主 agent 的 worktree：在主 agent 当前 worktree 目录内执行，不单独创建 worktree，不切换到其他目录或主仓库根目录。
- 子 agent 使用低推理强度（low），模型沿用默认；每个子 agent 只执行一个任务。
- 多个子 agent 并行时，各自只处理自己负责的文件，同一文件不并发写。
- 交付与提交统一由主 agent 在主 worktree 完成。

## 步骤

1. 按[Worktree 创建时机](worktree-timing.md)判定任务是否需要隔离：只读任务与[小改动](worktree-timing.md)直接在当前分支执行，不创建 worktree。
2. 需要隔离时创建 worktree 与分支，冲突、脏工作区、基线缺失时脚本会拒绝执行：

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/worktree/worktree-guard/scripts/worktree_create.sh" <branch> [base]
```

3. 在 worktree 内完成修改与验证；计划目录见[任务执行与交付](change-delivery.md)。
4. 提交前检查 `git diff`，确认只包含任务范围内的改动。
5. 合并前按[任务计划](../version/plan.md)清理计划目录，再合并到 `develop`。
6. 删除已合并的 worktree 与分支：

```bash
git worktree remove .worktrees/<branch 的 / 换成 -> && git branch -d <branch>
```

7. 运行收尾清单，确认没有残留的任务 worktree 与已合并分支：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/worktree/worktree-guard/scripts/worktree_cleanup.py" --check
```

- 脚本输出任务 worktree 与已合并任务分支；存在残留时退出码为 1，逐项清理后重跑。
- 未合并的 worktree 与分支会列在输出中但不阻断，按任务是否需要继续保留处理。

## 守卫

`PreToolUse` 钩子把上述规则变成门禁：`git worktree add` 只有在命令包含 `worktree_create.sh` 时放行，`list`、`prune` 放行，`remove`、`move` 等写操作要求路径直接位于 `<repo>/.worktrees/` 下。

- 仓库根按目标路径所属的主仓库判定（`git rev-parse --git-common-dir`），在 worktree 内执行同样按主仓库的 `.worktrees/` 校验，不受当前目录影响。
- 目标路径不存在或不属于任何仓库时，退回当前目录所属仓库判定；两者都无法定位时放行，不阻塞命令。
- 只放行 `.worktrees/` 的直接子目录；解析到 `.worktrees/` 之下的嵌套目录仍拒绝。

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

- 首次回复已说明 worktree 绝对路径与分支，改动只发生在该路径内。
- 工作区干净，无未提交改动。
- 分支基于最新 `develop`，合并后无残留 worktree。
- worktree 位于 `<repo>/.worktrees/` 下，`git status` 中没有未忽略的 worktree 目录。
- 本仓库刷新插件后，`~/.claude/plugins/cache/<插件>/<插件>/<版本>/` 下没有 `.worktrees/`。
- 计划目录、临时文件与测试专用文件已清理。
- 收尾清单 `worktree_cleanup.py --check` 退出码为 0，未列出任务 worktree 或已合并的任务分支。

## 相关

- [任务计划](../version/plan.md)
