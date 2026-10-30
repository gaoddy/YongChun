# {{PROJECT}}

> 本文件同时是接入项目的声明模板：按[项目接入](runbooks/implementation/project-init.md)填写 `{{PROJECT}}`、`{{SERVER_DIR}}`、`{{CLIENT_DIR}}`、`{{VERSION}}` 与正文中的 `<...>` 取值，runbook 仍以本仓库为唯一出处。

## 协作原则

1. 使用中文，默认简短、直接，优先报告结果。
2. 开始任务时用一句话说明目标，不展开执行步骤。
3. 过程更新每次控制在 1–2 句，仅说明关键发现、阻塞或需要用户决定的事项；不逐步播报搜索、读文件、运行命令和常规验证。
4. 最终回复简述完成内容、验证结果和未解决问题；简单任务一句话即可，不复述执行过程。
5. 命令、日志、文件清单和技术细节按需提供；用户明确要求详细解释时再展开。
6. 精简表达不减少实际执行、验证和交付工作，也不隐瞒失败或风险。
7. 先查仓库事实，仅对无法查证的关键歧义提问。精准修改，不扩展功能或顺带重构。
8. 多 agent 协作时，主 agent 只负责通信、协同与规划，不直接执行具体任务；每个子 agent 只完成一个任务，出现新任务时必须启用新的 agent，不复用已有 agent 承接新任务。
9. 用户明确限定的范围与交付边界优先于本文件默认流程；已授权的开发连续执行，不重复询问是否继续、构建或部署。
10. 搜索先缩小目录、文件或符号范围；较大命令输出限制在 8,000–16,000 字节，日志和测试优先展示末尾相关内容并保留退出状态。

## 项目阶段

项目只有「开发阶段」与「已上线」两个阶段，由用户明确宣布切换；切换时须同步修改本节标记。

当前阶段：**开发阶段**。

当前阶段的兼容要求：所有修改和方案制定均不考虑旧版兼容，不为旧版本保留兼容逻辑或设计兼容方案。切换到「已上线」时须同步定义兼容窗口与客户端、服务端版本共存的规则。

