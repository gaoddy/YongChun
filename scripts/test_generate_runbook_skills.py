#!/usr/bin/env python3
"""generate_runbook_skills.py 的测试：每个用例在临时目录构造最小仓库。"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "generate_runbook_skills.py")
AGENTS = os.path.join(REPO, "scripts", "generate_runbook_agents.py")


def fixture(title="A", skill=None):
    if skill is True:
        block = "skill:\n  enabled: true\n"
    elif skill is False:
        block = "skill:\n  enabled: false\n"
    elif skill is None:
        block = ""
    else:
        block = "skill:\n  enabled: %s\n" % skill
    return """---
agent:
  effort: high
%s---

# Runbook：%s

## 适用场景

- 处理 %s 场景。

## 规则

- 规则。

## 步骤

1. 步骤。

## 验证

- 通过。
""" % (block, title, title)


def make_repo(files):
    d = tempfile.mkdtemp(prefix="runbook-skill-")
    for name, content in files.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    # 生成器从 root/scripts/ 加载 agent 生成器，测试仓库必须自带一份。
    os.makedirs(os.path.join(d, "scripts"), exist_ok=True)
    shutil.copy(AGENTS, os.path.join(d, "scripts", "generate_runbook_agents.py"))
    return d


def run(root, *args):
    r = subprocess.run(
        [sys.executable, SCRIPT, "--root", root] + list(args),
        capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


def run_ok(root, *args):
    """运行生成器并断言退出码为 0。"""
    code, out = run(root, *args)
    if code != 0:
        raise AssertionError("生成器退出码 %d：%s" % (code, out))
    return out


def read(root, name):
    with open(os.path.join(root, name), encoding="utf-8") as f:
        return f.read()


def write(root, name, content):
    p = os.path.join(root, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def append(root, name, content):
    with open(os.path.join(root, name), "a", encoding="utf-8") as f:
        f.write(content)


class GenerateSkillsTest(unittest.TestCase):
    def test_no_enabled_generates_nothing_and_check_passes(self):
        root = make_repo({"runbooks/a.md": fixture("A")})
        run_ok(root)
        self.assertFalse(os.path.isdir(os.path.join(root, "skills/runbooks")))
        run_ok(root, "--check")

    def test_generate_creates_dual_end_skill(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        text = read(root, "skills/runbooks/a/SKILL.md")
        self.assertIn("name: a", text)
        self.assertIn('description: "A：处理 A 场景"', text)
        self.assertIn("../../../runbooks/a.md", text)
        self.assertIn("CLAUDE_PLUGIN_ROOT", text)
        self.assertIn("Codex", text)

    def test_check_detects_content_drift(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        append(root, "skills/runbooks/a/SKILL.md", "\n手改\n")
        code, out = run(root, "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("内容与 runbook 不一致", out)

    def test_check_detects_extra_generated_skill(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        write(root, "skills/runbooks/old/SKILL.md",
              "---\nname: old\ndescription: x\n---\n\n"
              "由 scripts/generate_runbook_skills.py 根据 runbooks/old.md 生成\n")
        code, out = run(root, "--check")
        self.assertEqual(code, 1, out)
        self.assertIn("多余文件", out)

    def test_write_removes_extra_generated_skill_but_keeps_handwritten(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        write(root, "skills/runbooks/old/SKILL.md",
              "---\nname: old\ndescription: x\n---\n\n"
              "由 scripts/generate_runbook_skills.py 根据 runbooks/old.md 生成\n")
        write(root, "skills/worktree/hand/SKILL.md", "手写\n")
        run_ok(root)
        self.assertFalse(os.path.exists(os.path.join(root, "skills/runbooks/old/SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(root, "skills/worktree/hand/SKILL.md")))

    def test_skill_disabled_is_not_generated(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=False)})
        run_ok(root)
        self.assertFalse(os.path.exists(os.path.join(root, "skills/runbooks/a/SKILL.md")))

    def test_unmarked_skill_in_group_is_kept_and_not_reported(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        write(root, "skills/runbooks/hand/SKILL.md", "手写\n")
        run_ok(root, "--check")
        run_ok(root)
        self.assertTrue(os.path.isfile(os.path.join(root, "skills/runbooks/hand/SKILL.md")))

    def test_revert_to_zero_removes_group_dir(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        self.assertTrue(os.path.isdir(os.path.join(root, "skills/runbooks")))
        write(root, "runbooks/a.md", fixture("A"))
        run_ok(root)
        self.assertFalse(os.path.exists(os.path.join(root, "skills/runbooks")))

    def test_group_dir_survives_revert_when_unmarked_remains(self):
        root = make_repo({"runbooks/a.md": fixture("A", skill=True)})
        run_ok(root)
        write(root, "skills/runbooks/hand/SKILL.md", "手写\n")
        write(root, "runbooks/a.md", fixture("A"))
        run_ok(root)
        self.assertTrue(os.path.isdir(os.path.join(root, "skills/runbooks")))
        self.assertFalse(os.path.exists(os.path.join(root, "skills/runbooks/a")))


if __name__ == "__main__":
    unittest.main()
