"""Offline contract tests for golden-plan, preflight and CI selection."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "installer"))
import integration

CLI = ROOT / "installer" / "sanro_install.py"

BASE = {
    "schema": 2,
    "project": "contoh-node",
    "repository": "arioguswara-oss/Safe-Dev",
    "baseCommit": "1" * 40,
    "sourcePath": "backend/src/approved-file.js",
    "candidateBlob": "2" * 40,
    "profile": "node",
    "ownerApproval": "CODING_TEST_COMMIT_DRAFT_ONLY",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli(*args):
    return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                          capture_output=True, text=True, timeout=20, check=False)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest = self.root / "manifest.json"
        self.candidate = self.root / "reviewed-installer.py"
        self.candidate.write_text("# reviewed placeholder never executed\n", encoding="utf-8")

    def write_manifest(self, payload=None):
        self.manifest.write_text(json.dumps(BASE if payload is None else payload), encoding="utf-8")
        self.manifest.chmod(0o600)

    def plan(self, *extra):
        return cli("golden-plan", "--manifest", self.manifest,
                   "--manifest-sha256", digest(self.manifest),
                   "--external-installer", self.candidate,
                   "--installer-sha256", digest(self.candidate), *extra)

    def test_valid_manifest_and_external_artifact_without_execution(self):
        self.write_manifest()
        result = self.plan()
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["componentId"], "sanro.golden-worker.node.v2")
        self.assertEqual(out["status"], "PLANNED")
        self.assertFalse(out["externalInstallerExecuted"])
        self.assertFalse(out["readyForActivation"])
        self.assertFalse(out["productionMutation"])
        self.assertEqual(self.candidate.read_text(), "# reviewed placeholder never executed\n")

    def test_manifest_sha_tamper_is_blocked(self):
        self.write_manifest()
        trusted = digest(self.manifest)
        self.manifest.write_text(self.manifest.read_text() + " ", encoding="utf-8")
        result = cli("golden-plan", "--manifest", self.manifest,
                     "--manifest-sha256", trusted,
                     "--external-installer", self.candidate,
                     "--installer-sha256", digest(self.candidate))
        self.assertEqual(result.returncode, 2)
        self.assertIn("REVIEWED_SHA256_MISMATCH", result.stderr)

    def test_external_installer_sha_mismatch_is_blocked(self):
        self.write_manifest()
        result = cli("golden-plan", "--manifest", self.manifest,
                     "--manifest-sha256", digest(self.manifest),
                     "--external-installer", self.candidate,
                     "--installer-sha256", "0" * 64)
        self.assertEqual(result.returncode, 2)
        self.assertIn("REVIEWED_SHA256_MISMATCH", result.stderr)

    def test_manifest_extra_fields_rejected(self):
        self.write_manifest({**BASE, "shell": "rm -rf /"})
        out = self.plan()
        self.assertEqual(out.returncode, 2)
        self.assertIn("MANIFEST_SCHEMA_MISMATCH", out.stderr)

    def test_unsupported_repo_or_traversal_rejected(self):
        for payload, reason in [
            ({**BASE, "repository": "external/NotApproved"}, "GOLDEN_REPOSITORY_UNSUPPORTED"),
            ({**BASE, "sourcePath": "backend/../secret.js"}, "GOLDEN_SOURCE_INVALID"),
            ({**BASE, "profile": "android"}, "GOLDEN_PROFILE_UNSUPPORTED"),
            ({**BASE, "ownerApproval": "PRODUCTION_DEPLOY"}, "GOLDEN_APPROVAL_SCOPE_INVALID"),
        ]:
            with self.subTest(reason=reason):
                self.write_manifest(payload)
                out = self.plan()
                self.assertEqual(out.returncode, 2)
                self.assertIn(reason, out.stderr)

    def test_symlink_artifact_is_blocked(self):
        self.write_manifest()
        link = self.root / "symlink-installer.py"
        link.symlink_to(self.candidate)
        out = cli("golden-plan", "--manifest", self.manifest,
                  "--manifest-sha256", digest(self.manifest),
                  "--external-installer", link,
                  "--installer-sha256", digest(self.candidate))
        self.assertEqual(out.returncode, 2)
        self.assertIn("ARTIFACT_NOT_REGULAR_FILE", out.stderr)

    def test_preflight_does_not_claim_runtime_ready(self):
        result = cli("preflight")
        self.assertEqual(result.returncode, 0, result.stderr)
        info = json.loads(result.stdout)
        self.assertFalse(info["fullRuntimeReady"])
        self.assertFalse(info["hermesAgentIntegrated"])
        self.assertFalse(info["identityIsolationVerified"])
        self.assertFalse(info["productionMutation"])

    def test_gh_public_metadata_recommends_actions_without_starting(self):
        with mock.patch.object(integration, "query_github", return_value={
            "full_name": "arioguswara-oss/Safe-Dev", "private": False
        }):
            info = integration.select_ci("arioguswara-oss/Safe-Dev")
        self.assertEqual(info["status"], "PLANNED")
        self.assertFalse(info["ciJobStarted"])
        self.assertEqual(info["selection"], "GITHUB_ACTIONS_STANDARD_RECOMMENDED")

    def test_gh_private_metadata_blocks_unverified_local_ci(self):
        with mock.patch.object(integration, "query_github", return_value={
            "full_name": "arioguswara-oss/Safe-Dev", "private": True
        }):
            info = integration.select_ci("arioguswara-oss/Safe-Dev",
                                         local_ci_verified=True)
        self.assertEqual(info["status"], "BLOCKED")
        self.assertFalse(info["localCiVerifiedByToolkit"])
        self.assertFalse(info["billableFallbackStarted"])

    def test_gh_metadata_wrong_repo_or_non_boolean_private_blocked(self):
        for result in [
            {"full_name": "other/Repo", "private": False},
            {"full_name": "arioguswara-oss/Safe-Dev", "private": "false"},
        ]:
            with self.subTest(result=result),                  mock.patch.object(integration.shutil, "which", return_value="/usr/bin/gh"),                  mock.patch.object(integration.subprocess, "run",
                                   return_value=mock.Mock(returncode=0, stdout=json.dumps(result))):
                with self.assertRaises(integration.Blocked):
                    integration.query_github("arioguswara-oss/Safe-Dev")

    def test_gh_error_does_not_expose_stderr(self):
        with mock.patch.object(integration.shutil, "which", return_value="/usr/bin/gh"),              mock.patch.object(integration.subprocess, "run",
                               return_value=mock.Mock(returncode=1, stdout="",
                                                      stderr="sensitive GH message")):
            with self.assertRaises(integration.Blocked) as caught:
                integration.query_github("arioguswara-oss/Safe-Dev")
        self.assertEqual(str(caught.exception), "GH_METADATA_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
