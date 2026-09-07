from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/monomind-workflow/scripts'
sys.path.insert(0, str(SCRIPTS))
import policy


class PolicyTest(unittest.TestCase):
    def resolved(self):
        return {label: 'verified value — evidence: README.md' for label in policy.required_fields('release')}

    def test_empty_owner_does_not_consume_heading(self):
        text = '- Repository owner or project lead:\n\n## Collaboration\n'
        fields = policy.parse_fields(text)
        self.assertEqual(fields['Repository owner or project lead'], '')
        self.assertIn(('Repository owner or project lead', 'empty'), policy.issues(fields, 'build'))

    def test_crlf_empty_field_stays_empty(self):
        fields = policy.parse_fields('- Focused test:\r\n- Full regression suite: python -m unittest\r\n')
        self.assertEqual(fields['Focused test'], '')
        self.assertEqual(fields['Full regression suite'], 'python -m unittest')

    def test_duplicate_fields_are_rejected(self):
        with self.assertRaisesRegex(policy.PolicyError, 'duplicate'):
            policy.parse_fields('- Integration strategy: UNRESOLVED\n- Integration strategy: squash\n')

    def test_example_fences_are_not_policy(self):
        fields = policy.parse_fields('```markdown\n- Repository owner or project lead: example\n```\n')
        self.assertEqual(fields, {})

    def test_information_does_not_change_release_schema(self):
        fields = self.resolved()
        fields['Context pipeline'] = 'UNRESOLVED optional documentation'
        self.assertEqual(policy.issues(fields, 'release'), [])

    def test_legacy_profile_without_context_link_remains_ready(self):
        self.assertEqual(policy.issues(self.resolved(), 'release'), [])

    def test_integration_does_not_require_deployment_policy(self):
        fields = self.resolved()
        fields['Release command or pipeline'] = 'UNRESOLVED'
        self.assertEqual(policy.issues(fields, 'integration'), [])
        self.assertIn(('Release command or pipeline', 'UNRESOLVED'), policy.issues(fields, 'release'))

    def test_integration_requires_review_policy(self):
        fields = self.resolved()
        fields['Blocking-finding policy'] = 'UNRESOLVED'
        self.assertEqual(policy.issues(fields, 'build'), [])
        self.assertIn(('Blocking-finding policy', 'UNRESOLVED'), policy.issues(fields, 'integration'))

    def test_unknown_schema_is_not_silently_certified(self):
        fields = self.resolved()
        fields['Policy schema version'] = '999'
        with self.assertRaisesRegex(policy.PolicyError, 'unsupported'):
            policy.issues(fields, 'build')

    def test_owner_cannot_be_not_applicable(self):
        fields = self.resolved()
        fields['Repository owner or project lead'] = 'NOT_APPLICABLE — nobody owns it'
        self.assertTrue(policy.issues(fields, 'build'))

    def test_unresolved_in_approved_prose_is_not_a_status_marker(self):
        fields = self.resolved()
        fields['Blocking-finding policy'] = 'failed checks and unresolved P1 findings block integration'
        self.assertEqual(policy.issues(fields, 'integration'), [])
        fields['Blocking-finding policy'] = 'unresolved — owner must decide'
        self.assertIn(('Blocking-finding policy', 'UNRESOLVED'), policy.issues(fields, 'integration'))

    def test_missing_and_blank_are_different(self):
        fields = self.resolved()
        fields.pop('Focused test')
        fields['Full regression suite'] = ''
        self.assertIn(('Focused test', 'missing'), policy.issues(fields, 'build'))
        self.assertIn(('Full regression suite', 'empty'), policy.issues(fields, 'build'))


if __name__ == '__main__':
    unittest.main()
