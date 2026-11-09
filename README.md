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
