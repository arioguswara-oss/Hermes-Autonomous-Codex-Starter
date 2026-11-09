# Golden Worker integration — single toolkit installer roadmap

**Status (9 Nov 2026):** A Node.js backend **Golden Worker Installer V2 candidate** exists separately in the private SANRO AI Supervisor repository, **Draft PR #72**. It is **not merged, publicly redistributed, or independently verified as installed on the VPS**. Its implementation was reported to cover manifest/checksum validation, constrained Node worker setup, development workspace, baseline tests, and project-only systemd service/timer templates. The Android SDK/Gradle profile is **not implemented**.

The public SANRO Hermes Coding Toolkit **must not pretend that private code is already bundled**. The single installer is the **entry point**, but component providers need rights review, security audit, version pinning, isolated execution and an explicit Owner activation gate.

## Target unified installation model

```text
One SANRO Hermes Coding Toolkit installer
  ├─ prerequisites: upstream Hermes Agent (Nous Research) + Codex CLI
  ├─ SANRO Agent Bridge: GitHub task/status channel (no direct ChatGPT SSH)
  ├─ scheduler / queue / idempotent ledger / per-project isolation
  ├─ Golden Worker Installer
  │     ├─ Node.js backend profile — internal candidate PR #72, not bundled
  │     ├─ Web/frontend profile — planned
  │     └─ Android/Gradle profile — planned
  ├─ SANRO Local CI adapter — external; optional
  └─ GitHub: Issues, development commits and Draft PR
```

**Hermes remains the orchestrator and Codex-CLI the coding engine.** Local CI is an optional independent quality gate, not a replacement for Codex. The Owner alone controls merge, deployment, production database changes, extraction and release activation.

## One entrypoint — safe phase already in this PR

The public `installer/sanro_install.py` exposes:

- `plan`: checks the published component catalog, prints what is external/missing, and **does not modify the host**.
- `prepare --output ... --ack-nonlive`: creates a **new**, explicit, non-live directory containing public-safe documentation and example configs, together with SHA-256 checksums. **It does not install Hermes, Codex, Local CI, Golden Worker, services or task consumers.**
- `verify --output ...`: reads staged files and checks their hashes without starting services.

This is a **public installer/staging scaffold**, not an operational end-to-end Hermes installer. An automated `install` or `activate` command does not exist yet. Do not issue blanket privileged shell commands or copy actual SANRO VPS keys/config into the toolkit.

## Kompatibilitas dengan Golden Worker Installer V2 (integration contract)

**Interface ID:** `sanro.golden-worker.node.v2` — **planned adapter**, not an installed provider. The public Toolkit installer is the *orchestrator entrypoint*; the Golden Worker Installer is an independently reviewed, development-only component. Upstream Hermes Agent (Nous Research) remains an external orchestration foundation; Codex CLI remains the coding engine. The Toolkit does **not** silently install a private Supervisor component.

**Source-of-truth for first Node candidate:** `arioguswara-oss/Sanro-AI-Supervisor` Draft PR #72 (**private, unmerged, not redistributed**). Its version/provenance must be separately reviewed and pinned. Do not vendor, download by anonymous URL, execute, or publish its source, VPS config, auth, `.env`, or secret keys as part of a public Toolkit build. A public reusable implementation requires explicit permission/license review and a new security evaluation.

### Contract mapping (reviewed component only)

| Toolkit public-facing field | Node V2 component expects | Constraint |
| --- | --- | --- |
| `project` | `project` | Project-specific isolated path, branch, ledger and timer; no overwrite. |
| `repository` | `repository` | Authenticated exact repo name; worker-specific GitHub Write permission. |
| `expectedHead` | `baseCommit` | Exact 40-character `main` SHA verified against GitHub, not an issue assertion. |
| `sourcePath` | `sourcePath` | Narrowly reviewed JS allowlist, no arbitrary shell or paths. |
| `executorBlob` | `candidateBlob` | Pinned, reviewed Git blob of candidate executor; verify during copy. |
| `profile=node-backend` | `profile=node` | Explicit adapter mapping. Android/Gradle **not supported**. |
| `ownerApproval=CODING_TEST_COMMIT_DRAFT_ONLY` | identical `ownerApproval` | No merge, production deploy or database migration. |
| approved manifest SHA-256 | `--approved-sha256` | Pin from trusted Owner review, not self-approved local hash. |

