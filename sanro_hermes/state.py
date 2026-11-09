"""Atomic one-attempt demo claim ledger, isolated from any repository."""
from __future__ import annotations
from pathlib import Path
import json
import os
from .manifest import Task


def claim_once(folder: Path, task: Task) -> Path:
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("UNSAFE_STATE_DIRECTORY")
    if folder.stat().st_mode & 0o077:
        raise ValueError("STATE_DIRECTORY_NOT_PRIVATE")
    file = folder / f"{task.task_id}.claim.json"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(file, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"taskId": task.task_id, "repository": task.repository,
                       "status": "DEMO_CLAIMED_NO_EXECUTION"}, stream)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        # Keep the claim for investigation rather than silently replaying.
        raise
    return file
