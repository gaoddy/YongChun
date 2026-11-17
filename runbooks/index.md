# Runbook 全局索引

> `runbooks/` 下全部 runbook 的唯一登记处。新增、改名、移动或删除 runbook 时，在同一任务内更新本表。
> 目录树与项目基线见 [README.md](README.md)；编写与索引规则见 [runbook.md](runbook.md)。
> 按场景查找入口见根 [AGENTS.md](../AGENTS.md) 的触发表。

## 索引

| 分组 | Runbook | 适用场景 |
| --- | --- | --- |
| runbook | [runbook.md](runbook.md) | runbook 的编写、拆分、命名与索引维护 |
| runbook | [runbook-agent-mapping.md](runbook-agent-mapping.md) | runbook 与 Claude Code/Codex agent 的映射、思考强度与生成 |
| docs | [docs-sync.md](docs/docs-sync.md) | 代码实现后的文档回写 |
| docs | [docs-restructure.md](docs/docs-restructure.md) | 将现有 docs 目录重构为 runbook 文档结构 |
| docs | [docs-writing.md](docs/docs-writing.md) | 文档表述、状态标注与写作规则 |
| docs | [structure/README.md](docs/structure/README.md) | 文档结构分册索引与阅读顺序 |
| docs | [structure/docs-structure.md](docs/structure/docs-structure.md) | docs 目录与文档内部结构规范 |
| docs | [structure/ui-docs-structure.md](docs/structure/ui-docs-structure.md) | UI 文档结构：落点、目录、文件职责与生命周期 |
| docs | [structure/version-docs-structure.md](docs/structure/version-docs-structure.md) | 版本文档结构：目录、文件形式与生命周期 |
| version | [version-development.md](version/version-development.md) | 版本建立、推进与收尾的整体流程 |
| version | [requirement-change.md](version/requirement-change.md) | 需求变动的拆分、确认与实施 |
| version | [bugfix.md](version/bugfix.md) | 缺陷修复的执行与验证 |
| version | [plan.md](version/plan.md) | 任务计划与进度跟踪 |
| version | [retrospective.md](version/retrospective.md) | 交付效率与质量问题的周期复盘与改进沉淀 |
| product | [product-init.md](product/product-init.md) | 产品初始化：引导完成产品名、介绍、用户规模、端与平台、功能列表的收集 |
| product | [product-definition.md](product/product-definition.md) | 产品规则、页面与交互的定义、调整与完备性审查 |
| product | [feature-requirements.md](product/feature-requirements.md) | 新增功能前的产品需求澄清与确认 |
| product | [feature-feasibility.md](product/feature-feasibility.md) | 已确认需求的技术可行性、冲突与风险评估 |
| product | [ui-design.md](product/ui/ui-design.md) | UI 设计、改版、实现与评审 |
| product | [ui/README.md](product/ui/README.md) | UI 分册索引与阅读顺序 |
| product | [ui/directions.md](product/ui/directions.md) | 三种方向方案的写法与约束 |
| product | [ui/design-system.md](product/ui/design-system.md) | 设计系统与公共 UI 的落地 |
| product | [ui/theme.md](product/ui/theme.md) | 深色浅色、主题切换与视觉资源 |
| product | [ui/pages.md](product/ui/pages.md) | 页面结构、页面状态、适配与首屏性能 |
| product | [ui/components.md](product/ui/components.md) | 组件化粒度、复用判定、接口边界与扩展 |
| product | [ui/tokens.md](product/ui/tokens.md) | 视觉令牌的定义、使用与变更 |
| product | [ui/icons.md](product/ui/icons.md) | 图标的共享入口、语义、风格与可访问性 |
| product | [ui/interaction.md](product/ui/interaction.md) | 操作状态、反馈、表单、动效与无障碍 |
| engineering | [tech-change.md](engineering/tech-change.md) | 引入、升级或移除技术依赖 |
| engineering | [directory-structure.md](engineering/directory-structure.md) | 顶层与源码目录、模块归属与命名 |
| engineering | [codebase-audit.md](engineering/codebase-audit.md) | 历史设计与遗留代码审计、认知成本评估与简化 |
| engineering | [database/README.md](engineering/database/README.md) | 数据库分册索引与阅读顺序 |
| engineering | [database/table-design.md](engineering/database/table-design.md) | 数据库表、字段、关系与索引的规划 |
| engineering | [database/schema-change.md](engineering/database/schema-change.md) | 数据模型、索引与迁移变更 |
| engineering | [data-structure-design.md](engineering/data-structure-design.md) | 代码数据结构：领域模型、值对象、传输结构与枚举 |
| engineering | [algorithm-design.md](engineering/algorithm-design.md) | 复杂问题的抽象建模与算法选择 |
| engineering | [server/README.md](engineering/server/README.md) | 服务端分册索引与阅读顺序 |
| engineering | [server/layering.md](engineering/server/layering.md) | 服务端依赖方向、端口、装配与文件粒度 |
| engineering | [server/architecture/index.md](engineering/server/architecture/index.md) | 服务架构场景路由与分册入口；入口与索引合一使用 index.md |
| engineering | [server/architecture/requirements.md](engineering/server/architecture/requirements.md) | 服务架构三种方案的通用输入、要求与选择规则 |
| engineering | [server/architecture/realtime-frame-sync.md](engineering/server/architecture/realtime-frame-sync.md) | 固定 tick、确定性输入广播的实时对战帧同步 |
| engineering | [server/architecture/realtime-state-sync.md](engineering/server/architecture/realtime-state-sync.md) | 服务端权威、客户端预测校正的实时对战状态同步 |
| engineering | [server/architecture/sports-competition.md](engineering/server/architecture/sports-competition.md) | 高帧率体育竞技、延迟补偿与观战回放 |
| engineering | [server/architecture/turn-based.md](engineering/server/architecture/turn-based.md) | 回合请求-响应、服务端校验与异步对战 |
| engineering | [server/architecture/persistent-world.md](engineering/server/architecture/persistent-world.md) | 持久大世界、分线分片与 AOI |
| engineering | [server/architecture/sandbox.md](engineering/server/architecture/sandbox.md) | 玩家可改世界、区块加载与 UGC |
| engineering | [server/architecture/slg.md](engineering/server/architecture/slg.md) | 大地图定时事件、资源强一致与分区开服 |
| engineering | [server/architecture/casual.md](engineering/server/architecture/casual.md) | 弱在线、本地计算、云存档与排行 |
| engineering | [server/implementation.md](engineering/server/implementation.md) | 在选定架构下实现服务端方案 |
| engineering | [server/runtime.md](engineering/server/runtime.md) | 服务端源码、依赖、部署形态与本地运行 |
| engineering | [server/api/README.md](engineering/server/api/README.md) | 服务端接口分册索引与阅读顺序 |
| engineering | [server/api/contract.md](engineering/server/api/contract.md) | 接口通用契约规则与协议选择 |
| engineering | [server/api/http.md](engineering/server/api/http.md) | HTTP 接口规则 |
| engineering | [server/api/websocket.md](engineering/server/api/websocket.md) | WebSocket 接口规则 |
| engineering | [server/api/grpc.md](engineering/server/api/grpc.md) | gRPC 接口规则 |
| engineering | [server/api/sse.md](engineering/server/api/sse.md) | SSE 接口规则 |
| engineering | [server/api/subscription.md](engineering/server/api/subscription.md) | 消息订阅接口规则 |
| engineering | [server/api/long-polling.md](engineering/server/api/long-polling.md) | 长轮询接口规则 |
| engineering | [server/new-api.md](engineering/server/new-api.md) | 新增或修改服务端接口 |
| engineering | [client/README.md](engineering/client/README.md) | 客户端分册索引与阅读顺序 |
| engineering | [client/layering.md](engineering/client/layering.md) | 客户端页面、状态、数据源与共享层分层 |
| engineering | [client/design.md](engineering/client/design.md) | 客户端技术方案设计 |
| engineering | [client/runtime.md](engineering/client/runtime.md) | 客户端运行、构建参数、联调与实机验证 |
| engineering | [client/flutter-build.md](engineering/client/flutter-build.md) | Flutter 各端构建产物、混淆、签名与校验 |
| implementation | [project-init.md](implementation/project-init.md) | 项目初始化：开发工作空间声明、文档骨架与首个版本目录 |
| implementation | [task-delivery.md](implementation/task-delivery.md) | 任务执行、验证与交付 |
| implementation | [discussion-record.md](implementation/discussion-record.md) | 草案、探讨与咨询的结论记录与注意力锚定 |
| implementation | [worktree-timing.md](implementation/worktree-timing.md) | 判断任务是否需要创建 worktree |
| implementation | [worktree.md](implementation/worktree.md) | Worktree 创建、分支与清理 |
| implementation | [make.md](implementation/make.md) | 构建、测试、检查与本地运行入口 |
| implementation | [testing.md](implementation/testing.md) | 补充测试与执行验证 |
| delivery | [server-deploy.md](delivery/server-deploy.md) | 服务端发布与回滚 |
| delivery | [client-release.md](delivery/client-release.md) | 客户端灰度发布 |
| delivery | [version-release.md](delivery/version-release.md) | 版本收尾后的正式发版、打 tag 与插件发版 |
| delivery | [worktree-delivery.md](delivery/worktree-delivery.md) | 隔离 worktree 与合并队列的交付流程 |
| problems | [troubleshooting.md](problems/troubleshooting.md) | 本地或线上问题定位 |
| problems | [fix-decision.md](problems/fix-decision.md) | 确认根因后的修复层次、修改端与范围 |
| problems | [observability.md](problems/observability.md) | 日志、指标、追踪与告警 |

## 维护

- 本表是 runbook 的唯一登记处：每个可执行 runbook 一行，路径与文件名一致，适用场景写成一句话。
- 新增、改名、移动或删除 runbook 时，同一任务内更新本表；旧条目随文件删除，不留「已废弃」记录。
- 索引不重复正文内容；适用场景只写触发条件，不写步骤与规则。
- 索引与 `README.md` 的目录树、根 `AGENTS.md` 的触发表保持一致；每次调整后校验链接与锚点。
