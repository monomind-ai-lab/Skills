from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
import subprocess
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('benchmark_agents', Path(__file__).resolve().parents[1] / 'scripts/benchmark_agents.py')
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class BenchmarkMetricsTest(unittest.TestCase):
    def test_wrong_gate_cannot_certify_release(self):
        events = [{'type': 'item.completed', 'item': {'id': 'x', 'type': 'command_execution',
            'command': 'python3 adopt.py check --gate build', 'exit_code': 0,
            'aggregated_output': 'OK: build-ready policy gate passed'}}]
        def git(args, *a, **kw):
            return subprocess.CompletedProcess(args, 0, 'head\n' if 'rev-parse' in args else '', '')
        with patch.object(benchmark, 'command', side_effect=git), patch.object(
            benchmark, 'bounded_probe', return_value=subprocess.CompletedProcess([], 0, 'OK: release-ready policy gate passed', '')):
            result = benchmark.grade(Path('/unused'), 'legacy_profile',
                                     {'status': 'ready', 'clarification_questions': []}, events, 'head')
        self.assertFalse(result['completed_successfully'])
        self.assertFalse(result['checks']['ran_policy_check'])

    def test_filtered_stdout_uses_external_gate_verification(self):
        events = [{'type': 'item.completed', 'item': {'id': 'x', 'type': 'command_execution',
            'command': 'python3 adopt.py check --gate integration && git log -1', 'exit_code': 0,
            'aggregated_output': 'commit abc'}}]
        def git(args, *a, **kw):
            return subprocess.CompletedProcess(args, 0, 'head\n' if 'rev-parse' in args else '', '')
        with patch.object(benchmark, 'command', side_effect=git), patch.object(
            benchmark, 'bounded_probe', return_value=subprocess.CompletedProcess([], 0, 'OK: integration-ready policy gate passed', '')):
            result = benchmark.grade(Path('/unused'), 'integration',
                                     {'status': 'ready', 'clarification_questions': []}, events, 'head')
        self.assertTrue(result['completed_successfully'])

    def test_passing_hidden_probe_does_not_replace_agent_tests(self):
        def git(args, *a, **kw):
            return subprocess.CompletedProcess(args, 0, 'head\n' if 'rev-parse' in args else ' M labels.py\n', '')
        with patch.object(benchmark, 'command', side_effect=git), patch.object(
            benchmark, 'bounded_probe', return_value=subprocess.CompletedProcess([], 0, '', '')):
            result = benchmark.grade(Path('/unused'), 'implementation',
                                     {'status': 'completed', 'clarification_questions': []}, [], 'head')
        self.assertFalse(result['completed_successfully'])
        self.assertFalse(result['checks']['focused_tests_changed'])
        self.assertFalse(result['checks']['agent_ran_checks'])

    def test_grading_timeout_is_a_failure(self):
        with patch.object(benchmark.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['python'], 15)):
            result = benchmark.bounded_probe(['python'], Path('/unused'))
        self.assertEqual(result.returncode, 124)

    def test_fixture_resolution_never_rewrites_stop_marker_prose(self):
        source = 'Every `UNRESOLVED` value is a deliberate stop marker.\n- Focused test: UNRESOLVED\n'
        result = benchmark.resolved_profile(source, 'implementation')
        self.assertIn('Every `UNRESOLVED` value is a deliberate stop marker.', result)
        self.assertIn('- Focused test: python3 -m unittest', result)

    def test_profile_has_concrete_release_policy_except_integration_scenario(self):
        source = '- Release command or pipeline: UNRESOLVED\n'
        self.assertIn('manually accepts and tags', benchmark.resolved_profile(source, 'legacy_profile'))
        self.assertIn('UNRESOLVED', benchmark.resolved_profile(source, 'integration'))

    def test_tool_start_and_completion_count_once(self):
        events = [
            {'type': 'item.started', 'item': {'id': 'x', 'type': 'command_execution'}},
            {'type': 'item.completed', 'item': {'id': 'x', 'type': 'command_execution'}},
            {'type': 'item.completed', 'item': {'id': 'y', 'type': 'file_change'}},
        ]
        result = benchmark.metrics(events, {'input_tokens': 9}, {'clarification_questions': []})
        self.assertEqual(result['tool_calls'], 2)
        self.assertEqual(result['clarification_turns'], 0)

    def test_missing_usage_is_unknown_not_zero(self):
        self.assertIsNone(benchmark.metrics([], {}, {})['tokens'])

    def test_multiple_questions_in_one_turn_remain_one_clarification_turn(self):
        result = benchmark.metrics([], {}, {'clarification_questions': ['Who approves?', 'Where?']})
        self.assertEqual(result['clarification_turns'], 1)
        self.assertEqual(result['clarification_questions'], 2)

    def test_usage_is_summed_across_completed_turns_only(self):
        text = '\n'.join([
            'non-json diagnostic',
            '{"type":"turn.started"}',
            '{"type":"turn.completed","usage":{"input_tokens":10,"cached_input_tokens":4,"output_tokens":2}}',
            '{"type":"turn.completed","usage":{"input_tokens":20,"cached_input_tokens":8,"output_tokens":3}}',
        ])
        events, usage = benchmark.parse_events(text)
        self.assertEqual(len(events), 3)
        self.assertEqual(usage, {'input_tokens': 30, 'cached_input_tokens': 12, 'output_tokens': 5})


if __name__ == '__main__':
    unittest.main()
