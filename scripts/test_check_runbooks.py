#!/usr/bin/env python3
"""check-runbooks.py 的测试：每个用例在临时目录构造最小仓库。"""
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "check-runbooks.py")

BASE = {
    "AGENTS.md": """# Agent

## 触发

| 场景 | 必读 |
| --- | --- |
| 改文档 | [a](runbooks/a.md) |
""",
    "runbooks/index.md": """# 索引

| 分组 | Runbook | 场景 |
| --- | --- | --- |
| test | [a.md](a.md) | A |
| test | [b.md](b.md) | B |
""",
    "runbooks/a.md": """# Runbook：A

## 适用场景

- 测试。

## 前置读取

- [B](b.md)

## 规则

- 规则。

## 步骤

1. 步骤。

## 验证

- 通过。
""",
    "runbooks/b.md": """# Runbook：B

## 适用场景

- 测试。

## 规则

- 规则。

## 步骤

1. 步骤。

## 验证

- 通过。
""",
}


def make_repo(overrides=None, extra=None):
    d = tempfile.mkdtemp(prefix="runbook-check-")
    files = dict(BASE)
    if overrides:
        files.update(overrides)
    if extra:
        files.update(extra)
    for name, content in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return d


def run(root):
    r = subprocess.run(
        [sys.executable, SCRIPT, "--root", root],
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


class CheckRunbooksTest(unittest.TestCase):
    def test_valid_repo_passes(self):
        code, out = run(make_repo())
        self.assertEqual(code, 0, out)

    def test_unindexed_file_fails(self):
        code, out = run(make_repo(extra={"runbooks/c.md": BASE["runbooks/b.md"].replace("B", "C")}))
        self.assertEqual(code, 1, out)
        self.assertIn("索引", out)

    def test_dead_link_fails(self):
        a = BASE["runbooks/a.md"] + "\n[缺失](missing.md)\n"
        code, out = run(make_repo(overrides={"runbooks/a.md": a}))
        self.assertEqual(code, 1, out)
        self.assertIn("链接", out)

    def test_bad_anchor_fails(self):
        a = BASE["runbooks/a.md"] + "\n[锚点](b.md#不存在)\n"
        code, out = run(make_repo(overrides={"runbooks/a.md": a}))
        self.assertEqual(code, 1, out)
        self.assertIn("锚点", out)

    def test_cycle_fails(self):
        b = BASE["runbooks/b.md"].replace(
            "## 规则", "## 前置读取\n\n- [A](a.md)\n\n## 规则"
        )
        code, out = run(make_repo(overrides={"runbooks/b.md": b}))
        self.assertEqual(code, 1, out)
        self.assertIn("环", out)

    def test_missing_section_fails(self):
        a = BASE["runbooks/a.md"].split("## 验证")[0]
        code, out = run(make_repo(overrides={"runbooks/a.md": a}))
        self.assertEqual(code, 1, out)
        self.assertIn("章节", out)

    def test_placeholder_fails(self):
        a = BASE["runbooks/a.md"].replace("- 规则。", "- 规则：<说明文字，含标点>。")
        code, out = run(make_repo(overrides={"runbooks/a.md": a}))
        self.assertEqual(code, 1, out)
        self.assertIn("占位符", out)

    def test_trigger_path_missing_fails(self):
        agents = BASE["AGENTS.md"] + "\n| 缺失 | [x](runbooks/x.md) |\n"
        code, out = run(make_repo(overrides={"AGENTS.md": agents}))
        self.assertEqual(code, 1, out)
        self.assertIn("触发表", out)


if __name__ == "__main__":
    unittest.main()
