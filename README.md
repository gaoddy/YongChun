# Agent Runbook

一套集中维护的 runbook 集合：把协作原则、开发流程、文档规范与验证标准写成 AI agent 能直接执行的操作手册。其他项目不需要自建或复制 runbook，只需在根 `AGENTS.md`（`CLAUDE.md` 指向它）中声明引用，agent 便按同一套规则判断该读什么、该做什么、做到什么程度算完成。

## 解决什么问题

- 规则散落在对话、聊天记录与个人习惯里，换一个会话或换一个 agent 就失效。
- 流程只存在于人的经验中，agent 容易跳过调研、方案确认、测试与文档回写。
- 每个项目各存一份规则，版本分叉后互相矛盾，无法判断哪份有效。
- 文档与代码脱节，已实现状态和规划混在一起，无法作为后续工作的依据。

本项目的做法是把这些内容集中固化为 runbook：每篇有适用场景、前置读取、规则、步骤与验证，agent 触发对应场景时按文执行，人按同一篇文评审。接入项目只声明「遵循哪套 runbook」，规则本身只维护一份。

## 工作方式

```text
接入项目 AGENTS.md / CLAUDE.md   声明 runbook 位置、使用规则与项目事实
本仓库 runbooks/                 可执行手册：场景、规则、步骤与验证
接入项目 docs/                   项目状态：当前已实现的产品与技术，按版本推进
```

三层单向依赖：项目声明只做路由与项目事实，细节在本仓库 runbook，runbook 约束项目 `docs/` 的编写与回写。规则只有一处出处，其他位置链接而不复制。

## 如何指导 agent 在不同场景下工作

runbooks 记录的不是泛泛的建议，而是每个场景下 agent 的进场条件、执行顺序与完成标准：

- **场景识别**：本仓库根 `AGENTS.md` 的触发表与[全局索引](runbooks/index.md)按「触发 / 场景」列出必读 runbook。agent 修改仓库前先定位场景，不凭记忆执行。
- **进场约束**：每篇的「适用场景」判断是否命中，「前置读取」给出动手前必须读的上下文，避免只读到片段就开始改。
- **执行路径**：「规则」划定边界与禁止项，「步骤」给出顺序，agent 按步骤推进而不是自由发挥。
- **完成判定**：「验证」列出可检查项，未通过不算完成；跨场景任务要求读完全部相关 runbook。
- **场景举例**：新增接口读 [new-api](runbooks/engineering/server/new-api.md)；调整目录或分层读 [directory-structure](runbooks/engineering/directory-structure.md)、[server/layering](runbooks/engineering/server/layering.md)、[client/layering](runbooks/engineering/client/layering.md)；定位问题先读 [troubleshooting](runbooks/problems/troubleshooting.md) 再读 [fix-decision](runbooks/problems/fix-decision.md)；做 UI 从 [ui-design](runbooks/product/ui/ui-design.md) 进入分册；推进版本读 [version-development](runbooks/version/version-development.md)。

新增场景时先写 runbook，再登记到触发表与[全局索引](runbooks/index.md)；两者缺一，agent 就不会在该场景读到它。

## 插件分发

本仓库同时是 Claude Code 与 Codex 插件，两端共用 `runbooks/`、`skills/` 与 `hooks/hooks.json`，命令目录分开维护。

### Claude Code

根 `.claude-plugin/plugin.json` 声明插件，`claude-commands/` 提供六个命令，marketplace 的 `source` 指向仓库根。接入项目在 Claude Code 中安装：

```bash
claude plugin marketplace add gaoddy/agent-runbook
```

```bash
claude plugin install agent-runbook@agent-runbook
```

安装后可用 `/agent-runbook:deliver`、`/agent-runbook:bugfix`、`/agent-runbook:new-api`、`/agent-runbook:plan`、`/agent-runbook:ui`、`/agent-runbook:docs-restructure`。命令通过 `${CLAUDE_PLUGIN_ROOT}` 引用插件内的 runbook，接入项目不复制 runbook 或命令文件。GitHub 源安装的是发布副本，更新时执行 `claude plugin update agent-runbook`；参与本仓库开发时用 `claude --plugin-dir <本仓库路径>` 直接加载工作区。

### Codex

根 `.codex-plugin/plugin.json` 声明插件，`.agents/plugins/marketplace.json` 提供 marketplace 登记，命令在 `codex-commands/`。接入项目安装：

