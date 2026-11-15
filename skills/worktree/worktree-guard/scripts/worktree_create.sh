#!/bin/sh
# 唯一允许的 worktree 创建入口。规则见 runbooks/implementation/worktree.md。
#
# 用法：worktree_create.sh <branch> [base] [--root DIR]
#   branch  任务分支名，需带配置或默认白名单中的前缀
#   base    基线分支，缺省为队列配置的 project.base_branch，再缺省为 develop
#   --root  worktree 根目录，缺省为 <repo>/.worktrees
#
# 成功时把新建 worktree 的绝对路径打印到 stdout；失败时退出码非 0，原因写到 stderr。

set -eu

usage() {
    printf '用法: %s <branch> [base] [--root DIR]\n' "$(basename "$0")" >&2
    exit 2
}

die() {
    printf '%s\n' "$1" >&2
    exit 1
}

branch=""
base=""
root=""
while [ $# -gt 0 ]; do
    case "$1" in
        --root)
            [ $# -ge 2 ] || usage
            root="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            usage
            ;;
        *)
            if [ -z "$branch" ]; then
                branch="$1"
            elif [ -z "$base" ]; then
                base="$1"
            else
                usage
            fi
            shift
            ;;
    esac
done
[ -n "$branch" ] || usage

# 1) 必须在 git 仓库内执行
repo=$(git rev-parse --show-toplevel 2>/dev/null) || die "不在 git 仓库内执行"
cd "$repo"

# 2) 读取队列配置（存在时）
config=""
for candidate in "$repo/.yongchun/worktree-merge-queue.toml" \
                 "$repo/.codex/worktree-merge-queue-delivery.toml"; do
    if [ -f "$candidate" ]; then
        config="$candidate"
        break
    fi
done

read_config() {
    awk -v want_section="$2" -v want_key="$3" '
        /^[[:space:]]*#/ { next }
        /^[[:space:]]*\[/ {
            section = $0
            gsub(/[][[:space:]]/, "", section)
            next
        }
        section == want_section {
            pos = index($0, "=")
            if (pos == 0) next
            key = substr($0, 1, pos - 1)
            value = substr($0, pos + 1)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", key)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
            gsub(/^"|"$/, "", value)
            if (key == want_key) {
                print value
                exit
            }
        }
    ' "$1"
}

config_base=""
config_prefix=""
if [ -n "$config" ]; then
    config_base=$(read_config "$config" project base_branch)
    config_prefix=$(read_config "$config" project branch_prefix)
fi

[ -n "$base" ] || base="${config_base:-develop}"

# 3) 基线必须存在
git rev-parse --verify --quiet "$base^{commit}" >/dev/null \
    || die "基线分支不存在: $base"

# 4) 分支名合法，且前缀在白名单内
git check-ref-format --branch "$branch" >/dev/null 2>&1 \
    || die "分支名非法: $branch"

if [ -n "$config_prefix" ]; then
    case "$branch" in
        "$config_prefix"*) ;;
        *) die "分支必须带队列配置的 project.branch_prefix 前缀: $config_prefix" ;;
    esac
else
    case "$branch" in
        feature/*|fix/*|claude/*) ;;
        *) die "分支必须带前缀: feature/ fix/ claude/" ;;
    esac
fi

# 5) 工作区必须干净，避免把未提交改动带进 worktree 判定
if [ -n "$(git status --porcelain)" ]; then
    die "工作区不干净，先提交或清理改动再创建 worktree"
fi

# 6) 目标路径不能已存在
[ -n "$root" ] || root="$repo/.worktrees"
slug=$(printf '%s' "$branch" | tr '/' '-')
target="$root/$slug"
[ ! -e "$target" ] || die "目标目录已存在: $target"

# 7) worktree 根必须在忽略范围内，避免污染 git status
relative_root=${root#"$repo"/}
if [ "$relative_root" != "$root" ]; then
    git check-ignore --quiet -- "$relative_root/probe" \
        || die "worktree 目录未被忽略，先把 /$relative_root/ 写入 .gitignore"
fi
mkdir -p "$root"

# 8) 创建：已有分支直接挂载，否则从基线新建
if git show-ref --verify --quiet "refs/heads/$branch"; then
    git worktree add "$target" "$branch" >&2
else
    git worktree add -b "$branch" "$target" "$base" >&2
fi

printf '%s\n' "$target"
