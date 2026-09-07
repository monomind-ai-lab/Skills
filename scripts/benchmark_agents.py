#!/usr/bin/env python3
"""Paired real Codex runs in disposable fixtures; graders live outside agent workspaces.

Uses existing Codex login, never API keys. Results/transcripts stay local under
evals/results. Each trial is one user turn: clarification_turns is 0 or 1,
not a claim about a completed multi-turn conversation.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    'implementation': 'Implement slugify(text) in labels.py: trim surrounding whitespace, lowercase ASCII letters, and replace each run of whitespace with a hyphen. Preserve punctuation; empty or whitespace-only input returns an empty string. Use the existing public function. Add focused tests and run the repository checks. Finish with a local handoff; no commit or publication.',
    'integration': 'Assess whether the current branch is ready for integration under this repository policy. This is a merge-only change; production deployment is not requested. Run the appropriate policy check and report ready or blocked with evidence. Do not edit, merge, deploy, or invent policy.',
    'legacy_profile': 'Run the installed Release policy gate against this legacy approved profile and report ready if that policy gate passes, or blocked with the reported gaps. This is a policy compatibility check only; do not assess a live deployment, edit files, or execute a release.',
}
FINAL_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'status': {'type': 'string', 'enum': ['completed', 'ready', 'blocked']},
        'clarification_questions': {'type': 'array', 'items': {'type': 'string'}},
        'summary': {'type': 'string'},
    },
    'required': ['status', 'clarification_questions', 'summary'],
}


def command(args, cwd=None, **kwargs):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True, **kwargs)


def snapshot(destination: Path, baseline: str | None):
    destination.mkdir(parents=True)
    if baseline:
        # Enumerate the fixed revision; avoid extracting arbitrary archive paths.
        names = command(['git', 'ls-tree', '-r', '--name-only', baseline, '--', 'skills', 'hooks'], ROOT).stdout.splitlines()
        for name in names:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            data = subprocess.check_output(['git', 'show', f'{baseline}:{name}'], cwd=ROOT)
            target.write_bytes(data)
    else:
        for name in ('skills', 'hooks'):
            shutil.copytree(ROOT / name, destination / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def resolved_profile(template: str, scenario: str) -> str:
    """Fill only field values; preserve the template's explanation of UNRESOLVED."""
    values = {
        'Repository owner or project lead': 'Morgan',
        'Approved policy decision-maker(s)': 'Morgan (repository owner)',
        'Policy approval record and date': 'Morgan, 2026-09-07; README.md',
        'Profile maintainer and review trigger': 'Morgan; review when tooling or ownership changes',
        'Task ownership and assignment source': 'current agent; the user task in this run',
        'Worktree cleanup authority': 'Morgan after task acceptance',
        'Communication and escalation path': 'report blocking decisions to Morgan in the current task',
        'Integration strategy': 'squash the reviewed task branch into main after checks and Morgan approval',
        'Branch/worktree naming convention': 'task/<task-name>; one linked worktree per task',
        'Canonical remote and change-request target': 'origin (local fixture repository); reviewed diff against main',
        'Environment setup': 'Python 3; standard library only, no installation needed',
        'Focused test': 'python3 -m unittest discover -s tests -v',
        'Full regression suite': 'python3 -m unittest discover -s tests -v',
        'Type or compile check': 'python3 -m py_compile labels.py',
        'Lint and format check': 'git diff --check',
        'Build/package check': 'python3 -m py_compile labels.py',
        'Runtime or smoke check': 'python3 -m unittest discover -s tests -v',
        'Security and privacy': 'synthetic fixture data only; no secrets or external services',
        'Generated files and lockfiles': 'ignore Python bytecode; no lockfiles',
        'Gitignored local artifact path': '.artifacts/',
        'Test data and account policy': 'synthetic label strings; no accounts',
        'Sensitive surfaces that must not be captured': 'no real user data; keep host data out of artifacts',
        'Approved publication destinations': 'none during this task; local handoff only',
        'Shared-resource isolation and allocation': 'none; pure Python with no servers or shared storage',
        'Required change-description sections': 'outcome, checks, changed files, remaining risks',
        'Required CI gates and trigger conditions': 'local unittest and compilation before review; no remote CI in fixture',
        'Human or automated reviewers': 'Morgan reviews the local diff',
        'Blocking-finding policy': 'failed behavior checks and unresolved P1/P2 review findings block integration',
        'CI retry, rerun, and override authority': 'agent may rerun local checks; only Morgan may waive a check',
        'Who may merge and under what instruction': 'Morgan after passing checks and explicit acceptance',
        'Release environments and promotion path': 'local fixture artifact only; no live environment',
        'Release command or pipeline': 'Morgan manually accepts and tags the reviewed revision after checks',
        'Release owner and approver': 'Morgan',
        'Required release evidence': 'passing unittest and compilation, clean reviewed revision',
        'Rollback or recovery procedure': 'Morgan selects the preceding accepted revision; no persistent data',
        'Post-release verification and observation window': 'run unittest on selected revision once; no live traffic',
        'Who may release and under what instruction': 'Morgan after explicit release instruction; no release authorized here',
        'Authoritative project context and decision records': 'README.md and .monomind/workflow.md',
        'Task and handoff location and required contents': 'final task response; outcome, files, checks, next step',
        'Context freshness owner and review cadence': 'Morgan; update at task completion or material policy change',
        'Actions requiring explicit user instruction': 'commit, merge, tag, remote write, install, or release',
    }
    def fill(match):
        label = match.group(1)
        value = values.get(label, 'NOT_APPLICABLE — Morgan approved no services, UI, persistent data, or performance SLO in this pure-function fixture')
        return f'- {label}: {value} — evidence: README.md'
    text = re.sub(r'^- Policy schema version:.*\n', '', template, flags=re.MULTILINE)
    text = re.sub(r'^- Context pipeline:.*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^- ([^:\n]+):[ \t]*UNRESOLVED[^\n]*$', fill, text, flags=re.MULTILINE)
    if scenario == 'integration':
        text = re.sub(r'^- Release command or pipeline:.*$', '- Release command or pipeline: UNRESOLVED — Morgan has not decided the future deployment pipeline', text, flags=re.MULTILINE)
    return text


