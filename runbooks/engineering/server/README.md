# 服务端分册

> 服务端的分层、方案设计与运行按主题拆分；跨端主题留在 `engineering/` 分组内。
> 需求与技术方案的文档形式见[版本文档结构](../../docs/structure/version-docs-structure.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 依赖方向、端口、装配与分层 | [layering.md](layering.md) |
| 按产品需求与用户规模生成三种服务架构方案 | [architecture-options.md](architecture-options.md) |
| 服务端技术方案设计 | [design.md](design.md) |
| 源码、依赖、部署形态与本地运行 | [runtime.md](runtime.md) |
| HTTP 接口的新增与修改 | [../new-api.md](../new-api.md) |
| 数据模型、索引与迁移 | [../schema-change.md](../schema-change.md) |

## 阅读顺序

1. 先读 [layering.md](layering.md)，确认分层与依赖方向。
2. 架构方向未定时读 [architecture-options.md](architecture-options.md)，选定后再读 [design.md](design.md) 细化技术方案；接口与数据变更再读 [../new-api.md](../new-api.md)、[../schema-change.md](../schema-change.md)。
3. 本地运行、依赖与部署形态读 [runtime.md](runtime.md)。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件、[全局索引](../../index.md)与根 `AGENTS.md` 触发表。
