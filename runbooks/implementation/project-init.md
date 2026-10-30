# Runbook：项目接入

## 适用场景

- 新项目接入本 runbook 集合，或已有项目补建声明与文档骨架。
- 项目已有自己的规则体系时，按同一方式声明引用，不从本仓库复制目录。

## 前置读取

- [根规则](../../AGENTS.md)
- [runbook 编写与维护](../runbook.md)
- [文档结构](../docs/structure/docs-structure.md)
- [版本文档结构](../docs/structure/version-docs-structure.md)

## 规则

- 项目内不复制 `runbooks/`；本仓库是 runbook 的唯一出处，项目根 `AGENTS.md` 只做声明与项目事实。
- `CLAUDE.md` 只引入 `AGENTS.md`（一行 `@AGENTS.md` 或等价写法），不重复任何规则。
- 项目 `AGENTS.md` 保留四部分：runbook 声明块、协作原则、项目阶段与兼容要求、项目事实；不复制触发表明细与 runbook 内容。
- 项目特有场景在 `AGENTS.md` 补充入口并指向本仓库对应 runbook；确需项目内独有的规则时新增单篇 runbook 并声明位置，不分叉整套目录。
- 项目事实必须覆盖 runbook 正文中出现的全部 `<...>` 取值：服务端与客户端目录、框架、入口、构建与迁移命令、接口前缀等。
- 项目阶段默认标记「开发阶段」；未上线前不做旧版兼容设计。
- `docs/` 骨架在项目内建立：`docs/README.md`、`docs/product/`、`docs/technical/`、`docs/versions/<版本>/`，结构按[文档结构](../docs/structure/docs-structure.md)。

## 步骤

1. 确认本 runbook 仓库的地址或本地路径，作为声明中的引用目标。
2. 在项目根写 `AGENTS.md`：runbook 声明块、协作原则、项目阶段、项目事实。
3. 写 `CLAUDE.md`，引入 `AGENTS.md`。
4. 按文档结构建立 `docs/` 骨架与 `docs/README.md` 索引。
5. 按版本文档结构建立首个版本目录，写 `README.md` 与 `open-questions.md`。
6. 逐项核对 runbook 中的 `<...>`，把取值补入项目事实。
7. 校验声明可解析、文档骨架完整、项目内无 `runbooks/` 副本。

## 验证

- 项目内不存在 `runbooks/` 副本；`AGENTS.md` 声明的仓库与 `runbooks/index.md` 可访问。
- `CLAUDE.md` 只引入 `AGENTS.md`，项目内无重复规则。
- 项目事实覆盖全部 `<...>` 取值，无占位符残留。
- `docs/` 骨架与首个版本目录符合文档结构与版本文档结构。
- 项目阶段标记为「开发阶段」。
