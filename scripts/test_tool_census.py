"""Offline regression tests; run: python3 -m unittest discover -s scripts."""

import unittest
import io
from pathlib import Path
from unittest.mock import patch

from tool_census import build_index, census, inline_identifiers, main


class CensusTests(unittest.TestCase):
    def catalog(self):
        return {"copilot": [{"name": "find_contacts"}]}

    def test_qualified_and_unknown_are_extracted(self):
        self.assertEqual(list(inline_identifiers("`guzli:find_contacts` and `invented_tool`")),
                         ["guzli:find_contacts", "invented_tool"])

    def test_fenced_json_is_not_inline_code(self):
        self.assertEqual(list(inline_identifiers('```json\n{"key":"value"}\n```\n`find_contacts`')),
                         ["find_contacts"])

    def test_eval_json_code_spans_are_extracted(self):
        self.assertEqual(list(inline_identifiers('{"expected_behavior":["Calls `guzli:find_contacts`"]}')),
                         ["guzli:find_contacts"])

    def test_unknown_survives_as_unknown_row(self):
        root = Path("skills")
        with patch("tool_census.skill_files", return_value=[root / "example" / "SKILL.md"]), \
             patch.object(Path, "read_text", return_value="`guzli:find_contacts` `invented_tool`"):
            rows = census(build_index(self.catalog()), [("skills", root)])
        self.assertEqual(rows[0]["status"], "copilot")
        self.assertEqual(rows[1]["status"], "unknown")
        self.assertEqual(rows[1]["files"], ["skills/example/SKILL.md"])

    def test_no_inferred_copilot_schema(self):
        index = build_index(self.catalog())
        self.assertIn("find_contacts", index)
        self.assertNotIn("contact_id", index)
        self.assertNotIn("invented_tool", index)

    def test_invalid_catalog_fails(self):
        with self.assertRaisesRegex(ValueError, "nonempty array"):
            build_index({})

    def test_other_catalog_entries_are_not_evidence(self):
        catalog = self.catalog()
        catalog["other"] = [{"name": "private_tool"}]
        self.assertNotIn("private_tool", build_index(catalog))

    def test_invalid_catalog_type_fails(self):
        with self.assertRaisesRegex(ValueError, "JSON object"):
            build_index([])

    def test_invalid_row_fails(self):
        for row in (None, {}, {"name": 1}, {"name": "bad name"}):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, "invalid name"):
                build_index({"copilot": [row]})

    def test_catalog_schema_is_evidence_but_description_is_not(self):
        catalog = self.catalog()
        catalog["copilot"][0]["inputSchema"] = {
            "properties": {"contact_id": {"type": "string", "description": "invented_tool"}}
        }
        index = build_index(catalog)
        self.assertIn("contact_id", index)
        self.assertNotIn("invented_tool", index)

    def test_unknown_fails_cli_with_explicit_location(self):
        args = ["tool_census.py", "--catalog", "catalog.json", "--skills-root", "skills",
                "--plugin-root", "plugin"]
        errors = io.StringIO()
        with patch("sys.argv", args), patch("tool_census.load_json", return_value=self.catalog()), \
             patch("tool_census.census", return_value=[{
                 "identifier": "private_tool", "status": "unknown", "files": ["skills/example/SKILL.md"]
             }]), patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", errors):
            self.assertEqual(main(), 1)
        self.assertIn("ERROR: unknown identifier private_tool in skills/example/SKILL.md", errors.getvalue())

    def test_duplicate_catalog_fails(self):
        catalog = self.catalog()
        catalog["copilot"] *= 2
        with self.assertRaisesRegex(ValueError, "Duplicate tool"):
            build_index(catalog)


if __name__ == "__main__":
    unittest.main()
