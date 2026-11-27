#!/usr/bin/env python3
"""check-runbooks.py 的测试：每个用例在临时目录构造最小仓库。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "scripts", "check-runbooks.py")
GENERATOR = os.path.join(REPO, "scripts", "generate_runbook_agents.py")
SKILL_GENERATOR = os.path.join(REPO, "scripts", "generate_runbook_skills.py")

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


def with_agent(text, effort="high"):
    return "---\nagent:\n  effort: %s\n---\n\n%s" % (effort, text)


def agent_repo(overrides=None):
    merged = {
        "runbooks/a.md": with_agent(BASE["runbooks/a.md"]),
        "runbooks/b.md": with_agent(BASE["runbooks/b.md"]),
    }
    if overrides:
        merged.update(overrides)
    root = make_repo(overrides=merged)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    shutil.copy(GENERATOR, os.path.join(root, "scripts", "generate_runbook_agents.py"))
    if os.path.isfile(SKILL_GENERATOR):
        shutil.copy(SKILL_GENERATOR, os.path.join(root, "scripts", "generate_runbook_skills.py"))
    return root


def generate(root):
    subprocess.run(
        [sys.executable, GENERATOR, "--root", root],
        capture_output=True, text=True,
    )


def with_skill(text, enabled="true"):
    return "---\nagent:\n  effort: high\nskill:\n  enabled: %s\n---\n\n%s" % (enabled, text)


def generate_skills(root):
    subprocess.run([sys.executable, SKILL_GENERATOR, "--root", root],
                   capture_output=True, text=True)


class CheckRunbooksTest(unittest.TestCase):
    def test_valid_repo_passes(self):
        code, out = run(make_repo())
        self.assertEqual(code, 0, out)

    def test_unindexed_file_fails(self):
        code, out = run(make_repo(extra={"runbooks/c.md": BASE["runbooks/b.md"].replace("B", "C")}))
        self.assertEqual(code, 1, out)
        self.assertIn("索引", out)

    def test_maintenance_runbook_registered_in_agents_passes(self):
        agents = BASE["AGENTS.md"] + "\n| 维护 | [runbook.md](runbooks/runbook.md) |\n"
        content = BASE["runbooks/b.md"].replace("B", "维护")
        code, out = run(make_repo(overrides={"AGENTS.md": agents},
                                  extra={"runbooks/runbook.md": content}))
        self.assertEqual(code, 0, out)

    def test_maintenance_runbook_missing_from_agents_fails(self):
        content = BASE["runbooks/b.md"].replace("B", "维护")
        code, out = run(make_repo(extra={"runbooks/runbook.md": content}))
        self.assertEqual(code, 1, out)
        self.assertIn("AGENTS.md 触发表", out)

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

    def test_too_many_prerequisites_fails(self):
        a = BASE["runbooks/a.md"].replace(
            "- [B](b.md)", "- [B](b.md)\n- [C](c.md)\n- [D](d.md)"
        )
        index = BASE["runbooks/index.md"] + (
            "| test | [c.md](c.md) | C |\n"
            "| test | [d.md](d.md) | D |\n"
        )
        extra = {
            "runbooks/c.md": BASE["runbooks/b.md"].replace("B", "C"),
            "runbooks/d.md": BASE["runbooks/b.md"].replace("B", "D"),
        }
        code, out = run(make_repo(overrides={
            "runbooks/a.md": a,
            "runbooks/index.md": index,
        }, extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("前置", out)

    def test_registered_subdir_index_is_checked(self):
        index = BASE["runbooks/index.md"] + "| test | [sub/index.md](sub/index.md) | S |\n"
        sub = """# 索引

## 适用场景

- 测试。

## 步骤

1. 步骤。

## 验证

- 通过。
"""
        overrides = {"runbooks/index.md": index}
        code, out = run(make_repo(overrides=overrides, extra={"runbooks/sub/index.md": sub}))
        self.assertEqual(code, 0, out)

        missing = sub.replace("## 验证\n\n- 通过。\n", "")
        code, out = run(make_repo(overrides=overrides, extra={"runbooks/sub/index.md": missing}))
        self.assertEqual(code, 1, out)
        self.assertIn("章节", out)

    def test_unregistered_subdir_index_fails(self):
        sub = """# 索引

## 适用场景

- 测试。

## 步骤

1. 步骤。

## 验证

