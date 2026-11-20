#!/bin/sh
# Claude Code PreToolUse 守卫：拦住绕过 worktree_create.sh 的 git worktree 调用。
# 规则见 runbooks/implementation/worktree.md；钩子配置见 runbooks/implementation/worktree.md 的「守卫」小节。
#
# 输入：stdin 的 Claude Code 钩子 JSON（tool_name、tool_input.command、cwd）。
# 输出：放行时不打印任何内容；拒绝时打印 permissionDecision=deny 的 JSON。

set -eu

deny() {
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
    exit 0
}

payload=$(cat || true)
[ -n "$payload" ] || exit 0

separator=$(printf '\037')
fields=$(printf '%s' "$payload" | python3 -c '
import json
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
tool = data.get("tool_name") or ""
cwd = data.get("cwd") or ""
command = (data.get("tool_input") or {}).get("command") or ""
sys.stdout.write("\x1f".join([tool, cwd, command]))
' 2>/dev/null) || exit 0

tool=${fields%%"$separator"*}
rest=${fields#*"$separator"}
cwd=${rest%%"$separator"*}
command=${rest#*"$separator"}

[ "$tool" = "Bash" ] || exit 0
[ -n "$command" ] || exit 0

# 只处理真正的 git worktree 调用；引号内容与 grep 模式不算
subcommand=$(printf '%s' "$command" | python3 -c '
import shlex
import sys

SUBCOMMANDS = {"add", "remove", "move", "prune", "repair", "lock", "unlock", "list"}
CONTROL = {";", "&&", "||", "|", "&", "(", ")", ">", "<", ">>", "2>", "\n"}

try:
    lexer = shlex.shlex(sys.argv[1], posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = list(lexer)
except ValueError:
    tokens = sys.argv[1].split()

found = "none"
index = 0
while index < len(tokens):
    token = tokens[index]
    if token == "git" or token.endswith("/git"):
        end = index + 1
        args = []
        while end < len(tokens) and tokens[end] not in CONTROL:
            args.append(tokens[end])
            end += 1
        if "worktree" in args:
            position = args.index("worktree")
            rest = [item for item in args[position + 1:] if not item.startswith("-")]
            if rest and rest[0] in SUBCOMMANDS:
                found = rest[0]
                break
        index = end
        continue
    index += 1
print(found)
' "$command" 2>/dev/null) || exit 0

case "$subcommand" in
    none)
        exit 0
        ;;
    list|prune)
        exit 0
        ;;
    add)
        case "$command" in
            *worktree_create.sh*)
                exit 0
                ;;
            *)
                deny "worktree 必须通过 worktree_create.sh 创建，见 yongchun runbooks/implementation/worktree.md。改用 skills/worktree/worktree-guard/scripts/worktree_create.sh <branch> [base]，不要直接调用 git worktree add。"
                ;;
        esac
        ;;
esac

# remove / move / repair / lock / unlock：只允许操作 <repo>/.worktrees 下的 worktree。
# 仓库根按目标路径所属的主仓库判定，路径不可定位时退回 cwd 所属仓库；在 worktree 内执行时同样按主仓库校验。
[ -n "$cwd" ] || cwd="."

repo_root_of() {
    common=$(git -C "$1" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || return 1
    [ -n "$common" ] || return 1
    dirname "$common"
}

fallback_repo=$(repo_root_of "$cwd" 2>/dev/null) || fallback_repo=""

paths=$(printf '%s' "$command" | python3 -c '
import shlex
import sys

CONTROL = {";", "&&", "||", "|", "&", "(", ")", ">", "<", ">>", "2>", "\n"}

try:
    lexer = shlex.shlex(sys.argv[1], posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = list(lexer)
except ValueError:
    tokens = sys.argv[1].split()

if "worktree" not in tokens:
    raise SystemExit(0)
position = tokens.index("worktree")
for token in tokens[position + 2:]:
    if token in CONTROL:
        break
    if not token.startswith("-"):
        print(token)
' "$command" 2>/dev/null) || exit 0

[ -n "$paths" ] || deny "无法从命令中解析 worktree 路径，拒绝执行 git worktree $subcommand。"

while IFS= read -r path; do
    [ -n "$path" ] || continue
    resolved=$(python3 -c '
import os
import sys

print(os.path.realpath(os.path.join(sys.argv[1], sys.argv[2])))
' "$cwd" "$path" 2>/dev/null) || continue
    repo=$(repo_root_of "$resolved" 2>/dev/null) || repo="$fallback_repo"
    [ -n "$repo" ] || continue
    root="$repo/.worktrees"
    if [ "$(dirname "$resolved")" = "$root" ]; then
        continue
    fi
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"只允许操作 %s 下的 worktree，命令中的路径是 %s。"}}\n' "$root" "$resolved"
    exit 0
done <<EOF
$paths
EOF

exit 0
