"""Opt-in bounded local Codex one-shot runner.

This is a development-only tool. It is NOT a general-purpose security
sandbox. Run it only under a separate, properly isolated Linux user/container
with no production access or unrelated credentials.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from typing import Sequence

from .manifest import ManifestError, Task, load
from .state import claim_once


class RunBlocked(RuntimeError):
    """Fixed error category safe to print; never attach raw subprocess logs."""


@dataclass(frozen=True)
class RunResult:
    status: str
    task_id: str
    branch: str | None = None
    draft_pr: str | None = None

    def public(self) -> dict[str, str | None]:
        return {
            "status": self.status,
            "taskId": self.task_id,
            "branch": self.branch,
            "draftPR": self.draft_pr,
            "deployed": "false",
        }


def _invoke(args: Sequence[str], cwd: Path, *, timeout: int = 20,
            env: dict[str, str] | None = None) -> str:
    try:
        result = subprocess.run(
            list(args), cwd=cwd, env=env, capture_output=True, text=True,
            timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunBlocked("LOCAL_COMMAND_UNAVAILABLE_OR_TIMEOUT") from exc
    if result.returncode:
        # Deliberately never expose stderr/stdout: can contain secrets.
        raise RunBlocked("LOCAL_COMMAND_FAILED")
    # Do not use .strip(): it can corrupt git status leading columns.
    return result.stdout.rstrip(chr(10) + chr(13))


def _silent(args: Sequence[str], cwd: Path, *, timeout: int,
            env: dict[str, str]) -> None:
    """Kill an entire model/test process group on timeout, with no raw logs."""
    try:
        child = subprocess.Popen(
            list(args), cwd=cwd, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as exc:
        raise RunBlocked("EXECUTOR_NOT_AVAILABLE") from exc
    try:
        child.communicate(input=b"", timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        os.killpg(child.pid, signal.SIGKILL)
        child.communicate()
        raise RunBlocked("EXECUTOR_TIMEOUT") from exc
    if child.returncode:
        raise RunBlocked("EXECUTOR_EXIT_NONZERO")


def _safe_env() -> dict[str, str]:
    # Never pass GitHub or paid API keys into the model/test process.
    # Home/CODEX_HOME still require a truly isolated external environment.
    allow = ("PATH", "HOME", "CODEX_HOME", "LANG", "LC_ALL", "TERM",
             "TMPDIR", "SSL_CERT_FILE", "SSL_CERT_DIR", "XDG_CONFIG_HOME",
             "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY")
    return {key: os.environ[key] for key in allow if key in os.environ}


def _confirm_private_root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir() or path.stat().st_mode & 0o077:
        raise RunBlocked("STATE_OR_WORK_ROOT_NOT_PRIVATE")
    return path.resolve(strict=True)


def _repo_remote(root: Path, task: Task) -> None:
    remote = _invoke(("git", "remote", "get-url", "origin"), root)
    # Don't log remote URL: it may embed credentials.
    accepted = {
        f"https://github.com/{task.repository}",
        f"https://github.com/{task.repository}.git",
        f"git@github.com:{task.repository}",
        f"git@github.com:{task.repository}.git",
        f"ssh://git@github.com/{task.repository}",
        f"ssh://git@github.com/{task.repository}.git",
    }
    if remote not in accepted:
        raise RunBlocked("GIT_ORIGIN_MISMATCH")


def preflight(task: Task, checkout: Path, state_root: Path,
              job_root: Path, *, base: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", base) or base.startswith("-"):
        raise RunBlocked("INVALID_BASE")
    if checkout.is_symlink() or not checkout.is_dir():
        raise RunBlocked("CHECKOUT_NOT_REAL_DIRECTORY")
    checkout = checkout.resolve(strict=True)
    state_root = _confirm_private_root(state_root)
    job_root = _confirm_private_root(job_root)
    if checkout in (state_root, job_root):
        raise RunBlocked("OVERLAPPING_WORK_ROOT")
    if state_root.is_relative_to(checkout) or job_root.is_relative_to(checkout):
        raise RunBlocked("STATE_INSIDE_REPOSITORY")
    if state_root == job_root or state_root.is_relative_to(job_root) or job_root.is_relative_to(state_root):
        raise RunBlocked("OVERLAPPING_STATE_ROOTS")
    if _invoke(("git", "rev-parse", "--show-toplevel"), checkout) != str(checkout):
        raise RunBlocked("INVALID_REPOSITORY_ROOT")
    _repo_remote(checkout, task)
    if _invoke(("git", "rev-parse", "HEAD"), checkout) != task.expected_head:
        raise RunBlocked("BASE_COMMIT_CHANGED")
    if _invoke(("git", "status", "--porcelain", "-z"), checkout):
        raise RunBlocked("CHECKOUT_DIRTY")
    _invoke(("git", "rev-parse", "--verify", f"refs/heads/{base}"), checkout)
    if _invoke(("git", "rev-parse", base), checkout) != task.expected_head:
        raise RunBlocked("BASE_BRANCH_MOVED")
    _invoke(("git", "ls-files", "--error-unmatch", "--", task.source_path), checkout)
    source = checkout / task.source_path
    if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(checkout):
        raise RunBlocked("UNSAFE_SOURCE_FILE")
    return checkout


def _changed_paths(work: Path) -> set[str]:
    # NUL-separated paths preserve leading spaces (porcelain .strip() bug).
    tracked = subprocess.run(
        ["git", "diff", "--name-only", "-z", "HEAD"], cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=work, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    if tracked.returncode or untracked.returncode:
        raise RunBlocked("GIT_DIFF_FAILED")
    return {
        os.fsdecode(name)
        for name in (tracked.stdout + untracked.stdout).split(b"\x00")
        if name
    }


def _assert_only_target(work: Path, task: Task) -> None:
    if _invoke(("git", "rev-parse", "HEAD"), work) != task.expected_head:
        raise RunBlocked("CODEX_CHANGED_GIT_HISTORY")
    target = work / task.source_path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(work):
        raise RunBlocked("TARGET_MISSING_OR_SYMLINK")
    if _changed_paths(work) != {task.source_path}:
        raise RunBlocked("CHANGED_PATH_SCOPE")


def _test_argv(profile: str, target: str) -> tuple[str, ...]:
    if profile == "node-check":
        if not target.endswith((".js", ".cjs", ".mjs")):
            raise RunBlocked("TEST_PROFILE_MISMATCH")
        return ("node", "--check", target)
    if profile == "python-ast":
        if not target.endswith(".py"):
            raise RunBlocked("TEST_PROFILE_MISMATCH")
        # AST parsing validates syntax without generating __pycache__ files.
        return ("python3", "-c",
                "import ast,pathlib,sys; ast.parse(pathlib.Path(sys.argv[1]).read_text())",
                target)
    raise RunBlocked("UNSUPPORTED_TEST_PROFILE")


def _branch(task: Task) -> str:
    return "sanro-hermes/" + task.task_id


def run_once(task: Task, *, checkout: Path, state_root: Path,
             job_root: Path, base: str, test_profile: str,
             execute: bool, publish: bool, isolated: bool,
             timeout: int = 480) -> RunResult:
    checkout = preflight(task, checkout, state_root, job_root, base=base)
    tests = _test_argv(test_profile, task.source_path)
    branch = _branch(task)
    if not execute:
        return RunResult("PREVIEW_ONLY", task.task_id, branch)
    if not isolated:
        raise RunBlocked("ISOLATED_RUNTIME_CONFIRMATION_REQUIRED")
    if os.geteuid() == 0:
        raise RunBlocked("ROOT_EXECUTION_FORBIDDEN")
    if timeout < 30 or timeout > 900:
        raise RunBlocked("INVALID_TIMEOUT")
    if publish and not shutil.which("gh"):
        raise RunBlocked("GITHUB_CLI_UNAVAILABLE")
    if not shutil.which("codex"):
        raise RunBlocked("CODEX_CLI_UNAVAILABLE")
    # Check branch collisions BEFORE claiming a one-shot job.
    existing = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", "refs/heads/" + branch],
        cwd=checkout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if existing.returncode == 0:
        raise RunBlocked("LOCAL_BRANCH_ALREADY_EXISTS")
    if existing.returncode not in (0, 1):
        raise RunBlocked("BRANCH_CHECK_FAILED")
    if publish:
        remote = _invoke(("git", "ls-remote", "--heads", "origin", branch),
                         checkout, timeout=25)
        if remote:
            raise RunBlocked("REMOTE_BRANCH_ALREADY_EXISTS")

    # One-attempt claim: any failure needs manual diagnosis and a NEW task ID.
    claim_once(state_root, task)
    workspace = Path(tempfile.mkdtemp(prefix="task-", dir=job_root))
    workspace.chmod(0o700)
    work = workspace / "source"
    added = False
    try:
        _invoke(("git", "worktree", "add", "--detach", str(work),
                 task.expected_head), checkout, timeout=60)
        added = True
        _invoke(("git", "switch", "-c", branch), work)
        prompt = (
            "SANRO Hermes task " + task.task_id + ".\n"
            "Repository: " + task.repository + "\n"
            "Only edit existing file: " + task.source_path + "\n"
            "Goal: " + task.goal + "\n"
            "Do not modify any other file, run git commit/push, "
            "read secrets, contact external sites, or attempt deployment."
        )
        env = _safe_env()
        # Real execution requires the isolated identity/container described in
        # SECURITY.md. Codex's own workspace-write sandbox is kept enabled.
        _silent(("codex", "exec", "--sandbox", "workspace-write",
                 "--ask-for-approval", "never", prompt),
                work, timeout=timeout, env=env)
        _assert_only_target(work, task)
        _silent(tests, work, timeout=min(timeout, 120), env=env)
        _assert_only_target(work, task)
        if not publish:
            return RunResult("TESTED_LOCAL_NOT_PUBLISHED", task.task_id, branch)

        git_env = os.environ.copy()
        git_env.update({
            "GIT_AUTHOR_NAME": "SANRO Hermes Worker",
            "GIT_AUTHOR_EMAIL": "sanro-hermes-worker@users.noreply.github.com",
            "GIT_COMMITTER_NAME": "SANRO Hermes Worker",
            "GIT_COMMITTER_EMAIL": "sanro-hermes-worker@users.noreply.github.com",
        })
        _invoke(("git", "add", "--", task.source_path), work)
        if _changed_paths(work) != {task.source_path}:
            raise RunBlocked("PRECOMMIT_SCOPE_CHANGED")
        _invoke(("git", "commit", "-m", "chore(hermes): " + task.task_id),
                work, timeout=40, env=git_env)
        _invoke(("git", "push", "origin", "HEAD:refs/heads/" + branch),
                work, timeout=120)
        result = _invoke((
            "gh", "pr", "create", "--repo", task.repository,
            "--draft", "--base", base, "--head", branch,
            "--title", "SANRO Hermes: " + task.task_id,
            "--body", "Owner task " + task.task_id +
            ". Test profile: " + test_profile +
            ". Development only, not merged or deployed."
        ), work, timeout=60)
        expected = "https://github.com/" + task.repository + "/pull/"
        if not (result.startswith(expected)
                and result.removeprefix(expected).isdigit()):
            raise RunBlocked("PR_RESULT_UNVERIFIED")
        return RunResult("DRAFT_PR_CREATED", task.task_id, branch, result)
    finally:
        if added:
            # Only the unique, private transient worktree created above.
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(work)],
                cwd=checkout, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=30, check=False)
        shutil.rmtree(workspace, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SANRO Hermes bounded one-shot Codex candidate")
    parser.add_argument("manifest")
    parser.add_argument("--repo-checkout", required=True, type=Path)
    parser.add_argument("--allowed-repo", required=True)
    parser.add_argument("--allow-prefix", default="src/")
    parser.add_argument("--base", default="main")
    parser.add_argument("--state-root", required=True, type=Path)
    parser.add_argument("--job-root", required=True, type=Path)
    parser.add_argument("--test", choices=("node-check", "python-ast"), required=True)
    parser.add_argument("--timeout", type=int, default=480)
    parser.add_argument("--execute", action="store_true", help="call Codex, requires isolated runtime")
    parser.add_argument("--publish-draft", action="store_true", help="commit, push and Draft PR (requires --execute)")
    parser.add_argument("--isolated-runtime", action="store_true",
                        help="acknowledge external user/container isolation; NOT checked by this script")
    args = parser.parse_args(argv)
    if args.publish_draft and not args.execute:
        parser.error("--publish-draft requires --execute")
    try:
        task = load(args.manifest, allowed_repository=args.allowed_repo,
                    allowed_prefix=args.allow_prefix)
        result = run_once(
            task, checkout=args.repo_checkout, state_root=args.state_root,
            job_root=args.job_root, base=args.base, test_profile=args.test,
            execute=args.execute, publish=args.publish_draft,
            isolated=args.isolated_runtime, timeout=args.timeout)
        print(json.dumps(result.public(), sort_keys=True))
        return 0
    except (ManifestError, RunBlocked, FileExistsError) as exc:
        category = str(exc) if isinstance(exc, (ManifestError, RunBlocked)) else "TASK_ALREADY_CLAIMED"
        print(json.dumps({"status": "BLOCKED", "reason": category}),
              file=sys.stderr)
        return 2
    except (OSError, subprocess.SubprocessError):
        print(json.dumps({"status": "BLOCKED", "reason": "LOCAL_RUNTIME_ERROR"}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
