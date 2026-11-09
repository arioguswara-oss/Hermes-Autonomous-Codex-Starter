# VPS reference — Contabo and other affordable hosts

**Project:** SANRO Hermes Coding Toolkit · **Developer:** Ario Guswara · **Example infrastructure:** Contabo VPS.

## Why Contabo?

The original SANRO Hermes development setup uses a **Contabo VPS**. According to Ario Guswara's practical assessment, Contabo offered attractive resources for a modest monthly budget. **This is a developer experience, not a claim that Contabo is universally the cheapest or fastest provider.** Compare total cost, billing term, region, support, VAT, data transfer, performance and backup add-ons.

Official current product and pricing references:
- https://contabo.com/en-us/pricing/
- https://docs.contabo.com/docs/servers-hosting/vps/

Contabo's published entry **Core VPS** plans are Linux-capable virtual servers with shared vCPU, RAM and SSD storage. Actual offers can change by date and region; **we deliberately avoid hard-coded monthly price claims**. Production subscriptions and infrastructure costs are the user's responsibility. The open-source starter is not sponsored by or affiliated with Contabo.

## What the SANRO pilot used (public, sanitized overview)

| Component | Role | Notes |
| --- | --- | --- |
| Contabo VPS with Linux | Always-on task worker host | No public IP, hostname, usernames or private systemd configs are distributed |
| SSH client (Android Termux optional) | Owner's remote terminal | Phone is a control device; worker runtime remains on VPS |
| Python 3 | Worker orchestration, queue, validation, claims | Public v0.1 CLI uses only Python stdlib |
| Git + Git worktree | Isolate per-task and per-project edits | Never edit a production repo directly |
| GitHub + GitHub CLI `gh` | Owner-authored tasks, publisher identity, development Draft PR | Permission limited to development repositories |
| Node.js + npm + Codex CLI | AI coding executor in the successful SANRO pilot | ChatGPT sign-in, not separate pay-as-you-go OpenAI API key; plan usage limits apply |
| Bubblewrap (Linux) | One reviewed *outer* filesystem boundary for the historical pilot | Check kernel support; nested sandbox incompatibility caused errors previously |
| systemd oneshot + timer | Autonomous periodic pickup for Superadmin | GitHub queue check is cheap; model runs only for authorized work |
| Test suite / CI | Verify behavior and allowed scope before publishing PR | CI PASS alone does not prove a working provider |
| Resource limits + local audit/backup | Reduce interference and support recovery | Protect the human developer's sessions; backup testing policy is deployment-specific |

The public starter **does not ship actual SANRO VPS config, secrets, production paths, or historical private server files**.

## Sizing guide — planning estimate, not a benchmark

| Workload | Starting assumption | Caveat |
| --- | --- | --- |
| Offline v0.1 demo | Any modern laptop or small Linux VM with Python 3.11+ | No VPS, AI login or model needed |
| One light coding worker | Roughly 2 vCPU, 4 GB RAM, 20–40 GB disk may be a starting point | Depends strongly on Node, tests, repository, model and process peak memory |
| Two or more bounded concurrent project workers | Prefer at least 4 vCPU, 8 GB RAM and SSD; **queue model tasks when memory limited** | This is a planning suggestion, not the measured SANRO VPS configuration |
| Android builds / heavy integration tests | Typically more RAM and disk; measure workload | Separate CI/build host can be cheaper than permanently upsizing the VPS |

Choose packages after assessing actual process RSS, swap activity, disk growth and test duration. A plan with 8 GB RAM does not guarantee that two memory-intensive AI tasks should run simultaneously. **Serial execution/queuing is often more economical.** Cloud VPS may not support nested hardware virtualization; Bubblewrap namespaces are different from full nested virtual machines—verify host/kernel capabilities before selecting an isolation mechanism.

## Install components — conceptual checklist

These packages are described so contributors understand the architecture, **not as an auto-install script**:
- Linux server (Ubuntu/Debian or another maintained distro), SSH configured with least privilege and OS updates.
- `python3`, `git`, `gh`; `node`/`npm` and Codex CLI only for users enabling that provider.
- An isolated, non-root user/container per project and a separate provider authentication home.
- Worktrees, write allowlist, immutable base SHA verification, one-attempt durable ledger.
- systemd timer, bounded CPU/RAM/runtime, redacted logs, alerting/backup.
- One harmless task executed end-to-end through the **timer** before declaring autonomous status WORK.

Do not use credentials from another account or project. Do not copy the original SANRO worker's shared Linux UID design into new projects; it has known isolation limitations. Prefer one process/identity per project or a well-reviewed container boundary.

## Estimating true monthly cost

```text
Total = VPS or electricity
      + eligible ChatGPT subscription (or other licensed provider access)
      + any optional paid services/backups/domains
      + time spent on reviews and maintenance
```

When a user already has an eligible ChatGPT plan and uses Codex CLI login, a **separate API key/billing account is not required** for that path. Model usage is still metered against account limits; it is not unlimited or token-free. Optional Claude, 9router or other adapters may introduce different costs.

## Transparency

- Contabo is listed because **Rio/Ario used it**, not because this repo contains referral links or is sponsored.
- Current specs/prices: https://contabo.com/en-us/pricing/
- ChatGPT/Codex plan eligibility: https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- Underlying upstream Hermes Agent: https://github.com/NousResearch/hermes-agent (not bundled here).

**Never publish IP addresses, auth files, server IDs, customer data, staging credentials or internal SANRO application source in community installation guides.**
