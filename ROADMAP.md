# SANRO Hermes Coding Toolkit — Community Roadmap

**Maintainer:** Ario Guswara · **SANRO ecosystem** · no dates promised.

| Milestone | Status | Deliverable / acceptance |
| --- | --- | --- |
| v0.1 — Public documentation and offline starter | IMPLEMENTED IN PR | Strict task manifest, mock provider, Codex preview only, tests, guides and attribution |
| v0.2 — Real Codex one-shot executor | IMPLEMENTED CANDIDATE — Draft PR #2; offline tests only | Opt-in CLI command and Draft PR path implemented; real model call and real GitHub publication from public code remain UNVERIFIED |
| v0.3 — GitHub autonomous task consumer | PLANNED | Verified Owner-authored Issue → automatic claim → Codex → tests → dev Draft PR with no manual Codex run |
| v0.4 — Per-project scheduler and resource arbitration | PLANNED | Multiple workers in separate Linux identities, queue precedence, safe recovery, low-memory operation |
| v0.5 — Hermes Agent upstream integration | PROPOSED | Tested bridge to real Nous Research Hermes Agent, following upstream APIs and license |
| Community adapter: Claude Code | PROPOSED | Optional provider, documented authentication, cost, scope gates and end-to-end tests |
| Community adapter: 9router | PROPOSED | Optional gateway connector, independent configuration, provider terms/cost and tests |
| Community adapter: local models | PROPOSED | Resource-aware worker with clear capability, RAM/CPU and test results |
| Android/APK release workflow | PROPOSED | Separate Android toolchain and verified debug build; no production deploy |

**Reference cases are not this project's current release:** internal SANRO POS Public and SANRO Superadmin proved bounded Codex automation during November 2026, but this public package does not yet reproduce their complete worker runtime.

Current security priorities: true per-project UID separation, credential isolation, outbound network control, repository tests treated as untrusted code, and reliable one-attempt queues.

All public releases use explicit version tags and changelog entries; do not promise an automatic deployment feature.
