---
agent:
  effort: high
---

# Runbook：文档回写

## 适用场景

- 代码实现后同步产品与技术文档，或需求、缺陷完成后清理记录。

## 前置读取

- [文档写作](docs-writing.md)

## 文档体系约束

- 规则入口：根 `AGENTS.md` 只放协作原则、项目阶段、项目事实与 runbook 声明，流程写在 runbook 仓库，`docs/` 只存状态；新增规则先判断归属，不在两处重复。
- 目录职责：`docs/current/product/`、`docs/current/technical/` 描述当前代码已实现的状态；`docs/versions/<版本>/` 描述未实现的目标形态与需求变动；跨版本规则不进版本目录。
- 写作规则：按[文档规则](docs-writing.md)；描述现状时标注「已实现」「方案未实施」「待确认」，命令、路径、字段必须能在仓库核实。
- 结论落点：已定夺的事项即为确定要求，直接写入承载该内容的文件；不在 `open-questions.md`、计划或文档中另行记录结论、备选方案与决策过程。
- 计划生命周期：计划只在实施计划时创建，写入 `docs/plan/<分支名>/`；`docs/plan/` 已忽略、不提交，任务完成后、合并前删除。
- 回写在验证通过后、提交前完成；先实现后补文档视为任务未完成。

## 回写位置

| 改动 | 写入位置 | 同时删除 |
| --- | --- | --- |
| 产品规则、页面与交互 | `docs/current/product/` 对应文档，标注「已实现」 | `update/<需求>/product.md` 中已实现部分 |
| UI 页面、组件与设计系统 | `docs/current/product/ui/` 对应文档，按[UI 文档结构](structure/ui-docs-structure.md) | 版本 `product/ui/` 与 `update/` 中已实现部分 |
| 接口契约、数据模型 | `docs/current/technical/` 对应文档；数据结构与表按[文档结构](structure/docs-structure.md#数据结构文档)一结构一文件 | `update/<需求>/technical.md` 中已实现部分 |
| 缺陷修复 | 受影响的 `docs/current/product/`、`docs/current/technical/` | `bugfix/<日期>-<slug>/` |
| 分层、目录与命名 | [目录结构与命名](../engineering/directory-structure.md)、[服务端分层](../engineering/server/layering.md)、[客户端分层](../engineering/client/layering.md)、相关技术文档 | — |
| 版本完成 | `docs/current/product/`、`docs/current/technical/` 覆盖版本基线 | 版本 `product/`、`technical/` |

## 步骤

1. 判断内容归属：已实现内容写入 `docs/current/product/`、`docs/current/technical/`；未实现内容留在 `versions/<版本>/update/` 或 `bugfix/`。
2. 把已实现的产品规则、接口契约与数据模型写入对应文档，只描述当前代码状态，不写实现过程。
3. 同步更新版本 `product/`、`technical/` 基线中对应的结论。
4. 从 `update/` 删除已实现部分；需求全部实现后删除需求目录。
5. 缺陷修复完成后删除对应 `bugfix/` 目录。
6. 检查文档中的命令、路径、字段能在仓库核实，更新相关索引与相对链接。

## 验证

- 文档与代码一致，已实现文档中不含规划内容。
- `update/`、`bugfix/` 只剩未完成项。
- 新增或修改的相对链接有效，索引已登记。
- 文档中的命令、路径、字段可在仓库核实。

## 相关

- [版本开发](../version/version-development.md)
