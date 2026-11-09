# SANRO Hermes Coding Toolkit

**Public repository:** `Hermes-Autonomous-Codex-Starter` (name may be updated later)

**A SANRO ecosystem open-source project · Created by Ario Guswara**

🇮🇩 [Bahasa Indonesia](docs/ID.md) · 🇬🇧 [English](docs/EN.md) · [Architecture](docs/ARCHITECTURE.md) · [Contribute](CONTRIBUTING.md) · [Security](SECURITY.md) · [Roadmap](ROADMAP.md)

> **Autonomous coding for developers on a budget.** GitHub task → isolated workspace → AI coding provider → tests → development commit → **Draft PR**. Final merge and production deployment always belong to the human owner.

## Origin and identity

**SANRO** is the software ecosystem developed by **Ario Guswara**. The SANRO coding automation toolkit extends the developer workflow around AI agents. The original **Hermes Agent is a separate project created by Nous Research**; this toolkit is an independent community starter, not its official distribution and **does not yet bundle or integrate the upstream agent**. See [attribution](NOTICE.md). The internal SANRO source, VPS configuration, customer data and credentials are never published here.

SANRO's POS Public and Superadmin development provided two practical case studies. Their observed task outcomes inform the architecture; **this newly published starter is an independent implementation and must be tested on its own.**

**Original creator / lead developer: Ario Guswara** · **Project / brand: SANRO Hermes** · **License: MIT** (copyright notice and license must be retained in copies). Community contributions are welcome, and contributors retain credit for their work. This project is not affiliated with OpenAI, Anthropic, or 9Router.

## What is included in v0.1?

- A Python-standard-library **safe starter CLI** for validating scoped Owner-authored task manifests and simulating the job lifecycle.
- A **mock provider** for zero-model-cost demonstrations and a clearly marked **Codex-CLI command preview** (no model execution yet).
- An extensible **provider contract** so contributors can propose Claude Code, 9Router or other providers.
- **Fail-closed defaults:** no arbitrary repository or shell command from an issue, no production deploy, no automatic merge, no secret logging.
- Docs, tests, GitHub Actions, examples and a contributor roadmap.

**Maturity:** Reference starter / v0.1. The CLI has only `init-task`, `validate`, `demo`, and `codex-preview`; **none of these runs an AI model or creates a Draft PR**. Actual autonomous execution is a separate roadmap milestone.

## Cost model

Codex CLI can be used with an eligible **ChatGPT sign-in**, with **no separate OpenAI API key**. Codex is currently offered on ChatGPT plans including Free, Go and Plus, **subject to plan-specific usage limits and availability**. This does **not** imply unlimited tokens, free compute, bypass of subscription limits, or that other provider subscriptions cover Codex. You may still pay for a VPS, GitHub-related services, or other provider usage.

The successful SANRO experiments used a **Contabo VPS** with Linux, Git/GitHub CLI, Python, Node/Codex CLI, Bubblewrap and systemd. See [Contabo VPS and software checklist](docs/VPS_CONTABO.md), plus [costs and official references](docs/COSTS.md). **No VPS is required for the mock demo.** Do not share ChatGPT credentials or circumvent provider quotas.

## ChatGPT ↔ Hermes uses SANRO Agent Bridge (not direct SSH)

The SANRO reference workflow **does not give ChatGPT direct SSH access to the Hermes VPS**. Task and status messages travel through a narrowly authorized **SANRO Agent Bridge**, historically using GitHub as the transport. Hermes dispatches isolated **Codex-CLI** workers, and reviewed code/test evidence and Draft PRs return through GitHub.

A separately priced SSH-based MCP integration is **not required** by that reference architecture; GitHub, VPS, model subscriptions and quotas may still incur costs. **The original live Bridge is not shipped or verified in this public starter.** See [Agent Bridge architecture and boundaries](docs/AGENT_BRIDGE.md).

## CI routing: public vs private repositories

The toolkit's future autonomous workflow must choose a **cost-aware CI execution path** instead of assuming GitHub-hosted Actions is free for every project.

| Repository | Preferred execution path |
| --- | --- |
| **Public** | Standard **GitHub-hosted GitHub Actions** (free for standard runners under current terms) |
| **Private** | Separately installed, isolated **SANRO Local CI** on the developer's host/VPS |
| **Private fallback** | Explicitly approved GitHub Actions self-hosted runner or GitHub-hosted Actions with cost controls |

**These are architecture defaults, not working automatic routing in this starter.** SANRO Local CI is **not bundled here**; private-repo CI still requires an installed and verified executor. Public jobs may have additional service/storage limits; VPS compute is not free. GitHub remains the source/Issue/Draft PR service regardless of CI path.

