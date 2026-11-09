# Operations guide (future real worker)

> v0.1 is a **no-side-effects mock/preview**. This page is a review checklist for contributors implementing an executing worker, **not a command recipe for unattended VPS deployment**.

## Preparing one project

1. Identify the development repository, accepted tasks, base SHA, test suite, branch naming convention and final reviewer.
2. Create a dedicated non-root Linux identity/container or VM with no production permissions. Keep separate `HOME`, `CODEX_HOME`, GitHub publisher, workspace, worktrees, ledger and logs.
3. Establish a narrow filesystem write allowlist and a reviewed outbound network/credential policy. AI model or test command must not read production files, host SSH keys or customer records.
4. Verify GitHub issue author against GitHub's authenticated identity, not a freely typed `owner` field in an uploaded JSON file.
5. Check original repository is clean and HEAD equals the reviewed commit, then create an exclusive worktree/branch and one-attempt task claim.
6. Run provider in a **single compatible isolation boundary**; prove it can genuinely edit a harmless allowlisted file.
7. Verify the exact diff, run relevant tests, commit/push only to a development branch and create a **Draft PR**. Require human review for merge/release.
8. Apply resource and concurrency bounds. If another worker or the human is busy, **queue** rather than kill or preempt.
9. For any failure, preserve result and logs with secrets redacted. Report one **BLOCKED** reason; do not automatically re-run risky jobs or erase claims.

## End-to-end acceptance checklist

- [ ] Task authorized by actual repository Owner; known immutable base and fresh expiry.
- [ ] Only approved repo/source file writable.
- [ ] Actual provider/model executed (not just `--help` or login success).
- [ ] Changed-file list matches allowlist; tests PASS with evidence.
- [ ] Commit and development Draft PR published by authorized worker account.
- [ ] No production changes, secret exfiltration, impact on other workers or owner's CLI.
- [ ] Status accurately recorded: VERIFIED/UNVERIFIED/BLOCKED as appropriate.

## Safety and audit

A provider CLI may run subprocesses. Treat workspace tests and code as untrusted; a shared Linux UID does not protect other projects. Don't re-use proprietary SANRO files or copy any real SANRO server config into this public starter.

## Low-cost operations

Run only needed jobs, right-size models to tasks, keep prompts focused, avoid repeated failing trials, schedule modest poll intervals and observe rate limits. A lighter model may help simple changes but should be measured, not promised.
