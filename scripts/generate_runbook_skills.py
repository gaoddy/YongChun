#!/usr/bin/env python3
"""从 runbook frontmatter 生成双端 skill 薄壳。退出码 0 表示成功。"""
import argparse
import importlib.util
import json
import os
import sys

GROUP = "skills/runbooks"
MARKER = "由 scripts/generate_runbook_skills.py 根据"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_agents(root):
    """加载 root/scripts/generate_runbook_agents.py，复用其 frontmatter 与描述解析。"""
    path = os.path.join(root, "scripts", "generate_runbook_agents.py")
    if not os.path.isfile(path):
        raise RuntimeError("找不到 %s，无法解析 runbook frontmatter" % path)
    spec = importlib.util.spec_from_file_location("generate_runbook_agents_for_skills", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skill_content(source, name, desc):
    return """---
name: %s
description: %s
---

<!-- 由 scripts/generate_runbook_skills.py 根据 %s 生成，不要手改。 -->

当任务符合本技能描述时，按本文件相对路径 `../../../%s` 执行。

1. 先读完该 runbook，再按「前置读取」补齐上游。
2. 只处理本次请求；范围、判定与产物以该 runbook 为准。
3. 按「步骤」执行，按「验证」判定；验证未通过不得声称完成。

插件根目录在 Claude Code 为 `${CLAUDE_PLUGIN_ROOT}`，在 Codex 为插件安装目录；在本仓库内执行时为仓库根目录。
""" % (name, json.dumps(desc, ensure_ascii=False), source, source)


def collect(root):
    """返回 (entries, errors)。entries 只含 skill_enabled 的 runbook。"""
    agents = load_agents(root)
    agent_entries, errors = agents.collect(root)
    entries = []
    for e in agent_entries:
        if not e["skill_enabled"]:
            continue
        entries.append({
            "source": e["source"],
            "name": e["name"],
            "path": "%s/%s/SKILL.md" % (GROUP, e["name"]),
            "content": skill_content(e["source"], e["name"], e["description"]),
        })
    return entries, errors


def expected_files(entries):
    return {e["path"]: e["content"] for e in entries}


def generated_files(root):
    """返回 skills/runbooks/ 下带生成标记的 SKILL.md 相对路径。"""
    base = os.path.join(root, GROUP)
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        rel = "%s/%s/SKILL.md" % (GROUP, name)
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        try:
            text = read(path)
        except (OSError, UnicodeDecodeError):
            continue
        if MARKER in text:
            out.append(rel)
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
    for rel in generated_files(root):
        if rel not in expected:
            problems.append((rel, "多余文件"))
    return problems


def write(root, entries):
    """写入差异文件，删除多余生成物；返回 (written, removed)。"""
    expected = expected_files(entries)
    written = 0
    for rel, content in sorted(expected.items()):
        path = os.path.join(root, rel)
        current = read(path) if os.path.isfile(path) else None
        if current != content:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            written += 1
    removed = 0
    for rel in generated_files(root):
        if rel in expected:
            continue
        path = os.path.join(root, rel)
        os.remove(path)
        removed += 1
        parent = os.path.dirname(path)
        if not os.listdir(parent):
            os.rmdir(parent)
    base = os.path.join(root, GROUP)
    if os.path.isdir(base) and not os.listdir(base):
        os.rmdir(base)
    return written, removed


def main(argv=None):
    ap = argparse.ArgumentParser(description="从 runbook frontmatter 生成双端 skill 薄壳")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--check", action="store_true", help="只检查漂移，不写文件")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    try:
        entries, errors = collect(root)
    except RuntimeError as e:
        print("skill 错误: %s" % e)
        return 1
    if errors:
        for rel, msg in errors:
            print("runbook 错误: %s: %s" % (rel, msg))
        return 1

    if args.check:
        problems = check(root, entries)
        for rel, msg in problems:
            print("skill 漂移: %s: %s" % (rel, msg))
        if problems:
            return 1
        print("skill 检查通过：%d 个启用项，%d 个生成物" % (len(entries), len(entries)))
        return 0

    written, removed = write(root, entries)
    print("skill 已同步：%d 个启用项，写入变更 %d 个，删除多余文件 %d 个" % (
        len(entries), written, removed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