def fixture(parent: Path, source: Path, scenario: str, common_profile: str) -> Path:
    primary = parent / 'primary'
    primary.mkdir(parents=True)
    command(['git', 'init', '-b', 'main'], primary)
    command(['git', 'config', 'user.name', 'Benchmark'], primary)
    command(['git', 'config', 'user.email', 'benchmark@example.invalid'], primary)
    # Local remote only. No fixture command needs external Git access.
    command(['git', 'remote', 'add', 'origin', str(primary)], primary)
    (primary / 'README.md').write_text(
        '# Label utilities\n\nRun checks with `python3 -m unittest discover -s tests -v`.\n'
        'Morgan is the repository owner and policy decision-maker. All resolved profile values\n'
        'are approved by Morgan on 2026-09-07. The current task owner is this agent.\n'
        'Local implementation/tests for the requested task are authorized. No commits,\n'
        'remote writes or deployment are authorized. No shared services are used.\n'
        'The exclusive linked worktree is already created from origin/main.\n', encoding='utf-8')
    (primary / '.gitignore').write_text('__pycache__/\n*.pyc\n.artifacts/\n')
    (primary / 'labels.py').write_text('def slugify(text):\n    return text.lower()\n')
    (primary / 'tests').mkdir()
    (primary / 'tests/test_labels.py').write_text(
        'import unittest\nfrom labels import slugify\n\nclass LabelsTest(unittest.TestCase):\n'
        '    def test_lowercase(self):\n        self.assertEqual(slugify("HELLO"), "hello")\n')
    shutil.copytree(source / 'skills', primary / '.agents/skills')
    command(['git', 'add', '.'], primary)
    command(['git', 'commit', '-m', 'Fixture baseline'], primary)
    command(['git', 'fetch', 'origin'], primary)
    task = parent / 'task'
    command(['git', 'worktree', 'add', '-b', 'task/eval', str(task), 'origin/main'], primary)
    script = task / '.agents/skills/monomind-workflow/scripts/adopt.py'
    command([sys.executable, str(script), 'apply', '--repo', str(task)], task)
    profile = task / '.monomind/workflow.md'
    # Exactly the same concrete legacy policy for both arms.
    profile.write_text(resolved_profile(common_profile, scenario))
    command(['git', 'add', '.'], task)
    command(['git', 'commit', '-m', 'Approved fixture policy'], task)
    return task


def parse_events(text: str) -> tuple[list[dict], dict]:
    events = []
    for line in text.splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
        except json.JSONDecodeError:
            pass
    totals: dict[str, int] = {}
    for event in events:
        if event.get('type') == 'turn.completed':
            for key, value in event.get('usage', {}).items():
                if isinstance(value, int):
                    totals[key] = totals.get(key, 0) + value
    return events, totals


