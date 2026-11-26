# YongChun

## Runbook

本项目遵循本地 `runbooks/` 的 runbook。

- 场景与必读对应见 [runbooks/index.md](runbooks/index.md)；修改代码、文档或配置前按场景读取对应 runbook。
- 项目特有场景在本文件补充入口，指向上述 runbook；不复制 runbook 内容。
- runbook 与本文件冲突时以 runbook 为准，并修正本文件。
- `runbooks/index.md` 登记面向外部项目的全部 runbook：每个可执行 runbook 一行，路径与文件名一致，适用场景写成一句话；新增、改名、移动或删除 runbook 时，同一任务内更新该表，旧条目随文件删除，不留「已废弃」记录。
- `runbooks/` 根目录的维护文档（`README.md`、`runbook.md`、`runbook-agent-mapping.md`）不进入全局索引，在本文件触发表登记。
- 索引不重复正文内容：适用场景只写触发条件，不写步骤与规则；每次调整后与 `runbooks/README.md` 的目录树、本文件触发表保持一致，并校验链接与锚点。

## 协作原则

1. 使用中文，结论先行：先给结果或判断，再给必要依据；默认简短、直接。
2. 开始任务时用一句话说明目标，不展开执行步骤。
3. 过程更新每次控制在 1–2 句，仅说明关键发现、阻塞或需要用户决定的事项；不逐步播报搜索、读文件、运行命令和常规验证。
4. 最终回复简述完成内容、验证结果和未解决问题；简单任务一句话即可，不复述执行过程。
5. 命令、日志、文件清单和技术细节按需提供；用户明确要求详细解释时再展开。
6. 精简表达不减少实际执行、验证和交付工作，也不隐瞒失败或风险。
7. 先查仓库事实，仅对无法查证的关键歧义提问。精准修改，不扩展功能或顺带重构。
8. 多 agent 协作时，主 agent 只负责通信、协同与规划，不直接执行具体任务；每个子 agent 只完成一个任务，出现新任务时必须启用新的 agent，不复用已有 agent 承接新任务。
9. 用户明确限定的范围与交付边界优先于本文件默认流程；已授权的开发连续执行，构建、测试与本地验证不逐项询问；推送、部署与发版只在用户当轮明确要求时执行。
10. 搜索先缩小目录、文件或符号范围；命令输出裁剪、退出码采集与后台任务按[终端命令执行](runbooks/implementation/terminal-execution.md#退出码)执行。
11. 本仓库修改文件后，自动执行 `/reload-plugins` 重新加载插件，使改动生效。

## 项目阶段

项目只有「开发阶段」与「已上线」两个阶段，由用户明确宣布切换；切换时须同步修改本节标记。

当前阶段：**开发阶段**。

当前阶段的兼容要求：所有修改和方案制定均不考虑旧版兼容，不为旧版本保留兼容逻辑或设计兼容方案。切换到「已上线」时须同步定义兼容窗口与客户端、服务端版本共存的规则。

## 项目事实

- 本仓库即 runbook 集合本身，没有服务端与客户端代码，接入项目所需的目录、框架、迁移与运维命令取值在本仓库不适用。
- 文档位于 `runbooks/`，入口见 [runbooks/index.md](runbooks/index.md)。
- 配置模板位于 `templates/`，当前提供 `worktree-merge-queue.toml`；复制位置、字段与校验方式见[Worktree 合并队列交付](runbooks/delivery/worktree-delivery.md)。
- 任务计划的创建、结构与删除时机见[任务计划](runbooks/version/plan.md)；`docs/plan/` 已忽略、不提交。
- Agent 产物由 `scripts/generate_runbook_agents.py` 从 runbook frontmatter 生成：Claude Code 在 `agents/`，Codex 在 `codex-agents/`；生成物提交、禁止手改，规则见 [Runbook 与 Agent 映射](runbooks/runbook-agent-mapping.md)。
- 项目初始化的声明模板与取值填写见[项目初始化](runbooks/implementation/project-init.md)；产品定义收集见[产品初始化](runbooks/product/product-init.md)。
- worktree 的唯一创建入口是 `skills/worktree/worktree-guard/scripts/worktree_create.sh`，绕过它的 `git worktree add` 由 `skills/worktree/worktree-guard/scripts/worktree_guard.sh` 在插件 `PreToolUse` 钩子中拒绝；规则与钩子配置见[Worktree 与分支](runbooks/implementation/worktree.md)。
- 本仓库的校验入口是 `python3 scripts/check-runbooks.py`（索引、链接、锚点、前置图、章节、占位符、命令引用、agent frontmatter 与生成物漂移、双端插件清单），退出码 0 为通过；该脚本只校验本仓库自身，不随插件提供给接入项目，接入项目不得调用；skill 执行器测试入口是 `python3 -m unittest discover -s skills/delivery/delivery-merge-queue/scripts` 与 `python3 -m unittest discover -s skills/worktree/worktree-guard/scripts`，插件安装自检入口是 `python3 scripts/plugin_selfcheck.py`，测试为 `python3 -m unittest discover -s scripts -p 'test_plugin_selfcheck.py'`；不定义构建、测试、生成、迁移与本地启动目标，接入项目按 [Make 构建入口](runbooks/implementation/make.md) 自行登记。
- 插件双端分发：Claude Code 通过 GitHub marketplace `gaoddy/YongChun` 安装，清单在 `.claude-plugin/`，命令在 `claude-commands/`；Codex 通过 `codex plugin marketplace add gaoddy/YongChun` 安装，清单在 `.codex-plugin/`，命令在 `codex-commands/`（Codex 会把命令转换为 `source-command-*` skill）。两端共用 `skills/`、`hooks/hooks.json` 与 `runbooks/`；命令只做路由与执行契约，规则以 runbook 为准。
- 开发阶段只向 `develop` 提交与合并；推送按协作原则 9 执行。正式发版按[版本发布](runbooks/delivery/version-release.md)执行，快进合并到 `main`，以 `.claude-plugin/plugin.json` 的 `version` 打 `v<version>` annotated tag 并推送。

## 触发

- 未指定命令或场景时，按[任务执行与交付](runbooks/implementation/change-delivery.md#场景判定)的场景判定自动路由；只读问答不触发，按受众解释的请求读[解释与讲解](runbooks/docs/explanation.md)。
- 只读观察、验证、回查、评审、答疑和检索等不修改仓库文件的任务，无需 worktree。
- 修改仓库文件一律在该任务的 worktree 内完成，改动量不作为豁免；无法创建 worktree 时阻塞并报告，不在当前目录修改。
- 修改代码、文档或配置前，按触发读取对应 runbook；跨场景任务读取所有相关文档。
- 本表只服务本仓库；接入项目的场景路由使用[全局索引](runbooks/index.md)，不复制本表。

| 触发 / 场景 | 必读 |
| --- | --- |
| 版本建立、推进与收尾的整体流程 | [runbooks/version/version-development.md](runbooks/version/version-development.md) |
| 正式发版、版本收尾后发布、打 tag | [runbooks/delivery/version-release.md](runbooks/delivery/version-release.md) |
| 新建项目，初始化开发工作空间与文档骨架 | [runbooks/implementation/project-init.md](runbooks/implementation/project-init.md) |
| 产品定义收集：产品名、介绍、用户规模、端与平台、功能列表 | [runbooks/product/product-init.md](runbooks/product/product-init.md) |
| 建立或调整版本文档 | [runbooks/docs/structure/version-docs-structure.md](runbooks/docs/structure/version-docs-structure.md) |
| 新建或调整 UI 文档 | [runbooks/docs/structure/ui-docs-structure.md](runbooks/docs/structure/ui-docs-structure.md) |
| 新增、拆分、合并、移动或删除 runbook，或调整结构、命名与索引 | [runbooks/runbook.md](runbooks/runbook.md) |
| 新增、调整或校验 runbook 对应的 agent 与思考强度 | [runbooks/runbook-agent-mapping.md](runbooks/runbook-agent-mapping.md) |
| 查看 runbooks 目录树与项目基线 | [runbooks/README.md](runbooks/README.md) |
| 需求变动的拆分、确认与实施 | [runbooks/version/requirement-change.md](runbooks/version/requirement-change.md) |
| 缺陷修复、验证与收尾 | [runbooks/version/bugfix.md](runbooks/version/bugfix.md) |
| 任务计划的规划、跟踪与清理 | [runbooks/version/plan.md](runbooks/version/plan.md) |
| 复盘最近一段时间的 PR 时长、Bug、返工、回滚与重复修改 | [runbooks/version/retrospective.md](runbooks/version/retrospective.md) |
| 记录不应被重新推翻的决策，或判断某项需求、方案是否已否决 | [runbooks/version/decision-record.md](runbooks/version/decision-record.md) |
| 定义或调整产品规则、页面与交互 | [runbooks/product/product-definition.md](runbooks/product/product-definition.md) |
| 汇总或更新产品需求、维护需求文档与实现版本 | [runbooks/product/requirements-document.md](runbooks/product/requirements-document.md) |
| 新增产品功能，先在产品层面澄清需求并审查到无缺口 | [runbooks/product/feature-requirements.md](runbooks/product/feature-requirements.md) |
| 产品需求已确认，确认技术可行性、约束与现有功能冲突 | [runbooks/product/feature-feasibility.md](runbooks/product/feature-feasibility.md) |
| 在选定架构下实现服务端技术方案 | [runbooks/engineering/server/implementation.md](runbooks/engineering/server/implementation.md) |
| 按产品需求、用户规模与游戏类型生成三种服务架构方案，并按类型选择分册 | [runbooks/engineering/server/architecture/index.md](runbooks/engineering/server/architecture/index.md) |
| 设计客户端技术方案 | [runbooks/engineering/client/design.md](runbooks/engineering/client/design.md) |
| UI 设计、实现、改版与评审 | [runbooks/product/ui/ui-design.md](runbooks/product/ui/ui-design.md) |
| UI 设计与改版前的方向方案与选择 | [runbooks/product/ui/directions.md](runbooks/product/ui/directions.md) |
| 设计系统与公共 UI 落地 | [runbooks/product/ui/design-system.md](runbooks/product/ui/design-system.md) |
| 主题范围（单主题或深浅色）与视觉资源 | [runbooks/product/ui/theme.md](runbooks/product/ui/theme.md) |
| 页面结构、页面状态与适配 | [runbooks/product/ui/pages.md](runbooks/product/ui/pages.md) |
| 组件化粒度、公共组件拆分、接口与扩展 | [runbooks/product/ui/components.md](runbooks/product/ui/components.md) |
| 设计 tokens 的定义与变更 | [runbooks/product/ui/tokens.md](runbooks/product/ui/tokens.md) |
| 图标新增、替换与复用 | [runbooks/product/ui/icons.md](runbooks/product/ui/icons.md) |
| 操作反馈、表单、动效与无障碍 | [runbooks/product/ui/interaction.md](runbooks/product/ui/interaction.md) |
| 修改代码、文档或配置，执行与交付 | [runbooks/implementation/change-delivery.md](runbooks/implementation/change-delivery.md) |
| 在终端执行命令：输出裁剪、退出码、后台任务与危险操作 | [runbooks/implementation/terminal-execution.md](runbooks/implementation/terminal-execution.md) |
| 草案、方案探讨或技术咨询，需持续记录结论 | [runbooks/implementation/discussion-record.md](runbooks/implementation/discussion-record.md) |
| 任务开始前判断是否需要创建 worktree | [runbooks/implementation/worktree-timing.md](runbooks/implementation/worktree-timing.md) |
| 创建或清理 worktree、切换分支，或并行派发子 agent | [runbooks/implementation/worktree.md](runbooks/implementation/worktree.md) |
| 构建、测试、静态检查、本地运行 | [runbooks/implementation/make.md](runbooks/implementation/make.md) |
| 引入、升级或移除技术依赖 | [runbooks/engineering/tech-change.md](runbooks/engineering/tech-change.md) |
| 新增或调整目录、模块归属、命名与业务对象登记 | [runbooks/engineering/directory-structure.md](runbooks/engineering/directory-structure.md) |
| 评估历史设计与遗留代码可否移除，或新人接手的认知成本与简化 | [runbooks/engineering/codebase-audit.md](runbooks/engineering/codebase-audit.md) |
| 新增或调整服务端分层、依赖方向、装配与文件粒度 | [runbooks/engineering/server/layering.md](runbooks/engineering/server/layering.md) |
| 设计或调整服务端数据访问：真相源、事务边界、查询、锁与并发、缓存键 | [runbooks/engineering/server/data-access.md](runbooks/engineering/server/data-access.md) |
| 新增或调整客户端页面、状态、数据源分层 | [runbooks/engineering/client/layering.md](runbooks/engineering/client/layering.md) |
| 设计或调整服务端接口通用规则，或 HTTP、WebSocket、gRPC、SSE、消息订阅、长轮询协议规则 | [runbooks/engineering/server/api/contract.md](runbooks/engineering/server/api/contract.md) |
| 新增或修改服务端接口 | [runbooks/engineering/server/new-api.md](runbooks/engineering/server/new-api.md) |
| 数据库表、字段、关系与索引规划 | [runbooks/engineering/database/table-design.md](runbooks/engineering/database/table-design.md) |
| 数据模型、索引或迁移变更 | [runbooks/engineering/database/schema-change.md](runbooks/engineering/database/schema-change.md) |
| 新增或调整代码数据结构、DTO 与枚举 | [runbooks/engineering/data-structure-design.md](runbooks/engineering/data-structure-design.md) |
| 复杂问题先抽象为通用模型，再讨论算法实现 | [runbooks/engineering/algorithm-design.md](runbooks/engineering/algorithm-design.md) |
| 文案外置、多语言、locale、时区与格式化、运营内容翻译 | [runbooks/engineering/internationalization-design.md](runbooks/engineering/internationalization-design.md) |
| 补充测试与执行验证 | [runbooks/implementation/testing.md](runbooks/implementation/testing.md) |
| 代码实现后的文档回写 | [runbooks/docs/docs-sync.md](runbooks/docs/docs-sync.md) |
| 服务端部署、发布、配置变更与回滚 | [runbooks/delivery/server-deploy.md](runbooks/delivery/server-deploy.md) |
| worktree 与合并队列交付 | [runbooks/delivery/worktree-delivery.md](runbooks/delivery/worktree-delivery.md) |
| 客户端发布、灰度扩量、强制更新与回滚 | [runbooks/delivery/client-release.md](runbooks/delivery/client-release.md) |
| 测试失败、线上异常或行为不符，先定位根因 | [runbooks/problems/troubleshooting.md](runbooks/problems/troubleshooting.md) |
| 已确认根因，决定修复层次、修改端与范围 | [runbooks/problems/fix-decision.md](runbooks/problems/fix-decision.md) |
| 日志、指标、追踪与告警 | [runbooks/problems/observability.md](runbooks/problems/observability.md) |
| 服务端源码、依赖与本地运行 | [runbooks/engineering/server/runtime.md](runbooks/engineering/server/runtime.md) |
| 客户端运行、联调与实机验证 | [runbooks/engineering/client/runtime.md](runbooks/engineering/client/runtime.md) |
| Flutter 客户端构建、产物、混淆与签名 | [runbooks/engineering/client/flutter-build.md](runbooks/engineering/client/flutter-build.md) |
| 文档写作与表述规范 | [runbooks/docs/docs-writing.md](runbooks/docs/docs-writing.md) |
| 按受众层次解释代码、概念、报错或方案 | [runbooks/docs/explanation.md](runbooks/docs/explanation.md) |
| 新建文档、调整 docs/ 目录与文档结构 | [runbooks/docs/structure/docs-structure.md](runbooks/docs/structure/docs-structure.md) |
| 按 runbook 模式重构现有 docs 目录 | [runbooks/docs/docs-restructure.md](runbooks/docs/docs-restructure.md) |
