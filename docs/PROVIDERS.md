# Provider adapters — contribution contract

The **core remains SANRO Hermes Coding Toolkit**, even when alternative AI systems are plugged in. Original developer **Ario Guswara**. **Hermes Agent** upstream credit remains with **Nous Research**.

## Current adapters

| Adapter | Status | Side effects |
| --- | --- | --- |
| `MockProvider` | IMPLEMENTED | No network, no model call, no source edits |
| `CodexCliProvider` | PREVIEW ONLY | Produces an example argument vector; does not execute Codex |
| Claude Code | PROPOSED | None; no real adapter |
| 9router | PROPOSED | None; no gateway configured |
| local LLM / other models | PROPOSED | None |

Do **not** advertise an adapter as implemented until real coding, isolated tests and Draft PR evidence exists.

## Minimum interface

The built-in interface is deliberately small:

```python
from sanro_hermes.providers import ProviderPlan

class MyProvider:
    def plan(self, task):
        return ProviderPlan("my-provider", None, "EXPERIMENTAL_NOT_EXECUTED")
```

A future *executor* must verify:
- A dedicated, least-privilege project workspace and provider-specific authentication distinct from the maintainer's account.
- Network boundary/egress policy, repository diff allowlist, risk limits and no production access.
- Resource/time budget, command permissions and redacted error logging.
- API or subscription terms; no credential sharing, automated limit circumvention or hidden expenses.
- Test evidence on a harmless repository leading to a development Draft PR; no automatic merge.

## Model selection and cost efficiency

Avoid hard-coding a provider or model in the core. A provider may publish its supported model names, supported auth methods, effort controls and use limits. Small changes may use a lighter model where the user's account supports it (for example GPT-6 Luna for eligible Codex configurations). Give heavier work a model with better capability, chosen deliberately.

**Cost optimization is not rate-limit evasion.** Expose remaining quotas/status when supported, queue when exhausted, keep context and tests minimal *without sacrificing meaningful safety*, and use real measurements instead of claims like "always twice the quota."

## Contributor ideas

Claude Code / 9router / local / other adapters are **community extension ideas**. A PR should include configuration examples that contain no secrets, billing/provider requirements, unit tests (including negative cases), installation/rollback instructions and an explicit status label.
