#!/usr/bin/env python3
"""Nudge opted-in repositories using the plugin's trusted shared policy reader."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Import only the trusted plugin bundle, never Python from the target repository.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/monomind-workflow/scripts'))
from policy import PolicyError, issues, parse_fields

PROFILE_RELATIVE_PATH = Path('.monomind/workflow.md')


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
        result = subprocess.run(['git', '-C', cwd, 'rev-parse', '--show-toplevel'],
                                capture_output=True, text=True, timeout=2, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def read_local(repo: Path, relative: str | Path) -> str:
    path = repo / relative
    if not path.resolve().is_relative_to(repo.resolve()):
        raise PolicyError(f'{relative} resolves outside the repository')
    return path.read_text(encoding='utf-8')


def onboarding_settings(repo: Path) -> tuple[bool, str]:
    """A profile/managed policy opts in; an explicit setting can dismiss the nudge."""
    setting_path = repo / '.monomind/onboarding.json'
    if setting_path.is_file():
        settings = json.loads(read_local(repo, '.monomind/onboarding.json'))
        if not isinstance(settings, dict) or not isinstance(settings.get('enabled'), bool):
            raise PolicyError('onboarding.json requires a boolean enabled value')
        if not settings['enabled']:
            return False, 'build'
        gate = settings.get('gate', 'build')
        if not isinstance(gate, str) or gate not in {'build', 'integration', 'release'}:
            raise PolicyError('onboarding.json gate must be build, integration, or release')
        return True, gate
    if (repo / PROFILE_RELATIVE_PATH).is_file():
        return True, 'build'
    for name in ('AGENTS.override.md', 'AGENTS.md'):
        if (repo / name).is_file():
            text = read_local(repo, name)
            if text.strip():
                return '<!-- monomind-workflow:start -->' in text, 'build'
    return False, 'build'


def profile_issues(repo: Path, gate: str = 'build') -> tuple[str, list[str]]:
    if not (repo / PROFILE_RELATIVE_PATH).is_file():
        return 'profile is absent', []
    fields = parse_fields(read_local(repo, PROFILE_RELATIVE_PATH))
    pending = issues(fields, gate)
    if pending:
        return f'{len(pending)} {gate} profile field(s) need resolution', [label for label, _ in pending]
    return '', []


def onboarding_context(reason: str, fields: list[str], gate: str = 'build') -> str:
    preview = ', '.join(fields[:6])
    if len(fields) > 6:
        preview += f', and {len(fields) - 6} more'
    return (
        f'Monomind {gate} onboarding: {reason}. {preview}. '
        'For work crossing this boundary, invoke $monomind-onboarding and ask the repository owner '
        'only for missing policy decisions. Never guess policy. Read-only work may continue. '
        'This reminder grants no mutation authority. Resolve this boundary only; reuse approved facts.'
    )


def main() -> int:
    repo = repository_root(read_payload().get('cwd'))
    if repo is None:
        return 0
    try:
        enabled, gate = onboarding_settings(repo)
        if not enabled:
            return 0
        reason, fields = profile_issues(repo, gate)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, PolicyError) as error:
        reason, fields, gate = f'cannot validate local policy: {error}', [], 'build'
    if reason:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'SessionStart', 'additionalContext': onboarding_context(reason, fields, gate),
        }}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
