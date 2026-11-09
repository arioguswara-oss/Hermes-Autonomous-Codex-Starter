# Real-world background — SANRO Hermes coding automation

**Created and developed within the SANRO ecosystem by Ario Guswara.** These cases describe *separate internal implementations*, **not an end-to-end acceptance result for this public starter**.

## 1. SANRO POS Public — bounded Codex

On 8 November 2026, SANRO's Codex pilot on a separate development repository produced:
- [Draft PR #29](https://github.com/arioguswara-oss/Sanro-POS-Stock/pull/29), a pinned one-shot task.
- Issue #30 → [Draft PR #31](https://github.com/arioguswara-oss/Sanro-POS-Stock/pull/31), commit `87954a0641dce75ac89daa613232e37117ea35fa`, created by `sanro-hermes-dev`.

The proof is a coding/commit/Draft PR workflow under a scoped task. **The POS continuous systemd candidate was created later, so the early Draft PRs alone do not prove continuous systemd model execution.** The public case should not reproduce SANRO's private source or host configuration.

## 2. SANRO Superadmin — scheduled automatic uptake

On 9 November 2026, after one-shot Fast-track acceptance [Draft PR #7](https://github.com/arioguswara-oss/Sanro-SuperAdmin-Dev/pull/7), a timer-driven Superadmin worker processed a new authorized Issue #9 without a human running Codex:
- Automatically claimed the task.
- Made a scoped source edit (7 JSDoc lines in one `errors.js` file).
- Committed `1dbc858361ce6f9515bedf9efb6d3d5162f3706b`, pushed and produced [Draft PR #10](https://github.com/arioguswara-oss/Sanro-SuperAdmin-Dev/pull/10) via `sanro-hermes-dev`.
- Owner-verified result ledger showed SUCCESS, PR URL and `deployed=false`. POS service stayed active. PR said tests passed; full test logs for this specific issue were not independently assessed.

**Boundary:** This proves *bounded-task* automatic coding, not unrestricted full-project execution or safe production deployment.

## Lessons that saved time

1. **Re-use the proven one-shot flow**, then add a minimal scheduler. Don't infer a continuously running service's model success from `systemctl active`.
2. Avoid incompatible **nested sandbox layers**. A procfs mount failed inside an over-restricted systemd unit, while a direct single outer Bubblewrap flow succeeded. Do **not** turn off all sandboxing.
3. Beware Python `.strip()` on `git status --porcelain`: it removes leading status characters, causing a false changed-file-scope failure. Use `-z`/raw bytes or newline-only trimming.
4. Enforce one-project development scope and human-only production deployment.
5. Use **one representative end-to-end acceptance** and fix specific failure evidence, not indefinite diagnostic Issue loops.

## Trademark/license credit

This repository doesn't include Nous Research Hermes Agent's source code. Upstream project: https://github.com/NousResearch/hermes-agent . Hermes Agent and its developers receive separate credit; SANRO's original toolkit and case studies are attributed to Ario Guswara.
