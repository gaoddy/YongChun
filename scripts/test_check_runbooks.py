#!/usr/bin/env python3
"""check-runbooks.py 的测试：每个用例在临时目录构造最小仓库。"""
import json
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


def plugin_files(name="demo", entry_name=None, source="./"):
    return {
        ".claude-plugin/plugin.json": json.dumps({
            "name": name, "version": "0.1.0", "description": "测试", "license": "MIT",
        }),
        ".claude-plugin/marketplace.json": json.dumps({
            "name": "demo",
            "owner": {"name": "t"},
            "plugins": [{"name": entry_name or name, "source": source}],
        }),
    }


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

    def test_command_reference_missing_fails(self):
        cmd = "---\ndescription: 测试\n---\n\n@${CLAUDE_PLUGIN_ROOT}/runbooks/missing.md\n"
        extra = plugin_files()
        extra["commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("命令引用", out)

    def test_plugin_command_with_variable_passes(self):
        cmd = "---\ndescription: 测试\n---\n\n@${CLAUDE_PLUGIN_ROOT}/runbooks/a.md\n"
        extra = plugin_files()
        extra["commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 0, out)

    def _with_hook(self, command):
        extra = plugin_files()
        extra["commands/x.md"] = "---\ndescription: 测试\n---\n"
        extra["hooks/hooks.json"] = json.dumps({
            "hooks": {"UserPromptSubmit": [{"hooks": [
                {"type": "command", "command": command},
            ]}]},
        })
        return extra

    def test_hook_script_missing_fails(self):
        extra = self._with_hook('"${CLAUDE_PLUGIN_ROOT}/hooks/missing.sh"')
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("钩子", out)

    def test_hook_script_not_executable_fails(self):
        extra = self._with_hook('"${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"')
        extra["hooks/run.sh"] = "#!/bin/sh\necho ok\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("钩子", out)

    def test_hook_script_executable_passes(self):
        extra = self._with_hook('"${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"')
        extra["hooks/run.sh"] = "#!/bin/sh\necho ok\n"
        root = make_repo(extra=extra)
        os.chmod(os.path.join(root, "hooks", "run.sh"), 0o755)
        code, out = run(root)
        self.assertEqual(code, 0, out)

    def test_missing_license_fails(self):
        extra = plugin_files()
        manifest = json.loads(extra[".claude-plugin/plugin.json"])
        del manifest["license"]
        extra[".claude-plugin/plugin.json"] = json.dumps(manifest)
        extra["commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("许可证", out)

    def test_license_file_without_field_passes(self):
        extra = plugin_files()
        manifest = json.loads(extra[".claude-plugin/plugin.json"])
        del manifest["license"]
        extra[".claude-plugin/plugin.json"] = json.dumps(manifest)
        extra["LICENSE"] = "MIT License\n"
        extra["commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 0, out)

    def test_plugin_command_bare_path_fails(self):
        cmd = "---\ndescription: 测试\n---\n\n@runbooks/a.md\n"
        extra = plugin_files()
        extra["commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("命令引用", out)

    def test_plugin_name_mismatch_fails(self):
        extra = plugin_files(entry_name="other")
        extra["commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("插件", out)

    def test_marketplace_source_missing_fails(self):
        extra = plugin_files(source="./missing")
        extra["commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("插件", out)

    def test_duplicate_command_dirs_fail(self):
        cmd = "---\ndescription: 测试\n---\n"
        extra = plugin_files()
        extra["commands/x.md"] = cmd
        extra[".claude/commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("副本", out)


if __name__ == "__main__":
    unittest.main()
