#!/usr/bin/env python3
"""generate_runbook_agents.py 的测试：每个用例在临时目录构造最小仓库。"""
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "generate_runbook_agents.py")


def fixture(title="A", effort="high"):
    return """---
agent:
  effort: %s
---

# Runbook：%s

## 适用场景

- 处理 %s 场景。

## 规则

- 规则。

## 步骤

1. 步骤。

## 验证

- 通过。
""" % (effort, title, title)


def make_repo(files):
    d = tempfile.mkdtemp(prefix="runbook-agent-")
    for name, content in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return d


def run(root, *args):
    r = subprocess.run(
        [sys.executable, SCRIPT, "--root", root] + list(args),
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


def read(root, name):
    with open(os.path.join(root, name), encoding="utf-8") as f:
        return f.read()


class GenerateAgentsTest(unittest.TestCase):
    def test_generate_and_check(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        code, out = run(root)
        self.assertEqual(code, 0, out)
        claude = read(root, "agents/a.md")
        self.assertIn("name: a", claude)
        self.assertIn('description: "A：处理 A 场景"', claude)
        self.assertIn("effort: high", claude)
        self.assertIn("runbooks/a.md", claude)
        codex = read(root, "codex-agents/a.toml")
        self.assertIn('name = "a"', codex)
        self.assertIn('model_reasoning_effort = "high"', codex)
        code, out = run(root, "--check")
        self.assertEqual(code, 0, out)

    def test_check_detects_content_drift(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        self.assertEqual(run(root)[0], 0)
        with open(os.path.join(root, "agents/a.md"), "a", encoding="utf-8") as f:
            f.write("\n手改\n")
        code, out = run(root, "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("内容与 runbook 不一致", out)

    def test_check_detects_extra_file(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        self.assertEqual(run(root)[0], 0)
        with open(os.path.join(root, "agents/old.md"), "w", encoding="utf-8") as f:
            f.write("旧文件\n")
        code, out = run(root, "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("多余文件", out)

    def test_duplicate_basename_uses_parent(self):
        root = make_repo({
            "runbooks/x/runtime.md": fixture("X"),
            "runbooks/y/runtime.md": fixture("Y"),
        })
        code, out = run(root)
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.isfile(os.path.join(root, "agents/x-runtime.md")))
        self.assertTrue(os.path.isfile(os.path.join(root, "agents/y-runtime.md")))
        self.assertFalse(os.path.exists(os.path.join(root, "agents/runtime.md")))

    def test_missing_frontmatter_fails(self):
        root = make_repo({"runbooks/a.md": fixture("A").split("---\n\n", 1)[1]})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("缺少 agent.effort frontmatter", out)

    def test_invalid_effort_fails(self):
        root = make_repo({"runbooks/a.md": fixture("A", effort="max")})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("取值非法: max", out)

    def test_install_codex(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        target = tempfile.mkdtemp(prefix="runbook-project-")
        code, out = run(root, "--install-codex", target)
        self.assertEqual(code, 0, out)
        self.assertTrue(os.path.isfile(os.path.join(target, ".codex/agents/a.toml")))

    def test_generate_is_idempotent(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        self.assertEqual(run(root)[0], 0)
        first = read(root, "agents/a.md")
        self.assertEqual(run(root)[0], 0)
        self.assertEqual(first, read(root, "agents/a.md"))


if __name__ == "__main__":
    unittest.main()
