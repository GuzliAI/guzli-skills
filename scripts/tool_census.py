#!/usr/bin/env python3
"""Audit inline backticked identifiers against catalog surfaces and schemas.

Run with --catalog, --primitives, --skills-root, and --plugin-root paths.
Uses only the Python standard library. Emits a Markdown table and fails on
unknown identifiers, missing inputs, malformed evidence, or empty skill trees.
Fenced examples are not inline code spans; their JSON arguments need a separate
schema check. No identifier allowlist or unknown-row suppression is supported.
"""

import argparse
import json
from pathlib import Path
import re
import sys


IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.:/-]*")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)
SURFACES = ("copilot", "tenant-operations", "webchat")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read JSON evidence {path.as_posix()}: {error}") from error


def schema_identifiers(value):
    """Include literal schema keys/values, not tokens guessed from descriptions."""
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if IDENTIFIER.fullmatch(key):
                found.add(key)
            if key not in {"description", "title", "$ref"}:
                found.update(schema_identifiers(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_identifiers(child))
    elif isinstance(value, str) and IDENTIFIER.fullmatch(value):
        found.add(value)
    return found


def build_index(catalog, registry):
    if not isinstance(catalog, dict) or not isinstance(registry, dict):
        raise ValueError("Catalog and primitives evidence must be JSON objects")
    index = {}
    names = {}

    def add(identifier, surface):
        index.setdefault(identifier, set()).add(surface)

    for key, surface, name_key in (
        ("copilot", "copilot", "name"),
        ("hosted", "tenant-operations", "operation_name"),
        ("webchat", "webchat", "name"),
    ):
        rows = catalog.get(key)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"Catalog {key} must be a nonempty array")
        names[surface] = set()
        for row in rows:
            if key == "hosted" and isinstance(row, dict):
                scope = row.get("oauth_scope")
                if scope in {"guzli:copilot:read", "guzli:copilot:act"}:
                    continue
                if scope not in {"guzli:read", "guzli:write"}:
                    raise ValueError(f"Hosted row has unrecognized oauth_scope: {scope!r}")
            name = row.get(name_key) if isinstance(row, dict) else None
            if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
                raise ValueError(f"Catalog {key} row has invalid {name_key}: {row!r}")
            if name in names[surface]:
                raise ValueError(f"Duplicate tool on {surface}: {name}")
            names[surface].add(name)
            add(name, surface)
            for schema_key in ("input_schema", "inputSchema", "output_schema", "outputSchema"):
                for identifier in schema_identifiers(row.get(schema_key)):
                    add(identifier, surface)

    primitives = registry.get("primitives")
    if not isinstance(primitives, list) or not primitives:
        raise ValueError("Registry primitives must be a nonempty array")
    hosted_actions = {
        row.get("engine_action"): row["operation_name"]
        for row in catalog["hosted"]
        if row.get("engine_action") and row["operation_name"] in names["tenant-operations"]
    }
    for primitive in primitives:
        if not isinstance(primitive, dict) or not isinstance(primitive.get("operation_id"), str):
            raise ValueError("Primitive lacks a string operation_id")
        operation = primitive["operation_id"]
        action = f"{primitive.get('method')} {primitive.get('path')}"
        for surface in SURFACES:
            # A primitive is evidence for a surface only when the catalog names
            # that operation, or explicitly maps its REST action to that surface.
            if operation in names[surface] or (
                surface == "tenant-operations" and action in hosted_actions
            ):
                for schema_key in ("input_schema", "output_schema"):
                    for identifier in schema_identifiers(primitive.get(schema_key)):
                        add(identifier, surface)
    return index


def inline_identifiers(text):
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    for match in INLINE_CODE.finditer("\n".join(lines)):
        yield from IDENTIFIER.findall(match.group(2))


def skill_files(root):
    if not root.is_dir():
        raise ValueError(f"Skill root is not a directory: {root.as_posix()}")
    entrypoints = sorted(root.glob("*/SKILL.md"))
    if not entrypoints:
        raise ValueError(f"No SKILL.md entrypoints under {root.as_posix()}")
    files = set(entrypoints)
    for entrypoint in entrypoints:
        for folder in ("references", "evals"):
            directory = entrypoint.parent / folder
            if directory.exists():
                files.update(path for path in directory.rglob("*") if path.is_file())
    return sorted(files)


def census(index, roots):
    occurrences = {}
    for label, root in roots:
        for path in skill_files(root):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise ValueError(f"Cannot read {path.as_posix()}: {error}") from error
            location = f"{label}/{path.relative_to(root).as_posix()}"
            for identifier in inline_identifiers(text):
                occurrences.setdefault(identifier, set()).add(location)
    if not occurrences:
        raise ValueError("No backticked identifiers found; refusing a vacuous census")
    rows = []
    for identifier, files in sorted(occurrences.items()):
        lookup = identifier.removeprefix("guzli:")
        surfaces = [surface for surface in SURFACES if surface in index.get(lookup, set())]
        rows.append({"identifier": identifier, "surfaces": surfaces or ["none"], "files": sorted(files)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("catalog", "primitives", "skills-root", "plugin-root"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--json", action="store_true", help="Emit rows with occurrence paths as JSON")
    args = parser.parse_args()
    try:
        index = build_index(load_json(args.catalog), load_json(args.primitives))
        rows = census(index, [("skills", args.skills_root), ("plugin", args.plugin_root)])
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    unknown = [row for row in rows if row["surfaces"] == ["none"]]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print("| Identifier | Surface | Files |")
        print("| --- | --- | --- |")
        for row in rows:
            print(f"| `{row['identifier']}` | {', '.join(row['surfaces'])} | {len(row['files'])} |")
        print(f"\nIdentifiers: {len(rows)}; none: {len(unknown)}")
    for row in unknown:
        print(f"ERROR: unknown identifier {row['identifier']} in {', '.join(row['files'])}", file=sys.stderr)
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main())
