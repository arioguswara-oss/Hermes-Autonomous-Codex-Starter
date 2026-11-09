"""Offline tests for SANRO unified installer non-live scaffold."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "installer" / "sanro_install.py"


def command(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, timeout=30, check=False,
    )


class UnifiedInstallerTest(unittest.TestCase):
    def test_plan_does_not_claim_components_installed(self):
        proc = command("plan")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        obj = json.loads(proc.stdout)
        self.assertEqual(obj["status"], "PLANNED")
        self.assertFalse(obj["fullRuntimeReady"])
        self.assertFalse(obj["goldenWorkerNodeBundled"])
        self.assertFalse(obj["productionMutation"])
        self.assertIn("golden-worker-node", [x["id"] for x in obj["items"]])

    def test_prepare_requires_explicit_nonlive_ack(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "staging"
            proc = command("prepare", "--output", target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(target.exists())
            self.assertIn("BLOCKED", proc.stderr)

    def test_prepare_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "staging"
            proc = command("prepare", "--output", target, "--ack-nonlive")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["status"], "PREPARED_NONLIVE")
            self.assertTrue((target / "docs" / "GOLDEN_WORKER.md").is_file())
            self.assertTrue((target / "SANRO_STAGING_LOCK.json").is_file())
            verify = command("verify", "--output", target)
            self.assertEqual(verify.returncode, 0, verify.stderr)
            self.assertTrue(json.loads(verify.stdout)["verified"])
            again = command("prepare", "--output", target, "--ack-nonlive")
            self.assertNotEqual(again.returncode, 0)
            self.assertTrue((target / "SANRO_STAGING_LOCK.json").exists())

    def test_hash_tampering_blocks_verification(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "staging"
            self.assertEqual(command("prepare", "--output", target, "--ack-nonlive").returncode, 0)
            (target / "docs" / "GOLDEN_WORKER.md").write_text("tampered", encoding="utf-8")
            result = command("verify", "--output", target)
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "BLOCKED")
            self.assertIn("docs/GOLDEN_WORKER.md", payload["failed"])

    def test_relative_path_refused(self):
        proc = command("prepare", "--output", "relative-staging", "--ack-nonlive")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("absolute", proc.stderr)


if __name__ == "__main__":
    unittest.main()
