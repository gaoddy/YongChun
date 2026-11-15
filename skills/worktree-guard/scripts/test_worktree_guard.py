"""worktree_create.sh 与 worktree_guard.sh 的执行器测试。

运行：python3 -m unittest discover -s skills/worktree-guard/scripts
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
CREATE = os.path.join(SCRIPTS, "worktree_create.sh")
GUARD = os.path.join(SCRIPTS, "worktree_guard.sh")

GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def run(argv, cwd, stdin=None, env=None):
    merged = dict(os.environ)
    merged.update(GIT_ENV)
    if env:
        merged.update(env)
    return subprocess.run(
        argv,
        cwd=cwd,
        input=stdin,
        capture_output=True,
        text=True,
        env=merged,
    )


class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="worktree-guard-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = os.path.join(self.tmp, "project")
        os.makedirs(self.repo)
        self.git("init", "-q", "-b", "develop")
        self.write(".gitignore", "/.worktrees/\n")
        self.write("README.md", "test\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "init")

    def git(self, *args, cwd=None):
        result = run(["git", *args], cwd or self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def write(self, rel, content):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(rel) else None
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def create(self, *args, cwd=None):
        return run([CREATE, *args], cwd or self.repo)

    def guard(self, command, cwd=None):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd or self.repo})
        result = run([GUARD], self.repo, stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        return json.loads(output) if output else None


class WorktreeCreateTests(RepositoryTestCase):
    def test_creates_worktree_under_project_worktrees(self):
        result = self.create("feature/login")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = os.path.join(self.repo, ".worktrees", "feature-login")
        self.assertEqual(result.stdout.strip(), target)
        self.assertTrue(os.path.isdir(target))
        listed = self.git("worktree", "list", "--porcelain")
        self.assertIn(target, listed)
        self.assertEqual(self.git("-C", target, "rev-parse", "--abbrev-ref", "HEAD").strip(), "feature/login")
        self.assertEqual(self.git("-C", target, "rev-parse", "HEAD").strip(),
                         self.git("rev-parse", "develop").strip())

    def test_refuses_when_worktrees_dir_is_not_ignored(self):
        self.write(".gitignore", "\n")
        self.git("commit", "-q", "-am", "drop ignore")
        result = self.create("feature/login")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gitignore", result.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".worktrees", "feature-login")))

    def test_refuses_dirty_worktree(self):
        self.write("README.md", "dirty\n")
        result = self.create("feature/login")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("工作区", result.stderr)

    def test_refuses_branch_outside_prefix_whitelist(self):
        result = self.create("release/1.0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("前缀", result.stderr)

    def test_refuses_existing_target(self):
        os.makedirs(os.path.join(self.repo, ".worktrees", "feature-login"))
        result = self.create("feature/login")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("已存在", result.stderr)

    def test_refuses_missing_base_branch(self):
        result = self.create("feature/login", "nope")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("基线", result.stderr)

    def test_reuses_existing_branch(self):
        self.git("branch", "feature/login")
        result = self.create("feature/login")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = os.path.join(self.repo, ".worktrees", "feature-login")
        self.assertEqual(self.git("-C", target, "rev-parse", "HEAD").strip(),
                         self.git("rev-parse", "develop").strip())

    def test_reads_queue_config_for_base_and_prefix(self):
        self.git("branch", "main-base")
        self.write(".yongchun/worktree-merge-queue.toml",
                   "[project]\nbase_branch = \"main-base\"\nbranch_prefix = \"task/\"\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "config")
        result = self.create("task/pay")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = os.path.join(self.repo, ".worktrees", "task-pay")
        self.assertEqual(self.git("-C", target, "rev-parse", "HEAD").strip(),
                         self.git("rev-parse", "main-base").strip())
        refused = self.create("feature/other")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("前缀", refused.stderr)

    def test_refuses_invalid_ref_name(self):
        result = self.create("feature/..bad")
        self.assertNotEqual(result.returncode, 0)

    def test_custom_root_override(self):
        root = os.path.join(self.tmp, "elsewhere")
        result = self.create("feature/login", "--root", root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.path.isdir(os.path.join(root, "feature-login")))


class WorktreeGuardTests(RepositoryTestCase):
    def assert_allowed(self, command, cwd=None):
        self.assertIsNone(self.guard(command, cwd), "命令应放行: %s" % command)

    def assert_denied(self, command, cwd=None, needle=None):
        payload = self.guard(command, cwd)
        self.assertIsNotNone(payload, "命令应拒绝: %s" % command)
        decision = payload["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        if needle:
            self.assertIn(needle, decision["permissionDecisionReason"])

    def test_allows_unrelated_commands(self):
        self.assert_allowed("git status --short")
        self.assert_allowed("ls -la")

    def test_allows_read_only_worktree_commands(self):
        self.assert_allowed("git worktree list")

    def test_denies_raw_worktree_add(self):
        self.assert_denied("git worktree add ../x feature/login", needle="worktree_create.sh")

    def test_allows_canonical_create_script(self):
        self.assert_allowed("%s feature/login" % CREATE)
        self.assert_allowed("sh %s feature/login develop" % CREATE)

    def test_denies_add_with_dash_c(self):
        self.assert_denied("git -C . worktree add ../x feature/login", needle="worktree_create.sh")

    def test_allows_remove_inside_project_worktrees(self):
        self.assert_allowed("git worktree remove .worktrees/feature-login")

    def test_denies_remove_outside_project_worktrees(self):
        self.assert_denied("git worktree remove /tmp/elsewhere")

    def test_denies_move(self):
        self.assert_denied("git worktree move .worktrees/a /tmp/b")

    def test_allows_prune(self):
        self.assert_allowed("git worktree prune")

    def test_allows_quoted_mentions(self):
        self.assert_allowed('git log --grep "worktree add"')
        self.assert_allowed('echo "git worktree add ../x feature/login"')

    def test_allows_chained_remove_inside_project(self):
        self.assert_allowed("git worktree remove .worktrees/feature-login && git branch -d feature/login")

    def test_ignores_non_bash_tools(self):
        payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": self.repo})
        result = run([GUARD], self.repo, stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
