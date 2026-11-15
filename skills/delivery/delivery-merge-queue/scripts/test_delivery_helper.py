import contextlib
import io
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest


SCRIPT_PATH = pathlib.Path(__file__).with_name("delivery_helper.py")


def load_module():
    spec = importlib.util.spec_from_file_location("delivery_helper", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONFIG_TEXT = textwrap.dedent(
    """
    version = 1

    [project]
    name = "Example"
    base_branch = "develop"
    branch_prefix = "feature/"

    [worktree]
    create = "make worktree-create BRANCH={branch}"
    clean = "make worktree-clean BRANCH={branch}"

    [queue]
    enabled = true
    status = "make merge-queue-status"
    enqueue = "make merge-queue-enqueue BRANCH={branch}"
    claim = "make merge-queue-claim BRANCH={branch}"
    require_stage = "make merge-queue-require-stage BRANCH={branch} STAGE={stage}"
    mark_root_merged = "make merge-queue-mark-root-merged BRANCH={branch}"
    root_merged_checklist = "make merge-queue-root-merged-checklist BRANCH={branch}"
    finish = "make merge-queue-finish BRANCH={branch}"
    stages = ["queued", "api-merged", "root-merged"]

    [delivery]
    merge_base = "git merge --ff-only {branch}"
    push_base = "git push origin {base_branch}"

    [[repos]]
    name = "server/api"
    path = "server/api"
    role = "api"
    verify = ["make lint BRANCH={branch}"]
    merge_base = true
    push_base = true
    queue_advance_after_merge = "api-merged"

    [[repos]]
    name = "clients/miniprogream"
    path = "clients/miniprogream"
    role = "miniprogram"
    needs = ["server/api"]
    verify = ["npm run lint -- --branch={branch}"]
    sdk_generate = "npm run sdk:gen -- --base={base_branch}"
    merge_base = true
    push_base = true
    upload = "make miniprogram-upload"

    [[repos]]
    name = "docs"
    path = "docs"
    role = "docs"
    verify = []
    merge_base = true
    push_base = true

    [[repos]]
    name = "root"
    path = "."
    role = "root"
    verify = []
    merge_base = true
    push_base = true
    post_delivery_checks = ["echo {branch} {base_branch}"]

    [policies]
    api_before_clients = true
    """
)


class DeliveryHelperTests(unittest.TestCase):
    def write_config(self) -> pathlib.Path:
        tmp_dir = pathlib.Path(tempfile.mkdtemp())
        config_path = tmp_dir / "delivery.toml"
        config_path.write_text(CONFIG_TEXT)
        return config_path

    def test_render_command_replaces_placeholders(self):
        module = load_module()
        result = module.render_command(
            "git push origin {base_branch} && echo {branch}",
            {"branch": "feature/topic", "base_branch": "develop", "stage": "queued"},
        )
        self.assertEqual(result, "git push origin develop && echo feature/topic")

    def test_repo_order_respects_needs(self):
        module = load_module()
        config = module.load_config(self.write_config())
        ordered = module.select_repos(config, None)
        self.assertEqual(
            [repo["name"] for repo in ordered],
            ["server/api", "clients/miniprogream", "docs", "root"],
        )

    def test_plan_contains_queue_and_root_finish_steps(self):
        module = load_module()
        config = module.load_config(self.write_config())
        steps = module.build_plan_steps(config, "feature/topic", None)
        commands = [step.command for step in steps]
        self.assertEqual(commands[0], "make merge-queue-enqueue BRANCH=feature/topic")
        self.assertEqual(commands[1], "make merge-queue-claim BRANCH=feature/topic")
        self.assertIn("make merge-queue-mark-root-merged BRANCH=feature/topic", commands)
        self.assertIn("make merge-queue-finish BRANCH=feature/topic", commands)

    def test_plan_appends_worktree_cleanup_after_root_finish_steps(self):
        module = load_module()
        config = module.load_config(self.write_config())
        module._find_base_worktree = lambda _root, _base_branch: pathlib.Path("/tmp/example-main")

        steps = module.build_plan_steps(config, "feature/topic", None)

        self.assertEqual(steps[-1].kind, "worktree-clean")
        self.assertEqual(steps[-1].repo, "root")
        self.assertEqual(steps[-1].cwd, "/tmp/example-main")
        self.assertEqual(steps[-1].command, "make worktree-clean BRANCH=feature/topic")
        self.assertEqual(steps[-2].command, "make merge-queue-status")

    def test_root_merge_and_push_run_from_base_branch_worktree(self):
        module = load_module()
        config = module.load_config(self.write_config())

        with tempfile.TemporaryDirectory() as tmp:
            main = pathlib.Path(tmp) / "main"
            task = pathlib.Path(tmp) / "task"
            subprocess.run(["git", "init", str(main)], check=True, capture_output=True)
            subprocess.run(["git", "checkout", "-b", "develop"], cwd=main, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=main, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=main, check=True)
            (main / "README.md").write_text("initial\n")
            subprocess.run(["git", "add", "README.md"], cwd=main, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=main, check=True, capture_output=True)
            subprocess.run(["git", "worktree", "add", "-b", "feature/topic", str(task), "develop"], cwd=main, check=True, capture_output=True)

            steps = module.build_plan_steps(config, "feature/topic", ["root"], root=task)

        merge_step = next(step for step in steps if step.kind == "merge-base")
        push_step = next(step for step in steps if step.kind == "push-base")
        self.assertEqual(merge_step.cwd, str(main.resolve()))
        self.assertEqual(push_step.cwd, str(main.resolve()))

    def test_plan_skips_worktree_cleanup_without_root_repo_or_clean_command(self):
        module = load_module()
        config = module.load_config(self.write_config())
        module._find_base_worktree = lambda _root, _base_branch: pathlib.Path("/tmp/example-main")

        docs_steps = module.build_plan_steps(config, "feature/topic", ["docs"])
        self.assertNotIn("worktree-clean", [step.kind for step in docs_steps])

        config_without_clean = module.load_config(self.write_config())
        del config_without_clean["worktree"]["clean"]
        root_steps = module.build_plan_steps(config_without_clean, "feature/topic", ["root"])
        self.assertNotIn("worktree-clean", [step.kind for step in root_steps])

    def test_find_base_worktree_falls_back_to_root_when_git_query_fails(self):
        module = load_module()

        def fake_git_output(*args, **kwargs):
            raise subprocess.CalledProcessError(128, "git worktree list")

        module._git_output = fake_git_output

        self.assertEqual(module._find_base_worktree(pathlib.Path("/tmp/task"), "develop"), pathlib.Path("/tmp/task"))

    def test_plan_renders_repo_command_templates_and_keeps_raw_upload(self):
        module = load_module()
        config = module.load_config(self.write_config())
        steps = module.build_plan_steps(config, "feature/topic", ["clients/miniprogream", "root"])
        commands = [step.command for step in steps]

        self.assertIn("make lint BRANCH=feature/topic", commands)
        self.assertIn("npm run lint -- --branch=feature/topic", commands)
        self.assertIn("npm run sdk:gen -- --base=develop", commands)
        self.assertIn("make miniprogram-upload", commands)
        self.assertIn("echo feature/topic develop", commands)

    def test_parse_status_paths_collects_modified_and_untracked_files(self):
        module = load_module()
        parsed = module.parse_status_paths(
            " M docs/README.md\nM  server/api/main.go\n?? clients/miniprogream/src/app.ts\n",
        )
        self.assertEqual(
            parsed,
            ["docs/README.md", "server/api/main.go", "clients/miniprogream/src/app.ts"],
        )

    def test_collect_changed_paths_by_source_separates_diff_status_and_untracked(self):
        module = load_module()

        def fake_git_output(_root, *args):
            if args[0] == "diff":
                return "README.md\ndocs/README.md\n"
            if args[0] == "status":
                return " M server/api/main.go\n?? docs/new.md\n"
            raise AssertionError(args)

        module._git_output = fake_git_output
        changed = module.collect_changed_paths_by_source("/tmp/example", "develop", "feature/topic")

        self.assertEqual(changed["diff"], ["README.md", "docs/README.md"])
        self.assertEqual(changed["status"], ["server/api/main.go"])
        self.assertEqual(changed["untracked"], ["docs/new.md"])

    def test_detect_repo_selection_expands_needs_and_root(self):
        module = load_module()
        config = module.load_config(self.write_config())
        detection = module.detect_repo_selection(
            config,
            ["clients/miniprogream/src/app.ts"],
        )
        self.assertEqual(detection["direct_repos"], ["clients/miniprogream"])
        self.assertEqual(
            detection["expanded_repos"],
            ["server/api", "clients/miniprogream", "root"],
        )
        self.assertEqual(
            detection["detection_reasons"]["clients/miniprogream"],
            ["clients/miniprogream/src/app.ts"],
        )

    def test_detected_only_skips_dependency_and_root_expansion(self):
        module = load_module()
        config = module.load_config(self.write_config())
        detection = module.detect_repo_selection(
            config,
            ["clients/miniprogream/src/app.ts"],
            detected_only=True,
        )
        self.assertEqual(detection["direct_repos"], ["clients/miniprogream"])
        self.assertEqual(detection["expanded_repos"], ["clients/miniprogream"])

    def test_detect_repo_selection_tracks_multiple_sources_per_repo(self):
        module = load_module()
        config = module.load_config(self.write_config())
        detection = module.detect_repo_selection_from_sources(
            config,
            {
                "diff": ["docs/INDEX.md"],
                "status": ["docs/README.md"],
                "untracked": ["docs/new.md"],
            },
        )

        self.assertEqual(detection["direct_repos"], ["docs"])
        self.assertEqual(detection["repo_detection_sources"]["docs"]["sources"], ["diff", "status", "untracked"])
        self.assertEqual(detection["repo_detection_sources"]["docs"]["paths"]["diff"], ["docs/INDEX.md"])
        self.assertEqual(detection["repo_detection_sources"]["docs"]["paths"]["status"], ["docs/README.md"])
        self.assertEqual(detection["repo_detection_sources"]["docs"]["paths"]["untracked"], ["docs/new.md"])

    def test_detect_repo_selection_maps_root_level_paths_to_root(self):
        module = load_module()
        config = module.load_config(self.write_config())
        detection = module.detect_repo_selection(
            config,
            ["README.md"],
        )
        self.assertEqual(detection["direct_repos"], ["root"])
        self.assertEqual(detection["expanded_repos"], ["root"])
        self.assertEqual(detection["detection_reasons"]["root"], ["README.md"])

    def test_root_pointer_fallback_preserves_detection_source(self):
        module = load_module()
        config = module.load_config(self.write_config())
        detection = module.detect_repo_selection_from_sources(
            config,
            {"diff": [], "status": ["docs"], "untracked": []},
        )
        module._repo_has_branch = lambda *args, **kwargs: False
        refined = module.refine_detection_for_root_pointer_changes(config, detection, self.write_config().parent, "feature/topic")

        self.assertEqual(refined["direct_repos"], ["root"])
        self.assertEqual(refined["repo_detection_sources"]["root"]["sources"], ["status"])
        self.assertEqual(refined["repo_detection_sources"]["root"]["paths"]["status"], ["docs"])

    def test_plan_payload_uses_auto_detect_when_repos_omitted(self):
        module = load_module()
        config = module.load_config(self.write_config())
        module.collect_changed_paths_by_source = lambda *args, **kwargs: {
            "diff": [],
            "status": ["docs/README.md"],
            "untracked": [],
        }

        payload = module.plan_payload(
            config,
            "feature/topic",
            None,
            root=self.write_config().parent,
        )

        self.assertEqual(payload["detected_repos"], ["docs"])
        self.assertEqual(payload["expanded_repos"], ["docs", "root"])
        self.assertEqual(payload["repos"], ["docs", "root"])
        self.assertEqual(payload["changed_paths_by_source"]["status"], ["docs/README.md"])
        self.assertEqual(payload["repo_detection_sources"]["docs"]["sources"], ["status"])

    def test_manual_repos_override_auto_detect(self):
        module = load_module()
        config = module.load_config(self.write_config())
        module.collect_changed_paths_by_source = lambda *args, **kwargs: {
            "diff": [],
            "status": ["docs/README.md"],
            "untracked": [],
        }

        payload = module.plan_payload(
            config,
            "feature/topic",
            ["server/api"],
            root=self.write_config().parent,
        )

        self.assertEqual(payload["detected_repos"], [])
        self.assertEqual(payload["expanded_repos"], ["server/api"])
        self.assertEqual(payload["repos"], ["server/api"])
        self.assertEqual(payload["repo_detection_sources"], {})

    def test_plan_payload_treats_missing_child_branch_as_root_pointer_change(self):
        module = load_module()
        config = module.load_config(self.write_config())
        module.collect_changed_paths_by_source = lambda *args, **kwargs: {
            "diff": ["docs"],
            "status": [],
            "untracked": [],
        }
        module._repo_has_branch = lambda *args, **kwargs: False

        payload = module.plan_payload(
            config,
            "feature/topic",
            None,
            root=self.write_config().parent,
        )

        self.assertEqual(payload["detected_repos"], ["root"])
        self.assertEqual(payload["expanded_repos"], ["root"])
        self.assertEqual(payload["repos"], ["root"])
        self.assertEqual(payload["repo_detection_sources"]["root"]["sources"], ["diff"])

    def test_print_plan_includes_detection_summary_and_expanded_only_repos(self):
        module = load_module()
        payload = {
            "project": "Example",
            "branch": "feature/topic",
            "base_branch": "develop",
            "root": "/tmp/example",
            "repos": ["docs", "root"],
            "detected_repos": ["docs"],
            "expanded_repos": ["docs", "root"],
            "detection_reasons": {"docs": ["docs/README.md"]},
            "changed_paths_by_source": {"diff": [], "status": ["docs/README.md"], "untracked": []},
            "repo_detection_sources": {
                "docs": {
                    "sources": ["status"],
                    "paths": {"status": ["docs/README.md"]},
                }
            }, 
            "unmatched_paths": ["tmp/debug.log"],
            "steps": [],
        }

        lines = module.render_detection_summary(payload)
        self.assertIn("Detected: docs [status]", lines)
        self.assertIn("docs: status=docs/README.md", lines)
        self.assertIn("Expanded only: root", lines)
        self.assertIn("Unmatched: tmp/debug.log", lines)

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            module.print_plan(payload)

        rendered = buffer.getvalue()
        self.assertIn("Detected: docs [status]", rendered)
        self.assertIn("docs: status=docs/README.md", rendered)
        self.assertIn("Expanded only: root", rendered)
        self.assertIn("Unmatched: tmp/debug.log", rendered)

    def test_run_steps_prints_failure_context_to_stderr(self):
        module = load_module()
        step = module.Step(kind="merge-base", repo="root", cwd="/tmp/example", command="false")
        failure = subprocess.CalledProcessError(1, "false")

        def fake_run(*args, **kwargs):
            raise failure

        self.addCleanup(setattr, module.subprocess, "run", module.subprocess.run)
        module.subprocess.run = fake_run
        stderr = io.StringIO()
        with self.assertRaises(subprocess.CalledProcessError):
            with contextlib.redirect_stderr(stderr):
                module.run_steps(
                    [step],
                    failure_context_lines=[
                        "Detected: root [diff]",
                        "Expanded only: docs",
                        "Unmatched: tmp/debug.log",
                    ],
                )

        rendered = stderr.getvalue()
        self.assertIn("FAILED: false", rendered)
        self.assertIn("Detected: root [diff]", rendered)
        self.assertIn("Expanded only: docs", rendered)
        self.assertIn("Unmatched: tmp/debug.log", rendered)

    def test_run_steps_omits_failure_context_when_empty(self):
        module = load_module()
        step = module.Step(kind="merge-base", repo="root", cwd="/tmp/example", command="false")
        failure = subprocess.CalledProcessError(1, "false")

        def fake_run(*args, **kwargs):
            raise failure

        self.addCleanup(setattr, module.subprocess, "run", module.subprocess.run)
        module.subprocess.run = fake_run
        stderr = io.StringIO()
        with self.assertRaises(subprocess.CalledProcessError):
            with contextlib.redirect_stderr(stderr):
                module.run_steps([step], failure_context_lines=[])

        rendered = stderr.getvalue()
        self.assertIn("FAILED: false", rendered)
        self.assertNotIn("Detected:", rendered)
        self.assertNotIn("Expanded only:", rendered)
        self.assertNotIn("Unmatched:", rendered)

    def test_run_steps_reports_cleanup_failure_without_raising(self):
        module = load_module()
        step = module.Step(kind="worktree-clean", repo="root", cwd="/tmp/example-main", command="false")
        failure = subprocess.CalledProcessError(1, "false")

        def fake_run(*args, **kwargs):
            raise failure

        self.addCleanup(setattr, module.subprocess, "run", module.subprocess.run)
        module.subprocess.run = fake_run
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            module.run_steps([step])

        rendered = stderr.getvalue()
        self.assertIn("CLEANUP FAILED: false", rendered)
        self.assertIn("CWD: /tmp/example-main", rendered)
        self.assertIn("EXIT CODE: 1", rendered)


if __name__ == "__main__":
    unittest.main()
