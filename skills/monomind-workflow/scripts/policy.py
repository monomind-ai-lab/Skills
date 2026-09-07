"""Versioned policy parsing shared by the standalone workflow and plugin hook.

Schema membership is code, not every bullet in a documentation template.
Unversioned profiles use the original fields; v2 adds integration as a boundary,
without adding required data to previously complete profiles.
"""
from __future__ import annotations

import re

SCHEMA_VERSION = 2
SUPPORTED_VERSIONS = {1, 2}
FIELD_RE = re.compile(r'^- (?P<label>[^:\r\n]+):[ \t]*(?P<value>[^\r\n]*)$')
UNRESOLVED_RE = re.compile(r'^UNRESOLVED\b', re.IGNORECASE)
NOT_APPLICABLE_RE = re.compile(r'^NOT_APPLICABLE\s*(?:—|–|-)\s*\S.*$', re.IGNORECASE)
NON_OPTIONAL_POLICY_FIELDS = {
    'Repository owner or project lead', 'Approved policy decision-maker(s)',
    'Policy approval record and date',
}
BUILD_REQUIRED_FIELDS = (
    'Repository owner or project lead', 'Approved policy decision-maker(s)',
    'Policy approval record and date', 'Task ownership and assignment source',
    'Parallel work and overlap coordination', 'Authoritative base branch',
    'Task isolation', 'Branch/worktree naming convention',
    'Canonical remote and change-request target', 'Environment setup',
    'Focused test', 'Full regression suite', 'Architecture and dependency direction',
    'Shared-resource isolation and allocation',
    'Authoritative project context and decision records',
    'Task and handoff location and required contents',
    'Actions agents may take without a new prompt', 'Actions requiring explicit user instruction',
)
INTEGRATION_REQUIRED_FIELDS = BUILD_REQUIRED_FIELDS + (
    'Profile maintainer and review trigger', 'Worktree cleanup authority',
    'Communication and escalation path', 'Integration strategy', 'History rewrite policy',
    'Type or compile check', 'Lint and format check', 'Build/package check',
    'Runtime or smoke check', 'Security and privacy', 'Data compatibility and migrations',
    'Performance or reliability budgets', 'Generated files and lockfiles',
    'Gitignored local artifact path', 'Test data and account policy',
    'UI/runtime targets and viewports', 'Sensitive surfaces that must not be captured',
    'Approved publication destinations',
    'How to verify a running service belongs to the current task',
    'Required change-description sections', 'Required CI gates and trigger conditions',
    'Human or automated reviewers', 'Blocking-finding policy',
    'CI retry, rerun, and override authority', 'Who may merge and under what instruction',
    'Context update triggers', 'Context freshness owner and review cadence',
    'Resumption verification',
)
RELEASE_REQUIRED_FIELDS = INTEGRATION_REQUIRED_FIELDS + (
    'Release environments and promotion path', 'Release command or pipeline',
    'Release owner and approver', 'Required release evidence',
    'Rollback or recovery procedure', 'Post-release verification and observation window',
    'Who may release and under what instruction',
)
GATES = {'build': BUILD_REQUIRED_FIELDS, 'integration': INTEGRATION_REQUIRED_FIELDS,
         'release': RELEASE_REQUIRED_FIELDS}


class PolicyError(ValueError):
    pass


def parse_fields(text: str) -> dict[str, str]:
    """Read single-line top-level fields, ignoring fenced examples."""
    fields: dict[str, str] = {}
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if marker:
            run, suffix = marker.groups()
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not suffix.strip():
                fence = None
            continue
        if fence is not None:
            continue
        match = FIELD_RE.fullmatch(line)
        if not match:
            continue
        label, value = match.group('label').strip(), match.group('value').strip()
        if label in fields:
            raise PolicyError(f'workflow profile has duplicate field label: {label}')
        fields[label] = value
    return fields


def required_fields(gate: str, fields: dict[str, str] | None = None) -> tuple[str, ...]:
    version = (fields or {}).get('Policy schema version', '1')
    if version not in {str(v) for v in SUPPORTED_VERSIONS}:
        raise PolicyError(f'unsupported policy schema version {version!r}; update the workflow/plugin together')
    if gate not in GATES:
        raise PolicyError(f'unknown readiness gate: {gate}')
    return GATES[gate]


def invalid_value(label: str, value: str) -> str | None:
    value = value.strip()
    if not value:
        return 'empty'
    if UNRESOLVED_RE.search(value):
        return 'UNRESOLVED'
    upper = value.upper()
    if upper in {'N/A', 'NA', 'NOT APPLICABLE', 'NOT_APPLICABLE'}:
        return 'not applicable without a reason'
    if upper.startswith(('N/A ', 'NA ')):
        return 'use NOT_APPLICABLE with a reason'
    if upper.startswith('NOT_APPLICABLE'):
        if not NOT_APPLICABLE_RE.fullmatch(value):
            return 'NOT_APPLICABLE without a reason'
        if label in NON_OPTIONAL_POLICY_FIELDS:
            return 'owner/lead approval field cannot be NOT_APPLICABLE'
    return None


def issues(fields: dict[str, str], gate: str) -> list[tuple[str, str]]:
    result = []
    for label in required_fields(gate, fields):
        reason = invalid_value(label, fields[label]) if label in fields else 'missing'
        if reason:
            result.append((label, reason))
    return result
