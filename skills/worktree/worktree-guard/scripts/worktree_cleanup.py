#!/usr/bin/env python3
"""列出 worktree 与任务分支的收尾状态。

用法：worktree_cleanup.py [--base BRANCH] [--check]
  --base   基线分支，缺省 develop，其次 main
  --check  存在未清理的任务 worktree 或已合并任务分支时退出 1

输出每项一行，供交付收尾核对；规则见 runbooks/implementation/worktree.md。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def git(*args, cwd=None):
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise SystemExit(f"worktree 收尾: git {' '.join(args)} 失败: {result.stderr.strip()}")
    return result.stdout


def repo_root():
    result = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).parent
    return Path(git("rev-parse", "--git-common-dir").strip()).resolve().parent


def parse_worktrees(root):
    entries = []
    current = {}
    for line in git("worktree", "list", "--porcelain", cwd=root).splitlines():
        if not line:
            if current:
                entries.append(current)
            current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        entries.append(current)
    return entries


def branch_list(root, base):
    branches = {}
    for name in git("for-each-ref", "--format=%(refname:short)", "refs/heads/", cwd=root).split():
        merged = subprocess.run(
            ["git", "merge-base", "--is-ancestor", name, base], cwd=root
        ).returncode == 0
        branches[name] = merged
    return branches


def main(argv):
    parser = argparse.ArgumentParser(description="列出 worktree 与任务分支的收尾状态")
    parser.add_argument("--base", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    root = repo_root()
    base = args.base
    if not base:
        available = git("for-each-ref", "--format=%(refname:short)", "refs/heads/", cwd=root).split()
        base = "develop" if "develop" in available else ("main" if "main" in available else "")

    worktrees = parse_worktrees(root)
    main_path = Path(worktrees[0]["worktree"]).resolve() if worktrees else root
    others = [w for w in worktrees[1:]] if worktrees else []

    branches = branch_list(root, base) if base else {}
    checked_out = {w.get("branch", "").replace("refs/heads/", "") for w in worktrees}

    # 与 worktree_create.sh 的 branch_prefixes 保持一致。
    prefixes = (
        "feature/",
        "fix/",
        "hotfix/",
        "chore/",
        "docs/",
        "refactor/",
        "test/",
        "perf/",
        "ci/",
        "build/",
        "release/",
    )
    residual_worktrees = []
    residual_branches = []
    for entry in others:
        path = Path(entry["worktree"])
        branch = entry.get("branch", "").replace("refs/heads/", "") or "游离 HEAD"
        status = "已合并" if entry.get("branch") and branches.get(branch) else "未合并"
        print(f"worktree {path} {branch} {status}")
        residual_worktrees.append(path)

    for name, merged in sorted(branches.items()):
        if name in checked_out or name in (base, "main", "develop"):
            continue
        if merged:
            print(f"branch {name} 已合并（可删除）")
            if name.startswith(prefixes):
                residual_branches.append(name)
        else:
            print(f"branch {name} 未合并")

    if not others and not residual_branches:
        print(f"worktree 收尾: 干净（基线 {base or '无'}）")

    if args.check and (residual_worktrees or residual_branches):
        targets = [str(p) for p in residual_worktrees] + residual_branches
        print(f"worktree 收尾: 存在残留 {len(targets)} 项", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
