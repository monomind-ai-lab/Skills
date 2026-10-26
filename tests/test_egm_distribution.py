from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("egm_distribution", ROOT / "scripts/egm_distribution.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EgmDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.repo = self.parent / "catalog"
        shutil.copytree(ROOT / "distributions/egm", self.repo / "distributions/egm")
        for relative in ("upstreams/egm.json", ".codex-plugin/plugin.json"):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.source = self.repo / MODULE.SNAPSHOT

    def test_complete_snapshot_verifies_offline(self):
        manifest = MODULE.verify(self.repo)
        self.assertEqual(manifest["distribution_model"], "complete-unmodified-snapshot")
        # Check Git compatibility independently, rather than comparing the helper to itself.
        readme = self.source / "README.md"
        blob = subprocess.check_output(["git", "hash-object", str(readme)], text=True).strip()
        self.assertEqual(blob, manifest["snapshot"]["files"]["README.md"]["blob"])

    def test_modified_shared_persona_is_rejected(self):
        path = self.source / "agents/comprehension.md"
        path.write_text(path.read_text() + "\nAn unauthorized instruction.\n")
        with self.assertRaisesRegex(ValueError, "changed=.*agents/comprehension"):
            MODULE.verify(self.repo)

    def test_missing_hidden_manifest_is_rejected(self):
        (self.source / ".codex-plugin/plugin.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing=.*.codex-plugin/plugin.json"):
            MODULE.verify(self.repo)

    def test_extra_runtime_file_is_rejected(self):
        (self.source / "new-hook.sh").write_text("exit 0\n")
        with self.assertRaisesRegex(ValueError, "extra=.*new-hook.sh"):
            MODULE.verify(self.repo)

    def test_modified_binary_asset_is_rejected(self):
        path = self.source / "site/public/og.png"
        path.write_bytes(path.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "changed=.*site/public/og.png"):
            MODULE.verify(self.repo)

    def test_executable_mode_drift_is_rejected(self):
        path = self.source / "README.md"
        path.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "changed=.*README.md"):
            MODULE.verify(self.repo)

    def test_redirected_resource_is_rejected(self):
        path = self.source / "README.md"
        path.unlink()
        path.symlink_to(self.parent / "outside.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.verify(self.repo)

    def test_tree_identity_must_match_inventory(self):
        path = self.repo / "upstreams/egm.json"
        manifest = json.loads(path.read_text())
        manifest["snapshot"]["tree"] = "0" * 40
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Git tree"):
            MODULE.verify(self.repo)

    def test_missing_font_license_is_rejected(self):
        (self.repo / "distributions/egm/licenses/googlesanscode-OFL.txt").unlink()
        with self.assertRaises(OSError):
            MODULE.verify(self.repo)

    def test_catalog_cannot_register_distribution_as_default_skill_root(self):
        path = self.repo / ".codex-plugin/plugin.json"
        plugin = json.loads(path.read_text())
        plugin["skills"] = "./distributions/egm/upstream/skills/"
        path.write_text(json.dumps(plugin))
        with self.assertRaisesRegex(ValueError, "only the normal skills directory"):
            MODULE.verify(self.repo)

    def test_export_retains_full_bundle_and_provenance(self):
        destination = self.parent / "exported"
        manifest = MODULE.export(self.repo, destination)
        self.assertEqual(MODULE.inventory(destination / "upstream"), manifest["snapshot"]["files"])
        self.assertEqual(json.loads((destination / "UPSTREAM.json").read_text()), manifest)
        self.assertTrue((destination / "licenses/googlesansflex-OFL.txt").is_file())
        self.assertFalse((destination / "upstream/.git").exists())

    def test_export_never_overwrites_existing_directory(self):
        destination = self.parent / "existing"
        destination.mkdir()
        sentinel = destination / "user-file"
        sentinel.write_text("retain me")
        with self.assertRaisesRegex(ValueError, "already exists"):
            MODULE.export(self.repo, destination)
        self.assertEqual(sentinel.read_text(), "retain me")

    def test_export_refuses_nested_catalog_and_redirected_destination(self):
        with self.assertRaisesRegex(ValueError, "outside the catalog"):
            MODULE.export(self.repo, self.repo / "new-export")
        link = self.parent / "linked-catalog"
        link.symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "outside the catalog"):
            MODULE.export(self.repo, link / "new-export")

    def test_tampered_snapshot_cannot_be_exported(self):
        (self.source / "resources/execution_instructions.md").unlink()
        destination = self.parent / "exported"
        with self.assertRaisesRegex(ValueError, "snapshot mismatch"):
            MODULE.export(self.repo, destination)
        self.assertFalse(destination.exists())

    def test_unrelated_bundle_file_cannot_be_exported(self):
        note = self.repo / "distributions/egm/unrelated-private-note.txt"
        note.write_text("fixture-only private note")
        destination = self.parent / "exported"
        with self.assertRaisesRegex(ValueError, "distribution bundle mismatch.*unrelated-private-note"):
            MODULE.export(self.repo, destination)
        self.assertFalse(destination.exists())
        self.assertEqual(note.read_text(), "fixture-only private note")

    def test_redirected_bundle_guide_cannot_be_exported(self):
        outside = self.parent / "outside.txt"
        outside.write_text("fixture outside the bundle")
        guide = self.repo / "distributions/egm/README.md"
        guide.unlink()
        guide.symlink_to(outside)
        destination = self.parent / "exported"
        with self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.export(self.repo, destination)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
