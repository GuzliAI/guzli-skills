# Guzli skills

Portable Agent Skills for Guzli MCP at `https://mcp.guzli.com/mcp`.

| Skill | Use |
| --- | --- |
| [guzli-mcp-core](skills/guzli-mcp-core/SKILL.md) | Connection, contacts, tags, segments, knowledge, managed numbers and issues |
| [guzli-mcp-email-outreach](skills/guzli-mcp-email-outreach/SKILL.md) | One-off email, HTML, permission and email campaign workflows |
| [guzli-mcp-voice-campaigns](skills/guzli-mcp-voice-campaigns/SKILL.md) | One-off calls, permission, voice campaigns and answer extraction |

Each skill is self-contained. Install the skills your work needs; the channel
skills do not require loading the general skill first.

## Install

See [INSTALL.md](INSTALL.md) for host paths. From a clone:

```sh
./scripts/install-skill.sh guzli-mcp-core ~/.agents/skills
```

The installer replaces the selected destination skill folder.
Complete the Guzli OAuth sign-in in your host.

## Validation

Use Python 3.9 or later (standard library only) for the census and its tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts
python3 scripts/tool_census.py --catalog /path/to/copilot-catalog.json \
  --skills-root skills \
  --plugin-root /path/to/plugin/plugins/guzli/skills
claude plugin validate --strict ./skills
```

The census checks every inline backticked identifier in SKILL.md, references and
evals, including unknown identifiers. It checks only the copilot catalog and fails
on unknowns. `--json` includes occurrence paths. Fenced JSON examples require a
separate schema review; a tool-name match does not prove argument validity.

Each skill's `evals/` contains manual/harness-run scenarios with `skills`, `query`
and `expected_behavior`. No network evaluation runs during local validation.
Run scenarios in a permitted harness with each target model before asserting
behavioral quality; schema and packaging checks alone do not prove it.

## Release notes

**1.8.0** targets engine **1.0.22**. Rewrites the three skills around the Guzli
tools, separates plugin skills by channel, removes historical skill
instructions, and adds permission, draft-edit, managed-number and readiness
feedback loops plus offline census checks and evaluation scenarios. Release
versions live here, not in agent-loaded instructions.

## License

Apache-2.0. See [LICENSE](LICENSE).
