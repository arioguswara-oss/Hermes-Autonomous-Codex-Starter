"""Small provider contract. No billing, token routing or hidden network calls."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from .manifest import Task


@dataclass(frozen=True)
class ProviderPlan:
    name: str
    command: tuple[str, ...] | None
    note: str


class Provider(Protocol):
    def plan(self, task: Task) -> ProviderPlan:
        ...


class MockProvider:
    """Always offline; useful for installation tests and contributor CI."""

    def plan(self, task: Task) -> ProviderPlan:
        return ProviderPlan("mock", None, "SIMULATED_ONLY_NO_AI_NO_CODE_CHANGES")


class CodexCliProvider:
    """Opt-in command *preview*; v0.1 never executes it.

    Integrators must implement and test a real, isolated executor. In
    particular, never disable the inner Codex sandbox unless a verified
    outer boundary already restricts filesystem and tools.
    """
    def plan(self, task: Task) -> ProviderPlan:
        return ProviderPlan(
            "codex-cli",
            ("codex", "exec", "--sandbox", "workspace-write",
             "--skip-git-repo-check", task.goal),
            "PREVIEW_ONLY_REQUIRES_VERIFIED_EXECUTOR_AND_CHATGPT_LOGIN",
        )


class UnsupportedProvider:
    """Community extension point. Does not pretend an adapter exists."""
    def __init__(self, name: str):
        self.name = name

    def plan(self, task: Task) -> ProviderPlan:
        raise NotImplementedError(
            f"{self.name}: contribute an isolated and tested provider adapter"
        )
