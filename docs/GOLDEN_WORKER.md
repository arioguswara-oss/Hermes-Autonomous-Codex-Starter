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
