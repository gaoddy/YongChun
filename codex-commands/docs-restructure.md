---
description: 按 runbook 把项目现有 docs 目录重构为 runbook 文档结构
argument-hint: <docs 目录或范围>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行 `runbooks/docs/docs-restructure.md`。
3. 先盘点现有文档与入链，再按目标结构迁移，规则只保留一处出处。
4. 迁移后更新全部相对链接、索引与触发表。

完成判定：目标结构完整，无死链与孤儿文件，原目录已清理。