```bash
codex plugin marketplace add gaoddy/agent-runbook
```

```bash
codex plugin add agent-runbook@agent-runbook
```

Codex 没有插件斜杠命令，加载时会把 `codex-commands/` 的命令转换为 `source-command-<name>` skill。命令正文统一用「用户本次请求」这类通用表述，不写 `$ARGUMENTS`、编号占位符、`{{...}}`、`` !` `` 或 `@` 开头的 token，含这些内容的命令会被 Codex 跳过；Claude Code 在正文没有占位符时把参数以 `ARGUMENTS: <原文>` 追加到末尾，因此两端正文一致，两个命令目录的差异只剩引用 runbook 的写法。插件钩子需要在本机确认信任，安装后按 Codex 提示审核。

### 本仓库结构

```text
AGENTS.md                 本仓库的根规则与场景触发表
CLAUDE.md                 入口，指向 AGENTS.md
README.md                 本说明
LICENSE                   MIT 许可证
.claude-plugin/           Claude Code 插件与 marketplace 清单
.codex-plugin/            Codex 插件清单
.agents/plugins/          Codex marketplace 登记
claude-commands/          Claude Code 插件命令
codex-commands/           Codex 插件命令
skills/                   双端共用的 skill：worktree 合并队列交付
hooks/                    UserPromptSubmit 路由提示
scripts/                  校验脚本与测试
runbooks/
├── README.md             目录树与项目基线
├── index.md              全局索引：全部 runbook 登记
├── runbook.md            runbook 的编写、拆分与索引维护
├── docs/                 文档：写作、回写与文档结构分册
├── version/              版本：流程、需求、缺陷、计划
├── product/              产品定义与 UI 分册
├── engineering/          选型、目录、接口、数据与服务端/客户端分册
├── implementation/       实施：接入、任务、讨论、worktree、构建、测试
├── delivery/             交付：服务端发布、客户端发布与合并队列交付
└── problems/             问题排查与修复决策
```

接入项目根下的 `docs/`、`server/`、`client/` 目录属于项目本身，不在本仓库内维护。

## 接入方式

1. 在项目根创建 `AGENTS.md`，加入下面的声明块；`CLAUDE.md` 只写一行 `@AGENTS.md`。
2. 填写项目事实：服务端与客户端目录、首个版本号，以及 runbook 中 `<...>` 对应的框架、命令与数据库取值。
3. 按[文档结构](runbooks/docs/structure/docs-structure.md)建立 `docs/` 骨架，按[版本文档结构](runbooks/docs/structure/version-docs-structure.md)建立首个版本目录。
4. 不复制 `runbooks/` 到项目；规则变化回本仓库修改，避免版本分叉。

声明块：

```markdown
## Runbook

本项目遵循 <runbook 仓库地址或本地路径> 的 runbook。

- 场景与必读对应见 <runbook 仓库>/runbooks/index.md；修改代码、文档或配置前按场景读取对应 runbook。
- 项目特有场景在本文件补充入口，指向上述 runbook；不复制 runbook 内容。
- runbook 与本文件冲突时以 runbook 为准，并修正本文件。
- 项目事实：服务端目录 `<...>`、客户端目录 `<...>`、首个版本 `<...>`、框架 `<...>`、构建与迁移命令见[构建入口](runbooks/implementation/make.md)。
```

确需项目内独有的流程时，新增一篇独立 runbook 并在项目 `AGENTS.md` 声明其位置；不要分叉整套 `runbooks/`。

## 设计原则

- **已实现 / 规划二分**：项目 `docs/product/`、`docs/technical/` 只写当前代码已实现的状态；未实现的目标形态与需求变动只写在 `docs/versions/<版本>/`。
- **版本闭环**：产品改动确认 → 技术方案确认 → 任务拆分 → 实施 → 同任务回写文档并从 `update/` 删除已实现部分。
- **触发即读**：触发表维护场景与 runbook 的对应关系，修改仓库前先读对应手册，不凭记忆执行。
- **单一出处**：一条规则只写一遍，其余位置链接；接入项目只声明引用，不分叉副本。
- **验证先于完成**：每篇 runbook 给出可执行的验证项，未通过不算完成。

## 许可证

[MIT](LICENSE)
