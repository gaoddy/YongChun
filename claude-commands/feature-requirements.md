---
description: 按 runbook 澄清产品功能需求：只谈产品规则，直到无待确认项
argument-hint: <功能设想或需求描述>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/product/feature-requirements.md

按上述 runbook 澄清用户本次提出的产品功能需求。

执行要求：
1. 只讨论产品层面，不讨论技术实现、接口、表结构、依赖与成本。
2. 按产品定义要素逐项写清规则、页面、状态、权限、字段与验收标准。
3. 未建立 `update/<需求>/` 时写 `output/product-requirements/<需求-slug>/product.md`；已建立时直接更新其中的 `product.md`；确认后回写 `update/` 并删除工作稿。
4. 每条结论标注「已确认」「待确认」或「已否决」，无法确认的写入版本 `open-questions.md`。
5. 满足无待确认项、每条可验收、用户确认后停止，不进入可行性调研。

完成判定：产品规则全部可验收、无待确认项、用户已确认。
