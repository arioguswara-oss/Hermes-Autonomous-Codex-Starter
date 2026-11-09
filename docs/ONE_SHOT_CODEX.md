# Bounded real Codex execution — SANRO Hermes v0.2 candidate

**Developer:** Ario Guswara · **Ecosystem:** SANRO · **Origin of Hermes Agent:** Nous Research. This is an independent coding toolkit, not an official Hermes Agent release.

## Status and boundaries

`python3 -m sanro_hermes.runner` is an **opt-in Codex-CLI one-shot candidate**. It can launch an already authenticated Codex CLI, check the actual source diff, run a fixed syntax test, and (only if separately requested) commit/push to a development branch and open a **Draft PR** using GitHub CLI. It never merges, deploys, migrates a database, or modifies hosting production.

**It is NOT yet an unattended GitHub Issue consumer, scheduled worker, or verified end-to-end VPS installation.** CI uses mocked Codex and GitHub publishing. No real authenticated Codex model call, real GitHub PR publication, or sandbox penetration test has been performed against this *public* module.

**Security warning:** Codex and tests can execute repository instructions/commands. This Python program's validation and post-hoc diff checks are *not* a security sandbox and cannot prevent secret reads or network exfiltration. Use a dedicated user/container/VM with genuine filesystem/network isolation before `--execute`. The `--isolated-runtime` flag is only your explicit acknowledgement; it is not proof of technical confinement.

## Before a real task

1. Work in a **development-only** GitHub repository containing a tracked, existing target file and a clean local checkout of the exact commit on your selected base branch.
2. Prepare a **separate worker identity**, isolated HOME/CODEX_HOME, narrow GitHub account, no production/other-project credentials, and an actual sandbox/container. The public runner preserves Codex `--sandbox workspace-write` and `--ask-for-approval never`, and does not disable its sandbox.
3. Confirm Codex CLI is installed and signed in through your own eligible ChatGPT account. For publishing, install `gh` and authenticate an account authorized to push a development branch and create Draft PRs. Do not create extra API billing accounts or copy anyone else's login secrets.
4. Create private (mode `0700`) **separate** `state` and `jobs` directories outside your source repository. Use only an isolated filesystem. No private file paths or production secrets belong in the task JSON.
5. Create a fresh manifest with real `repository`, `owner`, immutable 40-character commit SHA, exact `sourcePath`, short `goal`, and `expiresAt` within 24 hours. The `owner` field in the JSON is **not authenticated proof of delegation**; this one-shot CLI is for tasks the human owner already directly authorized and placed locally.

## Generic example (replace placeholders with *your* sandbox paths)

```bash
# These examples are for a disposable, dedicated development sandbox.
# This is NOT a SANRO production/VPS installation script.
python3 -m sanro_hermes.cli init-task --owner your-github-user \
  --repo your-github-user/your-test-repo \
  --source src/example.js > task.json
# Edit task.json to replace expectedHead with the actual git rev-parse HEAD.
# The example goal is documentation-only. Choose --test node-check for JS.

mkdir -m 700 -p "$HOME/sanro-run-state" "$HOME/sanro-run-jobs"

# Preflight only: no Codex, no git commits, no GitHub writes
python3 -m sanro_hermes.runner task.json \
  --allowed-repo your-github-user/your-test-repo \
  --repo-checkout /sandbox/your-test-repo \
  --state-root "$HOME/sanro-run-state" \
  --job-root "$HOME/sanro-run-jobs" \
  --test node-check

# Real Codex and fixed syntax test; NO push/PR, first validate your isolation
python3 -m sanro_hermes.runner task.json \
  --allowed-repo your-github-user/your-test-repo \
  --repo-checkout /sandbox/your-test-repo \
  --state-root "$HOME/sanro-run-state" \
  --job-root "$HOME/sanro-run-jobs" \
  --test node-check --execute --isolated-runtime
```

**IMPORTANT:** The real run consumes a one-attempt claim. Use a **fresh task ID/manifest** for the subsequent publishing run; the same task cannot run twice by design. The first real run discards its temporary worktree after the test and cannot publish that same change later. This is an intentional anti-replay safety choice. To create a Draft PR on the *first* real execution instead, choose `--execute --isolated-runtime --publish-draft` on a new, preapproved task, **after confirming the sandbox, tests and GitHub permissions**. Do not use this for production repositories.

## Verified/blocked behavior

Preflight refuses mismatched GitHub origin, wrong base SHA, dirty checkout, wrong source paths, filesystem symlink targets, repeated task claims and missing prerequisites. A real run creates a private temporary Git worktree; Codex sees a narrow, explicit instruction, and the changed paths must match **exactly** the one target file. Fixed tests currently available:
- `node-check`: `node --check <target.js|.mjs|.cjs>`, for syntax only.
- `python-ast`: parse the specified `.py` using Python AST without writing bytecode.

These **are syntax tests**, not full regression or security tests. Before release-grade PR automation, contributors must integrate real project regression suites **inside a secure execution environment**, not accept shell snippets from a GitHub issue.

On publish, the runner stages only the allowlisted file, writes a dev-only commit, pushes to `sanro-hermes/<task-id>` and asks `gh pr create --draft`. It never merges. When PR publication fails **after** a push, the branch can remain on GitHub; the claim stays taken and a human must inspect it—do not retry blindly.

The original dev checkout is not modified in source content (Git worktree metadata and temporary local branch refs may be created). Temporary worktrees are deleted, but the claim is retained. No raw subprocess stdout/stderr is exposed to console; keep your own protected observability outside the model.

## Community next steps

- Verified upstream **Hermes Agent** orchestration integration, following Nous Research API/extension points.
- Owner-authenticated GitHub Issue reader, one-attempt queue/timer, audit-safe statuses.
- Stronger technical isolation and credential/egress controls; non-root Linux identities per project.
- Real regression tests, resource limits, cancel/recovery and independent CI audit.
- Optional Claude Code, 9router and local model adapters with honest terms/cost reporting.

See [SECURITY](../SECURITY.md), [providers](PROVIDERS.md), and [roadmap](../ROADMAP.md).
