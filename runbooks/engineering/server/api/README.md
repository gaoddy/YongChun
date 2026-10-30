# 服务端接口分册

> 接口通用契约规则与各协议规则按协议拆分；接口的新增与修改流程见[新增接口](../new-api.md)。

## 何时读哪一篇

| 主题 | 文档 |
| --- | --- |
| 通用契约规则、兼容演进与协议选择 | [contract.md](contract.md) |
| HTTP 接口规则 | [http.md](http.md) |
| WebSocket 接口规则 | [websocket.md](websocket.md) |
| gRPC 接口规则 | [grpc.md](grpc.md) |
| SSE 接口规则 | [sse.md](sse.md) |
| 消息订阅规则 | [subscription.md](subscription.md) |
| 长轮询接口规则 | [long-polling.md](long-polling.md) |

## 阅读顺序

1. 先读 [contract.md](contract.md)，确认通用规则并从「协议选择」定位协议文档。
2. 再读所选协议文档，逐项核对规则与要求的例外。
3. 新增或修改接口按[新增接口](../new-api.md)执行。

## 分册规则

- 规则只在所属文档写一次，其他文档用相对链接引用，不复制内容。
- 新增、拆分或删除协议文档时，同一任务内更新本文件、[服务端分册](../README.md)、[全局索引](../../../index.md)与根 `AGENTS.md` 触发表。
