import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "review_upstream_skill.py"
SPEC = importlib.util.spec_from_file_location("review_upstream_skill", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class UpstreamReviewTests(unittest.TestCase):
    def manifest(self):
        return {
            "schema_version": 2,
            "integration": "example",
            "repository": "https://github.com/example/tool.git",
            "tracking_ref": "refs/heads/main",
            "audited_revision": "a" * 40,
            "tracked_files": [{"path": "SKILL.md", "reason": "instructions"}],
            "integration_files": ["skills/example/SKILL.md"],
            "curation_rules": [
                "Use Example as the user-facing name while preserving tool-cli."
            ],
        }

    def test_load_manifest_requires_full_audit_revision(self):
        data = self.manifest()
        data["audited_revision"] = "main"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "full lowercase Git SHA"):
                MODULE.load_manifest(path)

    def test_schema_one_manifest_remains_readable_without_rules(self):
        data = self.manifest()
        data["schema_version"] = 1
        del data["curation_rules"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(MODULE.load_manifest(path)["schema_version"], 1)

    def test_github_raw_url_preserves_nested_path(self):
        url = MODULE.github_raw_url(
            "https://github.com/example/tool.git", "b" * 40, "skills/demo/SKILL.md"
        )
        self.assertEqual(
            url,
            "https://raw.githubusercontent.com/example/tool/"
            + "b" * 40
            + "/skills/demo/SKILL.md",
        )

    def test_load_manifest_rejects_empty_curation_rule(self):
        data = self.manifest()
        data["curation_rules"] = [""]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "curation_rules"):
                MODULE.load_manifest(path)

    @mock.patch.object(MODULE.subprocess, "run")
    def test_resolve_revision_uses_exact_remote_ref(self, run):
        run.return_value.stdout = f"{'c' * 40}\trefs/heads/main\n"
        revision = MODULE.resolve_revision(
            "https://github.com/example/tool.git", "refs/heads/main"
        )
        self.assertEqual(revision, "c" * 40)
        run.assert_called_once_with(
            [
                "git",
                "ls-remote",
                "https://github.com/example/tool.git",
                "refs/heads/main",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_render_report_shows_diff_without_writing(self):
        manifest = self.manifest()

        def fetcher(_repository, revision, _path):
            return "name: old\n" if revision == "a" * 40 else "name: new\n"

        report = MODULE.render_report(manifest, "d" * 40, fetcher=fetcher)
        self.assertIn("-name: old", report)
        self.assertIn("+name: new", report)
        self.assertIn("Changes detected: yes", report)
        self.assertIn("no catalog files were changed", report)
        self.assertIn("Curation rules (mandatory before advancing the pin)", report)
        self.assertIn("Use Example as the user-facing name", report)


if __name__ == "__main__":
    unittest.main()