Read [CI strategy, security boundaries and acceptance criteria](docs/CI_STRATEGY.md), [cost model](docs/COSTS.md) and [GitHub's official billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-actions). **Never change a project's visibility or enable billable runners without Owner approval.**

## Unified installer initiative — Golden Worker included by profile

**Goal:** one SANRO Hermes Coding Toolkit installer that coordinates **upstream Nous Research Hermes Agent**, Codex-CLI, SANRO Agent Bridge, queue/scheduler, isolated project workers, Golden Worker profiles, and optional SANRO Local CI. **Hermes remains the orchestrator and Codex CLI remains the coding engine.**

**P0 integration adapters (development candidate):** The single installer CLI now additionally exposes `preflight` (read-only local dependency detection), `golden-plan` (exact Golden Worker V2 manifest plus separate independently pinned external installer checksum verification), and `ci-plan` (authenticated GitHub repo visibility, advisory policy only). These commands **do not execute Codex, install components, activate a worker, trigger CI or deploy anything**. Private CI remains BLOCKED until SANRO Local CI readiness is separately verified. See [P0 integration implementation and boundaries](docs/INTEGRATION.md).

**Current public installer milestone is intentionally limited:** `installer/sanro_install.py` supports `plan`, `prepare` and `verify` for a **non-live review package**. It does **not** automatically install, enable or integrate Hermes/Codex/Bridge/Local CI/systemd, and does not create a working autonomous worker. The **Node.js Golden Worker V2** exists as a **separate private candidate** (SANRO AI Supervisor Draft PR #72) pending rights/security/integration review; its source is **not distributed** here. Android Golden Worker is a separate planned profile.

Read [Golden Worker and unified installer roadmap](docs/GOLDEN_WORKER.md) and [component catalog](installer/components.json). Do not interpret `PREPARED_NONLIVE` as `STAGED` on hosting or `LIVE` in production.

## Quick start (safe, local)

Requirements: Python 3.11+, Git (for future adapters), optionally Codex CLI and GitHub CLI. The demonstration below needs **no AI login, API key, server, or GitHub write access**.

```bash
git clone https://github.com/arioguswara-oss/Hermes-Autonomous-Codex-Starter.git
cd Hermes-Autonomous-Codex-Starter
python3 -m unittest discover -s tests -v
python3 -m sanro_hermes.cli init-task > /tmp/sanro-task.json
python3 -m sanro_hermes.cli validate /tmp/sanro-task.json
python3 -m sanro_hermes.cli demo /tmp/sanro-task.json
python3 -m sanro_hermes.cli codex-preview /tmp/sanro-task.json
```

`demo` uses a mock provider. It does **not** modify the target repository, run Codex, create a GitHub issue or publish a PR.

## v0.2 development candidate (Draft PR #2)

A separate, opt-in **real Codex-CLI one-shot runner** is under review in [Draft PR #2](https://github.com/arioguswara-oss/Hermes-Autonomous-Codex-Starter/pull/2). Unlike the offline mock, `python3 -m sanro_hermes.runner` **can** execute a real Codex model, check a single allowlisted source edit, run a fixed syntax test, and optionally produce a development Draft PR. All real model/GitHub commands are **opt-in** and are **NOT** run by CI; tests mock them.

It requires a **separate non-root, externally isolated user/container**; `--isolated-runtime` is an acknowledgement, not a sandbox. It is **not** an automatic GitHub Issue consumer or timer worker yet. See [bounded Codex guide](docs/ONE_SHOT_CODEX.md). Never run this directly on SANRO production or an unrestricted owner account.

## Architecture

```text
Human Owner (scope & final approval)
               |
          GitHub Issue
               |
       Task validator / queue
               |
       SANRO Hermes worker
          |          |
    isolated job    provider adapter
    workspace      mock / Codex CLI / community integrations
          |          |
         tests, scope gate, traceable result
               |
          Development Draft PR
               |
       Owner review, merge & deploy
```

For deployment-grade security and a verified automatic worker, follow [architecture](docs/ARCHITECTURE.md), [security](SECURITY.md), and [operations](docs/OPERATIONS.md). **Do not copy an internal SANRO server's unit files or credentials.**

## Contributions

The **core remains SANRO Hermes Coding Toolkit** regardless of provider. **Nous Research is credited for the original Hermes Agent.** Claude Code, 9Router, local models and gateways are **optional community adapter proposals**, not working integrations in v0.1. Contributions may extend the toolkit without changing its SANRO origin or upstream attribution. Start with [provider protocol](docs/PROVIDERS.md) and [contribution guide](CONTRIBUTING.md).

**Issues and PRs are welcome**, especially for isolation, provider plugins, tests, accessibility, Indonesian/English documentation, and cost-aware scheduling. See [roadmap](ROADMAP.md).

---

Copyright © 2026 **Ario Guswara**. Developed as part of the **SANRO** ecosystem. Released under the [MIT License](LICENSE).