- 通过。
"""
        code, out = run(make_repo(extra={"runbooks/sub/index.md": sub}))
        self.assertEqual(code, 1, out)
        self.assertIn("索引", out)

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
        extra["claude-commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("命令引用", out)

    def test_plugin_command_with_variable_passes(self):
        cmd = "---\ndescription: 测试\n---\n\n@${CLAUDE_PLUGIN_ROOT}/runbooks/a.md\n"
        extra = plugin_files()
        extra["claude-commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 0, out)

    def _with_hook(self, command):
        extra = plugin_files()
        extra["claude-commands/x.md"] = "---\ndescription: 测试\n---\n"
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
        extra["claude-commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("许可证", out)

    def test_license_file_without_field_passes(self):
        extra = plugin_files()
        manifest = json.loads(extra[".claude-plugin/plugin.json"])
        del manifest["license"]
        extra[".claude-plugin/plugin.json"] = json.dumps(manifest)
        extra["LICENSE"] = "MIT License\n"
        extra["claude-commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 0, out)

    def test_plugin_command_bare_path_fails(self):
        cmd = "---\ndescription: 测试\n---\n\n@runbooks/a.md\n"
        extra = plugin_files()
        extra["claude-commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("命令引用", out)

    def test_plugin_name_mismatch_fails(self):
        extra = plugin_files(entry_name="other")
        extra["claude-commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("插件", out)

    def test_marketplace_source_missing_fails(self):
        extra = plugin_files(source="./missing")
        extra["claude-commands/x.md"] = "---\ndescription: 测试\n---\n"
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("插件", out)

    def test_duplicate_command_dirs_fail(self):
        cmd = "---\ndescription: 测试\n---\n"
        extra = plugin_files()
        extra["claude-commands/x.md"] = cmd
        extra[".claude/commands/x.md"] = cmd
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("副本", out)

    def codex_files(self, command_body="---\ndescription: 测试\n---\n\n读取 runbooks/a.md。\n"):
        extra = plugin_files()
        extra[".codex-plugin/plugin.json"] = json.dumps({
            "name": "demo", "version": "0.1.0",
            "skills": "./skills/", "commands": "./codex-commands/", "hooks": "./hooks/hooks.json",
        })
        extra[".agents/plugins/marketplace.json"] = json.dumps({
            "name": "demo",
            "plugins": [{"name": "demo", "source": {"source": "url", "url": "https://example.com/x.git"}}],
        })
        extra["skills/demo/SKILL.md"] = "---\nname: demo\ndescription: 测试\n---\n"
        extra["hooks/hooks.json"] = json.dumps({"hooks": {}})
        extra["codex-commands/x.md"] = command_body
        return extra

    def test_codex_manifest_passes(self):
        code, out = run(make_repo(extra=self.codex_files()))
        self.assertEqual(code, 0, out)

    def test_codex_command_with_arguments_fails(self):
        code, out = run(make_repo(extra=self.codex_files("---\ndescription: 测试\n---\n\n$ARGUMENTS\n")))
        self.assertEqual(code, 1, out)
        self.assertIn("Codex 命令", out)

    def test_codex_command_with_at_token_fails(self):
        code, out = run(make_repo(extra=self.codex_files("---\ndescription: 测试\n---\n\n@runbooks/a.md\n")))
        self.assertEqual(code, 1, out)
        self.assertIn("Codex 命令", out)

    def test_codex_marketplace_source_type_fails(self):
        extra = self.codex_files()
        extra[".agents/plugins/marketplace.json"] = json.dumps({
            "name": "demo",
            "plugins": [{"name": "demo", "source": {"source": "s3"}}],
        })
        code, out = run(make_repo(extra=extra))
        self.assertEqual(code, 1, out)
        self.assertIn("source 类型", out)

    def test_agent_metadata_and_generated_pass(self):
        root = agent_repo()
        generate(root)
        code, out = run(root)
        self.assertEqual(code, 0, out)

    def test_agent_missing_frontmatter_fails(self):
        root = agent_repo({"runbooks/a.md": BASE["runbooks/a.md"]})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("agent", out)
        self.assertIn("frontmatter", out)

    def test_agent_invalid_effort_fails(self):
        root = agent_repo({"runbooks/a.md": with_agent(BASE["runbooks/a.md"], "medium")})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("取值非法: medium", out)

    def test_agent_missing_generated_fails(self):
        root = agent_repo()
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("缺少生成物", out)

    def test_agent_generated_drift_fails(self):
        root = agent_repo()
        generate(root)
        with open(os.path.join(root, "agents/a.md"), "a", encoding="utf-8") as f:
            f.write("\n手改\n")
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("内容与 runbook 不一致", out)

    def test_skill_missing_generated_fails(self):
        root = agent_repo({"runbooks/a.md": with_skill(BASE["runbooks/a.md"])})
        generate(root)
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("[skill]", out)
        self.assertIn("缺少生成物", out)

    def test_frontmatter_error_reported_once(self):
        root = agent_repo({"runbooks/a.md": BASE["runbooks/a.md"]})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertEqual(1, out.count("缺少 agent.effort frontmatter"), out)

    def test_skill_generated_drift_fails(self):
        root = agent_repo({"runbooks/a.md": with_skill(BASE["runbooks/a.md"])})
        generate(root)
        generate_skills(root)
        with open(os.path.join(root, "skills/runbooks/a/SKILL.md"), "a", encoding="utf-8") as f:
            f.write("\n手改\n")
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("内容与 runbook 不一致", out)

    def test_invalid_skill_value_fails(self):
        root = agent_repo({"runbooks/a.md": with_skill(BASE["runbooks/a.md"], "yes")})
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("skill.enabled 取值非法", out)
        self.assertIn("[agent]", out)
        self.assertNotIn("[skill]", out)

    def test_skill_generator_without_agent_generator_fails_cleanly(self):
        root = make_repo({"runbooks/a.md": with_skill(BASE["runbooks/a.md"])})
        os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
        shutil.copy(SKILL_GENERATOR, os.path.join(root, "scripts", "generate_runbook_skills.py"))
        code, out = run(root)
        self.assertEqual(code, 1, out)
        self.assertIn("[skill]", out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
