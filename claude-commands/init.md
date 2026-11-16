---
description: 按 runbook 初始化项目：逐轮收集产品定义，再建立开发工作空间与文档骨架
argument-hint: <产品描述>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/product/product-init.md
@${CLAUDE_PLUGIN_ROOT}/runbooks/implementation/project-init.md

按上述 runbook 初始化当前项目。

执行要求：
1. 先按产品初始化逐轮收集产品定义：产品名与介绍、是否带服务端、是否带客户端、用户规模、客户端平台与包名、功能列表；一轮只问一组，不一次抛出全部问题。
2. 产品数据未定项写入 `docs/versions/0.0.1/open-questions.md`，不自行假设、不填默认值。
3. 不询问测试入口、慢命令阈值等工程数据；慢命令阈值写默认值 `120s`。
4. 产品数据齐备后按项目初始化建立 `AGENTS.md`、`CLAUDE.md`、`docs/` 骨架与首个 `0.0.1` 版本目录。
5. 不复制 `runbooks/` 或命令文件到项目；项目内已有规则体系时只做声明引用。

完成判定：产品数据写入项目事实与首个版本且无空占位，`docs/` 骨架完整，项目内无 `runbooks/` 副本；本仓库另需 `python3 scripts/check-runbooks.py` 退出 0。
