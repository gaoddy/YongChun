import json
import pathlib
import shlex
import subprocess
import unittest

import test_baseline_sync as baseline_tests


class MergeReleaseTests(unittest.TestCase):
    git = baseline_tests.BaselineSyncTests.git
    commit = baseline_tests.BaselineSyncTests.commit
    run_delivery = baseline_tests.BaselineSyncTests.run_delivery

    def setUp(self):
        baseline_tests.BaselineSyncTests.setUp(self)
        self.manifest_pointer = self.root / "manifest-path"
        self.config["queue"]["release_after_merge"] = (
            f"test ! -d {shlex.quote(str(self.task))} && touch {shlex.quote(str(self.finished))}"
        )
        self.config["worktree"] = {
            "clean": f"git worktree remove {shlex.quote(str(self.task))} && git branch -d {{branch}}"
        }
        self.config["post_merge"] = {
            "enqueue": f"test -f {shlex.quote(str(self.finished))} && printf '%s' {{manifest}} > {shlex.quote(str(self.manifest_pointer))}"
        }
        self.config["repos"][0]["push_base"] = True
        self.config["repos"][0]["deploy"] = "deploy-tool --commit {commit}"
        self.config["delivery"]["push_base"] = "git push origin {base_branch}"

    def test_release_and_handoff_survive_task_removal(self):
        self.run_delivery()
        self.assertFalse(self.task.exists())
        self.assertTrue(self.finished.exists())
        path = pathlib.Path(self.manifest_pointer.read_text())
        job = json.loads(path.read_text())
        self.assertEqual(job["status"], "ready")
        root_commit = self.git(self.base, "rev-parse", "HEAD")
        self.assertEqual(job["repos"][0]["commit"], root_commit)
        self.assertEqual(job["repos"][0]["commands"], [
            f"git push origin {root_commit}:refs/heads/develop",
            f"deploy-tool --commit {root_commit}",
        ])
        self.commit(self.base, "next-item", "next item merged")
        self.assertEqual(json.loads(path.read_text())["repos"][0]["commit"], root_commit)

    def test_no_post_delivery_command_runs_inside_merge_queue(self):
        steps = self.module.build_plan_steps(self.config, "feature/topic", None, root=self.task)
        kinds = [step.kind for step in steps]
        self.assertNotIn("push-base", kinds)
        self.assertNotIn("deploy", kinds)
        self.assertLess(kinds.index("merge-base"), kinds.index("worktree-clean"))
        self.assertLess(kinds.index("worktree-clean"), kinds.index("queue:release_after_merge"))
        self.assertLess(kinds.index("queue:release_after_merge"), kinds.index("post-merge-enqueue"))

    def test_unpinned_deployment_is_rejected_before_claim(self):
        self.config["repos"][0]["deploy"] = "deploy-latest-develop"
        with self.assertRaisesRegex(ValueError, "commit"):
            self.run_delivery()
        self.assertFalse(self.active.exists())

    def test_enqueue_failure_does_not_reacquire_queue_or_lose_manifest(self):
        self.config["post_merge"]["enqueue"] = "false {manifest}"
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_delivery()
        self.assertTrue(self.finished.exists())
        self.assertFalse(self.task.exists())
        jobs = list((self.base / ".git" / "delivery-jobs").glob("*.json"))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(json.loads(jobs[0].read_text())["status"], "ready")
        self.assertEqual(json.loads(jobs[0].read_text())["repos"][0]["commit"], self.git(self.base, "rev-parse", "HEAD"))

    def test_cleanup_failure_keeps_slot_and_does_not_enqueue_worker(self):
        self.config["worktree"]["clean"] = "false"
        self.config["queue"]["release_after_merge"] = f"touch {shlex.quote(str(self.finished))}"
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_delivery()
        self.assertTrue(self.task.exists())
        self.assertTrue(self.active.exists())
        self.assertFalse(self.finished.exists())
        self.assertFalse(self.manifest_pointer.exists())

    def test_release_failure_preserves_handoff_after_cleanup(self):
        self.config["queue"]["release_after_merge"] = "false"
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_delivery()
        self.assertFalse(self.task.exists())
        self.assertFalse(self.manifest_pointer.exists())
        jobs = list((self.base / ".git" / "delivery-jobs").glob("*.json"))
        self.assertEqual(len(jobs), 1)
        self.assertEqual(json.loads(jobs[0].read_text())["status"], "awaiting-release")

    def test_missing_worker_is_rejected_before_claim(self):
        del self.config["post_merge"]
        with self.assertRaisesRegex(ValueError, "post_merge.enqueue"):
            self.run_delivery()
        self.assertFalse(self.active.exists())

    def test_nonstandard_push_requires_explicit_pinned_destination(self):
        self.config["delivery"]["push_base"] = "git push company {base_branch}"
        with self.assertRaisesRegex(ValueError, "push_commit"):
            self.run_delivery()
        self.assertFalse(self.active.exists())

    def test_dry_run_creates_no_job_or_queue_changes(self):
        self.run_delivery(dry_run=True)
        self.assertTrue(self.task.exists())
        self.assertFalse(self.active.exists())
        self.assertFalse((self.base / ".git" / "delivery-jobs").exists())

    def test_legacy_run_is_rejected_before_queue_actions(self):
        path = self.root / "legacy.toml"
        path.write_text('[project]\nname="legacy"\nbase_branch="develop"\n[queue]\nenabled=true\n')
        result = subprocess.run([
            "python3", str(pathlib.Path(self.module.__file__)), "run", "--config", str(path),
            "--branch", "feature/topic",
        ], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Migrate queue.release_after_merge", result.stderr)
        self.assertFalse(self.active.exists())


if __name__ == "__main__":
    unittest.main()
