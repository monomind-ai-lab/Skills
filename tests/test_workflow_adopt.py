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


if __name__ == "__main__":
    unittest.main()
