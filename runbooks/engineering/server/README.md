# 服务端分册

> 服务端的架构选择、方案实现与运行按主题拆分；跨端主题留在 `engineering/` 分组内。
> 需求与技术方案的文档形式见[版本文档结构](../../docs/structure/version-docs-structure.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 依赖方向、端口、装配与分层 | [layering.md](layering.md) |
| 数据访问规则：真相源、事务边界、查询、锁与并发、缓存键 | [data-access.md](data-access.md) |
| 服务架构场景路由与分册入口：按游戏类型选择分册（帧同步、状态同步、体育、回合、大世界、沙盒、SLG、休闲） | [architecture/index.md](architecture/index.md) |
| 三种服务架构方案的通用输入、要求与选择 | [architecture/requirements.md](architecture/requirements.md) |
| 服务端方案实现（选定架构内） | [implementation.md](implementation.md) |
| 源码、依赖、部署形态与本地运行 | [runtime.md](runtime.md) |
| 接口规则：通用契约、协议选择与各协议 | [api/README.md](api/README.md) |
| 接口的新增与修改 | [new-api.md](new-api.md) |
| 数据模型、索引与迁移 | [../database/schema-change.md](../database/schema-change.md) |

## 阅读顺序

1. 先读 [layering.md](layering.md)，确认分层与依赖方向。
2. 涉及数据读写时读 [data-access.md](data-access.md)，确认真相源、事务边界与并发规则。
3. 架构方向未定时读 [architecture/requirements.md](architecture/requirements.md) 与 [architecture/index.md](architecture/index.md)，先按「场景路由」选择游戏类型分册，再按通用要求生成三种方案；选定后再读 [implementation.md](implementation.md) 写实现方案；接口规则从 [api/contract.md](api/contract.md) 选择协议文档、各协议细则见 [api/README.md](api/README.md)，新增或修改接口读 [new-api.md](new-api.md)，数据变更再读 [../database/schema-change.md](../database/schema-change.md)。
4. 本地运行、依赖与部署形态读 [runtime.md](runtime.md)。

## 分册规则

- 规则只在所属分册写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除分册时，同一任务内更新本文件、[全局索引](../../index.md)与根 `AGENTS.md` 触发表。
