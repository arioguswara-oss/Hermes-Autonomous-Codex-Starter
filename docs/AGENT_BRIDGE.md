# SANRO Agent Bridge — ChatGPT ↔ Hermes communication model

**Documentation update: 9 November 2026.** This describes the **SANRO reference architecture**, not a turnkey bridge included in this public repository. The separate upstream [Hermes Agent](https://github.com/NousResearch/hermes-agent) is maintained by Nous Research and must be credited independently.

## The missing layer: ChatGPT does not SSH into Hermes

SANRO's intended supervision and delegation path is **indirect**:

```text
Owner Rio → ChatGPT (supervisor)
                 |
                 v
      GitHub connector / scoped task submission
                 |
                 v
          GitHub bridge transport
       (private inbox, task/evidence)
                 |
                 v
       SANRO Agent Bridge on VPS
        (poll, validate, dispatch)
                 |
                 v
        Hermes autonomous workers
     (queue, per-project isolation)
                 |
                 v
           Codex CLI
       (coding/debug/test/build)
                 |
                 v
       Local tests / optional CI
       GitHub dev commit / Draft PR
                 |
                 v
      Bridge status + GitHub evidence
                 |
                 v
           ChatGPT → Owner
```

GitHub is a **communication transport and code/evidence platform**, not a substitute for Hermes or Codex. The Bridge communicates with a previously authorized backend/worker identity; it does not grant the ChatGPT chat session a direct Linux shell, credentials, or unrestricted remote-execution capability.

A separate **paid SSH-based MCP integration is not a requirement** for this design. The reference architecture uses existing allowed GitHub/VPS infrastructure; it does **not** make GitHub, VPS, model subscriptions, API quotas, monitoring, or operations free. Nor does it claim that every MCP/SSH offering has a particular price.

## Evidence and maturity must be separated

- **Historical internal SANRO Bridge evidence (October 22–25, 2026):** a GitHub → VPS → GitHub round trip was reported `DONE/SUCCESS`, including a safe read-only task, without a direct SSH channel from ChatGPT. This validates that **communication route**, not the current public starter and not all Hermes worker functionality.
- **Owner status (November 9, 2026):** the internal Hermes Autonomous system was declared **WORK**, and multiple project workers were reported active. This is Owner-reported operational status; each worker/job/CI outcome needs its own evidence.
- **Public toolkit in this repo:** v0.1 mock and v0.2 candidate are independent tooling. **The original SANRO Agent Bridge, its live GitHub inbox/poller, and a verified upstream Hermes integration are NOT shipped here.** A public bridge adapter and a reproducible end-to-end demonstration remain **PLANNED**.

Never label a new task notification, timer activation, GitHub issue submission, or `bridge ACK` as proof that code was written, tests passed, or production became LIVE.

## Minimal bridge design contract (proposal, not yet implemented in the public starter)

1. **Transport:** private, narrow GitHub task channel (or another explicitly approved connector). Authenticate the actual initiator and runner; do not trust the user/owner name embedded in a task file.
2. **Task envelope:** allowlisted project/repository, fixed branch/base SHA, bounded scope, expiry, unique task ID, priority, required output and **`productionMutation=false`**.
3. **Dispatcher:** validate signature/identity and policy before queueing; enforce per-project workspace, CODEX_HOME, Linux identity and credentials. Reject out-of-scope jobs without falling back to broad SSH or owner credentials.
4. **Worker:** Hermes chooses an already approved Codex-CLI execution lane, with bounded time/memory/concurrency, isolated development worktree, no effect on Owner's Codex session or active services.
5. **Evidence:** acknowledge receipt separately from job start, code changes, test/build results, commits, Draft PR, and final owner review. Persist idempotency and redacted status; handle downtime/retries without duplicate work.
6. **Security:** never expose SSH keys, tokens, `.env`, production files, customer data, raw session logs, or arbitrary shell execution through the transport. Limit GitHub permissions, handle hostile Issue/PR content, and sanitize all public docs/examples.
7. **Human release gate:** no automatic merge, staging extraction, database migration or production deployment. Only Owner may perform authorized production changes under SANRO policy.
8. **Cost:** no surprise paid API/MCP services or billable CI fallback; use local testing when suitable and the separately specified [public/private CI routing strategy](CI_STRATEGY.md).

## Bridge vs CI vs coding engine

| Layer | Responsibility | Does **not** replace |
| --- | --- | --- |
| **SANRO Agent Bridge** | Task/status communication from ChatGPT supervision to VPS | Hermes planning or Codex |
| **Hermes** | Autonomous coordination / queue / dispatch | Developer approval for production |
| **Codex CLI** | Code generation, debugging, development tests and builds | Bridge communications |
| **SANRO Local CI** | Optional separate structured CI validation on VPS | Codex CLI |
| **GitHub Actions** | Optional hosted CI, especially economical for public repositories | Hermes, Bridge or Codex |
| **Owner** | Delegation, scope, review, merge, release and production operations | Automated checks |

## Public contribution acceptance criteria

- [ ] Provide a generic Bridge transport adapter without internal SANRO server config or credentials.
- [ ] Verify authenticated task submission, least privilege, queue claim/idempotency, cancellation and replay prevention.
- [ ] Prove **ChatGPT-side GitHub submission → bridge receipt → Hermes/Codex execution → redacted evidence → Draft PR** on a disposable development repository; distinguish every stage.
- [ ] Prove unavailable/disconnected Bridge yields **BLOCKED**, not unauthorized fallback to SSH/MCP.
- [ ] Prove no production writes, cross-project leaks, surprise paid services, or interference with Owner's Codex environment.
- [ ] Publish reproducible tests and sanitized logs before marking public integration **TESTED**.

This is a **design and attribution document**, not a deployment command or proof of a live public integration.
