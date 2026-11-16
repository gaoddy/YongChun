#!/usr/bin/env python3
"""插件安装后自检：源码清单与已安装缓存是否一致。

用法：python3 scripts/plugin_selfcheck.py [--source-root DIR] [--cache-root DIR] [--require-installed]

检查项：
- 双端清单声明的版本一致，声明的技能组目录存在且各含 SKILL.md；
- `skills/` 下每个分组目录都在清单中声明；
- 命令目录存在且至少有一个命令文件；
- 已安装缓存版本目录与清单版本一致，必需文件存在，不含运行时目录。

退出码 0 表示通过，1 表示发现问题。规则见 runbooks/delivery/version-release.md。
"""

import argparse
import json
import os
import sys
from pathlib import Path

FORBIDDEN_IN_CACHE = (".git", ".worktrees", ".claude", "output", "docs/plan", "__pycache__")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"插件自检: 无法解析 {path}: {exc}")


def manifest_paths(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def skill_dirs(root, entry):
    group = (root / entry).resolve()
    if (group / "SKILL.md").is_file():
        return [group]
    if not group.is_dir():
        return []
    return sorted(p for p in group.iterdir() if (p / "SKILL.md").is_file())


def command_files(root, value):
    files = []
    for entry in manifest_paths(value):
        target = (root / entry).resolve()
        if target.is_dir():
            files.extend(sorted(target.glob("*.md")))
        elif target.is_file():
            files.append(target)
    return files


def check_source(root):
    problems = []
    claude = load_json(root / ".claude-plugin/plugin.json")
    codex = load_json(root / ".codex-plugin/plugin.json")
    if not claude:
        return ["缺少 .claude-plugin/plugin.json"]
    if not codex:
        return ["缺少 .codex-plugin/plugin.json"]
    if claude.get("version") != codex.get("version"):
        problems.append(
            f"双端版本不一致: claude={claude.get('version')} codex={codex.get('version')}"
        )

    declared = set()
    for entry in manifest_paths(claude.get("skills")):
        declared.add((root / entry).resolve())
        if not skill_dirs(root, entry):
            problems.append(f"技能组没有 SKILL.md: {entry}")

    skills_root = root / "skills"
    if skills_root.is_dir():
        for group in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            if group.resolve() not in declared:
                problems.append(f"技能组未在清单声明: skills/{group.name}/")

    for label, value in (("claude", claude.get("commands")), ("codex", codex.get("commands"))):
        files = command_files(root, value)
        if not files:
            problems.append(f"{label} 命令目录为空或不存在: {value}")

    hooks = codex.get("hooks")
    if hooks and not (root / hooks).is_file():
        problems.append(f"钩子文件不存在: {hooks}")
    return problems


def cache_dirs(cache_root, plugin, version):
    if not cache_root.is_dir():
        return []
    return sorted(p for p in cache_root.glob(f"*/{plugin}/{version}") if p.is_dir())


def check_cache(cache, root, claude, codex):
    problems = []
    for entry in FORBIDDEN_IN_CACHE:
        if (cache / entry).exists():
            problems.append(f"{cache}: 不应包含 {entry}")

    required = ("runbooks/index.md", "hooks/hooks.json")
    for entry in required:
        if not (cache / entry).is_file():
            problems.append(f"{cache}: 缺少 {entry}")

    for entry in manifest_paths(claude.get("skills")):
        cached = skill_dirs(cache, entry)
        if len(cached) != len(skill_dirs(root, entry)):
            problems.append(f"{cache}: 技能组不完整 {entry}")

    for label, value in (("claude", claude.get("commands")), ("codex", codex.get("commands"))):
        if len(command_files(cache, value)) != len(command_files(root, value)):
            problems.append(f"{cache}: {label} 命令文件与源码不一致")
    return problems


def main(argv):
    parser = argparse.ArgumentParser(description="插件安装后自检")
    parser.add_argument("--source-root", default=Path(__file__).resolve().parent.parent)
    parser.add_argument(
        "--cache-root",
        default=Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "plugins/cache",
    )
    parser.add_argument("--require-installed", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.source_root).resolve()
    problems = check_source(root)
    claude = load_json(root / ".claude-plugin/plugin.json") or {}
    codex = load_json(root / ".codex-plugin/plugin.json") or {}
    version = claude.get("version", "")

    caches = cache_dirs(Path(args.cache_root).resolve(), claude.get("name", "yongchun"), version)
    if not caches and args.require_installed:
        problems.append(f"未找到已安装缓存: {args.cache_root}/*/{claude.get('name')}/{version}")
    for cache in caches:
        problems.extend(check_cache(cache, root, claude, codex))

    if problems:
        for item in problems:
            print(f"问题: {item}")
        return 1
    suffix = f"（已检查缓存 {len(caches)} 处）" if caches else "（未安装缓存，跳过）"
    print(f"插件自检: ok 版本 {version}{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