The adapter may perform **plan** (no changes) and a separate, explicitly Owner-approved **development apply** on a verified host; enabling a timer requires scope approval and runtime gates. The existing public `installer/sanro_install.py` currently implements `plan`, `prepare` and `verify` for public-safe non-live files only. It **does not** implement this adapter or `apply`. A pinned ZIP (with internal `SHA256SUMS`) can be a *candidate* artifact, not proof of runtime compatibility.

### Required output/evidence handshake

The future Toolkit adapter should ingest only sanitized structured results:
`project`, `repository`, `componentId`, `version`, `sourceCommit`, `artifactSha256`, `manifestSha256`, `workerIdentity`, `timerState`, `testProfile`, `ciMode`, `issue`, `commit`, `draftPR`, `status`, `productionMutation=false`, and a redacted failure code. Accepted statuses: `PLANNED`, `IMPLEMENTED`, `TESTED`, `READY_FOR_OWNER`, `BLOCKED`; runtime `WORK` is reserved for proven automatic Owner-Issue→Codex→tests→commit→Draft PR, not for ZIP creation or service activation.

**CI routing is independent from worker installation:** for public repos use standard GitHub-hosted Actions; for private repos use **verified external SANRO Local CI** if installed. Visibility must be read via authenticated GitHub metadata. If private CI unavailable, fail closed or request Owner approval for an alternative—never silently incur API/billing costs. Resource queues must not displace Codex Rio, POS Public, Superadmin, Ticket, backup or monitoring.

A single future Toolkit command may orchestrate the adapter, but **does not grant additional server privileges**. No production changes, no auto-merge, no credential sharing, no overwrite of existing worker/systemd state. Before declaring integration `TESTED`, run one disposable/authorized Node development project from manifest to automatic Draft PR and verify the other workers remain active. The Android profile needs a separately reviewed JDK/Gradle/SDK integration and tests.

## Golden Worker adapter contract (planned)

A future adapter must consume a project-bound manifest with an explicit repository and pinned SHA, a reviewed executor source, dependency profile, resource budget, isolated non-root identity, independent CODEX_HOME, private ledger, GitHub publisher scope, and harmless canary task. The adapter must:

1. Check the original candidate PR and license/ownership **before** moving any source from a private repository to public.
2. Pin known hashes and provenance; reject unsigned/changed artifact or incorrect Git remote.
3. Prepare only a **new isolated development workspace**; never overwrite existing POS/Superadmin/Ticket workers or the Owner's Codex session.
4. Check availability of Bubblewrap, Node/npm, Git/GitHub, Codex and optionally PowerShell for SANRO Dev Toolkit; queue if VPS lacks resources.
5. Generate a reviewable service/timer **candidate only**. Installation/enablement of systemd service is an explicit Owner-authorized operation on the appropriate development host, never implied by `prepare`.
6. Test one authorized Issue → Codex edit → tests → dev commit → Draft PR with redacted evidence and no production mutation.
7. Produce a concise installation report: project, component version/source, hashes, worker identity, branch/PR, checks, status and required Owner action.

Android worker will need a different profile with Android SDK/Gradle and APK build validation. Do not assume the Node.js installer works for Android.

## Status and review boundaries

| Component | State in public toolkit |
| --- | --- |
| Installer catalog + non-live staging CLI | IMPLEMENTED candidate, subject to tests |
| Golden Worker Node backend | External private candidate PR #72, **NOT BUNDLED** |
| Actual Hermes Agent bridge | PLANNED integration |
| Golden Worker Android/Gradle | PLANNED |
| SANRO Local CI | External optional component; public adapter **NOT VERIFIED** |
| Unattended one-command worker installation | PLANNED — not part of this PR |

See [component catalog](../installer/components.json), [Bridge](AGENT_BRIDGE.md) and [CI strategy](CI_STRATEGY.md).