当前阶段的 schema 迁移形式与迁移命令的行为见[数据模型变更](runbooks/engineering/schema-change.md#数据库迁移)。

## 触发

- 只读观察、验证、回查、评审、答疑和检索等不修改仓库文件的任务，无需 worktree。
- 修改代码、文档或配置前，按触发读取对应 runbook；跨场景任务读取所有相关文档。

| 触发 / 场景 | 必读 |
| --- | --- |
| 版本建立、推进与收尾的整体流程 | [runbooks/version/version-development.md](runbooks/version/version-development.md) |
| 新项目接入 runbook，声明 AGENTS.md 与文档骨架 | [runbooks/implementation/project-init.md](runbooks/implementation/project-init.md) |
| 建立版本或调整版本文档 | [runbooks/docs/structure/version-docs-structure.md](runbooks/docs/structure/version-docs-structure.md) |
| 新建或调整 UI 文档 | [runbooks/docs/structure/ui-docs-structure.md](runbooks/docs/structure/ui-docs-structure.md) |
| 新增、拆分、移动或改名 runbook | [runbooks/runbook.md](runbooks/runbook.md) |
| 编写或调整需求变动文档 | [runbooks/version/requirement-change.md](runbooks/version/requirement-change.md) |
| 记录或收尾缺陷修复 | [runbooks/version/bugfix.md](runbooks/version/bugfix.md) |
| 编写或清理任务计划 | [runbooks/version/plan.md](runbooks/version/plan.md) |
| 定义或调整产品规则、页面与交互 | [runbooks/product/product-definition.md](runbooks/product/product-definition.md) |
| 设计服务端技术方案 | [runbooks/engineering/server/design.md](runbooks/engineering/server/design.md) |
| 设计客户端技术方案，包括状态与数据驱动 | [runbooks/engineering/client/design.md](runbooks/engineering/client/design.md) |
| UI 设计、实现、改版与评审 | [runbooks/product/ui/ui-design.md](runbooks/product/ui/ui-design.md) |
| UI 方向方案 | [runbooks/product/ui/directions.md](runbooks/product/ui/directions.md) |
| 设计系统与公共 UI 落地 | [runbooks/product/ui/design-system.md](runbooks/product/ui/design-system.md) |
| 主题、深浅色与视觉资源 | [runbooks/product/ui/theme.md](runbooks/product/ui/theme.md) |
| 页面结构、页面状态与适配 | [runbooks/product/ui/pages.md](runbooks/product/ui/pages.md) |
| 公共组件拆分、接口与扩展 | [runbooks/product/ui/components.md](runbooks/product/ui/components.md) |
| 设计 tokens 的定义与变更 | [runbooks/product/ui/tokens.md](runbooks/product/ui/tokens.md) |
| 图标新增、替换与复用 | [runbooks/product/ui/icons.md](runbooks/product/ui/icons.md) |
| 操作反馈、表单、动效与无障碍 | [runbooks/product/ui/interaction.md](runbooks/product/ui/interaction.md) |
| 修改代码、文档或配置，执行与交付 | [runbooks/implementation/task-delivery.md](runbooks/implementation/task-delivery.md) |
| 草案、方案探讨或技术咨询，需持续记录结论 | [runbooks/implementation/discussion-record.md](runbooks/implementation/discussion-record.md) |
| 任务开始前判断是否需要创建 worktree | [runbooks/implementation/worktree-timing.md](runbooks/implementation/worktree-timing.md) |
| 创建或清理 worktree、切换分支 | [runbooks/implementation/worktree.md](runbooks/implementation/worktree.md) |
| 构建、测试、静态检查、本地运行 | [runbooks/implementation/make.md](runbooks/implementation/make.md) |
| 引入、升级或移除技术依赖 | [runbooks/engineering/tech-change.md](runbooks/engineering/tech-change.md) |
| 新增或调整目录、模块归属、命名 | [runbooks/engineering/directory-structure.md](runbooks/engineering/directory-structure.md) |
| 新增或调整服务端分层、依赖方向与装配 | [runbooks/engineering/server/layering.md](runbooks/engineering/server/layering.md) |
| 新增或调整客户端页面、状态、数据源分层 | [runbooks/engineering/client/layering.md](runbooks/engineering/client/layering.md) |
| 新增或修改 HTTP 接口 | [runbooks/engineering/new-api.md](runbooks/engineering/new-api.md) |
| 数据模型、索引或迁移变更 | [runbooks/engineering/schema-change.md](runbooks/engineering/schema-change.md) |
| 补充测试与执行验证 | [runbooks/implementation/testing.md](runbooks/implementation/testing.md) |
| 代码实现后的文档回写 | [runbooks/docs/docs-sync.md](runbooks/docs/docs-sync.md) |
| 服务端发布与回滚 | [runbooks/delivery/server-deploy.md](runbooks/delivery/server-deploy.md) |
| 客户端灰度发布 | [runbooks/delivery/client-release.md](runbooks/delivery/client-release.md) |
| 遇到问题、故障或异常，需先定位根因 | [runbooks/problems/troubleshooting.md](runbooks/problems/troubleshooting.md) |
| 已确认根因，决定修复层次、修改端与范围 | [runbooks/problems/fix-decision.md](runbooks/problems/fix-decision.md) |
| 日志、指标、追踪与告警 | [runbooks/problems/observability.md](runbooks/problems/observability.md) |
| 服务端源码、依赖与本地运行 | [runbooks/engineering/server/runtime.md](runbooks/engineering/server/runtime.md) |
| 客户端运行、联调与实机验证 | [runbooks/engineering/client/runtime.md](runbooks/engineering/client/runtime.md) |
| 文档写作与表述规范 | [runbooks/docs/docs-writing.md](runbooks/docs/docs-writing.md) |
| 新建文档、调整 docs/ 目录与文档结构 | [runbooks/docs/structure/docs-structure.md](runbooks/docs/structure/docs-structure.md) |
