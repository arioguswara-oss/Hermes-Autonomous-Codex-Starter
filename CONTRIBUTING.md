# Contributing to SANRO Hermes Coding Toolkit

**Original developer:** Ario Guswara · **Ecosystem:** SANRO · **Upstream Hermes Agent:** Nous Research.

Our objective is to help developers with limited budgets build reliable, auditable coding automation. Contributions are welcome in Indonesian or English.

## What to contribute

- **Provider adapters:** Claude Code, 9router, local LLM gateways and other integrations. These are community extensions to SANRO Hermes, not a rebranding of the core. Include upstream references, account/service terms and explicit costs.
- **Security:** practical sandbox isolation, credential mediation, safe egress, Linux user separation, worktree confinement and adversarial tests.
- **Automation:** authenticated GitHub issue intake, robust claim ledger, timeout/cancellation, CI and Draft PR publication with least privilege.
- **Documentation:** onboarding for low-cost VPS or local machines, translations, diagrams, accessibility and test fixtures.

## Pull request checklist

1. Open an Issue describing the problem, goal, risk and test plan before proposing a large architectural change.
2. Fork or branch; keep changes small. Never commit any real credentials, private repo code or customer data.
3. Run `python -m unittest discover -s tests -v`; add offline unit tests and negative security cases.
4. Label new adapters **EXPERIMENTAL** until an actual task can demonstrate bounded source edit → tests → dev commit → Draft PR.
5. Keep dependency counts and optional paid services minimal. Document usage and rate limits.
6. Preserve copyright and upstream attribution. Contributors own their original work subject to the chosen project license.
7. Never make autonomous deployment, bypass usage quotas, share credentials or remove authentication gates a default behavior.

## Collaboration

SANRO sets the core design and final maintainer decisions; the community may contribute modular features via reviewed PRs. Attribution for individual contributors will be preserved. No CLA is required for now; code contributions are submitted under the MIT project license.

The original Hermes Agent belongs to **Nous Research**. Please do not suggest this repo is an official Nous Research product or a fork unless its composition actually changes and the necessary notices are added.
