---
agent:
  effort: high
---

# Runbook：UI 设计

## 适用场景

- 所有模块的 UI 设计、改版、实现与评审；任务域规则，按任务类型生效，不按目录生效。
- 细则按主题拆分在 `ui/` 分册，入口见[分册索引](README.md)。

## 前置读取

- [UI 分册](README.md)
- [文档写作](../../docs/docs-writing.md)

## 规则

- UI 相关任务优先使用当前环境可用的产品设计与 UI 技能；没有相应技能时，按本 runbook 与分册执行，不省略设计过程。
- 先确认现状并取得方向确认，再按分册细化；顺序为：现状与范围 → [方向方案](directions.md) → 分册设计 → 共享层落地 → 验证与回写。
- 跨主题的改动读取全部分册，不凭印象套用规则。

## 步骤

1. 确认现有实现、受影响页面与组件、需要覆盖的业务状态，区分已实现功能、设计建议与未实现能力。
2. 按[方向方案](directions.md)给出三种可区分方向与可视化，取得用户选择。
3. 按分册确定页面（[pages](pages.md)）、组件（[components](components.md)）、令牌与图标（[tokens](tokens.md)、[icons](icons.md)）、交互与主题（[interaction](interaction.md)、[theme](theme.md)）；数据与状态设计写入客户端方案。
4. 按[设计系统与公共 UI](design-system.md)先扩展共享层，再实现页面与业务组件。
5. 修改共享内容前检查全部消费者，按影响范围同步调整。
6. 按分册验证项检查后交付；按[UI 文档结构](../../docs/structure/ui-docs-structure.md)与[文档回写](../../docs/docs-sync.md)完成回写。

## 验证

- 方向方案符合[方向方案](directions.md)的验证项，且已取得用户确认或指定。
- 涉及分册的验证项全部满足；页面状态齐全、组件边界清晰、无硬编码视觉值、图标语义唯一、交互状态完整、深浅色结构一致。
- 数据与状态设计已在客户端方案中落点，页面状态与数据状态一一对应。
- 文档已按[UI 文档结构](../../docs/structure/ui-docs-structure.md)回写，索引与链接完整。
- 客户端验证入口见[任务执行与交付](../../implementation/task-delivery.md)。

## 相关

- [客户端运行](../../engineering/client/runtime.md)
- [前端方案设计](../../engineering/client/design.md)
