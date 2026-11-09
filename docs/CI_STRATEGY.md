# CI strategy — public vs private repositories

**Status: architecture decision / PLANNED integration (9 November 2026).** This document describes the intended SANRO Hermes Coding Toolkit CI routing policy. **It does not claim that the public starter currently detects repository visibility, includes SANRO Local CI, or has an end-to-end autonomous Hermes Agent integration.**

## Why CI routing matters

The toolkit is **not a standalone Hermes Agent**. Upstream [Hermes Agent by Nous Research](https://github.com/NousResearch/hermes-agent) is a separate project; this repository currently provides independent SANRO task-validation and coding-workflow tooling. A future integration must be implemented and tested against the upstream agent, with attribution preserved in [NOTICE](../NOTICE.md).

An autonomous development workflow needs an execution engine (for example, Codex CLI), repository/issue/PR integration, a scheduler or queue, isolated workspaces, tests/builds, and trustworthy results. CI is one of those dependencies. Repository **visibility changes the most economical CI default**.

| Repository | Recommended CI path | Notes |
| --- | --- | --- |
| **Public** | **Standard GitHub-hosted GitHub Actions** | Standard runners are free for public repositories under GitHub's current terms. Larger runners, storage and other products can have separate charges/limits. |
| **Private** | **SANRO Local CI on an isolated developer-owned VPS/host** (when separately installed and validated) | Avoids GitHub-hosted Actions compute usage for jobs executed entirely outside GitHub Actions. Still consumes CPU, RAM, disk, electricity/VPS fees, and operator time. |
| **Private (alternative)** | **GitHub Actions self-hosted runner** | GitHub Actions self-hosted runner usage is free under current terms; the host is not free, and GitHub remains the job control plane. This is **not** the same product as independent SANRO Local CI. |
| **Any (fallback)** | Standard GitHub-hosted Actions with account-level budgets and limits | Private repositories consume their included compute allocation and can incur charges, or be blocked after allowance exhaustion depending on billing configuration. |

**Source-of-truth for pricing/limits:** [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), and [self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners). Re-check before deployment; no fixed quota or price is guaranteed here.

## Proposed selection rules (not implemented)

1. Read repository identity and **visibility from an authenticated GitHub response**, not an AI prompt, issue title, or user-provided JSON field.
2. For **public** repos, default to a standard GitHub-hosted runner, with minimal workflow permissions. Do **not** attach an owner-credentialed VPS self-hosted runner to public PR workflows: forked PR content can be hostile.
3. For **private** repos, prefer an independently installed, verified SANRO Local CI executor. If unavailable or unsafe, report **BLOCKED** or use a **pre-approved** fallback; never silently enable billable GitHub-hosted jobs.
4. Store the selected CI mode **per project**, not as a global switch. Do not change project visibility to save compute minutes; visibility is the Owner's decision.
5. Keep Github for source, issue intake, development commits and **Draft PRs** even when tests/builds run through Local CI. Do not confuse a Draft PR with a passing CI result.
6. Never execute a newly opened PR's arbitrary shell instructions or repository scripts in a privileged context. Source checkouts, build tools and tests are untrusted executable inputs.
7. Apply bounded concurrency, disk/CPU/memory budgets, timeouts, log redaction and a one-attempt/idempotent result ledger. If the host is busy, queue work without preempting the human Owner's sessions, backups, monitoring or other workers.
8. **No CI path may merge, deploy, extract a production package, migrate production data, restart production services, or mutate live infrastructure.** These remain separate Owner-controlled gates.

## Responsibilities and boundaries

| Component | Function | Public starter status |
| --- | --- | --- |
| Nous Research Hermes Agent | Upstream agent/orchestration foundation | Separate dependency; **integration not yet implemented or verified** |
| SANRO coding worker / Codex adapter | Scoped code change in isolated development workspace | v0.1 mock/preview; v0.2 one-shot candidate in Draft PR #2, **not unattended** |
| Standard GitHub Actions | Public-repo default CI | An example workflow exists in the v0.1 Draft PR; actual run outcome must be checked independently |
| **SANRO Local CI** | Independent CI executor for private development repositories | **External SANRO component, not included or verified in this public starter** |
| GitHub self-hosted runner | Alternative GitHub Actions execution on user-owned host | Configuration option, **not shipped or automatically installed** |
| Queue, scheduler, identity and resource guards | Multi-project bounded automation | Additional engineering / verification required |

### Local CI minimum contract (proposal)

A separately reviewed Local CI adapter should accept a signed or otherwise authenticated job request containing: project allowlist, repository/ref, exact commit SHA, approved test profile, time and resource budget, and a unique job ID. It should return a structured, immutable result containing:

- Project/job ID, repository, immutable input SHA, CI mode and runner identity (non-secret).
- Test/build command profile identifier (**never arbitrary issue-supplied shell**), start/end timestamps, exit status and relevant test counts.
- Redacted log/artifact references, optional SHA-256 checksums, and VERIFIED/UNVERIFIED/BLOCKED evidence flags.
- Failure reason, bounded retry decision, and Draft PR/commit reference when available.

Test execution must be isolated from the owner shell session and any production data or credentials. Use separate per-project identities, worktrees, state directories and credentials; isolate filesystem and outbound networking, not merely branch names. Build artifacts must not be treated as released/live until verified through the approved human-led release process.

## Acceptance criteria before advertising automatic CI selection

- [ ] Detect public/private repository visibility using authenticated GitHub metadata.
- [ ] Document a secure, repeatable installation contract for SANRO Local CI **without publishing SANRO VPS secrets or internal config**.
- [ ] Prove public mode runs an actual safe GitHub-hosted test and records the run/job reference.
- [ ] Prove private mode runs a real bounded test on an isolated Local CI worker **without starting a GitHub-hosted Actions run for that test**.
- [ ] Prove blocked/failed paths cannot silently fall back to chargeable CI or privileged execution.
- [ ] Verify per-project resource isolation, queue fairness, redaction, exact-SHA traceability and recovery.
- [ ] Prove neither path can merge or deploy; Owner review remains mandatory.
- [ ] Publish evidence, configuration examples, test fixtures and limitations before claiming **TESTED**.

This document is a **design specification**, not an installation guide or proof that SANRO Local CI is present in the public repository.
