---
description: 按 runbook 执行版本发布：发布前校验、合并 main、打 tag、推送与回滚边界
argument-hint: <版本号或发版范围>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/delivery/version-release.md

按上述 runbook 执行用户本次的发版请求。

执行要求：
1. 先核对发布判定项；任一不满足时停止并报告，不进入合并与打 tag。
2. 区分通用版本发布与本仓库插件发版；本仓库同时同步 `.claude-plugin/plugin.json` 与 `.codex-plugin/plugin.json` 的 `version`。
3. `develop` 只快进合并到 `main`，不做普通合并、不改写历史；已推送的 tag 不移动、不删除、不复用。
4. 发版前运行本仓库校验命令，退出码均为 0 才继续。
5. 验证失败不跳过、不放宽断言，修复后重跑完整校验。

完成判定：`main` 是 `develop` 的快进结果，tag 已推送且与版本记录、插件清单一致，校验命令退出 0。
