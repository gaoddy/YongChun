#!/bin/sh
# 清理目录源安装复制进插件缓存的运行时目录。
# 规则见 runbooks/delivery/version-release.md 的「本仓库插件发版」。
#
# 本地目录市场同步按插件根目录整目录复制，只按 .gitignore 排除 /.worktrees/，
# 其余忽略目录（.claude/、output/、__pycache__/ 等）仍会进入缓存副本。
set -u

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
config_dir=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
manifest=$root/.claude-plugin/plugin.json

version=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$manifest" | head -n 1)
if [ -z "$version" ]; then
    echo "清理插件缓存: 无法从 $manifest 读取版本号" >&2
    exit 1
fi

cache=$config_dir/plugins/cache/yongchun/yongchun/$version
if [ ! -d "$cache" ]; then
    echo "清理插件缓存: 未找到 $cache，跳过" >&2
    exit 0
fi

for dir in .worktrees .claude output tmp docs/plan; do
    rm -rf "${cache:?}/$dir"
done

find "$cache" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
find "$cache" -type f \( -name .DS_Store -o -name '*.log' \) -delete 2>/dev/null

if [ -e "$cache/.worktrees" ]; then
    echo "清理插件缓存: $cache/.worktrees 仍存在" >&2
    exit 1
fi

echo "清理插件缓存: 已清理 $cache"
