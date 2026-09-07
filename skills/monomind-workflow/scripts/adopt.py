#!/usr/bin/env python3
"""Install and verify Monomind's persistent repository workflow contract."""

from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

from policy import PolicyError, issues, parse_fields, required_fields


START_MARKER = "<!-- monomind-workflow:start -->"
END_MARKER = "<!-- monomind-workflow:end -->"
POLICY_BLOCK = f"""{START_MARKER}
## Monomind software factory

- Before any newly started feature, fix, refactor, migration, or other code-changing task, invoke the installed `monomind-workflow` skill (in Codex: `$monomind-workflow`) and complete its Isolate gate before editing.
- Implementation must use a task-owned linked Git worktree from the profile's authoritative base. Never implement on `main` or the configured base branch, and never reuse another task's worktree.
- Resolve `UNRESOLVED` fields required by the requested boundary with the repository owner, project lead, or named delegate through `monomind-onboarding`. Reuse existing approvals; agents may establish mechanical facts but must not invent policy. Unrelated deployment fields do not block implementation or integration.
- Before Build, run `adopt.py check --gate build --repo <repository>`; before integration or merge, use `--gate integration`; before deployment, migration execution, or release, use `--gate release`. Resolve only the requested boundary's missing policy. Reuse results until policy, tools, revision, or environment changes invalidate them.
- In side-effecting workflows, actions or boundaries own policy and why/when; services or capabilities own reusable how through explicit inputs and structured returns. Do not extract pass-through services for ceremony.
- For a visible UI change, capture matched before/after evidence and include a PR-ready comparison. Invoke the installed `monomind-before-after` skill (in Codex: `$monomind-before-after`) when available.
- Read `.monomind/workflow.md` for project-native collaboration, integration, testing, CI/CD, release, evidence, continuity, shared-resource, and authority rules.
{END_MARKER}"""

PROFILE_RELATIVE_PATH = Path(".monomind/workflow.md")
PROJECT_SKILL_LOCATIONS = (
    Path(".agents/skills/monomind-workflow/SKILL.md"),
    Path(".claude/skills/monomind-workflow/SKILL.md"),
    Path(".factory/skills/monomind-workflow/SKILL.md"),
)

class AdoptionError(RuntimeError):
    """A safe adoption precondition or contract check failed."""


def read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as error:
        raise AdoptionError(f"{path} is not valid UTF-8") from error


