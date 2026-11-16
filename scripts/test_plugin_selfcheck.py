"""plugin_selfcheck.py 的测试。

运行：python3 -m unittest discover -s scripts -p 'test_plugin_selfcheck.py'
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "plugin_selfcheck.py"


def write(path, content=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class PluginSelfcheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="plugin-selfcheck-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.source = self.tmp / "source"
        self.cache_root = self.tmp / "cache"
        self.build_source(self.source)
        self.install("1.0.0")

    def build_source(self, root):
        write(
            root / ".claude-plugin/plugin.json",
            json.dumps(
                {
                    "name": "yongchun",
                    "version": "1.0.0",
                    "commands": ["./claude-commands/"],
                    "skills": ["./skills/worktree/"],
                }
            ),
        )
        write(
            root / ".codex-plugin/plugin.json",
            json.dumps(
                {
                    "name": "yongchun",
                    "version": "1.0.0",
                    "commands": "./codex-commands/",
                    "skills": ["./skills/worktree/"],
                    "hooks": "./hooks/hooks.json",
                }
            ),
        )
        write(root / "skills/worktree/demo/SKILL.md", "demo")
        write(root / "claude-commands/demo.md", "demo")
        write(root / "codex-commands/demo.md", "demo")
        write(root / "hooks/hooks.json", "{}")
        write(root / "runbooks/index.md", "index")

    def install(self, version):
        target = self.cache_root / "yongchun" / "yongchun" / version
        shutil.copytree(self.source, target)

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source-root", str(self.source), "--cache-root", str(self.cache_root), *args],
            capture_output=True,
            text=True,
        )

    def test_passes_with_matching_cache(self):
        result = self.run_script()
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("插件自检: ok", result.stdout)

    def test_reports_undeclared_skill_group(self):
        write(self.source / "skills/other/demo/SKILL.md", "demo")
        result = self.run_script()
        self.assertEqual(1, result.returncode)
        self.assertIn("技能组未在清单声明", result.stdout)

    def test_reports_runtime_dir_in_cache(self):
        write(self.cache_root / "yongchun/yongchun/1.0.0/.worktrees/x/file", "x")
        result = self.run_script()
        self.assertEqual(1, result.returncode)
        self.assertIn("不应包含 .worktrees", result.stdout)

    def test_requires_installed_cache_when_asked(self):
        shutil.rmtree(self.cache_root)
        self.assertEqual(0, self.run_script().returncode)
        result = self.run_script("--require-installed")
        self.assertEqual(1, result.returncode)
        self.assertIn("未找到已安装缓存", result.stdout)

    def test_reports_version_mismatch(self):
        manifest = self.source / ".codex-plugin/plugin.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["version"] = "2.0.0"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_script()
        self.assertEqual(1, result.returncode)
        self.assertIn("双端版本不一致", result.stdout)

    def test_reports_missing_command_in_cache(self):
        (self.cache_root / "yongchun/yongchun/1.0.0/claude-commands/demo.md").unlink()
        result = self.run_script()
        self.assertEqual(1, result.returncode)
        self.assertIn("命令文件与源码不一致", result.stdout)


if __name__ == "__main__":
    unittest.main()
