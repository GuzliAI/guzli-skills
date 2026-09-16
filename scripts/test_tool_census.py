"""Offline regression tests; run: python3 -m unittest discover -s scripts."""

import unittest
from pathlib import Path
from unittest.mock import patch

from tool_census import build_index, census, inline_identifiers


class CensusTests(unittest.TestCase):
    def catalog(self):
        return {
            "copilot": [{"name": "find_contacts"}],
            "hosted": [{"operation_name": "get_contact", "engine_action": "GET /contacts/{id}", "oauth_scope": "guzli:read"}],
            "webchat": [{"name": "capture"}],
        }

    def registry(self):
        return {"primitives": [{
            "operation_id": "get_contact", "method": "GET", "path": "/contacts/{id}",
            "input_schema": {"properties": {"contact_id": {"type": "string"}}},
        }]}

    def test_qualified_and_unknown_are_extracted(self):
        self.assertEqual(list(inline_identifiers("`guzli:find_contacts` and `invented_tool`")),
                         ["guzli:find_contacts", "invented_tool"])

    def test_fenced_json_is_not_inline_code(self):
        self.assertEqual(list(inline_identifiers('```json\n{"key":"value"}\n```\n`find_contacts`')),
                         ["find_contacts"])

    def test_eval_json_code_spans_are_extracted(self):
        self.assertEqual(list(inline_identifiers('{"expected_behavior":["Calls `guzli:find_contacts`"]}')),
                         ["guzli:find_contacts"])

    def test_unknown_survives_as_none_row(self):
        root = Path("skills")
        with patch("tool_census.skill_files", return_value=[root / "example" / "SKILL.md"]), \
             patch.object(Path, "read_text", return_value="`guzli:find_contacts` `invented_tool`"):
            rows = census(build_index(self.catalog(), self.registry()), [("skills", root)])
        self.assertEqual(rows[0]["surfaces"], ["copilot"])
        self.assertEqual(rows[1]["surfaces"], ["none"])
        self.assertEqual(rows[1]["files"], ["skills/example/SKILL.md"])

    def test_no_inferred_copilot_schema(self):
        index = build_index(self.catalog(), self.registry())
        self.assertEqual(index["find_contacts"], {"copilot"})
        self.assertEqual(index["contact_id"], {"tenant-operations"})
        self.assertNotIn("invented_tool", index)

    def test_invalid_catalog_fails(self):
        with self.assertRaisesRegex(ValueError, "nonempty array"):
            build_index({}, self.registry())

    def test_hosted_transport_not_tenant_tool(self):
        catalog = self.catalog()
        catalog["hosted"].append({"operation_name": "copilot_list_tools", "oauth_scope": "guzli:copilot:read"})
        self.assertNotIn("copilot_list_tools", build_index(catalog, self.registry()))

    def test_invalid_registry_fails(self):
        with self.assertRaisesRegex(ValueError, "nonempty array"):
            build_index(self.catalog(), {})

    def test_duplicate_catalog_fails(self):
        catalog = self.catalog()
        catalog["copilot"] *= 2
        with self.assertRaisesRegex(ValueError, "Duplicate tool"):
            build_index(catalog, self.registry())


if __name__ == "__main__":
    unittest.main()
