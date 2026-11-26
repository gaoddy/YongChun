"""worktree_cleanup.py 的测试。

运行：python3 -m unittest discover -s skills/worktree/worktree-guard/scripts
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "worktree_cleanup.py"
GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


class WorktreeCleanupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="worktree-cleanup-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "project"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "develop")
        self.write(".gitignore", "/.worktrees/\n")
        self.write("README.md", "test\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "init")

    def git(self, *args, cwd=None):
        env = dict(os.environ)
        env.update(GIT_ENV)
        result = subprocess.run(
            ["git", *args], cwd=cwd or self.repo, capture_output=True, text=True, env=env
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout

    def write(self, name, content=""):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )

    def create_worktree(self, branch):
        path = self.repo / ".worktrees" / branch.replace("/", "-")
        self.git("worktree", "add", "-q", str(path), "-b", branch)
        return path

    def test_clean_repository_passes_check(self):
        result = self.run_script("--check")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("干净", result.stdout)

    def test_reports_worktree_and_fails_check(self):
        path = self.create_worktree("feature/demo")
        result = self.run_script("--check")
        self.assertEqual(1, result.returncode)
        self.assertIn(str(path), result.stdout)
        self.assertIn("存在残留", result.stderr)

    def test_reports_merged_branch_after_worktree_removed(self):
        path = self.create_worktree("feature/demo")
        self.git("merge", "--no-ff", "-q", "-m", "merge", "feature/demo")
        self.git("worktree", "remove", str(path))
        result = self.run_script("--check")
        self.assertEqual(1, result.returncode)
        self.assertIn("branch feature/demo 已合并", result.stdout)

        self.git("branch", "-d", "feature/demo")
        self.assertEqual(0, self.run_script("--check").returncode)

    def test_counts_any_whitelist_prefix_as_task_branch(self):
        for branch in ("release/1.0", "chore/demo"):
            with self.subTest(branch=branch):
                path = self.create_worktree(branch)
                self.git("merge", "--no-ff", "-q", "-m", "merge", branch)
                self.git("worktree", "remove", str(path))
                result = self.run_script("--check")
                self.assertEqual(1, result.returncode)
                self.assertIn(f"branch {branch} 已合并", result.stdout)
                self.git("branch", "-d", branch)
        self.assertEqual(0, self.run_script("--check").returncode)


if __name__ == "__main__":
    unittest.main()
