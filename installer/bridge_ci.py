"""Fail-closed read-only SANRO Agent Bridge and Local CI evidence adapters.

Compatible *planning* contracts for existing internal SANRO bridge/local-ci
schemas. No GitHub queue writes, worker dispatch or CI execution here.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from integration import Blocked, reviewed_file, require

SAFE_ID = re.compile(r"[A-Za-z0-9._-]{3,120}\Z")
SHA1 = re.compile(r"[a-f0-9]{40}\Z")
MUTATION_WORDS = re.compile(
    r"\b(implement|edit|modify|refactor|commit|push|deploy|migrate|"
    r"restart|reconfigure|delete|merge|install|activate|write|chmod|"
    r"release\b(?![-\s]?check))\b", re.IGNORECASE
)
CI_COMMANDS = {"lint", "build", "verify", "release-check", "ci"}


def _parse_pinned_json(path: str, pin: str, size_limit: int = 65536) -> dict:
    checked = reviewed_file(path, pin)
    require(checked.stat().st_size <= size_limit, "EVIDENCE_TOO_LARGE")
    try:
        result = json.loads(checked.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise Blocked("EVIDENCE_INVALID_JSON") from exc
    require(isinstance(result, dict), "EVIDENCE_NOT_OBJECT")
    return result


def bridge_plan(task_path: str, task_pin: str) -> dict:
    """Allow only the existing v0.1 READ-ONLY task modes. No dispatch."""
    task = _parse_pinned_json(task_path, task_pin)
    require(task.get("schemaVersion") == 1, "BRIDGE_SCHEMA_INVALID")
    ident, project = task.get("id"), task.get("project")
    require(isinstance(ident, str) and bool(SAFE_ID.fullmatch(ident)) and
            isinstance(project, str) and bool(SAFE_ID.fullmatch(project)),
            "BRIDGE_ID_INVALID")
    require(task.get("risk") == "read-only" and
            task.get("productionMutationAllowed") is False,
            "BRIDGE_MUTATION_SCOPE_REJECTED")
    mode = task.get("mode", "auto")
    require(mode in ("deterministic-readonly", "deterministic-ci"),
            "BRIDGE_MODE_NOT_ALLOWED")
    goal = task.get("goal")
    require(isinstance(goal, str) and 3 <= len(goal.strip()) <= 4000 and
            not MUTATION_WORDS.search(goal), "BRIDGE_GOAL_REJECTED")
    if mode == "deterministic-ci":
        # Repo's internal contract uses only bounded SANRO Local CI commands.
        command = task.get("ciCommand")
        require(command in CI_COMMANDS, "BRIDGE_CI_COMMAND_NOT_ALLOWLISTED")
        require(re.search(r"\b" + re.escape(command) + r"\b", goal, re.I) is not None,
                "BRIDGE_CI_GOAL_MISMATCH")
    else:
        require(task.get("ciCommand") is None, "BRIDGE_READONLY_CI_NOT_ALLOWED")
    require(not any(k in task for k in ("shell", "command", "token", "credential")),
            "BRIDGE_UNEXPECTED_EXECUTION_FIELD")
    return {
        "status": "PLANNED", "componentId": "sanro.agent-bridge.v1",
        "taskId": ident, "project": project, "mode": mode,
        "taskSha256": task_pin,
        "transport": "EXTERNAL_GITHUB_BRIDGE_NOT_DISPATCHED",
        "dispatched": False, "productionMutation": False,
    }


def ci_report(report_path: str, report_pin: str) -> dict:
    """Validate the Supervisor Local CI v1 JSON envelope, redact raw logs."""
    report = _parse_pinned_json(report_path, report_pin, size_limit=1048576)
    require(report.get("schemaVersion") == 1, "CI_REPORT_SCHEMA_INVALID")
    status = report.get("status")
    code = report.get("exitCode")
    require(status in ("PASS", "FAIL", "BLOCKED") and type(code) is int and
            code in (0, 1, 2), "CI_REPORT_STATUS_INVALID")
    require(report.get("productionMutation") is False, "CI_PRODUCTION_MUTATION_REJECTED")
    require((status == "PASS" and code == 0) or
            (status != "PASS" and code in (1, 2)),
            "CI_REPORT_STATUS_CODE_MISMATCH")
    source = report.get("source")
    require(isinstance(source, dict), "CI_SOURCE_MISSING")
    commit = source.get("commit")
    require(isinstance(commit, str) and bool(SHA1.fullmatch(commit)),
            "CI_COMMIT_INVALID")
    require(source.get("dirty") is False, "CI_DIRTY_SOURCE_REJECTED")
    run = report.get("runId")
    require(isinstance(run, (str, int)) and 1 <= len(str(run)) <= 120,
            "CI_RUN_ID_INVALID")
    return {
        "status": status,
        "componentId": "sanro.local-ci.v1",
        "runId": str(run),
        "commit": commit,
        "reportSha256": report_pin,
        "reportEnvelopeParsed": True,
        "independentRunnerAttestationVerified": False,
        "ciJobStartedByToolkit": False,
        "productionMutation": False,
    }
