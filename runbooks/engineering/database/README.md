# 数据库分册

> 数据库表的规划与 schema 变更按主题拆分；跨端主题留在 `engineering/` 分组内。
> 需求与技术方案的文档形式见[版本文档结构](../../docs/structure/version-docs-structure.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 表划分、字段、主键、关系与索引规划 | [table-design.md](table-design.md) |
| 表、字段、索引、约束与迁移变更 | [schema-change.md](schema-change.md) |

## 阅读顺序

1. 新增或调整业务对象时先读 [table-design.md](table-design.md)，确定表结构与索引。
2. 表结构确定后的落库改动与迁移执行读 [schema-change.md](schema-change.md)。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件、[全局索引](../../index.md)与根 `AGENTS.md` 触发表。
