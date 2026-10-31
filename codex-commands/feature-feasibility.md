---
description: 按 runbook 调研产品功能可行性：技术实现、约束、冲突与成本
argument-hint: <已确认的功能需求或需求目录>
---

按 yongchun 插件的 runbook 执行用户请求。

1. 定位插件根目录：Claude Code 为插件根（环境变量 CLAUDE_PLUGIN_ROOT）；Codex 为插件安装目录，位于 `~/.codex/plugins/cache` 下。
2. 读取并按内容执行：
   - `runbooks/product/feature-feasibility.md`
   - `runbooks/product/feature-requirements.md`
3. 先确认产品需求已澄清且无待确认项；存在时停止并回到需求澄清。
4. 覆盖现有能力、技术实现、数据与权限、性能与容量、冲突、成本与风险六个维度，依据必须可核实。
5. 每个冲突点写明受影响对象与处理方式；给出可行、有条件可行或不可行结论。

完成判定：六个维度均有结论与依据，冲突点有处理方式，结论与后续动作明确。
