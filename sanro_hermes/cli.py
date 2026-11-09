"""Safe public SANRO Hermes CLI: manifest, mock demo and command preview only."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import sys
import tempfile
from pathlib import Path

from .manifest import APPROVAL, ManifestError, load
from .providers import CodexCliProvider, MockProvider
from .state import claim_once


def new_task(owner: str, repo: str, path: str) -> dict[str, object]:
    exp = datetime.now(timezone.utc) + timedelta(hours=2)
    return {
        "schema": 1,
        "taskId": "demo-documentation-001",
        "repository": repo,
        "expectedHead": "0" * 40,
        "sourcePath": path,
        "goal": "Add a short documentation comment without changing runtime behavior.",
        "expiresAt": exp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owner": owner,
        "ownerApproval": APPROVAL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sanro-hermes", description="SANRO Hermes v0.1 safe starter")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init-task", help="print a fresh example task manifest")
    init.add_argument("--owner", default="example-owner")
    init.add_argument("--repo", default="example-owner/example-repo")
    init.add_argument("--source", default="src/example.py")
    for cmd in ("validate", "demo", "codex-preview"):
        p = sub.add_parser(cmd)
        p.add_argument("manifest")
        p.add_argument("--repo", help="optional exact repository allowlist")
        p.add_argument("--prefix", default="src/", help="allowed source path prefix")
    args = parser.parse_args(argv)

    if args.command == "init-task":
        print(json.dumps(new_task(args.owner, args.repo, args.source), indent=2))
        return 0

    try:
        task = load(args.manifest,
                    allowed_repository=args.repo,
                    allowed_prefix=args.prefix)
        if args.command == "validate":
            print(json.dumps({"valid": True, "taskId": task.task_id,
                              "scope": task.source_path,
                              "mode": "VALIDATION_ONLY"}))
        elif args.command == "codex-preview":
            plan = CodexCliProvider().plan(task)
            print(json.dumps({"provider": plan.name, "argv": plan.command,
                              "mode": plan.note, "executed": False}, indent=2))
        elif args.command == "demo":
            with tempfile.TemporaryDirectory(prefix="sanro-hermes-demo-") as d:
                claim_once(Path(d), task)
                plan = MockProvider().plan(task)
                print(json.dumps({"provider": plan.name, "taskId": task.task_id,
                                  "status": plan.note, "claimRecorded": True,
                                  "codeChanged": False, "gitPushed": False,
                                  "prCreated": False}))
        return 0
    except (ManifestError, FileExistsError, ValueError, OSError) as exc:
        # Use fixed validation categories; never print a prompt, token or secret.
        code = str(exc) if isinstance(exc, ManifestError) else "LOCAL_STATE_ERROR"
        print(json.dumps({"ok": False, "error": code}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
