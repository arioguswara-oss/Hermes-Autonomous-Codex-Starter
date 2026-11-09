# English guide — SANRO Hermes Coding Toolkit

**Created by Ario Guswara, developed within the SANRO ecosystem.** The upstream **Hermes Agent** belongs to **Nous Research**. This is an **independent community toolkit**, not an official Nous Research release and not an official OpenAI product.

## Goal

Provide a low-cost, auditable starting point for coding agents that read an authorized development task, use a coding model/provider, run tests and prepare a **Draft PR** for human review. **No autonomous production deployment.**

## What's actually implemented in public v0.1?

- Strict, short-lived task manifest parsing and scope checks.
- An offline mock provider and single-task demo that never touches a repository.
- A provider interface and an opt-in **Codex CLI command preview**, not execution.
- Standard-library-only tests and security, contributor and cost guides.

**This repo is not yet a working end-to-end unattended agent.** It is a reviewed starting point intended to grow into one through community PRs.

## Try without API, model or VPS

```bash
git clone https://github.com/arioguswara-oss/Hermes-Autonomous-Codex-Starter.git
cd Hermes-Autonomous-Codex-Starter
python3 -m unittest discover -s tests -v
python3 -m sanro_hermes.cli init-task > /tmp/sanro-task.json
python3 -m sanro_hermes.cli validate /tmp/sanro-task.json
python3 -m sanro_hermes.cli demo /tmp/sanro-task.json
python3 -m sanro_hermes.cli codex-preview /tmp/sanro-task.json
```

Each `init-task` call generates an example that expires two hours later; the offline demo never executes its goal.

## What comes next?

A real adapter needs to verify authenticated GitHub issue authorship, protect model auth, run tests in controlled isolated workspaces, enforce one path/branch/PR scope, and implement idempotent job leases. See [architecture](ARCHITECTURE.md), [operations](OPERATIONS.md), [security](../SECURITY.md), [provider interface](PROVIDERS.md), and [roadmap](../ROADMAP.md).

## Historical evidence

SANRO's internal development workers previously generated bounded POS Public coding Draft PRs and an autonomous Superadmin PR. These are **case studies**, not evidence this public code is already wired up. See [case studies](CASE_STUDIES.md).

## Low-cost principle

Eligible Codex CLI users can sign in with ChatGPT instead of separate billable OpenAI API keys. Usage remains limited by plan and model. A lightweight model such as GPT-6 Luna may fit routine changes. Never promise unlimited use or bypass service terms. Claude, 9router and local-model integrations are optional community proposals, not installed adapters.
