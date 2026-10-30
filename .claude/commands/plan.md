---
description: 按 runbook 编写任务计划：阶段顺序、任务拆分与文件边界
argument-hint: <版本或任务范围>
---

@runbooks/version/plan.md
@runbooks/docs/structure/version-docs-structure.md

按上述 runbook 为以下范围编写任务计划：

$ARGUMENTS

执行要求：
1. 确认版本、关联需求目录与分支名。
2. 按版本文档结构建立计划目录；本仓库无版本目录时写到 `output/plans/<分支名>/`。
3. 阶段顺序固定：产品确认 → 技术确认 → 任务拆分；前一阶段未确认不进入下一阶段。
4. 每个任务写清输入、产出、文件边界与验证方式；并行任务不得写同一文件。
5. 合并前删除计划目录。

完成判定：任务可独立验证、文件边界清晰、计划只链接 `update/` 不复制结论。
