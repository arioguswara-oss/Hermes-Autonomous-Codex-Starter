# SANRO Hermes Coding Toolkit — Community Roadmap

**Maintainer:** Ario Guswara · **SANRO ecosystem** · no dates promised.

## Owner sequencing — integration first (10 Nov 2026)

**P0: unify and verify the actual runtime before any browser control panel work.** No second installer and no rewrite of the already WORK internal Hermes workers. The SANRO Hermes Coding Toolkit single installer is the only intended entrypoint. Hermes Agent (Nous Research) stays upstream; Codex-CLI remains the primary autonomous coding engine. SANRO Agent Bridge stays between ChatGPT and the VPS without mandatory direct SSH MCP. Golden Worker Installer V2 (private Supervisor Draft PR #72) becomes a reviewed, pinned module; SANRO Local CI is an optional CI adapter, not a Codex replacement.

**Integration acceptance gate:** component provenance/license/security review → actual pinned safe adapter → isolated worker install candidate → authenticated task round trip → real Codex task → relevant tests/build → dev commit and Draft PR → redacted evidence → Owner review. Maintain separate worker/CODEX_HOME/worktree/log and preserve existing POS, Superadmin, Ticket, monitoring, backups and the Owner's Codex sessions. No unattended service activation, merge, deploy or production mutation. Source/CI PASS is not proof of runtime installation. The public toolkit must not redistribute private Supervisor code or secrets without separate authorization.

**P1: usability and broader runtime profiles only after P0 acceptance:** idempotent upgrades, external dependency preflight, bounded recovery and Android/Gradle adaptation (separately tested).

**P2: SANRO Hermes Control Panel (browser UI), strictly AFTER P0 is VERIFIED:** initially read-only status and audit evidence; later explicitly approved limited worker management through the same control API. No unrestricted browser shell and no duplicate orchestration system. Dashboard designs or mockups are not runtime proof.


| Milestone | Status | Deliverable / acceptance |
| --- | --- | --- |
| v0.1 — Public documentation and offline starter | IMPLEMENTED IN PR | Strict task manifest, mock provider, Codex preview only, tests, guides and attribution |
| v0.2 — Real Codex one-shot executor | IMPLEMENTED CANDIDATE — Draft PR #2; offline tests only | Opt-in CLI command and Draft PR path implemented; real model call and real GitHub publication from public code remain UNVERIFIED |
| v0.x — Unified installer scaffold | IMPLEMENTED CANDIDATE — documentation + CLI | One entrypoint `plan/prepare/verify` for non-live review, catalog/status and SHA-256 lock; **not a runtime installer** |
| Golden Worker Node integration | EXTERNAL CANDIDATE — private Supervisor Draft PR #72 | Rights/security review + pinned adapter + isolated canary Issue→Codex→Draft PR; do not copy private source before authorization |
| Golden Worker Android/Gradle | PLANNED | Android-specific SDK, resource and APK validation; separate from Node profile |
| v0.3 — GitHub autonomous task consumer | PLANNED | Verified Owner-authored Issue → automatic claim → Codex → tests → dev Draft PR with no manual Codex run |
| v0.4 — Per-project scheduler and resource arbitration | PLANNED | Multiple workers in separate Linux identities, queue precedence, safe recovery, low-memory operation |
| SANRO Agent Bridge public adapter | PLANNED — [reference design](docs/AGENT_BRIDGE.md) | Authenticated GitHub task/status → Hermes → Codex-CLI → redacted evidence and Draft PR; no direct ChatGPT SSH |
| CI routing — public vs private | PLANNED — [specification only](docs/CI_STRATEGY.md) | Authenticated repository visibility → standard GitHub Actions for public / verified SANRO Local CI for private; explicit approved fallback; reliable evidence without production permissions |
| v0.5 — Hermes Agent upstream integration | PROPOSED | Tested bridge to real Nous Research Hermes Agent, following upstream APIs and license |
| Community adapter: Claude Code | PROPOSED | Optional provider, documented authentication, cost, scope gates and end-to-end tests |
| Community adapter: 9router | PROPOSED | Optional gateway connector, independent configuration, provider terms/cost and tests |
| Community adapter: local models | PROPOSED | Resource-aware worker with clear capability, RAM/CPU and test results |
| Android/APK release workflow | PROPOSED | Separate Android toolchain and verified debug build; no production deploy |

**Reference cases are not this project's current release:** internal SANRO POS Public and SANRO Superadmin proved bounded Codex automation during November 2026, but this public package does not yet reproduce their complete worker runtime.

Current security priorities: true per-project UID separation, credential isolation, outbound network control, repository tests treated as untrusted code, and reliable one-attempt queues.

All public releases use explicit version tags and changelog entries; do not promise an automatic deployment feature.
