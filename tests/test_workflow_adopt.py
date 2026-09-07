from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = ROOT / "skills" / "monomind-workflow"


def run(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(args)}\n{result.stdout}\n{result.stderr}"
        )
    return result


class WorkflowAdoptionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.remote = self.root / "remote.git"
        self.primary = self.root / "primary"
        self.task = self.root / "task"

        run("git", "init", "--bare", str(self.remote))
        run("git", "clone", str(self.remote), str(self.primary))
        run("git", "config", "user.name", "Monomind Test", cwd=self.primary)
        run("git", "config", "user.email", "test@example.invalid", cwd=self.primary)
        (self.primary / "README.md").write_text("fixture\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.primary)
        run("git", "commit", "-m", "initial", cwd=self.primary)
        run("git", "branch", "-M", "main", cwd=self.primary)
        run("git", "push", "-u", "origin", "main", cwd=self.primary)
        run(
            "git",
            "worktree",
            "add",
            "-b",
            "chore/adopt-monomind",
            str(self.task),
            "origin/main",
            cwd=self.primary,
        )
        destination = self.task / ".agents" / "skills" / "monomind-workflow"
        destination.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SOURCE, destination)
        self.installed_script = destination / "scripts" / "adopt.py"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def adopt(self, repo: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(
            "python3",
            str(self.installed_script),
            "apply",
            "--repo",
            str(repo),
            *extra,
            check=False,
        )

    def check_contract(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(
            "python3",
            str(self.installed_script),
            "check",
            "--repo",
            str(self.task),
            *extra,
            check=False,
        )

    def test_dry_run_prints_changes_without_writing(self) -> None:
        agents = self.task / "AGENTS.md"
        agents.write_text("# Existing instructions\n", encoding="utf-8")

        result = self.adopt(self.task, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("monomind-workflow:start", result.stdout)
        self.assertNotIn("monomind-workflow:start", agents.read_text(encoding="utf-8"))
        self.assertFalse((self.task / ".monomind").exists())

    def test_apply_preserves_existing_instructions_and_is_idempotent(self) -> None:
        agents = self.task / "AGENTS.md"
        agents.write_text("# Existing instructions\n\nKeep this text.\n", encoding="utf-8")

        first = self.adopt(self.task)
        self.assertEqual(first.returncode, 0, first.stderr)
        first_text = agents.read_text(encoding="utf-8")
        self.assertIn("# Existing instructions", first_text)
        self.assertIn("<!-- monomind-workflow:start -->", first_text)
        self.assertEqual(first_text.count("<!-- monomind-workflow:start -->"), 1)
        profile = self.task / ".monomind" / "workflow.md"
        self.assertTrue(profile.is_file())
        profile.write_text("# Verified project profile\n", encoding="utf-8")

        second = self.adopt(self.task)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first_text, agents.read_text(encoding="utf-8"))
        self.assertEqual(profile.read_text(encoding="utf-8"), "# Verified project profile\n")

        check = run(
            "python3",
            str(self.installed_script),
            "check",
            "--repo",
            str(self.task),
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn("managed policy is current", check.stdout)

    def test_active_override_file_is_updated_instead_of_shadowed_agents_file(self) -> None:
        agents = self.task / "AGENTS.md"
        override = self.task / "AGENTS.override.md"
        agents.write_text("# Shared\n", encoding="utf-8")
        override.write_text("# Active override\n", encoding="utf-8")

        result = self.adopt(self.task)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("monomind-workflow:start", agents.read_text(encoding="utf-8"))
        self.assertIn("monomind-workflow:start", override.read_text(encoding="utf-8"))

    def test_apply_preserves_existing_crlf_line_endings(self) -> None:
        agents = self.task / "AGENTS.md"
        original = b"# Existing instructions\r\n\r\nKeep this text.\r\n"
        agents.write_bytes(original)

        result = self.adopt(self.task)
        self.assertEqual(result.returncode, 0, result.stderr)
        adopted = agents.read_bytes()
        self.assertTrue(adopted.startswith(original))
        self.assertNotIn(b"\n", adopted.replace(b"\r\n", b""))

    def test_check_detects_policy_drift(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        agents = self.task / "AGENTS.md"
        agents.write_text(
            agents.read_text(encoding="utf-8").replace("Never implement on `main`", "Avoid main"),
            encoding="utf-8",
        )

        result = run(
            "python3",
            str(self.installed_script),
            "check",
            "--repo",
            str(self.task),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has drifted", result.stderr)

    def test_structural_check_warns_but_build_gate_fails_on_unresolved_policy(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)

        structural = self.check_contract()
        self.assertEqual(structural.returncode, 0, structural.stderr)
        self.assertIn("not Release-ready", structural.stdout)
        self.assertIn("Repository owner or project lead", structural.stdout)

        build = self.check_contract("--gate", "build")
        self.assertNotEqual(build.returncode, 0)
        self.assertIn("build-ready policy gate failed", build.stderr)
        self.assertIn("Repository owner or project lead [UNRESOLVED]", build.stderr)
        self.assertIn("monomind-onboarding", build.stderr)

    def test_build_and_release_gates_have_different_required_fields(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        profile = self.task / ".monomind" / "workflow.md"
        resolved = profile.read_text(encoding="utf-8").replace(
            "UNRESOLVED", "approved value — evidence: README.md"
        )
        resolved = resolved.replace(
            "- Integration strategy: approved value — evidence: README.md",
            "- Integration strategy: UNRESOLVED — decision required from project lead",
        )
        profile.write_text(resolved, encoding="utf-8")

        build = self.check_contract("--gate", "build")
        self.assertEqual(build.returncode, 0, build.stderr)
        self.assertIn("build-ready policy gate passed", build.stdout)

        release = self.check_contract("--gate", "release")
        self.assertNotEqual(release.returncode, 0)
        self.assertIn("release-ready policy gate failed", release.stderr)
        self.assertIn("Integration strategy [UNRESOLVED]", release.stderr)

    def test_release_gate_accepts_reasoned_not_applicable_but_rejects_bare_value(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        profile = self.task / ".monomind" / "workflow.md"
        resolved = profile.read_text(encoding="utf-8").replace(
            "UNRESOLVED", "approved value — evidence: README.md"
        )
        profile.write_text(
            resolved.replace(
                "- Runtime or smoke check: approved value — evidence: README.md",
                "- Runtime or smoke check: NOT_APPLICABLE",
            ),
            encoding="utf-8",
        )

        bare = self.check_contract("--gate", "release")
        self.assertNotEqual(bare.returncode, 0)
        self.assertIn("not applicable without a reason", bare.stderr)

        profile.write_text(
            profile.read_text(encoding="utf-8").replace(
                "- Runtime or smoke check: NOT_APPLICABLE",
                "- Runtime or smoke check: NOT_APPLICABLE — no runtime artifact is produced",
            ),
            encoding="utf-8",
        )
        reasoned = self.check_contract("--gate", "release")
        self.assertEqual(reasoned.returncode, 0, reasoned.stderr)
        self.assertIn("release-ready policy gate passed", reasoned.stdout)

    def test_build_gate_requires_a_real_owner_and_approval_record(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        profile = self.task / ".monomind" / "workflow.md"
        resolved = profile.read_text(encoding="utf-8").replace(
            "UNRESOLVED", "approved value — evidence: README.md"
        )
        profile.write_text(
            resolved.replace(
                "- Repository owner or project lead: approved value — evidence: README.md",
                "- Repository owner or project lead: NOT_APPLICABLE — no owner assigned",
            ),
            encoding="utf-8",
        )

        build = self.check_contract("--gate", "build")
        self.assertNotEqual(build.returncode, 0)
        self.assertIn("owner/lead approval field cannot be NOT_APPLICABLE", build.stderr)

    def test_apply_reports_reversed_markers_without_a_traceback(self) -> None:
        agents = self.task / "AGENTS.md"
        agents.write_text(
            "<!-- monomind-workflow:end -->\n<!-- monomind-workflow:start -->\n",
            encoding="utf-8",
        )

        result = self.adopt(self.task)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reversed Monomind managed markers", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_apply_refuses_main(self) -> None:
        destination = self.primary / ".agents" / "skills" / "monomind-workflow"
        destination.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SOURCE, destination)

        result = self.adopt(self.primary)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to adopt on main", result.stderr)
        self.assertFalse((self.primary / "AGENTS.md").exists())
        self.assertFalse((self.primary / ".monomind").exists())

    def test_apply_refuses_primary_checkout_even_on_a_task_branch(self) -> None:
        destination = self.primary / ".agents" / "skills" / "monomind-workflow"
        destination.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SOURCE, destination)
        run("git", "switch", "-c", "chore/primary-checkout", cwd=self.primary)

        result = self.adopt(self.primary)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to adopt in the primary checkout", result.stderr)
        self.assertFalse((self.primary / "AGENTS.md").exists())

    def test_apply_refuses_detached_head(self) -> None:
        run("git", "checkout", "--detach", cwd=self.task)

        result = self.adopt(self.task)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires a named task branch", result.stderr)
        self.assertFalse((self.task / "AGENTS.md").exists())

    def test_apply_refuses_an_ignored_project_skill(self) -> None:
        (self.task / ".gitignore").write_text(".agents/\n", encoding="utf-8")

        result = self.adopt(self.task)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project workflow skill is ignored", result.stderr)
        self.assertFalse((self.task / "AGENTS.md").exists())

    def test_approved_alternate_remote_base_is_used_and_persisted(self) -> None:
        run('git', 'remote', 'add', 'upstream', str(self.remote), cwd=self.task)
        run('git', 'push', 'upstream', 'HEAD:develop', cwd=self.task)
        run('git', 'fetch', 'upstream', cwd=self.task)
        result = self.adopt(self.task, '--base', 'upstream/develop')
        self.assertEqual(result.returncode, 0, result.stderr)
        profile = (self.task / '.monomind/workflow.md').read_text()
        self.assertIn('- Authoritative base branch: `upstream/develop`', profile)
        result = run('python3', str(self.installed_script), 'preflight', '--repo', str(self.task), check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('upstream/develop', result.stdout)
        mismatch = self.adopt(self.task, '--base', 'origin/main')
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn('conflicts with the recorded', mismatch.stderr)

    def test_protected_alternate_base_branch_is_refused(self) -> None:
        run('git', 'push', 'origin', 'HEAD:develop', cwd=self.task)
        run('git', 'fetch', 'origin', cwd=self.task)
        run('git', 'branch', '-m', 'develop', cwd=self.task)
        result = self.adopt(self.task, '--base', 'origin/develop')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('refusing to adopt on develop', result.stderr)

    def test_integration_passes_without_release_policy(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        profile = self.task / '.monomind/workflow.md'
        text = profile.read_text().replace('UNRESOLVED', 'approved value — evidence: README.md')
        text = text.replace('- Release command or pipeline: approved value — evidence: README.md',
                            '- Release command or pipeline: UNRESOLVED')
        profile.write_text(text)
        self.assertEqual(self.check_contract('--gate', 'integration').returncode, 0)
        self.assertNotEqual(self.check_contract('--gate', 'release').returncode, 0)

    def test_blank_owner_fails_through_cli(self) -> None:
        self.assertEqual(self.adopt(self.task).returncode, 0)
        profile = self.task / '.monomind/workflow.md'
        text = profile.read_text().replace('UNRESOLVED', 'approved value — evidence: README.md')
        text = text.replace('- Repository owner or project lead: approved value — evidence: README.md',
                            '- Repository owner or project lead:\n\n## Unrelated heading')
        profile.write_text(text)
        for gate in ('build', 'integration', 'release'):
            result = self.check_contract('--gate', gate)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Repository owner or project lead [empty]', result.stderr)


if __name__ == "__main__":
    unittest.main()
