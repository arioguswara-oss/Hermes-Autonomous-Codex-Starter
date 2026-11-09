# Low-cost autonomous coding — honest cost and quota guide

**Objective:** help hobbyists and developers with limited budgets learn AI coding automation without requiring a pay-as-you-go OpenAI API account.

## What is and isn't free

- Codex CLI can use eligible **ChatGPT sign-in** rather than an **OpenAI API key**. Codex availability and quotas vary by plan, model and account; Free and Go are included in official ChatGPT Codex availability, while some Cloud features have different plan requirements.
- Even without a separate API bill, inference consumes the plan's **usage allowance**, measured in model usage/tokens. **No plan guarantees infinite autonomous executions.**
- A rented VPS, development machine power, disk, network, optional GitHub tier or third-party model/gateway **may cost money**. SANRO's original Hermes VPS is hosted at **Contabo**, which Ario Guswara selected as an economical option. See [VPS and component checklist](VPS_CONTABO.md); confirm current price/term/region on https://contabo.com/en-us/pricing/ rather than assuming a fixed price.
- Other providers such as Claude or 9router have **separate terms, account models, authentication and possible usage fees**. Their adapters are not part of v0.1.

## GitHub Actions vs independent SANRO Local CI

Repository visibility affects operating costs:

- **Public repository:** GitHub Actions standard GitHub-hosted runners are free under GitHub's current rules. This does **not** make all runner sizes, artifacts, third-party dependencies, or external services unlimited/free.
- **Private repository:** GitHub-hosted Actions draws on the owner's included compute usage; exceeding the allowance can create costs or block execution depending on billing settings. **Do not silently enable paid fallback**.
- **Private repository with SANRO Local CI:** Tests/builds run on the operator's already provisioned VPS/host instead of consuming GitHub-hosted Actions compute for those particular jobs. Host costs, capacity and security controls still apply. The independent Local CI adapter is **not included or tested in this public starter**.
- **Self-hosted GitHub Actions runner:** Currently free from GitHub Actions usage charges, but needs a maintained host and depends on GitHub Actions orchestration. It is **not equivalent** to independent Local CI. Avoid using privileged self-hosted runners for untrusted public PRs.

Consult authoritative docs before budgeting: [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [standard GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners).

See [SANRO CI strategy](CI_STRATEGY.md) for proposed routing, project isolation, CI evidence and Owner-only release gates.

## GPT-6 Luna: contributor/user observation

**SANRO field observation (Ario Guswara, 9 Nov 2026):** using **GPT-6 Luna** for routine developer tasks felt substantially more economical and gave greater useful task capacity than his earlier settings. This is **anecdotal, not a benchmark**; neither "double quota" nor a fixed saving ratio has been independently verified.

Official OpenAI plan guidance describes substantially different ranges between lighter and more resource-intensive models; actual allowances depend on plan, chosen model, task, tools and time window. Where the CLI/account exposes model choice, use the exact supported name `gpt-6-luna` and **confirm it is available in that product/version**, rather than assuming that a model in Chat or API is automatically available in every Codex CLI configuration.

Sources to consult:
- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
- https://developers.openai.com/api/docs/guides/latest-model

## Better metric: tasks completed per allowance

Record (without secrets or raw prompts):
- Task class: documentation / minor bug / refactor / architecture.
- Model, effort and CLI version.
- Size of change, test result, human intervention and rework/retry count.
- Usage changes if product legitimately exposes them; duration and cost including VPS.
- Count only **reviewable, tested Draft PRs**, not empty assistant turns or claimed Issues.

Start with small tasks and a lower-cost available model. Escalate to a stronger model when task complexity requires it. Avoid repeated diagnosis and excessive tests, but **do not remove meaningful security controls or critical regressions**.

## No quota bypass

Never rotate multiple accounts, share sign-in credentials, scrape auth tokens, invent balance, manipulate client rate limits or promise unlimited use. If quota runs out, report/queue/stop and resume only when the service allows.
