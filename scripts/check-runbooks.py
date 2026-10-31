#!/usr/bin/env python3
"""校验 runbook 仓库的结构、链接与前置依赖。退出码 0 表示通过。"""
import argparse
import importlib.util
import json
import os
import re
import sys


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w一-鿿 -]", "", s)
    return s.replace(" ", "-")


def hook_commands(node):
    """遍历 hooks.json，产出全部 command 字符串。"""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "command" and isinstance(value, str):
                yield value
            else:
                yield from hook_commands(value)
    elif isinstance(node, list):
        for value in node:
            yield from hook_commands(value)


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def markdown_files(root, sub):
    out = []
    for dp, _, fs in os.walk(os.path.join(root, sub)):
        for f in fs:
            if f.endswith(".md"):
                out.append(os.path.join(dp, f))
    return sorted(out)


def links(text):
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if link.startswith(("http", "mailto:", "#")):
            continue
        yield link


def headings(text):
    return {slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", text, re.M)}


def section(text, name):
    m = re.search(r"^## %s\n(.*?)(?=^## |\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1) if m else None


def without_frontmatter(text):
    """去掉 YAML frontmatter，只统计正文字数。"""
    return re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)


def main():
    ap = argparse.ArgumentParser(description="校验 runbook 仓库")
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    problems = []

    def bad(cat, path, msg):
        problems.append((cat, path, msg))

    runbooks = markdown_files(root, "runbooks")
    all_md = list(runbooks)
    for name in ("AGENTS.md", "README.md"):
        p = os.path.join(root, name)
        if os.path.exists(p):
            all_md.append(p)

    # 索引覆盖
    index_path = os.path.join(root, "runbooks", "index.md")
    index_text = read(index_path) if os.path.exists(index_path) else ""
    indexed = set()
    for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", index_text):
        indexed.add(os.path.normpath(os.path.join(os.path.dirname(index_path), link)))
    for p in runbooks:
        if os.path.basename(p) != "index.md" and os.path.normpath(p) not in indexed:
            bad("索引", rel(root, p), "未在 runbooks/index.md 登记")

    # 触发表
    agents = os.path.join(root, "AGENTS.md")
    if os.path.exists(agents):
        for m in re.findall(r"\(([^)#]*runbooks/[^)#]+\.md)(?:#[^)]*)?\)", read(agents)):
            if not os.path.exists(os.path.join(root, m)):
                bad("触发表", "AGENTS.md", "路径不存在: %s" % m)

    # 相对链接与锚点
    for p in all_md:
        text = read(p)
        for link in links(text):
            target, _, anchor = link.partition("#")
            if not target:
                continue
            t = os.path.normpath(os.path.join(os.path.dirname(p), target))
            if not os.path.exists(t):
                bad("链接", rel(root, p), "目标不存在: %s" % link)
                continue
            if anchor and os.path.isfile(t) and anchor.lower() not in headings(read(t)):
                bad("锚点", rel(root, p), "目标标题不存在: %s" % link)

    # 前置依赖图
    bypath = {os.path.normpath(p): p for p in runbooks}
    graph = {}
    for p in runbooks:
        deps = []
        seg = section(read(p), "前置读取")
        if seg:
            for link in links(seg):
                t = os.path.normpath(os.path.join(os.path.dirname(p), link.split("#")[0]))
                if t in bypath and t != os.path.normpath(p):
                    deps.append(t)
        graph[os.path.normpath(p)] = deps

    seen, stack, on_stack = set(), [], set()
    cycles = set()

    def dfs(node):
        seen.add(node)
        stack.append(node)
        on_stack.add(node)
        for nxt in graph[node]:
            if nxt not in seen:
                dfs(nxt)
            elif nxt in on_stack:
                cycles.add(tuple(sorted(stack[stack.index(nxt):])))
        stack.pop()
        on_stack.discard(node)

    for node in graph:
        if node not in seen:
            dfs(node)
    for cycle in cycles:
        bad("环", " / ".join(rel(root, bypath[n]) for n in cycle), "前置读取成环")

    def closure(start):
        out, todo = set(), list(graph[start])
        while todo:
            n = todo.pop()
            if n in out or n == start:
                continue
            out.add(n)
            todo.extend(graph[n])
        return out

    for node in graph:
        c = closure(node)
        lines = sum(len(without_frontmatter(read(x)).splitlines()) for x in c)
        if len(c) > 5 or lines > 500:
            bad("闭包", rel(root, bypath[node]), "递归前置 %d 篇 / %d 行，超过 5 篇 / 500 行" % (len(c), lines))

    # 必备章节
    for p in runbooks:
        if os.path.basename(p) in ("README.md", "index.md"):
            continue
        text = read(p)
        for name in ("适用场景", "步骤", "验证"):
            if section(text, name) is None:
                bad("章节", rel(root, p), "缺少 ## %s" % name)
        pre = section(text, "前置读取")
        if pre is not None and not re.search(r"^- \[", pre, re.M):
            bad("章节", rel(root, p), "前置读取段为空")

    # agent frontmatter 与生成物
    generator = os.path.join(root, "scripts", "generate_runbook_agents.py")
    if os.path.isfile(generator):
        spec = importlib.util.spec_from_file_location("generate_runbook_agents", generator)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        entries, errors = module.collect(root)
        for source, msg in errors:
            bad("agent", source, msg)
        if not errors:
            for source, msg in module.check(root, entries):
                bad("agent", source, msg)

    # 占位符：尖括号内出现中文标点，说明整句说明被当成取值
    for p in runbooks:
        for m in re.finditer(r"<[^>\n]*[，。；、][^>\n]*>", read(p)):
            bad("占位符", rel(root, p), "尖括号内含中文标点: %s" % m.group(0))

    # 插件清单与命令
    cmd_dir = os.path.join(root, "claude-commands")
    legacy_cmd_dir = os.path.join(root, ".claude", "commands")
    if os.path.isdir(cmd_dir) and os.path.isdir(legacy_cmd_dir):
        bad("命令", rel(root, cmd_dir), "与 .claude/commands 存在副本，只保留 claude-commands/")

    plugin_name = None
    if os.path.isdir(cmd_dir):
        plugin_path = os.path.join(root, ".claude-plugin", "plugin.json")
        market_path = os.path.join(root, ".claude-plugin", "marketplace.json")
        if not os.path.isfile(plugin_path):
            bad("插件", rel(root, plugin_path), "缺少 plugin.json")
        else:
            try:
                plugin_data = json.loads(read(plugin_path))
            except ValueError as e:
                bad("插件", rel(root, plugin_path), "不是合法 JSON: %s" % e)
            else:
                plugin_name = plugin_data.get("name")
                if not plugin_name:
                    bad("插件", rel(root, plugin_path), "缺少 name")
                if not plugin_data.get("license") and not os.path.isfile(os.path.join(root, "LICENSE")):
                    bad("插件", rel(root, plugin_path), "缺少许可证：plugin.json 的 license 或根 LICENSE 文件")
                for key in ("commands", "skills", "hooks"):
                    value = plugin_data.get(key)
                    paths = value if isinstance(value, list) else [value]
                    for item in paths:
                        if not isinstance(item, str):
                            continue
                        if not os.path.exists(os.path.normpath(os.path.join(root, item))):
                            bad("插件", rel(root, plugin_path), "%s 路径不存在: %s" % (key, item))
        if not os.path.isfile(market_path):
            bad("插件", rel(root, market_path), "缺少 marketplace.json")
        else:
            try:
                entries = json.loads(read(market_path)).get("plugins") or []
            except ValueError as e:
                bad("插件", rel(root, market_path), "不是合法 JSON: %s" % e)
            else:
                if not entries:
                    bad("插件", rel(root, market_path), "未登记插件")
                for entry in entries:
                    if not isinstance(entry, dict):
                        bad("插件", rel(root, market_path), "条目不是对象")
                        continue
                    if entry.get("name") != plugin_name:
                        bad("插件", rel(root, market_path),
                            "条目名与 plugin.json 不一致: %s" % entry.get("name"))
                    source = entry.get("source")
                    if not isinstance(source, str) or not source.startswith("./"):
                        bad("插件", rel(root, market_path), "source 必须以 ./ 开头: %s" % source)
                        continue
                    target = os.path.normpath(os.path.join(root, source))
                    if not os.path.isdir(target):
                        bad("插件", rel(root, market_path), "source 目标不存在: %s" % source)
                    elif os.path.normpath(target) != os.path.normpath(root) and not os.path.isfile(
                            os.path.join(target, ".claude-plugin", "plugin.json")):
                        bad("插件", rel(root, market_path), "source 目标缺少 plugin.json: %s" % source)

        for f in sorted(os.listdir(cmd_dir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(cmd_dir, f)
            text = read(p)
            if not re.match(r"---\n.*?description:", text, re.S):
                bad("命令", rel(root, p), "缺少 description")
            if "@runbooks/" in text:
                bad("命令引用", rel(root, p), "插件内需用 @${CLAUDE_PLUGIN_ROOT}/runbooks/")
            for m in re.findall(r"@\$\{CLAUDE_PLUGIN_ROOT\}/(runbooks/[^\s)`]+\.md)", text):
                if not os.path.exists(os.path.join(root, m)):
                    bad("命令引用", rel(root, p), "目标不存在: %s" % m)

    # Codex 清单、命令与 marketplace
    codex_plugin_path = os.path.join(root, ".codex-plugin", "plugin.json")
    codex_cmd_dir = os.path.join(root, "codex-commands")
    if os.path.isfile(codex_plugin_path):
        try:
            codex_data = json.loads(read(codex_plugin_path))
        except ValueError as e:
            bad("Codex", rel(root, codex_plugin_path), "不是合法 JSON: %s" % e)
        else:
            if plugin_name and codex_data.get("name") != plugin_name:
                bad("Codex", rel(root, codex_plugin_path),
                    "name 与 plugin.json 不一致: %s" % codex_data.get("name"))
            for key in ("skills", "commands", "hooks"):
                value = codex_data.get(key)
                for item in (value if isinstance(value, list) else [value]):
                    if not isinstance(item, str) or not item.startswith("./"):
                        continue
                    if not os.path.exists(os.path.normpath(os.path.join(root, item))):
                        bad("Codex", rel(root, codex_plugin_path), "%s 路径不存在: %s" % (key, item))
    if os.path.isdir(codex_cmd_dir):
        for f in sorted(os.listdir(codex_cmd_dir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(codex_cmd_dir, f)
            text = read(p)
            if not re.match(r"---\n.*?description:", text, re.S):
                bad("Codex 命令", rel(root, p), "缺少 description")
            body = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
            for token in ("$ARGUMENTS", "{{", "}}", "!`", "! `"):
                if token in body:
                    bad("Codex 命令", rel(root, p), "含 Codex 跳过的 %s" % token)
            if re.search(r"\$\d", body):
                bad("Codex 命令", rel(root, p), "含编号占位符")
            if re.search(r"(^|\s)@\S", body):
                bad("Codex 命令", rel(root, p), "含 @ 开头的 token")

    codex_market_path = os.path.join(root, ".agents", "plugins", "marketplace.json")
    if os.path.isfile(codex_market_path):
        try:
            codex_market = json.loads(read(codex_market_path))
        except ValueError as e:
            bad("Codex", rel(root, codex_market_path), "不是合法 JSON: %s" % e)
        else:
            entries = codex_market.get("plugins") or []
            if not entries:
                bad("Codex", rel(root, codex_market_path), "未登记插件")
            for entry in entries:
                if not isinstance(entry, dict):
                    bad("Codex", rel(root, codex_market_path), "条目不是对象")
                    continue
                if plugin_name and entry.get("name") != plugin_name:
                    bad("Codex", rel(root, codex_market_path),
                        "条目名与 plugin.json 不一致: %s" % entry.get("name"))
                source = entry.get("source") or {}
                if source.get("source") not in ("url", "git-subdir", "local"):
                    bad("Codex", rel(root, codex_market_path),
                        "source 类型不受支持: %s" % source.get("source"))

    # 插件钩子引用
    hooks_path = os.path.join(root, "hooks", "hooks.json")
    if os.path.isfile(hooks_path):
        text = read(hooks_path)
        try:
            data = json.loads(text)
        except ValueError as e:
            bad("钩子", rel(root, hooks_path), "不是合法 JSON: %s" % e)
        else:
            for command in hook_commands(data):
                for m in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s\"']+)", command):
                    target = os.path.join(root, m)
                    if not os.path.exists(target):
                        bad("钩子", rel(root, hooks_path), "目标不存在: %s" % m)
                    elif not os.access(target, os.X_OK):
                        bad("钩子", rel(root, hooks_path), "目标不可执行: %s" % m)

    for cat, path, msg in sorted(problems):
        print("[%s] %s: %s" % (cat, path, msg))
    print("问题: %d" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
