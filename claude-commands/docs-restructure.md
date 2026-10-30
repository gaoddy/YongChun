---
description: 按 runbook 把项目现有 docs 目录重构为 runbook 文档结构
argument-hint: <docs 目录或范围>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/docs/docs-restructure.md
@${CLAUDE_PLUGIN_ROOT}/runbooks/docs/structure/docs-structure.md

按上述 runbook 重构以下项目的 docs 目录：

$ARGUMENTS

执行要求：
1. 先盘点现有文档，为每篇标注目标位置与处置；盘点完成前不移动或删除。
2. 只迁移、合并与拆分，不改写产品与技术结论；有歧义记入待确认项。
3. 用 `git mv` 保留历史，一次提交只做一类处置。
4. 合并重复内容并更新所有入链，删除空目录与无主文档。
5. 按文档结构校验命名、状态标注、索引与链接。

完成判定：docs 结构与 runbook 规范一致，无失效链接、孤儿文档与未归类文件。
