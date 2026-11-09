# P0 Integration baseline — SANRO Hermes Coding Toolkit

**Status: IMPLEMENTED candidate (offline integration adapters), NOT a functioning VPS runtime installer.** Applies to public toolkit development branch and Issue #6. Web Control Panel work remains deferred.

## What the unified installer can actually do

One entrypoint, `installer/sanro_install.py`, now exposes the following **non-mutating** operations:

| Command | Actual effect | Does NOT prove |
| --- | --- | --- |
| `plan` | Show component catalog and current external/missing status | Hermes installed, autonomy WORK |
| `preflight` | Inspect PATH for Git, GitHub CLI, Codex, Node/npm, Bubblewrap | Credentials, correct Linux identity, sandbox or sufficient VPS resources |
| `golden-plan` | Verify SHA-256 pinned Node Golden Worker V2 manifest **and separate external installer candidate**, validate exact private V2 manifest contract, print redacted integration plan | Does not execute/install worker, run tests, activate systemd or connect Hermes |
| `ci-plan` | Call **authenticated `gh api`** for allowlisted GitHub repository metadata and recommend CI policy | Does not start Actions or claim Local CI ready |
| `bridge-plan` | Validate separately pinned, READ-ONLY SANRO Agent Bridge V1 task envelope | Does not enqueue, execute Codex or write to GitHub |
| `ci-report` | Parse separately pinned Local CI V1 JSON result into **redacted** summary | Does not attest runner identity, run tests or prove the job was executed by trusted infrastructure |
| `prepare` | Copy only public-allowlisted docs/adapter to a NEW non-live directory, record SHA-256 checksums | Not VPS/hosting STAGED or installed |
| `verify` | Verify the prepared copy's file hashes without running code | Not a runtime proof |

The private Node installer from `Sanro-AI-Supervisor` Draft PR #72 is **not copied, downloaded or republished** here. The public side only validates a locally available, independently **Owner-reviewed and pinned** external file. This is a deliberately narrow integration boundary.

## Golden Worker Node V2 contract

The separately reviewed private candidate accepts exact keys:

```json
{
  "schema": 2,
  "project": "contoh-node",
  "repository": "arioguswara-oss/APPROVED-NODE-REPO",
  "baseCommit": "0000000000000000000000000000000000000000",
  "sourcePath": "backend/src/approved-file.js",
  "candidateBlob": "0000000000000000000000000000000000000000",
  "profile": "node",
  "ownerApproval": "CODING_TEST_COMMIT_DRAFT_ONLY"
}
```

**For illustration only:** zero SHAs are not real reviewed commits/blobs. Never treat placeholder data as delegation. Use **two independently recorded trusted pins**: the full manifest file SHA-256 and the external installer's SHA-256. These hashes **must be delivered by an Owner-controlled review channel**, not accepted merely from the untrusted manifest or a self-computed local hash. The adapter rejects extra keys, wrong paths, missing pins, invalid repo, symlinks and writable files.

Only the **Node backend** V2 contract is available; Android/Gradle still needs its own audited adapter. The private installer has a hard-coded SANRO-specific owner and VPS environment; **do not** assume it is a generic cross-company installer.

### Integration boundary to real runtime

A later, separate step may invoke the reviewed private V2 installer in **plan** mode inside an isolated, Owner-authorized environment. Its `--apply` or `--enable-timer` flags **are not available through the public toolkit CLI**. Any development-only installation must be separately authorized, isolate credentials/process identities/worktrees, and prove a bounded Issue → Codex → tests → dev Draft PR canary. There is **no automatic SSH/MCP VPS access** from this ChatGPT conversation.

## CI route / cost policy

`ci-plan` reads repository privacy through the currently authenticated GitHub CLI rather than through untrusted Issue text. **Public:** recommend standard GitHub Actions, without starting a run. **Private:** return `BLOCKED` until independent SANRO Local CI readiness and isolation have been established; do not silently fall back to billable GitHub-hosted Actions. The `localCiOperatorClaim` field does not authenticate such readiness.

Codex CLI remains the **primary coding engine**. SANRO Local CI is an optional validation gate, not a substitute. The public adapter does not assert an actual installation or CI test on the Owner's VPS.

## Security and non-distribution

- No arbitrary shell execution, HTTP fetch, package installation, token handling, production changes or GitHub workflow triggering in `golden-plan` / `preflight`.
- `ci-plan` makes a narrowly scoped **read-only GitHub metadata** API call and never exposes stderr/auth tokens to output.
- Strict manifest allowlist and SHA validation; external code is not executed.
- Existing Codex Rio, Hermes POS Public, Superadmin, Ticket, backup/cron and monitoring stay untouched.
- Merge/production deploy remain Owner-only. Existing successful workers do not need to be replaced.
- The source must pass standalone offline tests and then real disposable VPS canary before anyone claims runtime **TESTED** or **WORK**.

**The acceptance gate for Issue #6 remains OPEN:** one reviewed end-to-end task using separate authenticated worker identity, actual Codex code edit, real tests, dev commit and Draft PR with redacted evidence.
