"""Offline integration tests for the opt-in executor (no Codex login/API/GitHub access)."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase, mock
import os
import subprocess
import tempfile

from sanro_hermes.manifest import APPROVAL, validate
from sanro_hermes.runner import (
    RunBlocked, _assert_only_target, _changed_paths, _test_argv, preflight,
    run_once,
)


def cmd(*args: str, cwd: Path) -> str:
    p = subprocess.run(
        list(args), cwd=cwd, text=True, capture_output=True, check=True)
    return p.stdout.strip()


class RunnerTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.checkout = self.root / "checkout"
        self.checkout.mkdir()
        cmd("git", "init", "-b", "main", cwd=self.checkout)
        cmd("git", "config", "user.email", "test@example.invalid", cwd=self.checkout)
        cmd("git", "config", "user.name", "SANRO Test", cwd=self.checkout)
        (self.checkout / "src").mkdir()
        (self.checkout / "src" / "app.js").write_text(
            "'use strict';\nconst x = 1;\n", encoding="utf-8")
        cmd("git", "add", "src/app.js", cwd=self.checkout)
        cmd("git", "commit", "-m", "baseline", cwd=self.checkout)
        cmd("git", "remote", "add", "origin",
            "https://github.com/example-owner/example-repo.git",
            cwd=self.checkout)
        self.sha = cmd("git", "rev-parse", "HEAD", cwd=self.checkout)
        self.state = self.root / "state"
        self.jobs = self.root / "jobs"
        self.state.mkdir(mode=0o700)
        self.jobs.mkdir(mode=0o700)
        self.task = validate({
            "schema": 1,
            "taskId": "safe-codex-canary-001",
            "repository": "example-owner/example-repo",
            "expectedHead": self.sha,
            "sourcePath": "src/app.js",
            "goal": "Add a small JSDoc comment with no runtime behavior changes.",
            "expiresAt": (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "owner": "example-owner",
            "ownerApproval": APPROVAL,
        })

    def run_task(self, **overrides):
        kwargs = dict(
            checkout=self.checkout, state_root=self.state,
            job_root=self.jobs, base="main",
            test_profile="node-check",
            execute=False, publish=False, isolated=False)
        kwargs.update(overrides)
        return run_once(self.task, **kwargs)

    def test_preview_does_not_change_repo_or_claim(self):
        output = self.run_task()
        self.assertEqual(output.status, "PREVIEW_ONLY")
        self.assertEqual(list(self.state.iterdir()), [])
        self.assertEqual(cmd("git", "status", "--porcelain", cwd=self.checkout), "")

    def test_preflight_rejects_dirty_checkout(self):
        (self.checkout / "dirty.txt").write_text("unexpected")
        with self.assertRaises(RunBlocked):
            self.run_task()

    def test_preflight_rejects_wrong_remote(self):
        cmd("git", "remote", "set-url", "origin",
            "https://github.com/another/owner.git", cwd=self.checkout)
        with self.assertRaisesRegex(RunBlocked, "GIT_ORIGIN_MISMATCH"):
            self.run_task()

    def test_preflight_rejects_wrong_base_sha(self):
        other = type(self.task)(
            self.task.task_id, self.task.repository, "a"*40,
            self.task.source_path, self.task.goal,
            self.task.expires_at, self.task.owner)
        with self.assertRaisesRegex(RunBlocked, "BASE_COMMIT_CHANGED"):
            preflight(other, self.checkout, self.state, self.jobs, base="main")

    def test_no_silent_codex_execution_without_isolation(self):
        with self.assertRaisesRegex(RunBlocked, "ISOLATED_RUNTIME_CONFIRMATION_REQUIRED"):
            self.run_task(execute=True)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_syntax_test_profiles(self):
        self.assertEqual(_test_argv("node-check", "src/app.js")[:2],
                         ("node", "--check"))
        with self.assertRaisesRegex(RunBlocked, "TEST_PROFILE_MISMATCH"):
            _test_argv("python-ast", "src/app.js")

    def test_one_shot_local_with_mocked_codex(self):
        def fake_run(args, cwd, *, timeout, env):
            if args[0] == "codex":
                target = cwd / self.task.source_path
                target.write_text(target.read_text() + "// safe documentation\n")
                self.assertNotIn("GH_TOKEN", env)
                self.assertEqual(args[2:4], ("--sandbox", "workspace-write"))
            elif args[0] == "node":
                self.assertEqual(args[1], "--check")
            else:
                self.fail("Unexpected command")
        with mock.patch("sanro_hermes.runner.shutil.which", return_value="/fake/codex"):
            with mock.patch("sanro_hermes.runner._silent", side_effect=fake_run):
                with mock.patch.dict(os.environ, {"GH_TOKEN": "must-not-reach-codex"}):
                    result = self.run_task(execute=True, isolated=True)
        self.assertEqual(result.status, "TESTED_LOCAL_NOT_PUBLISHED")
        self.assertIsNone(result.draft_pr)
        self.assertEqual(len(list(self.state.iterdir())), 1)
        self.assertEqual(list(self.jobs.iterdir()), [])
        self.assertEqual(cmd("git", "status", "--porcelain", cwd=self.checkout), "")
        # No second execution of the same task ID.
        with mock.patch("sanro_hermes.runner.shutil.which", return_value="/fake/codex"):
            with self.assertRaises(FileExistsError):
                self.run_task(execute=True, isolated=True)

    def test_codex_extra_file_is_blocked(self):
        def fake_codex(args, cwd, *, timeout, env):
            if args[0] == "codex":
                (cwd / "src" / "another.js").write_text("unexpected")
                target = cwd / self.task.source_path
                target.write_text(target.read_text() + "// comment\n")
        with mock.patch("sanro_hermes.runner.shutil.which", return_value="/fake/codex"):
            with mock.patch("sanro_hermes.runner._silent", side_effect=fake_codex):
                with self.assertRaisesRegex(RunBlocked, "CHANGED_PATH_SCOPE"):
                    self.run_task(execute=True, isolated=True)
        self.assertEqual(list(self.jobs.iterdir()), [])

    def test_changed_paths_preserve_filenames_with_spaces(self):
        file = self.checkout / "src" / "leading space.js"
        file.write_text("const a=2;")
        self.assertIn("src/leading space.js", _changed_paths(self.checkout))

    def test_no_publish_without_test(self):
        # Fake Codex exits with a fixed error; test and GitHub publish are never called.
        def fail_codex(args, cwd, *, timeout, env):
            raise RunBlocked("EXECUTOR_EXIT_NONZERO")
        import sanro_hermes.runner as runner
        actual_invoke = runner._invoke
        def no_network(args, cwd, *, timeout=20, env=None):
            if tuple(args[:3]) == ("git", "ls-remote", "--heads"):
                return ""
            return actual_invoke(args, cwd, timeout=timeout, env=env)
        with mock.patch("sanro_hermes.runner.shutil.which", return_value="/fake/codex"):
            with mock.patch("sanro_hermes.runner._invoke", side_effect=no_network):
                with mock.patch("sanro_hermes.runner._silent", side_effect=fail_codex):
                    with self.assertRaisesRegex(RunBlocked, "EXECUTOR_EXIT_NONZERO"):
                        self.run_task(execute=True, publish=True, isolated=True)
        self.assertEqual(list(self.jobs.iterdir()), [])

    def test_git_publish_sequence_is_mocked_and_draft_only(self):
        import sanro_hermes.runner as runner
        invoke_real = runner._invoke
        invoked = []
        def guarded_invoke(args, cwd, *, timeout=20, env=None):
            if tuple(args[:3]) == ("git", "ls-remote", "--heads"):
                return ""
            if tuple(args[:2]) == ("git", "push"):
                invoked.append("development_push")
                self.assertEqual(args[-1], "HEAD:refs/heads/sanro-hermes/safe-codex-canary-001")
                return ""
            if tuple(args[:3]) == ("gh", "pr", "create"):
                self.assertIn("--draft", args)
                self.assertNotIn("merge", args)
                invoked.append("draft_pr")
                return "https://github.com/example-owner/example-repo/pull/99"
            return invoke_real(args, cwd, timeout=timeout, env=env)
        def fake_process(args, cwd, *, timeout, env):
            if args[0] == "codex":
                target = cwd / self.task.source_path
                target.write_text(target.read_text() + "// safe comment\n")
        with mock.patch("sanro_hermes.runner.shutil.which", return_value="/fake/bin"):
            with mock.patch("sanro_hermes.runner._invoke", side_effect=guarded_invoke):
                with mock.patch("sanro_hermes.runner._silent", side_effect=fake_process):
                    result = self.run_task(execute=True, isolated=True, publish=True)
        self.assertEqual(result.status, "DRAFT_PR_CREATED")
        self.assertEqual(result.draft_pr, "https://github.com/example-owner/example-repo/pull/99")
        self.assertEqual(invoked, ["development_push", "draft_pr"])
        self.assertEqual(cmd("git", "status", "--porcelain", cwd=self.checkout), "")
