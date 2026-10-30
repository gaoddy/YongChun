# Runbooks

> 可执行操作手册：按步骤完成常见工程任务。每篇包含适用场景、前置读取、步骤与验证标准。
> 技术底座内容已全部并入本目录；部署与发布规则见[服务端发布](delivery/server-deploy.md)、[客户端发布](delivery/client-release.md)与[可观测性](problems/observability.md)。

## 目录

```text
runbooks/
├── README.md          目录树与项目基线
├── index.md           全局索引：全部 runbook 登记
├── runbook.md         runbook 编写、拆分与索引维护
├── docs/              文档：写作、回写与文档结构分册
│   └── structure/     文档结构分册：通用、UI 与版本文档
├── version/           版本：流程、需求、缺陷、计划
├── product/           产品定义
│   └── ui/            UI 分册：流程、方向、设计系统、主题、页面、组件、tokens、图标、交互
├── engineering/       工程规则：选型、目录、接口、数据
│   ├── server/        服务端分册：分层、方案设计、运行
│   └── client/        客户端分册：分层、方案设计、运行
├── implementation/    实施：任务执行、讨论记录、worktree、构建、测试
├── delivery/          交付：服务端发布、客户端发布与合并队列交付
└── problems/          问题处理：排查与修复决策
```

## 索引

- 全部 runbook 的登记与适用场景见[全局索引](index.md)；本文件只维护目录树与项目基线。
- 本文件不重复登记单个 runbook，避免同一文件出现两处索引。

## 工程基线

- 本节只放项目的最终结论（技术栈、目录、分层、契约、测试与交付方式），每条一句话并链接承载它的 runbook；结论变化时先改 runbook，再更新本节。
- 与 runbook 冲突时以 runbook 为准；本节不重复规则细节。
- 技术选型结论写入[技术选型](engineering/tech-change.md)的项目选型表，目录与命名结论写入[目录结构与命名](engineering/directory-structure.md)，分层结论写入[服务端分层](engineering/server/layering.md)与[客户端分层](engineering/client/layering.md)。

## 落地顺序

- 按版本列出实施顺序与依赖，每项写清前置版本或模块、完成标志；不写日期与人力估算。
- 版本内细节留给该版本的 `README.md`，本节只维护跨版本顺序。

## 待定项

- 未决事项写入对应版本的 `open-questions.md`；本节只保留需要跨版本长期跟踪的指针。
- 事项确定后删除条目，结论写入承载它的文档。

## 编写与维护

- 新增、拆分、合并、移动或改名 runbook 前先读[runbook 编写与维护](runbook.md)；结构、归属、命名与索引规则以该文件为准。
- 本文件只维护目录树、索引入口与跨版本基线，不重复写作规则；新增 runbook 在[全局索引](index.md)登记后，同步更新根 `AGENTS.md` 的触发表。
