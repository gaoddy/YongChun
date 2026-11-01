---
description: 按 runbook 澄清产品功能需求：只谈产品规则，直到无待确认项
argument-hint: <功能设想或需求描述>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/product/feature-requirements.md`
   - `runbooks/product/product-definition.md`
3. 只讨论产品层面，不讨论技术实现、接口、表结构、依赖与成本。
4. 按产品定义要素逐项写清规则、页面、状态、权限、字段与验收标准；未建立 `update/<需求>/` 时工作稿写 `output/product-requirements/<需求-slug>/product.md`，已建立时直接更新其中的 `product.md`；无法确认的写入版本 `open-questions.md`。
5. 满足无待确认项、每条可验收、用户确认后停止。

完成判定：产品规则全部可验收、无待确认项、用户已确认。
