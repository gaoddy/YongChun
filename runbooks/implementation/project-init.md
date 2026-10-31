---
agent:
  effort: high
---

# Runbook：项目接入

## 适用场景

- 新项目接入本 runbook 集合，或已有项目补建声明与文档骨架。
- 项目已有自己的规则体系时，按同一方式声明引用，不从本仓库复制目录。

## 前置读取

- [runbook 编写与维护](../runbook.md)
- [文档结构](../docs/structure/docs-structure.md)

## 规则

- 项目内不复制 `runbooks/`；本仓库是 runbook 的唯一出处，项目根 `AGENTS.md` 只做声明与项目事实。
- `CLAUDE.md` 只引入 `AGENTS.md`（一行 `@AGENTS.md` 或等价写法），不重复任何规则。
- 项目 `AGENTS.md` 保留四部分：runbook 声明块、协作原则、项目阶段与兼容要求、项目事实；不复制触发表明细与 runbook 内容。
- 项目特有场景在 `AGENTS.md` 补充入口并指向本仓库对应 runbook；确需项目内独有的规则时新增单篇 runbook 并声明位置，不分叉整套目录。
- 项目事实必须覆盖 runbook 正文中出现的全部 `<...>` 取值：服务端与客户端目录、框架、入口、构建与迁移命令、接口前缀等。
- 项目使用隔离 worktree 与合并队列交付时，从[配置模板](../../templates/worktree-merge-queue.toml)复制到 `.yongchun/worktree-merge-queue.toml` 并替换占位符；不使用队列时不创建该文件。
- 项目阶段默认标记「开发阶段」；未上线前不做旧版兼容设计。
- `docs/` 骨架在项目内建立：`docs/README.md`、`docs/current/README.md`、`docs/current/product/`、`docs/current/technical/`、`docs/versions/<版本>/`，结构按[文档结构](../docs/structure/docs-structure.md)。
- Claude Code 通过公开 marketplace 使用命令层：`/plugin marketplace add gaoddy/YongChun` 后安装 `yongchun@yongchun`；本地开发可用 `claude --plugin-dir <本仓库路径>`。不复制 runbook 或命令文件到项目。

## 产品数据

项目初始化时确定产品数据并写入项目事实；缺失项向用户确认，不自行假设或留空。

| 数据 | 必须写明 | 适用 | 落点 |
| --- | --- | --- | --- |
| 产品名 | 对外名称与简称 | 全部项目 | 项目 `AGENTS.md` 项目事实 |
| 产品描述 | 一句话写明面向谁、解决什么问题 | 全部项目 | 项目 `AGENTS.md` 项目事实、首个版本 `README.md` |
| 产品形态 | 是否带客户端、是否带服务端 | 全部项目 | 项目 `AGENTS.md` 项目事实 |
| 初始版本号 | 默认 `1.0`，与首个版本目录名一致 | 全部项目 | `docs/versions/<版本>/README.md` |
| 包名 | 各端包名（如 `com.example.app`），全项目唯一且不随版本变更 | 带客户端 | 项目 `AGENTS.md` 项目事实 |
| 用户规模 | 上线后最终目标的总用户数与日活 | 带服务端 | 项目 `AGENTS.md` 项目事实 |

- 不带的端不填对应数据，也不在项目事实中保留空占位。
- 用户规模写最终目标值，不写当前值或短期目标；软件架构以该规模为容量基线演进，见[服务架构方案生成](../engineering/server/architecture-options.md)。
- 多端各有包名时逐端列出；包名与用户规模变化时更新项目事实并评估对架构的影响，不另建副本。

## 步骤

1. 确认产品数据：产品名、产品描述、产品形态；带客户端时确认包名，带服务端时确认最终用户规模。
2. 确认本 runbook 仓库的地址或本地路径，作为声明中的引用目标。
3. 在项目根写 `AGENTS.md`：runbook 声明块、协作原则、项目阶段、项目事实（含产品数据）。
4. 项目使用隔离 worktree 与合并队列交付时，复制配置模板并替换占位符；不使用时不创建。
5. 写 `CLAUDE.md`，引入 `AGENTS.md`。
6. 按文档结构建立 `docs/` 骨架与 `docs/README.md` 索引。
7. 按版本文档结构建立首个版本目录（版本号默认 `1.0`），写 `README.md` 与 `open-questions.md`。
8. 逐项核对 runbook 中的 `<...>`，把取值补入项目事实。
9. 校验声明可解析、文档骨架完整、项目内无 `runbooks/` 副本。

## 验证

- 产品名、产品描述、产品形态与初始版本号已写入项目事实与首个版本；带客户端时包名、带服务端时最终用户规模已写入，无空占位。
- 项目内不存在 `runbooks/` 副本；`AGENTS.md` 声明的仓库与 `runbooks/index.md` 可访问。
- `CLAUDE.md` 只引入 `AGENTS.md`，项目内无重复规则。
- 项目事实覆盖全部 `<...>` 取值，无占位符残留。
- 使用隔离 worktree 与合并队列交付时，`.yongchun/worktree-merge-queue.toml` 已创建且无 `<...>` 残留；不使用队列时未创建。
- `docs/` 骨架与首个版本目录符合文档结构与版本文档结构。
- 项目阶段标记为「开发阶段」。
- Claude Code 中 `/yongchun:deliver` 等命令可用；项目内无 `runbooks/`、`commands/` 或 `.claude/commands/` 副本。
