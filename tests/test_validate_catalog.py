import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_catalog", ROOT / "scripts" / "validate_catalog.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class CatalogSyntaxTests(unittest.TestCase):
    def test_rejects_frontmatter_that_a_yaml_host_cannot_parse(self):
        invalid_values = (
            "description: Use this: when needed",
            "\tdescription: Tabbed indentation",
            'description: "unterminated',
            'description: "invalid \\q escape"',
        )
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            path = Path(temporary) / "SKILL.md"
            for value in invalid_values:
                with self.subTest(value=value):
                    path.write_text(f"---\nname: example\n{value}\n---\n", encoding="utf-8")
                    validation = MODULE.Validation()
                    MODULE.read_frontmatter(path, validation)
                    self.assertTrue(validation.errors, value)

    def test_reads_current_frontmatter_shape_without_external_yaml(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            path = Path(temporary) / "SKILL.md"
            path.write_text(
                '---\nname: example\ndescription: "A colon: and \\"quote\\""\n'
                "metadata:\n  upstream: https://example.com/a:b\n---\n",
                encoding="utf-8",
            )
            validation = MODULE.Validation()
            fields = MODULE.read_frontmatter(path, validation)
            self.assertEqual(validation.errors, [])
            self.assertEqual(fields["description"], 'A colon: and "quote"')

    def test_comment_only_scalar_is_not_a_description(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            path = Path(temporary) / "SKILL.md"
            path.write_text(
                "---\nname: example\ndescription: # a sufficiently long comment\n---\n",
                encoding="utf-8",
            )
            validation = MODULE.Validation()
            fields = MODULE.read_frontmatter(path, validation)
            self.assertNotIn("description", fields)
            self.assertTrue(validation.errors)

    def test_inline_yaml_comment_is_removed_only_from_plain_scalar(self):
        validation = MODULE.Validation()
        self.assertEqual(
            MODULE.read_scalar("Useful guidance # note", "SKILL.md:3", validation),
            "Useful guidance",
        )
        self.assertEqual(
            MODULE.read_scalar('"Useful # guidance"', "SKILL.md:3", validation),
            "Useful # guidance",
        )
        self.assertEqual(
            MODULE.read_scalar('"Useful # guidance" # note', "SKILL.md:3", validation),
            "Useful # guidance",
        )
        self.assertEqual(
            MODULE.read_scalar("User's guide # note", "SKILL.md:3", validation),
            "User's guide",
        )
        self.assertEqual(validation.errors, [])

    def test_reference_links_resolve_from_containing_file(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            skill = Path(temporary) / "skills" / "example"
            references = skill / "references"
            references.mkdir(parents=True)
            (skill / "SKILL.md").write_text("[notes](references/notes.md)\n", encoding="utf-8")
            (references / "notes.md").write_text(
                "[root](../SKILL.md) [missing](missing.md) "
                "[outside](../../other.md) [remote](https://example.com/a.md) [section](#part)\n"
                "```markdown\n[example](not-a-file.md)\n```\n",
                encoding="utf-8",
            )
            validation = MODULE.Validation()
            MODULE.validate_local_links(skill, validation)
            self.assertEqual(len(validation.errors), 2)
            self.assertTrue(any("broken local link: missing.md" in e for e in validation.errors))
            self.assertTrue(any("escapes the standalone skill" in e for e in validation.errors))

    def test_explicit_reference_definitions_and_parenthesized_paths(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            skill = Path(temporary) / "skills" / "example"
            references = skill / "references"
            references.mkdir(parents=True)
            (references / "file(name).md").write_text("# Works\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(
                "[good](references/file(name).md) "
                "`[literal](../outside.md)` [guide][guide] [bad][bad] "
                "[missing][undefined]\n"
                "[guide]: references/file(name).md\n"
                "[bad]: ../outside.md\n",
                encoding="utf-8",
            )
            validation = MODULE.Validation()
            MODULE.validate_local_links(skill, validation)
            self.assertEqual(len(validation.errors), 2, validation.errors)
            self.assertTrue(any("escapes the standalone skill: ../outside.md" in e for e in validation.errors))
            self.assertTrue(any("undefined reference: undefined" in e for e in validation.errors))

    def test_parenthesized_missing_file_is_reported_without_truncation(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            skill = Path(temporary) / "skills" / "example"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("[missing](file(name).md)\n", encoding="utf-8")
            validation = MODULE.Validation()
            MODULE.validate_local_links(skill, validation)
            self.assertEqual(len(validation.errors), 1)
            self.assertIn("broken local link: file(name).md", validation.errors[0])

    def test_markdown_punctuation_escapes_resolve_without_stripping_other_backslashes(self):
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            MODULE, "ROOT", Path(temporary)
        ):
            skill = Path(temporary) / "skills" / "example"
            skill.mkdir(parents=True)
            (skill / "file(name).md").write_text("# Works\n", encoding="utf-8")
            (skill / "file\\q.md").write_text("# Literal backslash\n", encoding="utf-8")
            (skill / "SKILL.md").write_text(
                "[good](file\\(name\\).md) [literal](file\\q.md)\n",
                encoding="utf-8",
            )
            validation = MODULE.Validation()
            MODULE.validate_local_links(skill, validation)
            self.assertEqual(validation.errors, [])


if __name__ == "__main__":
    unittest.main()
