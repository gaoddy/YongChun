# 客户端分册

> 客户端的分层、方案设计与运行按主题拆分；UI 细则见 `product/ui/` 分册。
> 文档落点与形式见 [UI 文档结构](../../docs/structure/ui-docs-structure.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 页面、状态、数据源与共享层分层 | [layering.md](layering.md) |
| 客户端技术方案设计，包括状态与数据驱动 | [design.md](design.md) |
| 运行、构建参数、联调与实机验证 | [runtime.md](runtime.md) |
| UI 设计、实现与评审 | [../../product/ui/ui-design.md](../../product/ui/ui-design.md) |

## 阅读顺序

1. 先读 [layering.md](layering.md)，确认页面、状态与数据源的分层与依赖方向。
2. 设计技术方案时读 [design.md](design.md)；涉及界面时再读 [UI 设计](../../product/ui/ui-design.md)。
3. 本地运行与实机验证读 [runtime.md](runtime.md)。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件、[全局索引](../../index.md)与根 `AGENTS.md` 触发表。
