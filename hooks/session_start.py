#!/usr/bin/env python3
"""Add first-run onboarding context when a repository profile is incomplete."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


PROFILE_RELATIVE_PATH = Path(".monomind/workflow.md")
PROFILE_FIELD_RE = re.compile(r"^- (?P<label>[^:\n]+):\s*(?P<value>.*)$", re.MULTILINE)
UNRESOLVED_RE = re.compile(r"\bUNRESOLVED\b", re.IGNORECASE)
EXPLICIT_NOT_APPLICABLE_RE = re.compile(
    r"^NOT_APPLICABLE\s*(?:—|–|-)\s*\S.+$",
    re.IGNORECASE,
)
NON_OPTIONAL_POLICY_FIELDS = {
    "Repository owner or project lead",
    "Approved policy decision-maker(s)",
    "Policy approval record and date",
}


def read_payload() -> dict[str, object]:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def repository_root(cwd: object) -> Path | None:
    if not isinstance(cwd, str) or not cwd:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def parse_fields(text: str) -> dict[str, str]:
    return {
        match.group("label").strip(): match.group("value").strip()
        for match in PROFILE_FIELD_RE.finditer(text)
    }


def invalid_value(label: str, value: str) -> bool:
    stripped = value.strip()
    if not stripped or UNRESOLVED_RE.search(stripped):
        return True
    upper = stripped.upper()
    if upper in {"N/A", "NA", "NOT APPLICABLE", "NOT_APPLICABLE"}:
        return True
    if upper.startswith(("N/A ", "NA ")):
        return True
    if upper.startswith("NOT_APPLICABLE") and not EXPLICIT_NOT_APPLICABLE_RE.match(stripped):
        return True
    return label in NON_OPTIONAL_POLICY_FIELDS and bool(
        EXPLICIT_NOT_APPLICABLE_RE.match(stripped)
    )


def template_fields() -> tuple[str, ...]:
    template = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "monomind-workflow"
        / "assets"
        / "workflow-profile.md"
    )
    try:
        return tuple(parse_fields(template.read_text(encoding="utf-8")))
    except OSError:
        return ()


def profile_issues(repo: Path) -> tuple[str, list[str]]:
    profile = repo / PROFILE_RELATIVE_PATH
    if not profile.is_file():
        return "profile is absent", []
    try:
        fields = parse_fields(profile.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return "profile cannot be read as UTF-8", []

    issues = [label for label, value in fields.items() if invalid_value(label, value)]
    issues.extend(label for label in template_fields() if label not in fields)
    deduplicated = list(dict.fromkeys(issues))
    if deduplicated:
        return f"{len(deduplicated)} profile field(s) need resolution", deduplicated
    return "", []


def onboarding_context(reason: str, fields: list[str]) -> str:
    preview = ", ".join(fields[:6])
    if len(fields) > 6:
        preview += f", and {len(fields) - 6} more"
    detail = f" Affected fields include: {preview}." if preview else ""
    return (
        f"Monomind repository onboarding is incomplete because the {reason}.{detail} "
        "Invoke the installed $monomind-onboarding skill for fields required by the "
        "requested boundary. Before Build, run the build readiness gate; before "
        "integration, merge, deployment, or release, resolve the full current profile "
        "and run the release gate. Inspect repository evidence first, then ask the "
        "repository owner, project lead, or explicitly named delegate only for policy "
        "decisions that evidence cannot establish. Preserve existing approved values. "
        "Never guess policy or treat this hook as authorization for repository or "
        "remote mutations. Read-only work may continue."
    )


def main() -> int:
    payload = read_payload()
    repo = repository_root(payload.get("cwd"))
    if repo is None:
        return 0
    reason, fields = profile_issues(repo)
    if not reason:
        return 0
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": onboarding_context(reason, fields),
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
