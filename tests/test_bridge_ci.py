"""Offline tests for SANRO Bridge/Local CI contract adapters."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "installer" / "sanro_install.py"


def run(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          capture_output=True, text=True, timeout=15, check=False)


def pin(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BridgeAndCiContractTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        self.bridge = self.root / "bridge.json"
        self.report = self.root / "ci.json"

    def task(self, **updates):
        payload = {
            "schemaVersion": 1, "id": "abc-001", "project": "pos-public",
            "goal": "inspect project configuration", "mode": "deterministic-readonly",
            "risk": "read-only", "productionMutationAllowed": False
        }
        payload.update(updates)
        self.bridge.write_text(json.dumps(payload), encoding="utf-8")
        return run("bridge-plan", "--task", self.bridge,
                   "--task-sha256", pin(self.bridge))

    def local_ci(self, **updates):
        payload = {
            "schemaVersion": 1, "status": "PASS", "exitCode": 0,
            "runId": "ci-001", "productionMutation": False,
            "source": {"commit": "a" * 40, "dirty": False},
            "stages": [{"name": "test", "logTail": ["secret test log not to leak"]}]
        }
        payload.update(updates)
        self.report.write_text(json.dumps(payload), encoding="utf-8")
        return run("ci-report", "--report", self.report,
                   "--report-sha256", pin(self.report))

    def test_bridge_readonly_is_planned_never_dispatched(self):
        result = self.task()
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertFalse(parsed["dispatched"])
        self.assertFalse(parsed["productionMutation"])

    def test_bridge_rejects_mutating_goal_and_risk(self):
        for change in [
            {"goal": "deploy the live app"},
            {"productionMutationAllowed": True},
            {"risk": "write"},
            {"mode": "codex-readonly"},
            {"shell": "id"},
        ]:
            with self.subTest(change=change):
                result = self.task(**change)
                self.assertEqual(result.returncode, 2)
                self.assertIn("BLOCKED", result.stderr)

    def test_bridge_ci_allowlist(self):
        result = self.task(mode="deterministic-ci", goal="run SANRO CI",
                           ciCommand="ci")
        self.assertEqual(result.returncode, 0, result.stderr)
        bad = self.task(mode="deterministic-ci", goal="run SANRO CI",
                        ciCommand="deploy")
        self.assertEqual(bad.returncode, 2)
        release_check = self.task(mode="deterministic-ci",
                                  goal="run SANRO release-check",
                                  ciCommand="release-check")
        self.assertEqual(release_check.returncode, 0, release_check.stderr)

    def test_ci_envelope_sanitized(self):
        result = self.local_ci()
        self.assertEqual(result.returncode, 0, result.stderr)
        obj = json.loads(result.stdout)
        self.assertTrue(obj["reportEnvelopeParsed"])
        self.assertFalse(obj["independentRunnerAttestationVerified"])
        self.assertFalse(obj["ciJobStartedByToolkit"])
        self.assertNotIn("secret", result.stdout)

    def test_ci_report_rejects_inconsistent_and_mutating(self):
        for change in [
            {"status": "PASS", "exitCode": 1},
            {"status": "BLOCKED", "exitCode": 0},
            {"productionMutation": True},
            {"source": {"commit": "a" * 40, "dirty": True}},
        ]:
            with self.subTest(change=change):
                result = self.local_ci(**change)
                self.assertEqual(result.returncode, 2)

    def test_ci_pin_mismatch_blocks(self):
        self.local_ci()
        res = run("ci-report", "--report", self.report,
                  "--report-sha256", "0" * 64)
        self.assertEqual(res.returncode, 2)
        self.assertIn("REVIEWED_SHA256_MISMATCH", res.stderr)


if __name__ == "__main__":
    unittest.main()
