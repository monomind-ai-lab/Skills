from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "session_start.py"
HOOK_CONFIG = ROOT / "hooks" / "hooks.json"
PLUGIN_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PROFILE_TEMPLATE = ROOT / "skills" / "monomind-workflow" / "assets" / "workflow-profile.md"


def run_hook(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(
            {
                "session_id": "test-session",
                "cwd": str(cwd),
                "hook_event_name": "SessionStart",
                "source": "startup",
            }
        ),
        capture_output=True,
        text=True,
        check=False,
    )


class SessionStartHookTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name) / "repo"
        self.repo.mkdir()
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_profile(self, text: str) -> None:
        profile = self.repo / ".monomind" / "workflow.md"
        profile.parent.mkdir(parents=True)
        profile.write_text(text, encoding="utf-8")

    def complete_profile(self) -> str:
        template = PROFILE_TEMPLATE.read_text(encoding="utf-8")
        return re.sub(
            r"(?m)^(- [^:\n]+:\s*)UNRESOLVED(?:[^\n]*)$",
            r"\1approved value — evidence: README.md",
            template,
        )

    def test_missing_profile_adds_context_only_after_opt_in(self) -> None:
        (self.repo / 'AGENTS.md').write_text('<!-- monomind-workflow:start -->\n')
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("profile is absent", context)
        self.assertIn("$monomind-onboarding", context)
        self.assertIn("repository owner", context)
        self.assertIn("Never guess policy", context)

    def test_unresolved_or_missing_fields_add_onboarding_context(self) -> None:
        self.write_profile("# Partial\n\n- Integration strategy: UNRESOLVED\n")
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("field(s) need resolution", context)
        self.assertIn("build", context)

    def test_complete_profile_is_silent(self) -> None:
        self.write_profile(self.complete_profile())
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_bare_not_applicable_adds_onboarding_context(self) -> None:
        profile = self.complete_profile().replace(
            "- Focused test: approved value — evidence: README.md",
            "- Focused test: NOT_APPLICABLE",
        )
        self.write_profile(profile)
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Focused test", context)

    def test_unadopted_repository_is_silent(self) -> None:
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    def test_release_gaps_do_not_nag_build_sessions(self) -> None:
        self.write_profile(self.complete_profile().replace(
            '- Release command or pipeline: approved value — evidence: README.md',
            '- Release command or pipeline: UNRESOLVED'))
        self.assertEqual(run_hook(self.repo).stdout, '')

    def test_dismissal_suppresses_even_incomplete_profiles(self) -> None:
        self.write_profile('- Focused test: UNRESOLVED\n')
        (self.repo / '.monomind/onboarding.json').write_text('{"enabled":false}')
        self.assertEqual(run_hook(self.repo).stdout, '')

    def test_explicit_release_boundary_reports_release_gaps(self) -> None:
        self.write_profile(self.complete_profile().replace(
            '- Release command or pipeline: approved value — evidence: README.md',
            '- Release command or pipeline: UNRESOLVED'))
        (self.repo / '.monomind/onboarding.json').write_text('{"enabled":true,"gate":"release"}')
        self.assertIn('Release command or pipeline', run_hook(self.repo).stdout)

    def test_duplicate_profile_is_not_silently_accepted(self) -> None:
        self.write_profile(self.complete_profile() + '\n- Focused test: duplicate\n')
        self.assertIn('duplicate', run_hook(self.repo).stdout)

    def test_future_schema_requires_compatible_plugin(self) -> None:
        self.write_profile(self.complete_profile().replace('Policy schema version: 2', 'Policy schema version: 999'))
        self.assertIn('unsupported policy schema', run_hook(self.repo).stdout)

    def test_invalid_settings_are_reported_without_a_traceback(self) -> None:
        self.write_profile(self.complete_profile())
        (self.repo / '.monomind/onboarding.json').write_text('{"enabled":true,"gate":[]}')
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('gate must be', result.stdout)
        self.assertNotIn('Traceback', result.stderr)

    def test_owner_field_cannot_be_reasoned_not_applicable(self) -> None:
        profile = self.complete_profile().replace(
            "- Repository owner or project lead: approved value — evidence: README.md",
            "- Repository owner or project lead: NOT_APPLICABLE — no owner assigned",
        )
        self.write_profile(profile)
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Repository owner or project lead", context)

    def test_non_repository_is_silent(self) -> None:
        outside = Path(self.tempdir.name) / "outside"
        outside.mkdir()
        result = run_hook(outside)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_plugin_packages_catalog_and_default_session_start_hook(self) -> None:
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "monomind-software-factory")
        self.assertEqual(manifest["skills"], "./skills/")

        hook_config = json.loads(HOOK_CONFIG.read_text(encoding="utf-8"))
        group = hook_config["hooks"]["SessionStart"][0]
        self.assertEqual(group["matcher"], "startup|resume|clear")
        handler = group["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertIn("${PLUGIN_ROOT}/hooks/session_start.py", handler["command"])

    def test_marketplace_exposes_root_plugin_from_main(self) -> None:
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "monomind-software-factory")
        self.assertEqual(entry["source"]["source"], "url")
        self.assertEqual(entry["source"]["ref"], "main")


if __name__ == "__main__":
    unittest.main()
