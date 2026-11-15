import contextlib
import copy
import io
import pathlib
import shlex
import subprocess
import tempfile
import unittest

from test_delivery_helper import load_module


class BaselineSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name).resolve()
        self.base = self.root / "base"
        self.task = self.root / "task"
        self.base.mkdir()
        self.git(self.base, "init", "-b", "develop")
        self.git(self.base, "config", "user.name", "Test")
        self.git(self.base, "config", "user.email", "test@example.invalid")
        self.commit(self.base, "shared", "initial")
        self.git(self.base, "worktree", "add", "-b", "feature/topic", str(self.task))
        self.commit(self.task, "feature", "feature")
        self.commit(self.base, "previous", "previous queue item")
        self.module = load_module()
        self.verified = self.root / "verified"
        self.active = self.root / "active"
        self.finished = self.root / "finished"
        self.config = {
            "project": {"base_branch": "develop"},
            "queue": {
                "enabled": True,
                "enqueue": "true",
                "claim": f"touch {shlex.quote(str(self.active))}",
                "finish": f"touch {shlex.quote(str(self.finished))}",
            },
            "delivery": {"merge_base": "git merge --ff-only {branch}"},
            "repos": [{
                "name": "root", "path": ".", "role": "root", "merge_base": True,
                "verify": [f"git merge-base --is-ancestor develop HEAD && touch {shlex.quote(str(self.verified))}"],
            }],
        }

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, cwd, filename, value):
        (cwd / filename).write_text(value)
        self.git(cwd, "add", filename)
        self.git(cwd, "commit", "-m", value)

    def run_delivery(self, dry_run=False):
        steps = self.module.build_plan_steps(self.config, "feature/topic", None, root=self.task)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.module.run_steps(steps, dry_run=dry_run)

    def test_waiting_branch_is_rebased_before_verification(self):
        self.run_delivery()
        self.assertTrue(self.verified.exists())
        self.assertTrue(self.finished.exists())
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD"), self.git(self.task, "rev-parse", "HEAD"))
        self.assertTrue((self.task / "previous").exists())

    def test_plan_finds_task_worktree_when_config_is_loaded_from_base(self):
        config_dir = self.base / ".codex"
        config_dir.mkdir()
        config_path = config_dir / "worktree-merge-queue-delivery.toml"
        config_path.write_text("test config")
        config = copy.deepcopy(self.config)
        config["project"]["name"] = "Test Project"
        config["__config_path__"] = str(config_path)

        payload = self.module.plan_payload(
            config,
            "feature/topic",
            ["root"],
            auto_detect=False,
        )

        self.assertEqual(payload["root"], str(self.task))
        self.assertEqual(
            next(step["cwd"] for step in payload["steps"] if step["kind"] == "baseline-sync"),
            str(self.task),
        )

    def test_explicit_root_takes_precedence_over_branch_worktree_lookup(self):
        config = copy.deepcopy(self.config)
        config["project"]["name"] = "Test Project"
        config["__config_path__"] = str(self.base / ".codex" / "delivery.toml")

        payload = self.module.plan_payload(config, "feature/topic", ["root"], root=self.base)

        self.assertEqual(payload["root"], str(self.base))

    def test_wrong_task_checkout_fails_before_queue_claim(self):
        steps = self.module.build_plan_steps(self.config, "feature/missing", ["root"], root=self.base)

        with self.assertRaisesRegex(RuntimeError, "Expected branch feature/missing"):
            self.module.run_steps(steps)

        self.assertFalse(self.active.exists())

    def test_wrong_task_checkout_without_baseline_fails_before_queue_command(self):
        steps = [self.module.Step(
            kind="queue:claim", repo="root", cwd=str(self.base),
            command=f"touch {shlex.quote(str(self.active))}",
        )]

        with self.assertRaisesRegex(RuntimeError, "Expected branch feature/missing"):
            self.module.run_steps(steps, root=self.base, branch="feature/missing")

        self.assertFalse(self.active.exists())

    def test_sync_precedes_verification_in_monorepo_modules(self):
        (self.task / "flutter").mkdir()
        self.config["repos"].insert(0, {
            "name": "flutter", "path": "flutter", "role": "client",
            "verify": ["git merge-base --is-ancestor develop HEAD"],
        })
        self.run_delivery()
        self.assertTrue(self.finished.exists())

    def test_conflict_stops_before_verification_and_keeps_active_item(self):
        self.commit(self.task, "shared", "task change")
        self.commit(self.base, "shared", "base change")
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_delivery()
        self.assertTrue(self.active.exists())
        self.assertFalse(self.verified.exists())
        self.assertFalse(self.finished.exists())
        self.assertTrue(self.git(self.task, "diff", "--name-only", "--diff-filter=U"))

    def test_dirty_task_stops_before_rebase(self):
        old_head = self.git(self.task, "rev-parse", "HEAD")
        (self.task / "feature").write_text("unfinished")
        with self.assertRaisesRegex(RuntimeError, "clean"):
            self.run_delivery()
        self.assertEqual(old_head, self.git(self.task, "rev-parse", "HEAD"))
        self.assertFalse(self.verified.exists())

    def test_dirty_base_stops_before_rebase(self):
        (self.base / "previous").write_text("unfinished")
        with self.assertRaisesRegex(RuntimeError, "clean"):
            self.run_delivery()
        self.assertFalse(self.verified.exists())

    def test_missing_base_checkout_stops_before_verification(self):
        self.git(self.base, "checkout", "-b", "other")
        with self.assertRaisesRegex(RuntimeError, "checkout|branch"):
            self.run_delivery()
        self.assertFalse(self.verified.exists())

    def test_base_movement_after_verification_stops_before_merge(self):
        self.config["repos"][0]["verify"].append("git update-ref refs/heads/develop develop^")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.run_delivery()
        self.assertTrue(self.verified.exists())
        self.assertFalse(self.finished.exists())
        self.assertNotEqual(self.git(self.base, "rev-parse", "HEAD"), self.git(self.task, "rev-parse", "HEAD"))

    def test_task_commit_after_verification_invalidates_snapshot(self):
        self.config["repos"][0]["verify"].append("git commit --allow-empty -m changed")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.run_delivery()
        self.assertFalse(self.finished.exists())

    def test_failed_claim_does_not_rebase(self):
        old_head = self.git(self.task, "rev-parse", "HEAD")
        self.config["queue"]["claim"] = "false"
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_delivery()
        self.assertEqual(old_head, self.git(self.task, "rev-parse", "HEAD"))

    def test_dry_run_does_not_change_git_or_queue(self):
        old_head = self.git(self.task, "rev-parse", "HEAD")
        self.run_delivery(dry_run=True)
        self.assertEqual(old_head, self.git(self.task, "rev-parse", "HEAD"))
        self.assertFalse(self.active.exists())

    def test_current_branch_does_not_rewrite_commits(self):
        self.git(self.task, "rebase", "develop")
        old_head = self.git(self.task, "rev-parse", "HEAD")
        self.run_delivery()
        self.assertEqual(old_head, self.git(self.task, "rev-parse", "HEAD"))

    def test_independent_child_is_synchronized_before_its_verification(self):
        self.commit(self.base, ".gitignore", "child/\n")
        self.commit(self.task, ".gitignore", "child/\n")
        child_base = self.base / "child"
        child_task = self.task / "child"
        child_base.mkdir()
        self.git(child_base, "init", "-b", "develop")
        self.git(child_base, "config", "user.name", "Test")
        self.git(child_base, "config", "user.email", "test@example.invalid")
        self.commit(child_base, "initial", "initial")
        self.git(child_base, "worktree", "add", "-b", "feature/topic", str(child_task))
        self.commit(child_task, "feature", "child feature")
        self.commit(child_base, "previous", "child baseline moved")
        self.config["repos"].insert(0, {
            "name": "child", "path": "child", "merge_base": True,
            "verify": ["git merge-base --is-ancestor develop HEAD"],
        })
        self.run_delivery()
        self.assertEqual(self.git(child_base, "rev-parse", "HEAD"), self.git(child_task, "rev-parse", "HEAD"))
        self.assertTrue(self.finished.exists())

    def test_changed_checkout_after_verification_stops_merge(self):
        self.config["repos"][0]["verify"].append("git checkout -b wrong-branch")
        with self.assertRaisesRegex(RuntimeError, "Expected branch"):
            self.run_delivery()
        self.assertFalse(self.finished.exists())

    def test_untracked_work_is_not_stashed_or_removed(self):
        untracked = self.task / "unfinished"
        untracked.write_text("keep me")
        with self.assertRaisesRegex(RuntimeError, "clean"):
            self.run_delivery()
        self.assertEqual(untracked.read_text(), "keep me")
        self.assertFalse(self.verified.exists())

    def test_rebase_does_not_rewrite_other_branches_with_update_refs_enabled(self):
        old_head = self.git(self.task, "rev-parse", "HEAD")
        self.git(self.task, "branch", "other-task")
        self.git(self.task, "config", "rebase.updateRefs", "true")
        self.run_delivery()
        self.assertEqual(old_head, self.git(self.task, "rev-parse", "other-task"))


if __name__ == "__main__":
    unittest.main()
