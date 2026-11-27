# Runbook 索引

按任务查一行，读对应文件；多个场景同时命中时按依赖顺序全读。只读问答不读，按受众解释时读[解释与讲解](docs/explanation.md)；规则以 runbook 正文为准。

## 项目与版本

| 任务 / 触发 | 读 |
| --- | --- |
| 新建项目，初始化开发工作空间与文档骨架 | [implementation/project-init.md](implementation/project-init.md) |
| 产品初始化：产品名、介绍、用户规模、端与平台、功能列表 | [product/product-init.md](product/product-init.md) |
| 版本建立、推进与收尾的整体流程 | [version/version-development.md](version/version-development.md) |
| 任务计划的规划、跟踪与清理 | [version/plan.md](version/plan.md) |
| 记录不应被推翻的决策，或判断需求、方案是否已否决 | [version/decision-record.md](version/decision-record.md) |
| 复盘交付时长、缺陷、返工、回滚与重复修改 | [version/retrospective.md](version/retrospective.md) |

## 需求与产品

| 任务 / 触发 | 读 |
| --- | --- |
| 定义或调整产品规则、页面与交互 | [product/product-definition.md](product/product-definition.md) |
| 汇总全部产品需求，维护需求文档、待定夺事项与实现版本 | [product/requirements-document.md](product/requirements-document.md) |
| 新增功能，先在产品层面澄清需求 | [product/feature-requirements.md](product/feature-requirements.md) |
| 需求已确认，确认技术可行性、约束与冲突 | [product/feature-feasibility.md](product/feature-feasibility.md) |
| 需求变动：改成、新增、去掉、调整规则或行为 | [version/requirement-change.md](version/requirement-change.md) |
| 缺陷修复：报错、异常、行为不对，根因已确认且不改产品规则 | [version/bugfix.md](version/bugfix.md) |

## UI 设计

| 任务 / 触发 | 读 |
| --- | --- |
| UI 设计、改版、实现与评审 | [product/ui/ui-design.md](product/ui/ui-design.md) |
| UI 分册索引与阅读顺序 | [product/ui/README.md](product/ui/README.md) |
| UI 改版前给出可比较的方向方案 | [product/ui/directions.md](product/ui/directions.md) |
| 设计系统与公共 UI 落地 | [product/ui/design-system.md](product/ui/design-system.md) |
| 主题范围（单主题或深浅色）、主题切换、视觉资源 | [product/ui/theme.md](product/ui/theme.md) |
| 页面结构、页面状态与适配 | [product/ui/pages.md](product/ui/pages.md) |
| 组件粒度、公共组件拆分与接口边界 | [product/ui/components.md](product/ui/components.md) |
| 设计 tokens 的定义与变更 | [product/ui/tokens.md](product/ui/tokens.md) |
| 图标新增、替换与复用 | [product/ui/icons.md](product/ui/icons.md) |
| 操作反馈、表单、动效与无障碍 | [product/ui/interaction.md](product/ui/interaction.md) |

## 服务端设计与实现

| 任务 / 触发 | 读 |
| --- | --- |
| 服务端分册索引与阅读顺序 | [engineering/server/README.md](engineering/server/README.md) |
| 按游戏类型选择服务架构分册 | [engineering/server/architecture/index.md](engineering/server/architecture/index.md) |
| 三种服务架构方案的通用输入、要求与选择 | [engineering/server/architecture/requirements.md](engineering/server/architecture/requirements.md) |
| 帧同步：固定 tick、确定性输入广播 | [engineering/server/architecture/realtime-frame-sync.md](engineering/server/architecture/realtime-frame-sync.md) |
| 状态同步：服务端权威、客户端预测校正 | [engineering/server/architecture/realtime-state-sync.md](engineering/server/architecture/realtime-state-sync.md) |
| 体育竞技：高帧率、延迟补偿与观战回放 | [engineering/server/architecture/sports-competition.md](engineering/server/architecture/sports-competition.md) |
| 回合制：回合请求-响应、服务端校验、异步对战 | [engineering/server/architecture/turn-based.md](engineering/server/architecture/turn-based.md) |
| 大世界：角色长期在线、AOI 广播 | [engineering/server/architecture/persistent-world.md](engineering/server/architecture/persistent-world.md) |
| 沙盒：玩家可改世界、区块加载与持久化 | [engineering/server/architecture/sandbox.md](engineering/server/architecture/sandbox.md) |
| SLG：大地图、行军建造、资源与分区开服 | [engineering/server/architecture/slg.md](engineering/server/architecture/slg.md) |
| 弱联网与小游戏：本地计算、云存档与排行 | [engineering/server/architecture/weak-online.md](engineering/server/architecture/weak-online.md) |
| 在选定架构下实现服务端方案 | [engineering/server/implementation.md](engineering/server/implementation.md) |
| 服务端分层、依赖方向、端口与装配 | [engineering/server/layering.md](engineering/server/layering.md) |
| 服务端数据访问：真相源、事务、查询、锁与缓存 | [engineering/server/data-access.md](engineering/server/data-access.md) |
| 服务端源码结构、依赖与本地运行 | [engineering/server/runtime.md](engineering/server/runtime.md) |

## 接口

