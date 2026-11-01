---
description: 按 runbook 把复杂问题抽象为通用模型，再讨论并选定算法实现
argument-hint: <问题描述>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/engineering/algorithm-design.md`
   - `runbooks/implementation/discussion-record.md`
3. 先确认问题无法靠现成能力直接解决；在 `output/drafts/<主题>.md` 写问题陈述、约束、样例、对照表、规模与边界样例。
4. 至少给基线与优化两个候选，各写复杂度、正确性依据与成本；近似方案给质量指标与阈值。
5. 选满足规模与时限的最简单方案，经用户确认后写入承载文档并删除讨论记录。

完成判定：模型能表达全部样例与边界，选定方案有复杂度与正确性依据，结论已写入承载文档。
