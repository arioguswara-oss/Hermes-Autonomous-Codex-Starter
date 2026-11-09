# Architecture — SANRO Hermes Coding Toolkit

```text
              Human Owner — sets project, goal, scope, duration
                                  |
                            GitHub Issue
                                  |
              [authenticated owner + schema validation]
                                  |
                 task queue / one-attempt claim ledger
                                  |
          +-----------------------+------------------------+
          |                 SANRO Hermes                   |
          |              project dispatcher               |
          +-----------------------+------------------------+
                                  |
                     isolated project worktree
                                  |
                   AI provider adapter boundary
                        /       |       \
                 Codex CLI    Claude*   Router / local*
                        \       |       /
                  controlled code changes + tests
                                  |
                     exact source diff allowlist
                                  |
                 dev commit → GitHub Draft PR only
                                  |
                  Human review / merge / deploy
```

*Claude/router/local are **extension proposals**. v0.1 currently implements a mock adapter and a Codex CLI **preview**, not an executing provider.*

## Communication control plane — SANRO Agent Bridge

**ChatGPT does not directly SSH into Hermes.** The SANRO reference design uses GitHub-backed task/status transport and an authorized **SANRO Agent Bridge** on the VPS to validate and dispatch work. Hermes coordinates workers; **Codex-CLI** performs coding; CI checks may run separately. A bridge ACK is not evidence of a successful coding task.

**The Bridge is not bundled in this starter.** See [Agent Bridge architecture](AGENT_BRIDGE.md).

## CI selection boundary (planned)

Build/test execution is a selectable **per-project CI adapter**, independent of coding-provider selection. Public projects should normally use standard GitHub-hosted Actions; private projects can use separately installed SANRO Local CI on a genuinely isolated host. GitHub self-hosted Actions runners are a different option. All CI paths must report commit SHA, test evidence, resource use and blocked/billable fallback conditions. **This is not implemented by the v0.1 mock or the v0.2 one-shot candidate.** See [CI strategy](CI_STRATEGY.md).

## Core interfaces

**Manifest:** exact fields `schema`, `taskId`, `repository`, `expectedHead`, `sourcePath`, `goal`, `expiresAt`, `owner`, `ownerApproval`. The parser rejects extra fields, expired tasks, path traversal and unauthorized operations. An executing worker must separately **verify the remote GitHub Issue author's identity**, immutable base commit and non-symlink file path.

**Provider:** `Provider.plan(task) -> ProviderPlan`. No adapter gets raw GitHub token or deployment credentials by default. Real execution belongs behind a separate reviewed process boundary, not the plan API. Model prompts are untrusted input.

**Ledger:** an exclusive, create-once claim. v0.1 demo's ledger is temporary, not durable service state. An autonomous worker must retain ledger and result files across restarts, handle stale jobs without uncontrolled retries, and avoid simultaneous work in multiple projects.

**Execution topology (future):** one Linux user/container per project, separate provider authentication, repo/worktrees, work queue, GitHub publisher, log/artifact store and CPU/memory budget. Work is queued when the human's Codex session or another project job needs priority.

## Evidence levels

| Level | Proof |
| --- | --- |
| PLANNED | Proposal/document only |
| IMPLEMENTED | Source committed |
| TESTED | CI or local test result; describe exactly what was tested |
| READY FOR OWNER | Reviewed release/development artifact |
| WORK (bounded autonomous) | Timer/job starts *without manual Codex invocation*, verified issue claim, actual provider code edit, tests, commit, Draft PR |
| LIVE | Human deployed and independently verified production |

Keep GitHub PASS distinct from runtime Work. Never label the v0.1 mock demo as a working autonomous coder.

## Production boundary

No automatic merge, migration, service restarts or application deployment. Deployment always requires human authorization and a separate release process.