| 任务 / 触发 | 读 |
| --- | --- |
| 服务端接口分册索引与阅读顺序 | [engineering/server/api/README.md](engineering/server/api/README.md) |
| 接口通用契约规则与协议选择 | [engineering/server/api/contract.md](engineering/server/api/contract.md) |
| HTTP 接口规则 | [engineering/server/api/http.md](engineering/server/api/http.md) |
| WebSocket 接口规则 | [engineering/server/api/websocket.md](engineering/server/api/websocket.md) |
| gRPC 接口规则 | [engineering/server/api/grpc.md](engineering/server/api/grpc.md) |
| SSE 接口规则 | [engineering/server/api/sse.md](engineering/server/api/sse.md) |
| 消息订阅接口规则 | [engineering/server/api/subscription.md](engineering/server/api/subscription.md) |
| 长轮询接口规则 | [engineering/server/api/long-polling.md](engineering/server/api/long-polling.md) |
| 新增或修改服务端接口 | [engineering/server/new-api.md](engineering/server/new-api.md) |

## 数据

| 任务 / 触发 | 读 |
| --- | --- |
| 数据库分册索引与阅读顺序 | [engineering/database/README.md](engineering/database/README.md) |
| 建表前规划表、字段、关系与索引 | [engineering/database/table-design.md](engineering/database/table-design.md) |
| 表、字段、索引与迁移变更 | [engineering/database/schema-change.md](engineering/database/schema-change.md) |
| 领域模型、DTO、枚举与结构字段 | [engineering/data-structure-design.md](engineering/data-structure-design.md) |

## 客户端

| 任务 / 触发 | 读 |
| --- | --- |
| 客户端分册索引与阅读顺序 | [engineering/client/README.md](engineering/client/README.md) |
| 客户端页面、状态、数据源与共享层分层 | [engineering/client/layering.md](engineering/client/layering.md) |
| 客户端技术方案设计 | [engineering/client/design.md](engineering/client/design.md) |
| 客户端运行、构建参数、联调与实机验证 | [engineering/client/runtime.md](engineering/client/runtime.md) |
| Flutter 各端构建、混淆、签名与产物校验 | [engineering/client/flutter-build.md](engineering/client/flutter-build.md) |

## 工程规则

| 任务 / 触发 | 读 |
| --- | --- |
| 引入、升级或移除技术依赖 | [engineering/tech-change.md](engineering/tech-change.md) |
| 目录、模块归属与命名 | [engineering/directory-structure.md](engineering/directory-structure.md) |
| 审计历史设计与遗留代码，评估可否移除 | [engineering/codebase-audit.md](engineering/codebase-audit.md) |
| 复杂问题先抽象建模，再选算法 | [engineering/algorithm-design.md](engineering/algorithm-design.md) |
| 文案外置、多语言、locale、时区与格式化 | [engineering/internationalization-design.md](engineering/internationalization-design.md) |

## 实施与交付

| 任务 / 触发 | 读 |
| --- | --- |
| 修改代码、文档或配置：场景判定、执行与验证 | [implementation/change-delivery.md](implementation/change-delivery.md) |
| 建立或核对验收标准映射，判断「什么算完成」 | [implementation/acceptance.md](implementation/acceptance.md) |
| 在终端执行命令：非交互、输出裁剪、退出码、后台与危险操作 | [implementation/terminal-execution.md](implementation/terminal-execution.md) |
| 草案、方案探讨与技术咨询的结论记录 | [implementation/discussion-record.md](implementation/discussion-record.md) |
| 判断修改任务是否需要创建 worktree | [implementation/worktree-timing.md](implementation/worktree-timing.md) |
| 创建 worktree、切换分支与清理 | [implementation/worktree.md](implementation/worktree.md) |
| 构建、测试、静态检查与本地运行入口 | [implementation/make.md](implementation/make.md) |
| 补充测试与执行验证 | [implementation/testing.md](implementation/testing.md) |
| 服务端部署、发布、配置变更与回滚 | [delivery/server-deploy.md](delivery/server-deploy.md) |
| 客户端灰度发布、强制更新与回滚 | [delivery/client-release.md](delivery/client-release.md) |
| 版本收尾后正式发版、合并 main 与打 tag | [delivery/version-release.md](delivery/version-release.md) |
| worktree 与合并队列交付 | [delivery/worktree-delivery.md](delivery/worktree-delivery.md) |

## 排障

| 任务 / 触发 | 读 |
| --- | --- |
| 测试失败、线上异常或行为不符，先定位根因 | [problems/troubleshooting.md](problems/troubleshooting.md) |
| 根因已确认，决定修复层次、修改端与范围 | [problems/fix-decision.md](problems/fix-decision.md) |
| 日志、指标、追踪与告警 | [problems/observability.md](problems/observability.md) |

## 文档

| 任务 / 触发 | 读 |
| --- | --- |
| 文档写作与表述规范 | [docs/docs-writing.md](docs/docs-writing.md) |
| 按受众层次解释代码、概念、报错或方案（ELI5） | [docs/explanation.md](docs/explanation.md) |
| 代码实现后的文档回写 | [docs/docs-sync.md](docs/docs-sync.md) |
| 把现有 docs 目录重构为 runbook 文档结构 | [docs/docs-restructure.md](docs/docs-restructure.md) |
| 文档结构分册索引与阅读顺序 | [docs/structure/README.md](docs/structure/README.md) |
| docs 目录与文档内部结构规范 | [docs/structure/docs-structure.md](docs/structure/docs-structure.md) |
| UI 文档落点、目录、职责与生命周期 | [docs/structure/ui-docs-structure.md](docs/structure/ui-docs-structure.md) |
| 版本文档目录、文件形式与生命周期 | [docs/structure/version-docs-structure.md](docs/structure/version-docs-structure.md) |
