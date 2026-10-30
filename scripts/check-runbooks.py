#!/usr/bin/env python3
"""校验 runbook 仓库的结构、链接与前置依赖。退出码 0 表示通过。"""
import argparse
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
        lines = sum(len(read(x).splitlines()) for x in c)
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

    # 占位符：尖括号内出现中文标点，说明整句说明被当成取值
    for p in runbooks:
        for m in re.finditer(r"<[^>\n]*[，。；、][^>\n]*>", read(p)):
            bad("占位符", rel(root, p), "尖括号内含中文标点: %s" % m.group(0))

    # 命令引用
    cmd_dir = os.path.join(root, ".claude", "commands")
    if os.path.isdir(cmd_dir):
        for f in sorted(os.listdir(cmd_dir)):
            if not f.endswith(".md"):
                continue
            p = os.path.join(cmd_dir, f)
            text = read(p)
            if not re.match(r"---\n.*?description:", text, re.S):
                bad("命令", rel(root, p), "缺少 description")
            for m in re.findall(r"@(runbooks/[^\s)`]+\.md)", text):
                if not os.path.exists(os.path.join(root, m)):
                    bad("命令引用", rel(root, p), "目标不存在: %s" % m)

    for cat, path, msg in sorted(problems):
        print("[%s] %s: %s" % (cat, path, msg))
    print("问题: %d" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
