---
agent:
  effort: high
---

# Runbook：项目初始化

## 适用场景

- 新项目建立时初始化开发工作空间：声明 runbook、建 `docs/` 骨架与首个版本目录。
- 已有项目补建声明与文档骨架。
- 产品定义收集不属于本文，见[产品初始化](../product/product-init.md)；项目已有自己的规则体系时，按同一方式声明引用，不从本仓库复制目录。

## 前置读取

- [runbook 编写与维护](../runbook.md)
- [文档结构](../docs/structure/docs-structure.md)

## 规则

- 项目内不复制 `runbooks/`；本仓库是 runbook 的唯一出处，项目根 `AGENTS.md` 只做声明与项目事实。
- `CLAUDE.md` 只引入 `AGENTS.md`（一行 `@AGENTS.md` 或等价写法），不重复任何规则。
- 项目 `AGENTS.md` 保留四部分：runbook 声明块、协作原则、项目阶段与兼容要求、项目事实；不复制触发表明细与 runbook 内容。
- 项目特有场景在 `AGENTS.md` 补充入口并指向本仓库对应 runbook；确需项目内独有的规则时新增单篇 runbook 并声明位置，不分叉整套目录。
- 产品数据由[产品初始化](../product/product-init.md)确定后写入项目事实；本 runbook 不重新收集产品数据，缺失项不自行假设或留空。
- 项目事实必须覆盖 runbook 正文中出现的全部 `<...>` 与 `{{...}}` 取值：服务端与客户端目录、框架、入口、构建与迁移命令、接口前缀等。工程数据不向用户提问：慢命令阈值默认 `120s`；测试入口在首个需求实施时按[Make 构建入口](../implementation/make.md)登记。
- 项目使用隔离 worktree 与合并队列交付时，从[配置模板](../../templates/worktree-merge-queue.toml)复制到 `.yongchun/worktree-merge-queue.toml` 并替换占位符；不使用队列时不创建该文件。是否使用不向用户提问，用户要求时再配置。
- 项目阶段默认标记「开发阶段」；未上线前不做旧版兼容设计。
- 带客户端时项目事实登记 UI 主题范围：深浅色两套写「深浅色」，单主题写明具体主题（仅浅色或仅深色）；单主题声明同步写入项目 UI 文档 `README.md` 的「主题与使用方式」。
- 初始版本号默认 `0.0.1`，与首个版本目录名一致。
- `docs/` 骨架在项目内建立：`docs/README.md`、`docs/current/README.md`、`docs/current/product/`、`docs/current/technical/`、`docs/requirements/README.md`、`docs/versions/<版本>/`，结构按[文档结构](../docs/structure/docs-structure.md)。
- Claude Code 通过公开 marketplace 使用命令层：`/plugin marketplace add gaoddy/YongChun` 后安装 `yongchun@yongchun`；本地开发可用 `claude --plugin-dir <本仓库路径>`。不复制 runbook 或命令文件到项目。

## 步骤

1. 确认本 runbook 仓库的地址或本地路径，作为声明中的引用目标。
2. 核对产品数据是否齐全：按项目事实逐项检查产品名、产品描述、产品形态，以及带服务端时的用户规模、带客户端时的客户端平台与包名、功能列表；有缺失或未定项时先走[产品初始化](../product/product-init.md)补齐，不自行填值。
3. 在项目根写 `AGENTS.md`：runbook 声明块、协作原则、项目阶段、项目事实（含产品数据、UI 主题范围与慢命令阈值 `120s`）；产品数据取自产品初始化草稿 `output/drafts/product-init.md` 或已有文档。
4. 写 `CLAUDE.md`，引入 `AGENTS.md`。
5. 按文档结构建立 `docs/` 骨架与 `docs/README.md` 索引，含需求总表与分类代码表。
6. 按版本文档结构建立首个版本目录 `docs/versions/0.0.1/`，写 `README.md`（含产品描述与功能列表）与 `open-questions.md`（承接产品初始化草稿中的未定项）。
7. 用户要求隔离 worktree 与合并队列时，复制配置模板并替换占位符；未要求时不创建。
8. 逐项核对 runbook 中的 `<...>` 与 `{{...}}`，把取值补入项目事实；产品数据取自产品初始化结论。把产品初始化草稿的分项落盘到项目事实、首个版本 `README.md`、版本 `product/`、需求总表与逐个需求文档以及 `open-questions.md`，落盘后删除 `output/drafts/product-init.md`。
9. 校验声明可解析、文档骨架完整、项目内无 `runbooks/` 副本。

## 验证

- 产品名、产品描述、产品形态与初始版本号已写入项目事实与首个版本；带客户端时客户端平台与包名、带服务端时最终用户规模取自产品初始化结论，已写入且无空占位。
- 首个版本功能列表已写入 `docs/versions/0.0.1/README.md`；未定项已在 `open-questions.md`，无自行假设。
- 产品初始化草稿已落盘并删除（若曾存在）。
- 带客户端时 UI 主题范围已写入项目事实；单主题项目已同步写入项目 UI 文档 `README.md` 的「主题与使用方式」。
- 初始化过程未向用户询问测试入口等工程数据；项目事实中慢命令阈值已写默认值 `120s`。
- 项目内不存在 `runbooks/` 副本；`AGENTS.md` 声明的仓库与 `runbooks/index.md` 可访问。
- `CLAUDE.md` 只引入 `AGENTS.md`，项目内无重复规则。
- 项目事实覆盖全部 `<...>` 与 `{{...}}` 取值，无占位符残留。
- 使用隔离 worktree 与合并队列交付时，`.yongchun/worktree-merge-queue.toml` 已创建且无 `<...>` 残留；不使用队列时未创建。
- `docs/` 骨架与首个版本目录符合文档结构与版本文档结构。
- `docs/requirements/README.md` 已建立，表头为「编号、需求、状态、实现版本、待定夺、需求文档」，开头含类型与模块的分类代码表。
- 首个版本功能已在需求总表登记，每个功能有对应需求文档，实现版本为「待定」或已确定版本。
- 项目阶段标记为「开发阶段」。
- Claude Code 中 `/yongchun:deliver` 等命令可用；项目内无 `runbooks/`、`commands/` 或 `.claude/commands/` 副本。
