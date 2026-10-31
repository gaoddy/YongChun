---
description: 按 runbook 编写任务计划：阶段顺序、任务拆分与文件边界
argument-hint: <版本或任务范围>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/version/plan.md
@${CLAUDE_PLUGIN_ROOT}/runbooks/docs/structure/docs-structure.md

按上述 runbook 为用户本次指定的范围编写任务计划。

执行要求：
1. 确认版本、关联需求目录与分支名。
2. 产品与技术确认完成后进入实施阶段，在 `docs/plan/<分支名>/` 建立计划目录；一个计划一个目录，`docs/plan/` 已忽略、不提交。
3. 阶段顺序固定：产品确认 → 技术确认 → 任务拆分；前一阶段未确认不进入下一阶段。
4. 每个任务写清输入、产出、文件边界与验证方式；并行任务不得写同一文件。
5. 任务完成后、合并前删除计划目录。

完成判定：任务可独立验证、文件边界清晰、计划只链接 `update/` 不复制结论。
