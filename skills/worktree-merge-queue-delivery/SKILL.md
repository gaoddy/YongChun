---
name: worktree-merge-queue-delivery
description: Use when a project delivers work through isolated git worktrees, queue-gated base-branch merges, and a project-local delivery config describing verify, merge, push, deploy, or upload steps.
---

# Worktree Merge Queue Delivery

## 何时使用

请求涉及创建或复用任务 worktree、通过合并队列把任务分支合入 `develop` 一类基线分支、验证后自动完成本地合并与交付交接，或跨仓库与子模块协同合并时使用。只做本地临时修改、不合并不交付的任务不使用。

## 执行

按插件根目录的 `runbooks/delivery/worktree-delivery.md` 执行，路径相对本文件为 `../../runbooks/delivery/worktree-delivery.md`。插件根目录在 Claude Code 为 `${CLAUDE_PLUGIN_ROOT}`，在 Codex 为插件安装目录（`~/.codex/plugins/cache` 下）。

runbook 规定配置字段、队列阶段、基线同步、验证矩阵、合并顺序、交接与失败处理；不要执行本文件之外的默认流程。

## 辅助脚本

同目录 `scripts/delivery_helper.py`：

```bash
python3 scripts/delivery_helper.py plan --config <配置文件> --branch <任务分支> --root <任务 worktree 绝对路径>
```

```bash
python3 scripts/delivery_helper.py run --config <配置文件> --branch <任务分支> --root <任务 worktree 绝对路径>
```

- 先执行 `plan`，确认根目录、队列步骤与基线同步 checkout 指向正确位置，再执行 `run`。
- `--root` 始终传任务 worktree 的绝对路径。
- 省略 `--repos` 时按分支差异、工作区状态与未跟踪文件自动检测仓库；`--repos`、`--no-auto-detect`、`--detected-only`、`--json` 用于覆盖或诊断。

## 输出

报告使用的配置、涉及的仓库、到达的队列阶段、本地合并的分支与 commit、清理与释放结果、manifest 路径与独立 worker 的状态。推送、部署与上传只在观察到结果时报告。
