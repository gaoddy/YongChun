# Runbook：Worktree 合并队列交付

## 适用场景

- 项目用隔离 worktree 开发，并通过共享合并队列把任务分支合入基线分支。
- 项目已实现本文件约定的 make 目标与交付配置文件。
- 本仓库自身不适用：只有 `develop` 与 `main`，没有队列、部署与上传。

## 前置读取

- [任务执行与交付](../implementation/task-delivery.md)
- [Worktree 与分支](../implementation/worktree.md)

## 规则

### 配置

- 配置文件放在项目根：优先 `.agent-runbook/worktree-merge-queue.toml`，同时识别 `.codex/worktree-merge-queue-delivery.toml`；`--config` 显式指定时以参数为准。
- 配置缺失时停止，先创建配置或改为手工交付，不凭默认值执行。
- 分支前缀只由 `project.branch_prefix` 提供，不在脚本或文档中写死。
- 接入时从[配置模板](../../templates/worktree-merge-queue.toml)复制，替换全部 `<...>` 并删除未启用段；模板本身不参与运行。

| 字段 | 作用 |
| --- | --- |
| `project.name` | 配置标识 |
| `project.base_branch` | 合并目标分支，如 `develop` |
| `project.branch_prefix` | 任务分支前缀 |
| `worktree.create` / `clean` / `list` / `verify` | 任务 worktree 的创建、清理、列出与校验命令 |
| `queue.enabled` | 是否启用合并队列 |
| `queue.status` / `enqueue` / `claim` / `require_active` | 队列状态、入队、认领与占用校验 |
| `queue.advance` / `require_stage` / `drop` | 阶段推进、阶段校验与出队 |
| `queue.stages` | 只覆盖验证与本地集成的阶段名 |
| `queue.release_after_merge` | 记录本地合并完成并释放占位；接受 `{branch}`、`{base_branch}`、`{commit}`、`{manifest}` |
| `post_merge.enqueue` | 接收 `{manifest}` 的独立交付入口，必须幂等 |
| `delivery.merge_base` / `push_commit` | 基线分支合并与按 commit 推送 |
| `repos[].name` / `path` / `role` / `needs` | 仓库标识、根相对路径、角色与依赖顺序 |
| `repos[].verify` / `sdk_generate` | 任务 checkout 内的验证与生成命令 |
| `repos[].merge_base` / `push_base` | 是否合并到基线、是否推送基线分支 |
| `repos[].deploy` / `upload` / `post_delivery_checks` | 只由独立 worker 执行的交付命令 |

- 命令模板占位符：`{branch}`、`{base_branch}`、`{stage}`、`{repo_path}`、`{commit}`、`{manifest}`；`{manifest}` 由 helper 按 shell 参数引用，模板中不再加引号。

### 队列

- 队列按入队顺序先进先出，同一时刻只有一个占位。
- `enqueue` 对已入队分支是空操作，`run` 会再次调用它。
- 未认领不得合并基线、推送、部署或上传；认领失败即停止。
- 占位只覆盖基线同步、验证、子仓与根仓本地合并、交接记录、清理与释放。
- 释放后立即允许下一项认领，不等待推送、部署、上传或回读。
- 已在队列中的任务被中断时，保留占位并记录最后完成的步骤，不重跑完整 `run`。

### 基线同步与验证

- 认领后先同步根仓，再按配置顺序同步子仓；已包含基线顶端的干净分支不重复 rebase。
- 同步只使用本地基线分支，不隐式 `fetch` 或 `pull`；需要远端协同时按项目的队列规程单独处理。
- 同步产生冲突时停止，不自动 stash、跳过提交或强制合并。
- 每个改动仓库先跑定向验证，再跑全量验证；任一失败立即停止，不提交、不合并、不推送该仓库。
- 每次合并前校验记录的基线与任务 commit 未变、分支正确、工作区干净；不一致即停止并检查队列归属。

### 合并顺序

- 子仓按配置顺序与 `needs` 依赖先合并，根仓最后合并。
- 根仓任务分支在所有子仓合并完成后提交，使子模块指针指向最终集成结果。
- `merge_base` 使用快进合并；基线或任务分支被队列外的写入推进时停止，不回退、不覆盖。

### 交接与独立交付

- 根仓合并后，helper 把 manifest 写入共享 Git 目录的 `delivery-jobs/<id>.json`，记录每个仓库的来源路径、合并 commit 与已渲染的交付命令。
- manifest 状态从 `awaiting-release` 开始，队列释放成功后变为 `ready`；worker 不消费未释放的任务。
- 清理任务 worktree、释放占位、提交 handoff 都从基线 checkout 执行，不依赖已删除的任务目录。
- 独立 worker 按 `{commit}` 取独立 checkout 或产物执行命令，不复用会移动的基线工作区。
- 推送使用记录的确切 SHA，不加 force；远端已有更新的后代时先确认祖先关系。
- 同一环境的部署串行执行或做代数校验，旧任务不得覆盖新结果；重试只复用同一 manifest，不重新合并。

### 失败处理

- 失败即停止的环节：worktree 创建或校验、入队与认领、验证、提交、基线合并、任务清理、handoff 记录与队列释放。
- 停止时报告失败命令、已合并或已推送的仓库、队列项是否仍占用，不清理未完成合并的任务。
- 清理失败时先完成清理再释放，不重复合并、不强制删除。
- 推送、部署、上传失败属于独立 worker，不阻塞也不重新占用已释放的队列。

## 步骤

1. 读取配置，确认 `base_branch`、`branch_prefix`、仓库顺序与队列命令。
2. 复用或创建任务 worktree，运行 `worktree.verify`。
3. 任务完成后入队，等待前序任务结束并读取队列状态。
4. 成为队首后执行 `run`，由它完成入队、认领与基线同步。
5. 按仓库顺序执行验证，全部通过后先合并子仓、最后合并根仓。
6. 记录合并 commit 与交付命令到 manifest，清理任务 worktree。
7. 从基线 checkout 释放队列占位，再提交 handoff。
8. 由独立 worker 在记录 commit 上执行推送、部署与上传，并回报各自结果。

辅助脚本（插件内路径）：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/worktree-merge-queue-delivery/scripts/delivery_helper.py" plan \
  --config <配置文件> --branch <任务分支> --root <任务 worktree 绝对路径>
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/worktree-merge-queue-delivery/scripts/delivery_helper.py" run \
  --config <配置文件> --branch <任务分支> --root <任务 worktree 绝对路径>
```

- 先跑 `plan`，确认输出的根目录、队列步骤与基线同步 checkout 指向正确位置。
- 省略 `--repos` 时按分支差异、工作区状态与未跟踪文件自动检测仓库；`--repos`、`--no-auto-detect`、`--detected-only`、`--json` 用于覆盖或诊断。

## 验证

- 配置字段齐全，`queue.release_after_merge` 与 `post_merge.enqueue` 存在且不接受部署完成作为前提。
- 队列按 FIFO 串行，任一时刻只有一个占位；释放后下一项可立即认领。
- 验证在认领与基线同步之后执行，失败即停，未验证的仓库没有合并或推送。
- 子仓先于根仓合并，根仓提交包含最终子模块指针。
- manifest 记录精确 commit，worker 使用独立 checkout，推送无 force。
- 任务 worktree 已清理，队列已释放，worker 结果与合并结果分别报告。
- 异常路径报告失败命令、已合并范围与队列状态。

## 相关

- [服务端发布](server-deploy.md)
- [客户端发布](client-release.md)
- [任务计划](../version/plan.md)