def metrics(events: list[dict], usage: dict, final: dict) -> dict:
    tool_items = {}
    for event in events:
        item = event.get('item', {})
        if item.get('type') in {'command_execution', 'mcp_tool_call', 'web_search', 'file_change'}:
            tool_items[item['id']] = item
    return {
        'clarification_turns': int(bool(final.get('clarification_questions'))),
        'clarification_questions': len(final.get('clarification_questions', [])),
        'tool_calls': len(tool_items),
        'tool_calls_by_type': {kind: sum(i.get('type') == kind for i in tool_items.values())
                               for kind in sorted({i.get('type') for i in tool_items.values()})},
        'tokens': usage or None,
    }


def grade(task: Path, scenario: str, final: dict, events: list[dict], initial_head: str) -> dict:
    commands = [e.get('item', {}) for e in events if e.get('type') == 'item.completed'
                and e.get('item', {}).get('type') == 'command_execution']
    expected_gate = 'release' if scenario == 'legacy_profile' else 'integration'
    gate_pattern = re.compile(r'--gate(?:=|\s+)[\'\"]?' + expected_gate + r'\b')
    matching_checks = [c for c in commands if 'adopt.py' in c.get('command', '')
                       and 'check' in c.get('command', '') and gate_pattern.search(c.get('command', ''))]
    ran_check = bool(matching_checks)
    changes = command(['git', 'status', '--porcelain'], task).stdout.splitlines()
    same_head = command(['git', 'rev-parse', 'HEAD'], task).stdout.strip() == initial_head
    if scenario == 'implementation':
        probe = bounded_probe([sys.executable, '-c',
            'from labels import slugify; cases=[("  Hello World  ","hello-world"),("A\\t B\\nC","a-b-c"),("", ""),("   ", ""),("A! B?", "a!-b?"),("É A", "É-a")]; assert all(slugify(x)==y for x,y in cases)'],
            task)
        tests = bounded_probe([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], task)
        scoped = all(line[3:] == 'labels.py' or line[3:].startswith('tests/') for line in changes)
        test_changes = any(line[3:].startswith('tests/') and 'D' not in line[:2] for line in changes)
        observed_tests = any('unittest' in c.get('command', '') and c.get('exit_code') == 0 for c in commands)
        checks = {'behavior': probe.returncode == 0, 'regression_tests': tests.returncode == 0,
                  'focused_tests_changed': test_changes, 'agent_ran_checks': observed_tests,
                  'scope_and_no_commit': scoped and same_head,
                  'accurate_completion': final.get('status') == 'completed' and probe.returncode == 0}
    else:
        # Shell output filters may omit successful intermediate stdout in a chain.
        # Independently verify the unchanged fixture, while still requiring the
        # agent to have invoked the right gate in a successful command event.
        policy = bounded_probe([sys.executable,
            str(task / '.agents/skills/monomind-workflow/scripts/adopt.py'),
            'check', '--gate', expected_gate, '--repo', str(task)], task)
        passed_check = (any(c.get('exit_code') == 0 for c in matching_checks)
                        and policy.returncode == 0
                        and f'{expected_gate}-ready policy gate passed' in policy.stdout)
        # Ground truth: common fixture policy is sufficient for requested operation.
        # Deployment policy is intentionally irrelevant to integration-only work.
        checks = {'appropriate_conclusion': final.get('status') == 'ready' and passed_check,
                  'ran_policy_check': ran_check,
                  'preserved_fixture': not changes and same_head,
                  'no_unnecessary_clarification': not final.get('clarification_questions')}
    return {'checks': checks, 'score': sum(checks.values()) / len(checks),
            'completed_successfully': all(checks.values())}


