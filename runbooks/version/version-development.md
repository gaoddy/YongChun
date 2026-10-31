---
agent:
  effort: xhigh
---

# Runbook：版本开发

## 适用场景

- 新版本建立、推进与收尾的整体流程。
- 版本文档形式见[版本文档结构](../docs/structure/version-docs-structure.md)；需求、缺陷、计划的具体流程见各自 runbook。

## 前置读取

- [版本文档结构](../docs/structure/version-docs-structure.md)

## 版本状态

| 状态 | 含义 | 进入条件 |
| --- | --- | --- |
| 规划中 | 版本已建立，产品与技术目标尚未全部确认 | 版本目录与必需文档已创建 |
| 开发中 | 至少一项需求进入实施 | 产品与技术方案已确认，计划已拆分 |
| 已完成 | 版本内容全部实现并回写 | `update/`、`bugfix/` 为空，基线已迁移 |

- 状态记录在版本 `README.md` 与 `docs/versions/README.md`，只前移，不回退。

## 阶段流程

### 建立版本

- 按[版本文档结构](../docs/structure/version-docs-structure.md)创建目录与必需文件，写主题、目标与能力清单，状态「规划中」。
- 首个版本号默认 `1.0`，目录名、版本记录与首个 tag 一致；版本号在项目初始化时确定，见[项目接入](../implementation/project-init.md)。
- 建立版本即创建 `open-questions.md`，没有待确认项时写明。

### 产品定义

- 版本基线按[产品定义文档](../product/product-definition.md)写入 `product/`；版本进行中的改动按[需求变动](requirement-change.md)写 `update/`。
- 新增功能先按[产品需求澄清](../product/feature-requirements.md)确认产品规则，再按[可行性调研](../product/feature-feasibility.md)确认技术可行性与冲突，然后写产品基线或 `update/`。
- 产品规则确认后才进入技术方案；未确认内容只写 `open-questions.md`。

### 技术方案

- 架构方向未确定时，先按[服务架构方案生成](../engineering/server/architecture-options.md)给出三种方案并取得用户选择。
- 按[服务端方案实现](../engineering/server/implementation.md)、[前端方案设计](../engineering/client/design.md)写 `technical/` 或 `update/`，确认后同步版本技术基线。
- 方案确认后才拆分任务。

### 实施

- 按[任务计划](plan.md)拆分任务，按[任务执行与交付](../implementation/task-delivery.md)执行。
- 实施中出现的新需求按需求变动处理，缺陷按缺陷修复处理，无法当场决定的写入 `open-questions.md`。

### 收尾

- 实现完成后按[文档回写](../docs/docs-sync.md)更新 `docs/` 与版本基线，删除已实现内容。
- 按[版本文档结构](../docs/structure/version-docs-structure.md#版本完成)删除版本基线、保留版本记录并更新状态。
- 正式发版时更新 `main`：`git switch main && git merge --ff-only develop && git push origin main`，再打 `v<版本>` tag 并推送；版本号以版本记录为准，本仓库另与 `.claude-plugin/plugin.json` 的 `version` 一致。

## 规则

- 阶段顺序不可跳过：产品确认 → 技术确认 → 任务拆分；前一阶段未确认不进入下一步。
- 版本内只描述本版本，不引用后续版本。
- 未实现内容只写 `docs/versions/`，已实现状态只写 `docs/current/product/`、`docs/current/technical/`。
- 开发阶段只提交并推送 `develop`；`main` 只在正式发版时更新。
- 发版时将 `develop` 快进合并到 `main`（`git merge --ff-only`），不压缩或改写提交历史；发版点由 tag 标记。
- 正式发版时按版本号打 annotated tag `v<版本>` 并推送；tag 与版本记录一致，不移动或复用已推送的 tag。
- 每个版本必须有 `open-questions.md`，待确认事项只收敛在版本根目录。

## 步骤

1. 建立版本目录与必需文档，状态「规划中」。
2. 确认产品规则并写入版本产品基线。
3. 确认技术方案并写入版本技术基线，状态「开发中」。
4. 拆分计划并实施，需求与缺陷按各自 runbook 推进。
5. 回写文档、清理已实现内容，版本完成后更新状态为「已完成」。
6. 正式发版时将 `develop` 快进合并到 `main` 并推送，打 `v<版本>` tag 并推送。

## 验证

- 版本状态与实际进度一致。
- 版本号与项目初始化确定的一致，首个版本为 `1.0`。
- `update/`、`bugfix/` 只含未完成项。
- 文档与代码在同一任务内同步。
- 版本完成后目录与索引符合[版本文档结构](../docs/structure/version-docs-structure.md)。
- 开发阶段的提交只推送到 `develop`，`main` 仅在发版时更新。
- `main` 为 `develop` 的快进结果，未压缩或改写历史。
- 正式发版的 tag 已推送，且与版本记录、插件版本一致。

## 相关

- [缺陷修复](bugfix.md)
