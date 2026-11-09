#!/usr/bin/env python3
"""SANRO Hermes unified installer: safe planning and non-live staging only.

This public starter cannot install or activate upstream Hermes, Codex, a
private Golden Worker candidate, SANRO Agent Bridge or SANRO Local CI.
It never executes external commands, creates systemd services, or deploys.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

from integration import golden_plan, preflight, select_ci
from bridge_ci import bridge_plan, ci_report

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "installer" / "components.json"
STAGED_FILES = (
    "README.md",
    "NOTICE.md",
    "docs/AGENT_BRIDGE.md",
    "docs/ARCHITECTURE.md",
    "docs/CI_STRATEGY.md",
    "docs/COSTS.md",
    "docs/GOLDEN_WORKER.md",
    "docs/ID.md",
    "installer/components.json",
    "installer/integration.py",
    "installer/bridge_ci.py",
    "installer/sanro_install.py",
    "docs/INTEGRATION.md",
    "examples/golden-worker.node.example.json",
)
LOCK_NAME = "SANRO_STAGING_LOCK.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def catalog() -> dict:
    info = json.loads(CATALOG.read_text(encoding="utf-8"))
    if info.get("schemaVersion") != 1 or not isinstance(info.get("components"), list):
        raise ValueError("Invalid components catalog")
    ids = [row.get("id") for row in info["components"]]
    if not all(isinstance(item, str) and item for item in ids):
        raise ValueError("Invalid component identifiers")
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate component identifiers")
    if info.get("activation", {}).get("productionMutation") is not False:
        raise ValueError("Unsafe activation policy")
    return info


def source_files() -> list[Path]:
    paths = []
    for relative in STAGED_FILES:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Missing/unsafe bundled file: {relative}")
        paths.append(path)
    return paths


def plan() -> dict:
    info = catalog()
    files = source_files()
    return {
        "package": info["package"],
        "status": "PLANNED",
        "operation": "plan-only",
        "externalDependenciesAreInstalled": False,
        "goldenWorkerNodeBundled": False,
        "fullRuntimeReady": False,
        "productionMutation": False,
        "items": [{"id": row["id"], "status": row["status"],
                   "distribution": row["distribution"]} for row in info["components"]],
        "bundledFileCount": len(files),
        "requires": "Owner-reviewed external components, isolation and activation",
    }


def safe_destination(raw: str) -> Path:
    if not raw or not Path(raw).is_absolute():
        raise ValueError("--output must be an explicit absolute path")
    candidate = Path(raw).expanduser()
    if candidate.exists() or candidate.is_symlink():
        raise ValueError("Output already exists; will not overwrite it")
    parent = candidate.parent
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise ValueError("Output parent must be an existing real directory")
    resolved = candidate.resolve(strict=False)
    if resolved == ROOT or ROOT.is_relative_to(resolved) or resolved.is_relative_to(ROOT):
        raise ValueError("Cannot stage over or inside toolkit source")
    # This installer cannot know the user's production paths. Make intent explicit
    # and never perform service activation or run code from the staged package.
    if not os.access(parent, os.W_OK):
        raise ValueError("Output parent is not writable")
    return resolved


def prepare(output: str, ack_nonlive: bool) -> dict:
    if not ack_nonlive:
        raise ValueError("--ack-nonlive required: target must be a non-live review directory")
    info = catalog()
    files = source_files()
    target = safe_destination(output)
    target.mkdir(mode=0o700)
    try:
        entries = {}
        for src in files:
            relative = src.relative_to(ROOT)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, destination, follow_symlinks=False)
            entries[str(relative)] = sha256(destination)
        lock = {
            "schemaVersion": 1,
            "package": info["package"],
            "status": "PREPARED_NONLIVE",
            "active": False,
            "productionMutation": False,
            "externalDependenciesInstalled": False,
            "goldenWorkerNodeBundled": False,
            "files": entries,
        }
        (target / LOCK_NAME).write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:
        # Safe cleanup of the newly created staging directory ONLY.
        shutil.rmtree(target)
        raise
    return {"status": lock["status"], "path": str(target),
            "files": len(entries), "active": False, "productionMutation": False}


def verify(raw: str) -> dict:
    target = Path(raw).expanduser().resolve(strict=True)
    lock_path = target / LOCK_NAME
    if not lock_path.is_file() or lock_path.is_symlink():
        raise ValueError("Missing/unsafe staging lock")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("schemaVersion") != 1 or lock.get("productionMutation") is not False or lock.get("active") is not False:
        raise ValueError("Invalid staging safety metadata")
    expected = lock.get("files")
    if not isinstance(expected, dict) or set(expected) != set(STAGED_FILES):
        raise ValueError("Unexpected staged file list")
    checks = []
    for rel, checksum in expected.items():
        path = target / rel
        ok = path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(target) and sha256(path) == checksum
        checks.append({"file": rel, "match": bool(ok)})
    success = all(c["match"] for c in checks)
    return {"status": "PREPARED_NONLIVE" if success else "BLOCKED",
            "verified": success, "fileCount": len(checks),
            "failed": [c["file"] for c in checks if not c["match"]],
            "active": False, "productionMutation": False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("plan", help="Read-only component and staging plan")
    sub.add_parser("preflight", help="Read-only local binary preflight (not runtime proof)")
    golden = sub.add_parser("golden-plan", help="Inspect pinned Golden Worker Node V2; never run it")
    golden.add_argument("--manifest", required=True)
    golden.add_argument("--manifest-sha256", required=True)
    golden.add_argument("--external-installer", required=True)
    golden.add_argument("--installer-sha256", required=True)
    ci = sub.add_parser("ci-plan", help="Read authenticated GitHub visibility; never start CI")
    ci.add_argument("--repo", required=True)
    bridge = sub.add_parser("bridge-plan", help="Validate pinned read-only bridge task; no dispatch")
    bridge.add_argument("--task", required=True)
    bridge.add_argument("--task-sha256", required=True)
    report = sub.add_parser("ci-report", help="Validate pinned Local CI report without raw logs")
    report.add_argument("--report", required=True)
    report.add_argument("--report-sha256", required=True)
    p = sub.add_parser("prepare", help="Copy public-safe examples/docs to new non-live directory")
    p.add_argument("--output", required=True, help="Absolute path to NEW non-live staging directory")
    p.add_argument("--ack-nonlive", action="store_true")
    v = sub.add_parser("verify", help="Read-only SHA-256 check for a prepared staging directory")
    v.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "plan":
            result = plan()
        elif args.action == "preflight":
            result = preflight()
        elif args.action == "golden-plan":
            result = golden_plan(args.manifest, args.manifest_sha256,
                                 args.external_installer, args.installer_sha256)
        elif args.action == "ci-plan":
            result = select_ci(args.repo)
        elif args.action == "bridge-plan":
            result = bridge_plan(args.task, args.task_sha256)
        elif args.action == "ci-report":
            result = ci_report(args.report, args.report_sha256)
        elif args.action == "prepare":
            result = prepare(args.output, args.ack_nonlive)
        else:
            result = verify(args.output)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2 if result.get("status") == "BLOCKED" or result.get("verified") is False else 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "productionMutation": False}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
