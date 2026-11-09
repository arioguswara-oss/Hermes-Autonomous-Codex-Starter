"""Pure, strict task-manifest validation. No network or subprocess calls."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path, PurePosixPath
import re

APPROVAL = "CODING_TEST_COMMIT_DRAFT_ONLY"
_REPO = re.compile(r"[A-Za-z0-9_.-]{1,39}/[A-Za-z0-9_.-]{1,100}\Z")
_USER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?\Z")
_TASK = re.compile(r"[a-z][a-z0-9-]{2,63}\Z")
_SHA = re.compile(r"[0-9a-f]{40}\Z")
_KEYS = frozenset({"schema", "taskId", "repository", "expectedHead", "sourcePath",
                   "goal", "expiresAt", "owner", "ownerApproval"})


class ManifestError(ValueError):
    """Manifest rejected before any worker execution."""


@dataclass(frozen=True)
class Task:
    task_id: str
    repository: str
    expected_head: str
    source_path: str
    goal: str
    expires_at: datetime
    owner: str
    owner_approval: str = APPROVAL


def validate(payload: object, *, now: datetime | None = None,
             allowed_repository: str | None = None,
             allowed_prefix: str = "src/", max_hours: int = 24) -> Task:
    """Validate an exact Owner-delegated development-only task.

    A real worker must ALSO verify GitHub issue author against the authenticated
    platform identity, the remote commit, and filesystem symlinks before writing.
    This validator intentionally performs no GitHub or filesystem action.
    """
    if not isinstance(payload, dict) or set(payload) != _KEYS:
        raise ManifestError("INVALID_FIELDS")
    if payload.get("schema") != 1:
        raise ManifestError("UNSUPPORTED_SCHEMA")
    task_id = payload["taskId"]
    repo = payload["repository"]
    sha = payload["expectedHead"]
    owner = payload["owner"]
    source = payload["sourcePath"]
    goal = payload["goal"]
    if not isinstance(task_id, str) or not _TASK.fullmatch(task_id):
        raise ManifestError("INVALID_TASK_ID")
    if not isinstance(repo, str) or not _REPO.fullmatch(repo):
        raise ManifestError("INVALID_REPOSITORY")
    if allowed_repository is not None and repo != allowed_repository:
        raise ManifestError("REPOSITORY_NOT_ALLOWLISTED")
    if not isinstance(sha, str) or not _SHA.fullmatch(sha):
        raise ManifestError("INVALID_EXPECTED_HEAD")
    if not isinstance(owner, str) or not _USER.fullmatch(owner):
        raise ManifestError("INVALID_OWNER")
    if payload["ownerApproval"] != APPROVAL:
        raise ManifestError("UNAUTHORIZED_ACTION")
    if not isinstance(source, str) or len(source) > 180 or "\\" in source:
        raise ManifestError("INVALID_SOURCE_PATH")
    parts = PurePosixPath(source).parts
    if (not source or source.startswith("/") or source.endswith("/")
            or any(p in ("..", ".", "") for p in source.split("/"))
            or not parts or PurePosixPath(source).as_posix() != source
            or not source.startswith(allowed_prefix)
            or source == allowed_prefix):
        raise ManifestError("SOURCE_NOT_ALLOWLISTED")
    if not isinstance(goal, str) or not 20 <= len(goal) <= 500:
        raise ManifestError("INVALID_GOAL")
    if any(ord(ch) < 32 or ord(ch) > 126 for ch in goal):
        raise ManifestError("GOAL_MUST_BE_SINGLE_LINE_PRINTABLE_ASCII")
    expiry = payload["expiresAt"]
    if not isinstance(expiry, str) or not re.fullmatch(
            r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", expiry):
        raise ManifestError("INVALID_EXPIRATION")
    try:
        dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ManifestError("INVALID_EXPIRATION") from exc
    clock = now or datetime.now(timezone.utc)
    if clock.tzinfo is None:
        raise ManifestError("CLOCK_MUST_BE_TIMEZONE_AWARE")
    if not 1 <= max_hours <= 24 or not clock < dt <= clock + timedelta(hours=max_hours):
        raise ManifestError("TASK_EXPIRED_OR_TOO_LONG")
    return Task(task_id, repo, sha, source, goal, dt, owner)


def load(path: str | Path, **kwargs: object) -> Task:
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 8192:
        raise ManifestError("UNSAFE_MANIFEST_FILE")
    try:
        obj = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError("INVALID_JSON") from exc
    return validate(obj, **kwargs)
