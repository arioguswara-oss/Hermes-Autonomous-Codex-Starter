# SANRO Hermes — Autonomous Coding Agent Starter

**A SANRO ecosystem open-source project · Created by Ario Guswara**

🇮🇩 [Bahasa Indonesia](docs/ID.md) · 🇬🇧 [English](docs/EN.md) · [Architecture](docs/ARCHITECTURE.md) · [Contribute](CONTRIBUTING.md) · [Security](SECURITY.md) · [Roadmap](ROADMAP.md)

> **Autonomous coding for developers on a budget.** GitHub task → isolated workspace → AI coding provider → tests → development commit → **Draft PR**. Final merge and production deployment always belong to the human owner.

## Origin and identity

**SANRO** is the software ecosystem developed by **Ario Guswara**. **Hermes** is the SANRO AI agent for coordinating development tasks. This repository is its **public, generalized starter edition**—not a release of internal SANRO source, VPS configuration, customer data, or credentials.

SANRO's POS Public and Superadmin development provided two practical case studies. Their observed task outcomes inform the architecture; **this newly published starter is an independent implementation and must be tested on its own.**

**Original creator / lead developer: Ario Guswara** · **Project / brand: SANRO Hermes** · **License: MIT** (copyright notice and license must be retained in copies). Community contributions are welcome, and contributors retain credit for their work. This project is not affiliated with OpenAI, Anthropic, or 9Router.

## What is included in v0.1?

- A Python-standard-library **safe starter CLI** for validating scoped Owner-authored task manifests and simulating the job lifecycle.
- A **mock provider** for zero-model-cost demonstrations and a clearly marked **experimental Codex-CLI adapter** for opt-in development use.
- An extensible **provider contract** so contributors can propose Claude Code, 9Router or other providers.
- **Fail-closed defaults:** no arbitrary repository or shell command from an issue, no production deploy, no automatic merge, no secret logging.
- Docs, tests, GitHub Actions, examples and a contributor roadmap.

**Maturity:** Reference starter / v0.1. The example CLI is not an already verified, unattended production worker. Run `dry-run` and `mock` first; review isolation and privileges before enabling a real provider.

## Cost model

Codex CLI can be used with an eligible **ChatGPT sign-in**, with **no separate OpenAI API key**. Codex is currently offered on ChatGPT plans including Free, Go and Plus, **subject to plan-specific usage limits and availability**. This does **not** imply unlimited tokens, free compute, bypass of subscription limits, or that other provider subscriptions cover Codex. You may still pay for a VPS, GitHub-related services, or other provider usage.

Read [costs and official references](docs/COSTS.md). **Do not share ChatGPT credentials or try to circumvent provider quotas.**

## Quick start (safe, local)

Requirements: Python 3.11+, Git (for future adapters), optionally Codex CLI and GitHub CLI. The demonstration below needs **no AI login, API key, server, or GitHub write access**.

```bash
git clone https://github.com/arioguswara-oss/Hermes-Autonomous-Codex-Starter.git
cd Hermes-Autonomous-Codex-Starter
python3 -m unittest discover -s tests -v
python3 -m sanro_hermes.cli validate examples/task.example.json
python3 -m sanro_hermes.cli demo examples/task.example.json
```

`demo` uses a mock provider. It does **not** modify the target repository, run Codex, create a GitHub issue or publish a PR.

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

The **core is SANRO Hermes** regardless of provider. Claude Code, 9Router, local models and gateways are **optional community adapters**, not renamed forks of the core and not claimed as working integrations until tested. Start with [provider protocol](docs/PROVIDERS.md) and [contribution guide](CONTRIBUTING.md).

**Issues and PRs are welcome**, especially for isolation, provider plugins, tests, accessibility, Indonesian/English documentation, and cost-aware scheduling. See [roadmap](ROADMAP.md).

---

Copyright © 2026 **Ario Guswara**. Developed as part of the **SANRO** ecosystem. Released under the [MIT License](LICENSE).
