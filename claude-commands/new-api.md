---
description: 按 runbook 新增或修改 HTTP 接口：契约、分层、生成、测试与文档
argument-hint: <接口变更描述>
---

@${CLAUDE_PLUGIN_ROOT}/runbooks/engineering/server/new-api.md

按上述 runbook 新增或修改用户本次指定的接口。

执行要求：
1. 先在版本 `technical.md` 写明路径、字段、错误码、分页与幂等，确认后实施。
2. `handler` 只做参数解析、鉴权入口与状态码映射；业务规则进 `domain`，事务编排放 `application`。
3. 接口定义或注释变化后执行生成命令，生成物与源契约一起提交。
4. 端到端测试覆盖成功、参数错误、权限拒绝与幂等重复请求。
5. 同步更新 `docs/technical/` 的接口契约与错误码说明。

完成判定：生成命令无差异、端到端测试通过、接口路径与字段和文档一致。
