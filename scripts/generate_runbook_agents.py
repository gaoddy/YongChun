#!/usr/bin/env python3
"""从 runbook frontmatter 生成 Claude Code 与 Codex agent。退出码 0 表示成功。"""
import argparse
import json
import os
import re
import sys

LEVELS = ("low", "high", "xhigh")
FRONTMATTER = re.compile(r"\A---\nagent:\n  effort: ([a-z]+)\n---\n")
TITLE = re.compile(r"^#\s+(.+?)\s*$", re.M)
BULLET = re.compile(r"^-\s+(.+)$", re.M)
NAME = re.compile(r"\A[a-z0-9][a-z0-9-]*\Z")
TITLE_PREFIX = re.compile(r"^Runbook[：:]\s*")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def runbook_files(root):
    out = []
    base = os.path.join(root, "runbooks")
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith(".md") and f not in ("README.md", "index.md"):
                out.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    return sorted(out)


def section(text, name):
    m = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1) if m else None


def describe(rel, text):
    """返回 (title, description)。"""
    m = TITLE.search(text)
    if not m:
        raise ValueError("缺少 # 标题")
    title = TITLE_PREFIX.sub("", m.group(1).strip())
    usage = section(text, "适用场景")
    if not usage:
        raise ValueError("缺少 ## 适用场景")
    b = BULLET.search(usage)
    if not b:
        raise ValueError("## 适用场景 没有列表项")
    bullet = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b.group(1))
    bullet = re.sub(r"\s+", " ", bullet).strip().rstrip("。")
    desc = "%s：%s" % (title, bullet) if bullet else title
    return title, (desc[:200] + "…") if len(desc) > 200 else desc


def agent_names(files):
    """basename 唯一时用 basename，重名时用最短可区分的父目录后缀。"""
    stems = {rel: rel[len("runbooks/"):-len(".md")] for rel in files}
    counts = {}
    for stem in stems.values():
        base = os.path.basename(stem)
        counts[base] = counts.get(base, 0) + 1
    names = {}
    for rel, stem in stems.items():
        if counts[os.path.basename(stem)] == 1:
            names[rel] = os.path.basename(stem)
            continue
        parts = stem.split("/")
        for k in range(2, len(parts) + 1):
            cand = "-".join(parts[-k:])
            same = sum(1 for s in stems.values() if "-".join(s.split("/")[-k:]) == cand)
            if same == 1:
                names[rel] = cand
                break
        else:
            names[rel] = stem.replace("/", "-")
    return names


def claude_content(stem, name, desc, effort):
    return """---
name: %s
description: %s
effort: %s
---

<!-- 由 scripts/generate_runbook_agents.py 根据 runbooks/%s.md 生成，不要手改。 -->

按插件根目录下的 `runbooks/%s.md` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录见环境变量 `CLAUDE_PLUGIN_ROOT`；在本仓库内执行时为仓库根目录。
""" % (name, json.dumps(desc, ensure_ascii=False), effort, stem, stem)


def codex_content(stem, name, desc, effort):
    return """# 由 scripts/generate_runbook_agents.py 根据 runbooks/%s.md 生成，不要手改。

name = %s
description = %s
model_reasoning_effort = %s

developer_instructions = \"\"\"
先读取项目 AGENTS.md 声明的 runbook 仓库中的 `runbooks/%s.md`，再按该文「前置读取」补齐上游。

1. 只处理本次请求；范围、判定与产物以该 runbook 为准。
2. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。
\"\"\"
""" % (
        stem,
        json.dumps(name, ensure_ascii=False),
        json.dumps(desc, ensure_ascii=False),
        json.dumps(effort, ensure_ascii=False),
        stem,
    )


def collect(root):
    """返回 (entries, errors)。entries 含生成路径与内容。"""
    files = runbook_files(root)
    names = agent_names(files)

    entries, errors, used = [], [], {}
    for rel in files:
        try:
            text = read(os.path.join(root, rel))
            m = FRONTMATTER.match(text)
            if not m:
                raise ValueError("缺少 agent.effort frontmatter")
            effort = m.group(1)
            if effort not in LEVELS:
                raise ValueError("agent.effort 取值非法: %s" % effort)
            title, desc = describe(rel, text)
            name = names[rel]
            if not NAME.match(name):
                raise ValueError("agent 名称非法: %s" % name)
            if name in used:
                raise ValueError("agent 名称重复: %s 与 %s" % (name, used[name]))
            used[name] = rel
            stem = rel[len("runbooks/"):-len(".md")]
            entries.append({
                "source": rel,
                "name": name,
                "effort": effort,
                "title": title,
                "description": desc,
                "claude_path": "agents/%s.md" % name,
                "claude": claude_content(stem, name, desc, effort),
                "codex_path": "codex-agents/%s.toml" % name,
                "codex": codex_content(stem, name, desc, effort),
            })
        except ValueError as e:
            errors.append((rel, str(e)))
    return entries, errors


def expected_files(entries):
    out = {}
    for e in entries:
        out[e["claude_path"]] = e["claude"]
        out[e["codex_path"]] = e["codex"]
    return out


def check(root, entries):
    """返回 [(路径, 说明)]，空列表表示无漂移。"""
    problems = []
    expected = expected_files(entries)
    for rel, content in sorted(expected.items()):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            problems.append((rel, "缺少生成物"))
        elif read(path) != content:
            problems.append((rel, "内容与 runbook 不一致"))
    for sub in ("agents", "codex-agents"):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            rel = "%s/%s" % (sub, f)
            if os.path.isfile(os.path.join(d, f)) and rel not in expected:
                problems.append((rel, "多余文件"))
    return problems


def write(root, entries):
    expected = expected_files(entries)
    for rel, content in sorted(expected.items()):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        current = read(path) if os.path.isfile(path) else None
        if current != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
    removed = 0
    for sub in ("agents", "codex-agents"):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            rel = "%s/%s" % (sub, f)
            path = os.path.join(d, f)
            if os.path.isfile(path) and rel not in expected:
                os.remove(path)
                removed += 1
    return len(expected), removed


def install_codex(root, entries, project):
    dest = os.path.join(os.path.abspath(project), ".codex", "agents")
    os.makedirs(dest, exist_ok=True)
    for e in entries:
        with open(os.path.join(dest, "%s.toml" % e["name"]), "w", encoding="utf-8") as f:
            f.write(e["codex"])
    return len(entries), dest


def main(argv=None):
    ap = argparse.ArgumentParser(description="从 runbook frontmatter 生成两端 agent")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--check", action="store_true", help="只检查漂移，不写文件")
    ap.add_argument("--install-codex", metavar="DIR", help="把 Codex agent 安装到项目的 .codex/agents/")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    entries, errors = collect(root)
    if errors:
        for rel, msg in errors:
            print("agent 错误: %s: %s" % (rel, msg))
        return 1

    if args.check:
        problems = check(root, entries)
        for rel, msg in problems:
            print("agent 漂移: %s: %s" % (rel, msg))
        if problems:
            return 1
        print("agent 检查通过：%d 个 runbook，%d 个生成物" % (len(entries), len(entries) * 2))
        return 0

    total, removed = write(root, entries)
    print("已生成 %d 个生成物（%d 个 runbook），删除多余文件 %d 个" % (total, len(entries), removed))
    if args.install_codex:
        count, dest = install_codex(root, entries, args.install_codex)
        print("已安装 %d 个 Codex agent 到 %s" % (count, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
