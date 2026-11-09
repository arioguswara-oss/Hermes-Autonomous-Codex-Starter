# Security policy — SANRO Hermes Coding Toolkit

The v0.1 starter CLI is intentionally **non-executing**: it validates manifests, simulates a job and previews a provider command. It does not modify source, open live GitHub PRs, call models or perform autonomous development. Do not mistake a passing demo for a verified unattended worker.

## Threat model

AI-generated code, task descriptions, repository tests and external command output are **untrusted input**, even when a task is Owner-authored. A malicious prompt can try to read credentials, invoke shell tools, contact external hosts or modify unrelated files.

A production-grade integration needs *technical enforcement*:
- A dedicated Linux identity or well-confined container/VM per project and isolated worktree, state, logs, authentication home and GitHub publisher.
- Read-only filesystem boundaries by default with a narrow allowlist of writable development files. Never mount production, host sockets, backups or other tenants into AI tools.
- Compatible sandboxing, tested with an actual model-assisted coding task. Avoid incompatible nested sandbox/mount layers.
- Restricted outbound network connectivity or mediated authentication when AI commands might otherwise access credentials.
- Exact Owner-approved expiring manifest, verified GitHub issue-author identity, pinned base commit, source allowlist and a durable one-attempt claim.
- Least-privilege GitHub publishing: development branch and Draft PR only, no automatic merge or deploy.
- CPU/RAM/time budgets, bounded concurrency, redacted logging, and higher priority for the human owner's development session.
- Fail-closed behavior for unknown access, malformed tasks, dirty repositories or incomplete tests. Sensitive changes and expanded access require fresh Owner authorization.

**Historical SANRO lesson:** one verified outside Bubblewrap boundary worked with Codex's inner sandbox disabled *inside that outer boundary*. **NEVER** copy a sandbox-bypass flag into an unsandboxed environment. The v0.1 public Codex preview does not include that bypass flag.

**Known separation concern:** historical SANRO development pilots shared a Linux UID across worker projects. A shared UID is **not** strong OS-level project isolation; new community deployments should improve this. The open-source starter must not copy SANRO's private deployment topology.

Do not commit or log ChatGPT account authentication files, API keys, model transcripts containing secrets, customer information, private SANRO repositories, SSH keys or production database dumps.

## Reporting security issues

Please use this GitHub repository's **private security advisory** mechanism instead of a public issue when the report contains an exploitable vulnerability. Redact personal data and credentials. There is no guaranteed security response SLA for this early community starter.
