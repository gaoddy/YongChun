---
agent:
  effort: xhigh
---

# Runbook：产品定义文档

## 适用场景

- 建立版本时定义产品基线，或为需求变动编写 `update/<需求>/product.md`。
- 调整已实现产品的规则、页面与交互，需要先明确产品改动。

## 前置读取

- [文档写作](../docs/docs-writing.md)
- [版本文档结构](../docs/structure/version-docs-structure.md)

## 文档落点

| 产物 | 位置 | 状态 |
| --- | --- | --- |
| 版本产品基线 | `docs/versions/<版本>/product/` | 目标形态，标注「方案未实施」 |
| 需求变动 | `docs/versions/<版本>/update/<需求>/product.md` | 首行标注「待确认」或「已确认」 |
| 需求澄清讨论记录 | `output/drafts/<需求-slug>.md` | 按[讨论记录](../implementation/discussion-record.md)标注状态，确认后回写 `update/` 并删除，不提交 |
| 范围与排除项 | `docs/versions/<版本>/scope.md`（按需） | 与版本基线同步 |
| 已实现状态 | `docs/current/product/` | 代码落地的同一任务内写入，标注「已实现」 |
| 未确认事项 | `docs/versions/<版本>/open-questions.md` | 确认后移出，结论写入对应产品文档 |

## 产品定义要素

| 要素 | 必须写明 |
| --- | --- |
| 定位与用户 | 面向谁、解决什么问题、在什么场景下使用 |
| 规模目标 | 带服务端时写明上线后最终总用户数与日活，与项目事实一致；架构按该规模演进 |
| 范围 | 本次包含的能力，以及明确排除的内容与原因 |
| 功能规则 | 触发条件、可用条件、结果与例外，逐条可验收 |
| 页面与交互 | 页面清单、入口与返回、交互反馈与时机，遵循 UI 设计规则 |
| 状态与边界 | 加载中、空、错误、无权限、离线、达到限额等表现 |
| 角色与权限 | 谁能看到、谁能操作，以及越权时的表现 |
| 数据与字段 | 用户可见的字段、取值范围、格式与展示规则 |
| 体验要求 | 可感知的响应与反馈要求，不写实现方案 |
| 验收标准 | 每个功能对应的可观察结果，供测试与验收使用 |
| 受影响文档 | 需要同步的 `docs/current/product/` 页面与规则 |

## 编写原则

- 只写产品规则，不写技术实现、接口、表结构或任务拆分；技术方案见[服务架构方案生成](../engineering/server/architecture-options.md)、[服务端方案实现](../engineering/server/implementation.md)与[前端方案设计](../engineering/client/design.md)。
- 产品名、产品描述、产品形态、包名与用户规模在项目初始化时确定，见[项目接入](../implementation/project-init.md)；产品文档引用这些结论，不重复定义。
- 每条规则写成可观察、可验收的行为，避免「优化」「友好」等无法判定的表述。
- 术语全文统一，新增术语首次出现时给出定义。
- 影响产品的改动先确认产品定义，确认前不探讨技术实现，不写 `technical.md`。
- 尚未确认的规则写入 `open-questions.md`，不在产品文档中保留待定分支或备选方案。

## 步骤

1. 读取版本 `README.md`、`scope.md` 与版本 `product/` 基线，确认本次是新增能力还是调整既有规则。
2. 列出功能清单与受影响页面，逐项写出产品定义要素。
3. 标注文档状态：需求变动写「待确认」，版本基线写「方案未实施」。
4. 与用户确认产品规则；确认后把状态改为「已确认」，同步更新版本 `product/` 基线与 `scope.md`。
5. 实现落地时按[文档回写](../docs/docs-sync.md)把已实现状态写入 `docs/current/product/`，并从 `update/` 删除已实现部分。
6. 产品规则后续调整时在原文件内更新，不新建目录或副本。

## 验证

- 每条功能规则都能被测试或人工验收判定通过或失败。
- 页面、状态、角色权限与字段规则无遗漏，异常路径有明确表现。
- 带服务端时写明最终用户规模，且与项目事实一致。
- 文档中不含技术实现、接口契约与任务拆分。
- 未确认规则已进入 `open-questions.md`，文档内无待定分支。
- 状态标注与内容一致，受影响的产品文档已列出或在同一任务内更新。
- 需求澄清讨论记录位于 `output/drafts/`，未提交；确认后已回写 `update/` 并删除。

## 相关

- [版本开发](../version/version-development.md)
- [需求变动](../version/requirement-change.md)
- [文档结构](../docs/structure/docs-structure.md)
- [UI 设计](ui/ui-design.md)
- [产品功能需求澄清](feature-requirements.md)
- [产品功能可行性调研](feature-feasibility.md)