def write_utf8(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def newline_for(text: str) -> str:
    without_crlf = text.replace("\r\n", "")
    return "\r\n" if "\r\n" in text and "\n" not in without_crlf else "\n"


def rendered_policy(text: str) -> str:
    return POLICY_BLOCK.replace("\n", newline_for(text))


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise AdoptionError(detail)
    return result


def repository_root(candidate: str) -> Path:
    path = Path(candidate).expanduser().resolve()
    result = run_git(path, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def require_path_inside(repo: Path, path: Path, label: str) -> None:
    try:
        path.resolve().relative_to(repo)
    except ValueError as error:
        raise AdoptionError(f"{label} resolves outside {repo}: {path}") from error


def require_not_ignored(repo: Path, path: Path, label: str) -> None:
    relative = path.relative_to(repo)
    ignored = run_git(repo, "check-ignore", "--quiet", "--", str(relative), check=False)
    if ignored.returncode == 0:
        raise AdoptionError(f"{label} is ignored and would not establish shared policy: {relative}")


def instruction_path(repo: Path, override: str | None) -> Path:
    if override:
        candidate = Path(override)
        path = repo / candidate if not candidate.is_absolute() else candidate
        path = path.absolute()
        if path.parent != repo or path.name not in {"AGENTS.md", "AGENTS.override.md"}:
            raise AdoptionError(
                "--agents-file must name root AGENTS.md or root AGENTS.override.md"
            )
        require_path_inside(repo, path, "instruction file")
        return path

    override_path = repo / "AGENTS.override.md"
    require_path_inside(repo, override_path, "instruction file")
    path = (
        override_path
        if override_path.exists() and read_utf8(override_path).strip()
        else repo / "AGENTS.md"
    )
    require_path_inside(repo, path, "instruction file")
    return path


def require_project_skill(repo: Path) -> Path:
    escaped: list[Path] = []
    for relative in PROJECT_SKILL_LOCATIONS:
        candidate = repo / relative
        if candidate.is_file():
            try:
                candidate.resolve().relative_to(repo)
            except ValueError:
                escaped.append(relative)
                continue
            require_not_ignored(repo, candidate, "project workflow skill")
            return candidate
    if escaped:
        choices = ", ".join(str(path) for path in escaped)
        raise AdoptionError(
            "project workflow skill resolves outside the repository; reinstall with --copy: "
            + choices
        )
    choices = ", ".join(str(path) for path in PROJECT_SKILL_LOCATIONS)
    raise AdoptionError(
        "monomind-workflow is not installed in this repository; expected one of: " + choices
    )


def profile_template_path() -> Path:
    path = Path(__file__).resolve().parents[1] / "assets" / "workflow-profile.md"
    if not path.is_file():
        raise AdoptionError(f"bundled profile template is missing: {path}")
    return path


def parse_profile_fields(text: str, path: Path) -> dict[str, str]:
    try:
        return parse_fields(text)
    except PolicyError as error:
        raise AdoptionError(f'{path}: {error}') from error


def readiness_issues(profile: Path, gate: str) -> list[tuple[str, str]]:
    return issues(parse_profile_fields(read_utf8(profile), profile), gate)


def format_issues(issues: list[tuple[str, str]]) -> str:
    return "\n".join(f"  - {label} [{reason}]" for label, reason in issues)


def validate_markers(text: str, path: Path) -> tuple[int, int] | None:
    starts = text.count(START_MARKER)
    ends = text.count(END_MARKER)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise AdoptionError(
            f"{path} has malformed or duplicate Monomind managed markers; repair them manually"
        )
    start = text.index(START_MARKER)
    end_start = text.find(END_MARKER, start + len(START_MARKER))
    if end_start < 0:
        raise AdoptionError(
            f"{path} has reversed Monomind managed markers; repair them manually"
        )
    end = end_start + len(END_MARKER)
    return start, end


def merged_policy(text: str, path: Path) -> str:
    block = rendered_policy(text)
    span = validate_markers(text, path)
    if span:
        start, end = span
        return text[:start] + block + text[end:]

    newline = newline_for(text)
    separator = ""
    if text:
        separator = newline if text.endswith(("\n", "\r")) else newline * 2
    return text + separator + block + newline


def print_diff(path: Path, before: str, after: str) -> None:
    relative = str(path)
    diff = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=relative,
        tofile=relative,
    )
    sys.stdout.writelines(diff)


def authoritative_base(repo: Path, override: str | None = None) -> str:
    profile = repo / PROFILE_RELATIVE_PATH
    require_path_inside(repo, profile, 'workflow profile')
    fields = parse_profile_fields(read_utf8(profile), profile) if profile.is_file() else {}
    recorded = fields.get('Authoritative base branch')
    if recorded:
        match = re.match(r'^`?([^`\s]+)`?(?:\s.*)?$', recorded)
        base = match.group(1) if match else ''
        if override and override != base:
            raise AdoptionError('--base conflicts with the recorded authoritative base; update approved policy first')
    else:
        base = override or 'origin/main'
    if '/' not in base or base.startswith(('refs/', '-')):
        raise AdoptionError('authoritative base must be a remote-tracking branch such as origin/main')
    if run_git(repo, 'check-ref-format', f'refs/remotes/{base}', check=False).returncode:
        raise AdoptionError(f'invalid authoritative base: {base}')
    remote = base.split('/', 1)[0]
    if run_git(repo, 'config', '--get', f'remote.{remote}.url', check=False).returncode:
        raise AdoptionError(f'{remote} is not configured')
    return base


def preflight(repo: Path, base_override: str | None = None) -> str:
    require_project_skill(repo)
    base_name = authoritative_base(repo, base_override)

    branch = run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    branch_name = branch.stdout.strip()
    if branch.returncode or not branch_name:
        raise AdoptionError("workflow preflight requires a named task branch, not detached HEAD")
    if branch_name in {"main", base_name.split('/', 1)[1]}:
        raise AdoptionError(
            f"refusing to adopt on {branch_name}; create a fresh task worktree from {base_name} first"
        )
    base = run_git(repo, "rev-parse", "--verify", f"refs/remotes/{base_name}^{{commit}}", check=False)
    if base.returncode:
        raise AdoptionError(f"{base_name} is not available locally; fetch its remote first")

    git_dir = Path(run_git(repo, "rev-parse", "--git-dir").stdout.strip())
    common_dir = Path(run_git(repo, "rev-parse", "--git-common-dir").stdout.strip())
    git_dir = git_dir if git_dir.is_absolute() else repo / git_dir
    common_dir = common_dir if common_dir.is_absolute() else repo / common_dir
    if git_dir.resolve() == common_dir.resolve():
        raise AdoptionError("refusing to adopt in the primary checkout; use a linked task worktree")

    based_on_main = run_git(
        repo,
        "merge-base",
        "--is-ancestor",
        f"refs/remotes/{base_name}",
        "HEAD",
        check=False,
    )
    if based_on_main.returncode:
        raise AdoptionError(f"the current task branch is not based on the available {base_name}")

    print(f"OK: task workspace {repo} is isolated on {branch_name} from {base_name}")
    return base_name


def apply_contract(repo: Path, agents_file: str | None, dry_run: bool, base: str | None = None) -> None:
    base_name = preflight(repo, base)
    target = instruction_path(repo, agents_file)
    require_not_ignored(repo, target, "active repository instructions")
    before = read_utf8(target) if target.exists() else ""
    after = merged_policy(before, target)

    profile = repo / PROFILE_RELATIVE_PATH
    require_path_inside(repo, profile, "workflow profile")
    require_not_ignored(repo, profile, "workflow profile")
    if profile.exists() and not profile.is_file():
        raise AdoptionError(f"workflow profile path is not a file: {profile}")
    if profile.exists():
        read_utf8(profile)
    profile_template = profile_template_path()
    profile_after = read_utf8(profile_template)
    profile_after = profile_after.replace('`origin/main`', f'`{base_name}`')

    if dry_run:
        if before != after:
            print_diff(target, before, after)
        if not profile.exists():
            print_diff(profile, "", profile_after)
        if before == after and profile.exists():
            print("OK: adoption contract is already current")
        return

    if before != after:
        target.parent.mkdir(parents=True, exist_ok=True)
        write_utf8(target, after)
        print(f"UPDATED: {target}")
    else:
        print(f"OK: managed policy is current in {target}")

    if profile.exists():
        print(f"PRESERVED: existing {profile}")
    else:
        profile.parent.mkdir(parents=True, exist_ok=True)
        write_utf8(profile, profile_after)
        print(f"CREATED: {profile}")


def check_contract(
    repo: Path,
    agents_file: str | None,
    gate: str | None = None,
) -> None:
    skill = require_project_skill(repo)
    target = instruction_path(repo, agents_file)
    require_not_ignored(repo, target, "active repository instructions")
    if not target.is_file():
        raise AdoptionError(f"active repository instructions are missing: {target}")

    text = read_utf8(target)
    span = validate_markers(text, target)
    if not span:
        raise AdoptionError(f"managed Monomind policy is missing from {target}")
    start, end = span
    if text[start:end] != rendered_policy(text):
        raise AdoptionError(
            f"managed Monomind policy in {target} has drifted; rerun the apply command"
        )

    profile = repo / PROFILE_RELATIVE_PATH
    require_path_inside(repo, profile, "workflow profile")
    require_not_ignored(repo, profile, "workflow profile")
    if not profile.is_file():
        raise AdoptionError(f"workflow profile is missing: {profile}")

    # A structural check can report an incomplete profile; readiness below blocks it.
    fields = parse_profile_fields(read_utf8(profile), profile)
    if fields.get('Authoritative base branch') and not any(
        label == 'Authoritative base branch' for label, _ in issues(fields, 'build')
    ):
        authoritative_base(repo)

    print(f"OK: project skill found at {skill}")
    print(f"OK: managed policy is current in {target}")
    print(f"OK: workflow profile exists at {profile}")

    pending = readiness_issues(profile, gate or "release")
    if gate and pending:
        raise AdoptionError(
            f"{gate}-ready policy gate failed. The repository owner, project lead, or "
            "explicitly named delegate must define or approve these project fields:\n"
            f"{format_issues(pending)}\nRun the monomind-onboarding skill, update "
            ".monomind/workflow.md, and rerun this gate."
        )
    if gate:
        required_count = len(required_fields(gate, fields))
        print(f"OK: {gate}-ready policy gate passed ({required_count} required fields resolved)")
    elif pending:
        print(
            "WARN: workflow profile is structurally installed but not Release-ready; "
            f"{len(pending)} current field(s) need resolution:\n{format_issues(pending)}"
        )
        print(
            "NEXT: the repository owner or project lead should run monomind-onboarding, "
            "then use the build, integration, or release gate required for that work."
        )
    else:
        print("OK: workflow profile contains no unresolved required policy fields")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adopt, verify, or preflight the Monomind repository workflow."
    )
    parser.add_argument("command", choices=("apply", "check", "preflight"))
    parser.add_argument("--repo", default=".", help="Target repository or a path inside it")
    parser.add_argument('--base', help='Approved remote/base for initial apply or preflight; cannot override recorded policy')
    parser.add_argument(
        "--agents-file",
        help="Project-relative AGENTS.md or AGENTS.override.md to manage",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="For apply only, print the proposed diff without writing",
    )
    parser.add_argument(
        "--gate",
        choices=("build", "integration", "release"),
        help="For check only, fail unless fields required for that readiness level are resolved",
    )
    args = parser.parse_args()
    if args.dry_run and args.command != "apply":
        parser.error("--dry-run is valid only with apply")
    if args.gate and args.command != "check":
        parser.error("--gate is valid only with check")
    if args.base and args.command == 'check':
        parser.error('--base is only for initial apply or preflight')
    return args


def main() -> int:
    args = parse_args()
    try:
        repo = repository_root(args.repo)
        if args.command == "apply":
            apply_contract(repo, args.agents_file, args.dry_run, args.base)
        elif args.command == "check":
            check_contract(repo, args.agents_file, args.gate)
        else:
            preflight(repo, args.base)
    except (AdoptionError, PolicyError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
