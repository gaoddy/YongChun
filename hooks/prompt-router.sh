#!/bin/sh
# UserPromptSubmit 只注入场景判定入口，规则本体见 task-delivery.md。
root=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
printf '修改类请求先按 %s/runbooks/implementation/task-delivery.md 的「场景判定」路由；只读问答不触发。\n' "$root"