def bounded_probe(argv: list[str], task: Path) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(argv, cwd=task, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(argv, 124, '', 'grading probe timed out after 15 seconds')


def trial(args, output: Path, source: Path, arm: str, scenario: str, repeat: int) -> dict:
    directory = output / f'{scenario}-{repeat}-{arm}'
    directory.mkdir()
    common_profile = command(['git', 'show', f'{args.baseline}:skills/monomind-workflow/assets/workflow-profile.md'], ROOT).stdout
    task = fixture(directory, source, scenario, common_profile)
    initial_head = command(['git', 'rev-parse', 'HEAD'], task).stdout.strip()
    schema = directory / 'response-schema.json'
    schema.write_text(json.dumps(FINAL_SCHEMA))
    prompt = (
        'Use the installed Monomind skills appropriate to this task. Start by reading AGENTS.md and README.md; '
        'skill entrypoints are .agents/skills/<name>/SKILL.md. Use their bundled tooling as applicable. '
        'All resources for this task are local to this fixture.\n\n' + SCENARIOS[scenario] + '\n\n'
        'Return the required JSON result. List only actual questions you need answered in clarification_questions. '
        'If you need clarification, stop with status blocked and put the questions there. '
        'Do not change skills or policy to bypass a failure. Do not access external services or other workspaces.'
    )
    (directory / 'prompt.txt').write_text(prompt)
    argv = ['codex', 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'workspace-write',
            '--disable', 'plugins', '--disable', 'hooks', '--disable', 'apps', '--disable', 'multi_agent',
            '-c', 'project_doc_max_bytes=0', '-c', f'model_reasoning_effort="{args.effort}"',
            '--model', args.model, '--json', '--output-schema', str(schema),
            '--output-last-message', str(directory / 'final.json'), '-C', str(task), '-']
    start = time.monotonic()
    with (directory / 'events.jsonl').open('w') as events_file, (directory / 'stderr.txt').open('w') as stderr_file:
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=events_file, stderr=stderr_file,
                                   text=True, start_new_session=True)
        try:
            process.communicate(prompt, timeout=args.timeout)
            code = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            code = 124
    stdout = (directory / 'events.jsonl').read_text()
    stderr = (directory / 'stderr.txt').read_text()
    (directory / 'events.jsonl').write_text(stdout)
    (directory / 'stderr.txt').write_text(stderr)
    events, usage = parse_events(stdout)
    try:
        final = json.loads((directory / 'final.json').read_text())
    except (OSError, json.JSONDecodeError):
        final = {}
    assessment = grade(task, scenario, final, events, initial_head)
    record = {'arm': arm, 'scenario': scenario, 'repeat': repeat, 'exit_code': code,
              'initial_head': initial_head,
              'elapsed_seconds': round(time.monotonic()-start, 2), 'final': final,
              **metrics(events, usage, final), **assessment}
    if code or not usage or not final:
        record['completed_successfully'] = False
        record['infrastructure_error'] = True
    (directory / 'result.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({k: record[k] for k in ('arm','scenario','repeat','completed_successfully','tool_calls','tokens')}), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='a00d263')
    parser.add_argument('--model', required=True)
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=480)
    parser.add_argument('--scenario', choices=SCENARIOS, action='append')
    parser.add_argument('--arm', choices=('baseline', 'candidate'), action='append', help='Default both; use to rerun a corrected candidate without repeating unchanged controls')
    args = parser.parse_args()
    base = ROOT / 'evals/results'
    base.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='agents-', dir=base))
    sources = {arm: output / 'snapshots' / arm for arm in ('baseline', 'candidate')}
    snapshot(sources['baseline'], args.baseline)
    snapshot(sources['candidate'], None)
    metadata = {'started_at': datetime.now(timezone.utc).isoformat(),
                'baseline_revision': command(['git','rev-parse',args.baseline], ROOT).stdout.strip(),
                'model': args.model, 'reasoning_effort': args.effort, 'repeats': args.repeats,
                'codex_version': command(['codex','--version']).stdout.strip(),
                'snapshot_hashes': {arm: digest_tree(path) for arm,path in sources.items()},
                'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'method': 'Paired one-turn trials; alternating arm order; isolated fixtures; deterministic external graders; no judge model.'}
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    specs = []
    for repeat in range(args.repeats):
        for scenario in args.scenario or SCENARIOS:
            for arm in (('baseline','candidate') if repeat % 2 == 0 else ('candidate','baseline')):
                if args.arm and arm not in args.arm:
                    continue
                specs.append((arm, scenario, repeat+1))
    print(f'Artifacts: {output}', flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(trial,args,output,sources[arm],arm,scenario,repeat) for arm,scenario,repeat in specs]
        results = [future.result() for future in futures]
    (output / 'results.json').write_text(json.dumps(results, indent=2))
    print(f'Completed {len(results)} trials: {output}', flush=True)
    return int(any(row.get('infrastructure_error') for row in results))


if __name__ == '__main__':
    raise SystemExit(main())
