#!/usr/bin/env python3
"""Regrade retained trials consistently and summarize selected arms without model calls."""
import argparse
import hashlib
import json
from pathlib import Path

import benchmark_agents as benchmark


def rescore(directory):
    rows = []
    for path in sorted(directory.glob('*/result.json')):
        row = json.loads(path.read_text())
        task = path.parent / 'task'
        head = row.get('initial_head') or benchmark.command(
            ['git', 'log', '-1', '--format=%H', '--grep=^Approved fixture policy$'], task).stdout.strip()
        if not head:
            raise ValueError(f'Cannot identify fixture initial commit: {task}')
        events, usage = benchmark.parse_events((path.parent / 'events.jsonl').read_text())
        row.update(benchmark.grade(task, row['scenario'], row['final'], events, head))
        row.update(benchmark.metrics(events, usage, row['final']))
        if row.get('infrastructure_error') or row['exit_code'] or not usage or not row['final']:
            row['completed_successfully'] = False
        rows.append(row)
    if not rows:
        raise ValueError(f'No completed trial records: {directory}')
    return rows


def summarize(rows):
    totals = {}
    for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens'):
        values = [(row.get('tokens') or {}).get(key) for row in rows]
        totals[key] = sum(values) if all(value is not None for value in values) else None
    return {'trials': len(rows), 'completed': sum(row['completed_successfully'] for row in rows),
            'mean_quality': sum(row['score'] for row in rows) / len(rows),
            'tool_calls': sum(row['tool_calls'] for row in rows),
            'clarification_turns': sum(row['clarification_turns'] for row in rows),
            'clarification_questions': sum(row['clarification_questions'] for row in rows),
            'tokens': totals}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run', type=lambda value: Path(value).resolve(), required=True)
    parser.add_argument('--candidate-run', type=lambda value: Path(value).resolve(), required=True)
    args = parser.parse_args()
    output = {'grader_sha256': hashlib.sha256(Path(benchmark.__file__).read_bytes()).hexdigest(),
              'runs': {}, 'comparison': {}}
    for directory in dict.fromkeys((args.baseline_run, args.candidate_run)):
        rows = rescore(directory)
        audit = {'grader_sha256': output['grader_sha256'], 'results': rows}
        (directory / 'rescored-results.json').write_text(json.dumps(audit, indent=2) + '\n')
        output['runs'][str(directory)] = {'metadata': json.loads((directory / 'metadata.json').read_text()),
                                          'results': rows}
    for arm, directory in (('baseline', args.baseline_run), ('candidate', args.candidate_run)):
        rows = [row for row in output['runs'][str(directory)]['results'] if row['arm'] == arm]
        output['comparison'][arm] = {'overall': summarize(rows), 'scenarios': {
            scenario: summarize([row for row in rows if row['scenario'] == scenario])
            for scenario in sorted({row['scenario'] for row in rows})}}
    (args.candidate_run / 'comparison.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output['comparison'], indent=2))


if __name__ == '__main__':
    main()
