---
agent:
  effort: high
---

# Runbook：UI 文档结构

## 适用场景

- 新建或调整 `docs/current/product/ui/`、版本 `product/ui/` 与 UI 需求文档，确认页面、组件、设计系统文档的文件形式与落点。
- UI 的设计与实现流程见[UI 设计](../../product/ui/ui-design.md)与 `ui/` 分册；本文只规定文档形式。

## 前置读取

- [文档结构](docs-structure.md)
- [UI 设计](../../product/ui/ui-design.md)

## 落点

| 场景 | 位置 | 状态标注 |
| --- | --- | --- |
| 已实现的页面、组件、设计系统 | `docs/current/product/ui/` | 已实现 |
| 本版本的目标 UI | `docs/versions/<版本>/product/ui/` | 方案未实施 |
| UI 需求变动 | `update/<YYYY-MM-DD>-<slug>/product.md` 的页面与交互部分 | 按[需求变动](../../version/requirement-change.md) |
| 设计未决事项 | 版本 `open-questions.md` | — |

- UI 需求变动不新建文件，写在需求 `product.md` 内；目录与状态规则见[版本文档结构](version-docs-structure.md#需求变动-update)。
- 只描述当前代码已实现的 UI 写入 `docs/current/product/ui/`；未实现的目标形态只写入版本基线或需求目录。
- 不单独建「设计稿目录」；设计结论写入上述文档，原型与外部设计文件只留链接。

## 目录结构

```text
docs/current/product/ui/
├── README.md              设计系统入口：概览、页面与组件索引
├── tokens.md              设计令牌清单
├── icons.md               图标清单
├── interactions.md        通用交互模式与状态表现
├── pages/
│   ├── README.md          页面索引
│   └── <页面>.md          一个页面一个文件
└── components/
    ├── README.md          组件索引
    └── <组件>.md          一个组件一个文件
```

- 版本基线 `docs/versions/<版本>/product/ui/` 使用同一结构，只描述本版本目标。
- 文件与目录名用小写 kebab-case，与页面、组件的代码命名一致。
- `tokens.md`、`icons.md`、`interactions.md` 在首次出现对应内容时创建，不预建空文件。

## 文件职责

| 文件 | 内容 |
| --- | --- |
| `README.md` | 设计系统概览、主题与使用方式、页面与组件索引；不写具体规则 |
| `tokens.md` | 语义令牌名称、用途、深浅色取值与适用范围 |
| `icons.md` | 图标语义名、用途、来源与新增方式 |
| `interactions.md` | 通用操作状态、反馈、表单校验、动效与无障碍规则 |
| `pages/<页面>.md` | 页面目的、入口与返回、结构层级、状态清单、数据来源、适配与性能敏感点、关联组件 |
| `components/<组件>.md` | 用途、变体、属性与事件、禁用场景、使用者 |

- 页面文档列全状态：加载中、空、错误、无权限、离线、达到限额；每条状态写表现与出口。
- 页面文档不复制组件与令牌内容，用相对链接指向 `components/`、`tokens.md`。
- 组件文档按[组件设计](../../product/ui/components.md)登记用途、变体、禁用场景与示例。
- 通用交互写在 `interactions.md`，页面特有交互写在页面文档；同一规则只写一处。
- 不写设计过程、备选方向与比较结论；需求文档只保留已确认的方案。

## 生命周期

| 阶段 | 动作 |
| --- | --- |
| 设计确认 | 结论写入版本 `product/ui/` 或需求 `product.md`，标「方案未实施」 |
| 代码落地 | 同一任务写入 `docs/current/product/ui/`，状态改为「已实现」，删除版本基线与 `update/` 中已实现部分 |
| 版本完成 | 删除版本 `product/ui/` 基线，保留 `README.md` 与 `open-questions.md` |
| 删除或替换 UI | 同一任务删除对应页面、组件文档与索引条目，不留孤儿文件 |

- 共享令牌、图标与组件的变更同时更新 `tokens.md`、`icons.md`、`components/` 与所有引用它们的页面文档。
- 索引与入链在同一任务内更新，规则见[文档结构](docs-structure.md#索引与导航)。

## 步骤

1. 判断内容属于已实现状态、版本目标还是需求变动，按落点表选位置。
2. 按目录结构建立或更新文件，一个页面、一个组件各一个文件。
3. 按文件职责写内容，状态、入口与出口逐项列全，链接代替复制。
4. 更新 `README.md` 与 `pages/`、`components/` 索引。
5. 代码落地后回写 `docs/current/product/ui/`，删除已实现部分与版本基线。

## 验证

- 文件在正确落点，状态标注与实际实现一致。
- 页面与组件一文件一主题，页面状态完整，无复制其他文档内容。
- 索引与入链按[文档结构](docs-structure.md#索引与导航)校验，无死链与孤儿文档。
- 无设计过程、备选方案与未确认分支。

## 相关

- [文档写作](../docs-writing.md)
- [页面设计](../../product/ui/pages.md)
- [交互与反馈](../../product/ui/interaction.md)
