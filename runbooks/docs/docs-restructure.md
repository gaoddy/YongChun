---
agent:
  effort: xhigh
---

# Runbook：文档结构重构

## 适用场景

- 项目已有 `docs/` 目录，但目录、命名或内容归属不符合[文档结构](structure/docs-structure.md)，需要迁移与重组。
- 新建文档直接按[文档结构](structure/docs-structure.md)；本文只规定已有文档的重构流程。

## 前置读取

- [文档结构](structure/docs-structure.md)

## 规则

- 先盘点、后迁移：先产出每篇文档的目标位置与处置，再动文件；盘点完成前不删除、不覆盖。
- 只迁移、合并与拆分，不改写产品与技术结论；结论有误或缺漏时记入待确认项，按各自 runbook 处理。
- 已实现内容进 `docs/current/product/`、`docs/current/technical/`；未实现内容进 `versions/<版本>/`；进行中的草案移到 `output/drafts/`，不留在 `docs/`；流程与规则留在 runbook 仓库，不写进 `docs/`。
- 同一结论只保留一处；重复内容合并到承载文档，其余位置改为链接。
- 用 `git mv` 迁移以保留历史；一次提交只做一类处置，便于回滚。
- 无法判断归属或版本的文档先列入待确认项，不凭猜测归档。
- 重构不改变代码与产品行为，不提升版本号；完成后按[文档回写](docs-sync.md)确认状态标注。

## 步骤

1. 盘点 `docs/` 全部文件：记录路径、主题、当前状态（已实现 / 规划 / 草案 / 过程记录）与入链。
2. 对照[文档结构](structure/docs-structure.md)建立目标目录骨架，保留现有文件不动。
3. 为每篇文档标注处置：移动到目标路径、合并到某篇、拆分为多篇、删除（过程记录与重复内容）或待确认。
4. 用 `git mv` 迁移，合并重复内容，保留一份结论并更新所有入链。
5. 删除空目录与无主文档；待确认项写入 `output/drafts/` 或版本 `open-questions.md`，不留在正式文档。
6. 更新 `docs/README.md` 与各子目录 `README.md` 索引，按[文档结构](structure/docs-structure.md)校验命名、状态标注与链接。
7. 运行项目文档校验；没有校验脚本时逐项核对链接与索引。

## 验证

- `docs/` 顶层与子目录符合[文档结构](structure/docs-structure.md)，无未归类文件。
- 每篇文档有明确归属与状态标注，命名符合小写 kebab-case。
- 无死链、无孤儿文档、无重复结论。
- `versions/` 只含未实现内容，`docs/` 内没有草案与讨论记录。
- 迁移使用 `git mv`，历史可追溯；待确认项已记录。

## 相关

- [文档回写](docs-sync.md)
- [文档写作](docs-writing.md)
- [版本文档结构](structure/version-docs-structure.md)
