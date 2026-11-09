"""Read-only integration adapters for the SANRO Hermes Coding Toolkit.

These adapters inspect local reviewed artifacts and authenticated GitHub
repository metadata. They NEVER invoke an external installer, Codex, an
untrusted task, a CI job or a system service.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

MANIFEST_KEYS = {
    "schema", "project", "repository", "baseCommit", "sourcePath",
    "candidateBlob", "profile", "ownerApproval",
}
SHA1 = re.compile(r"[a-f0-9]{40}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
SLUG = re.compile(r"[a-z][a-z0-9-]{1,28}\Z")
REPO = re.compile(r"arioguswara-oss/[A-Za-z0-9_.-]+\Z")
SOURCE = re.compile(r"backend/[A-Za-z0-9_./-]+\.js\Z")
ALLOWED_APPROVAL = "CODING_TEST_COMMIT_DRAFT_ONLY"
REQUIRED_BINARIES = ("git", "gh", "codex", "node", "npm", "bwrap")


class Blocked(ValueError):
    """An intentionally closed integration gate."""


def require(value: bool, code: str) -> None:
    if not value:
        raise Blocked(code)


def reviewed_file(raw: str, sha: str) -> Path:
    """Verify a local regular file pinned by an independently reviewed SHA-256.

    Hashes alone do not authenticate the Owner. The caller must obtain pins
    through a separate trusted review channel, NEVER from the same file.
    """
    require(bool(SHA256.fullmatch(sha or "")), "REVIEWED_SHA256_REQUIRED")
    path = Path(raw)
    require(path.is_absolute(), "ABSOLUTE_ARTIFACT_PATH_REQUIRED")
    require(path.is_file() and not path.is_symlink(), "ARTIFACT_NOT_REGULAR_FILE")
    require(not path.stat().st_mode & 0o022, "ARTIFACT_GROUP_OR_WORLD_WRITABLE")
    resolved = path.resolve(strict=True)
    digest = hashlib.sha256()
    with resolved.open("rb") as stream:
        for part in iter(lambda: stream.read(65536), b""):
            digest.update(part)
    require(digest.hexdigest() == sha, "REVIEWED_SHA256_MISMATCH")
    return resolved


def golden_plan(manifest_path: str, manifest_pin: str, installer_path: str,
                installer_pin: str) -> dict:
    """Validate exact V2 manifest/pinned external candidate; do not execute it."""
    manifest_file = reviewed_file(manifest_path, manifest_pin)
    installer_file = reviewed_file(installer_path, installer_pin)
    require(manifest_file != installer_file, "MANIFEST_INSTALLER_PATH_COLLISION")
    require(manifest_file.stat().st_size <= 32768, "MANIFEST_TOO_LARGE")
    try:
        payload = json.loads(manifest_file.read_text("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise Blocked("MANIFEST_INVALID_JSON") from exc
    require(isinstance(payload, dict) and set(payload) == MANIFEST_KEYS,
            "MANIFEST_SCHEMA_MISMATCH")
    require(payload["schema"] == 2 and payload["profile"] == "node",
            "GOLDEN_PROFILE_UNSUPPORTED")
    require(isinstance(payload["project"], str) and bool(SLUG.fullmatch(payload["project"])),
            "GOLDEN_PROJECT_INVALID")
    require(isinstance(payload["repository"], str) and bool(REPO.fullmatch(payload["repository"])),
            "GOLDEN_REPOSITORY_UNSUPPORTED")
    require(all(isinstance(payload[k], str) and SHA1.fullmatch(payload[k])
                for k in ("baseCommit", "candidateBlob")),
            "GOLDEN_SHA_INVALID")
    source = payload["sourcePath"]
    require(isinstance(source, str) and bool(SOURCE.fullmatch(source)) and
            ".." not in Path(source).parts, "GOLDEN_SOURCE_INVALID")
    require(payload["ownerApproval"] == ALLOWED_APPROVAL,
            "GOLDEN_APPROVAL_SCOPE_INVALID")
    return {
        "status": "PLANNED",
        "componentId": "sanro.golden-worker.node.v2",
        "project": payload["project"],
        "repository": payload["repository"],
        "sourceCommit": payload["baseCommit"],
        "manifestSha256": manifest_pin,
        "installerSha256": installer_pin,
        "externalInstallerPresentAndPinned": True,
        "externalInstallerExecuted": False,
        "readyForActivation": False,
        "nextGate": "SEPARATE_OWNER_APPROVAL_AND_VERIFIED_ISOLATED_RUNTIME",
        "productionMutation": False,
    }


def preflight() -> dict:
    """Read PATH only. Presence is NOT authentication or sandbox proof."""
    checks = {name: bool(shutil.which(name)) for name in REQUIRED_BINARIES}
    return {
        "status": "PLANNED",
        "checks": checks,
        "python": list(sys.version_info[:3]),
        "fullRuntimeReady": False,
        "identityIsolationVerified": False,
        "hermesAgentIntegrated": False,
        "externalComponentsInstalledByThisCommand": False,
        "productionMutation": False,
    }


def query_github(repo: str) -> dict:
    """Read authenticated repo visibility via GH CLI; do not trigger Actions."""
    require(isinstance(repo, str) and bool(REPO.fullmatch(repo)),
            "REPOSITORY_NOT_ALLOWLISTED")
    gh = shutil.which("gh")
    require(bool(gh), "GH_CLI_NOT_INSTALLED")
    try:
        process = subprocess.run(
            [gh, "api", f"repos/{repo}", "--jq", "{full_name: .full_name, private: .private}"],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20,
            check=False, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Blocked("GH_METADATA_UNAVAILABLE") from exc
    require(process.returncode == 0, "GH_METADATA_UNAVAILABLE")
    require(len(process.stdout) <= 16384, "GH_METADATA_TOO_LARGE")
    try:
        result = json.loads(process.stdout)
    except ValueError as exc:
        raise Blocked("GH_METADATA_NOT_JSON") from exc
    require(isinstance(result, dict) and result.get("full_name") == repo and
            type(result.get("private")) is bool, "GH_METADATA_REPOSITORY_MISMATCH")
    return result


def select_ci(repo: str, local_ci_verified: bool = False) -> dict:
    """Policy advisory, never starts a CI job or treats flags as verification."""
    metadata = query_github(repo)
    private = metadata["private"]
    # A local operator flag is NOT runtime evidence; no automatic selection.
    if private:
        status = "BLOCKED"
        choice = "SANRO_LOCAL_CI_REQUIRES_INDEPENDENT_RUNTIME_VERIFICATION"
    else:
        status = "PLANNED"
        choice = "GITHUB_ACTIONS_STANDARD_RECOMMENDED"
    return {
        "status": status, "repository": repo, "private": private,
        "source": "authenticated-gh-api", "selection": choice,
        "localCiVerifiedByToolkit": False,
        "localCiOperatorClaim": bool(local_ci_verified),
        "billableFallbackStarted": False,
        "ciJobStarted": False,
        "productionMutation": False,
    }
