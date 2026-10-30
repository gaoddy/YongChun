# 文档结构分册

> 文档结构的细则按范围拆分：通用文档、UI 文档与版本文档。
> 文档写作与回写流程见[文档写作](../docs-writing.md)、[文档回写](../docs-sync.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| `docs/` 目录职责、文档内部结构与索引 | [docs-structure.md](docs-structure.md) |
| `docs/product/ui/` 的落点、目录与文件职责 | [ui-docs-structure.md](ui-docs-structure.md) |
| 版本文档的目录、文件清单与生命周期 | [version-docs-structure.md](version-docs-structure.md) |

## 阅读顺序

1. 先读 [docs-structure.md](docs-structure.md)，确认目录职责、命名与内部结构。
2. 涉及 UI 文档时读 [ui-docs-structure.md](ui-docs-structure.md)，涉及版本文档时读 [version-docs-structure.md](version-docs-structure.md)。
3. 表述与状态标注按[文档写作](../docs-writing.md)，代码实现后的回写按[文档回写](../docs-sync.md)。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件、[全局索引](../../index.md)与根 `AGENTS.md` 触发表。
