# UI 分册

> UI 设计的细则按主题拆分，规则按任务类型生效，不按目录生效。
> 任务流程、方向选择与交付检查的入口见 [UI 设计](ui-design.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 任务流程与交付检查 | [../ui-design.md](ui-design.md) |
| 三种方向方案的写法与约束 | [directions.md](directions.md) |
| 设计系统与公共 UI 的落地 | [design-system.md](design-system.md) |
| 主题、深浅色与视觉资源 | [theme.md](theme.md) |
| 页面结构、状态与适配 | [pages.md](pages.md) |
| 组件拆分、接口与扩展 | [components.md](components.md) |
| 设计 tokens | [tokens.md](tokens.md) |
| 图标 | [icons.md](icons.md) |
| 交互、反馈与无障碍 | [interaction.md](interaction.md) |
| 数据、状态与刷新 | [客户端方案设计](../../engineering/client/design.md#数据驱动界面) |
| UI 文档的落点与形式 | [UI 文档结构](../../docs/structure/ui-docs-structure.md) |

## 阅读顺序

1. 先读 [UI 设计](ui-design.md)，确认流程、范围与交付检查。
2. 按改动涉及的主题读对应分册；跨主题时全部读取。
3. 页面与组件同时改动时先读 `pages.md` 再读 `components.md`；令牌与图标先于二者确定。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件与[runbooks 索引](../../README.md)。
