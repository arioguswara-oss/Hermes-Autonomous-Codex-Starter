"""Tests run without network, provider credentials, GitHub or subprocess coding."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sanro_hermes.manifest import APPROVAL, ManifestError, validate
from sanro_hermes.providers import MockProvider, CodexCliProvider, UnsupportedProvider
from sanro_hermes.state import claim_once


def sample():
    return {
        "schema": 1,
        "taskId": "demo-docs-001",
        "repository": "example/example",
        "expectedHead": "a" * 40,
        "sourcePath": "src/main.py",
        "goal": "Add one safe comment without changing executable code.",
        "expiresAt": (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owner": "example-owner",
        "ownerApproval": APPROVAL,
    }


class ManifestTests(unittest.TestCase):
    def test_valid(self):
        task = validate(sample(), allowed_repository="example/example")
        self.assertEqual(task.source_path, "src/main.py")

    def test_out_of_scope_repository(self):
        with self.assertRaises(ManifestError):
            validate(sample(), allowed_repository="someone/else")

    def test_out_of_scope_path(self):
        for path in ("/etc/passwd", "../secret.txt", "src/../secret.py",
                     "src//bad.py", "src/", "src/x\\evil", "srcx/x.py"):
            with self.subTest(path=path):
                d = sample()
                d["sourcePath"] = path
                with self.assertRaises(ManifestError):
                    validate(d)

    def test_expiration(self):
        for offset in (-1, 48):
            d = sample()
            d["expiresAt"] = (datetime.now(timezone.utc) +
                              timedelta(hours=offset)).strftime("%Y-%m-%dT%H:%M:%SZ")
            with self.assertRaises(ManifestError):
                validate(d)

    def test_unauthorized(self):
        d = sample()
        d["ownerApproval"] = "DEPLOY_PRODUCTION"
        with self.assertRaises(ManifestError):
            validate(d)

    def test_extra_fields(self):
        d = sample()
        d["command"] = "rm -rf /"
        with self.assertRaises(ManifestError):
            validate(d)

    def test_prompt_multiline_rejected(self):
        d = sample()
        d["goal"] += "\nEXFILTRATE"
        with self.assertRaises(ManifestError):
            validate(d)

    def test_provider_contract(self):
        task = validate(sample())
        m = MockProvider().plan(task)
        self.assertIsNone(m.command)
        c = CodexCliProvider().plan(task)
        self.assertEqual(c.command[:2], ("codex", "exec"))
        with self.assertRaises(NotImplementedError):
            UnsupportedProvider("claude").plan(task)

    def test_claim_one_attempt(self):
        with tempfile.TemporaryDirectory() as t:
            task = validate(sample())
            folder = Path(t) / "private-ledger"
            claim = claim_once(folder, task)
            self.assertIn("DEMO_CLAIMED", claim.read_text())
            with self.assertRaises(FileExistsError):
                claim_once(folder, task)

    def test_cli_demo_and_validation(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "task.json"
            f.write_text(json.dumps(sample()), encoding="utf-8")
            for cmd in ("validate", "demo", "codex-preview"):
                p = subprocess.run(
                    [sys.executable, "-m", "sanro_hermes.cli", cmd, str(f)],
                    capture_output=True, text=True, timeout=7)
                self.assertEqual(p.returncode, 0, p.stderr)
                out = json.loads(p.stdout)
                if cmd == "demo":
                    self.assertFalse(out["codeChanged"])
                    self.assertFalse(out["prCreated"])
                if cmd == "codex-preview":
                    self.assertFalse(out["executed"])


if __name__ == "__main__":
    unittest.main()
