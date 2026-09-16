# Install Guzli skills

Clone the repository and copy each selected skill as a complete folder, including
references. The installer replaces an existing destination folder of that name.

```sh
git clone https://github.com/GuzliAI/guzli-skills.git
cd guzli-skills
./scripts/install-skill.sh guzli-mcp-core ~/.agents/skills
```

Repeat for `guzli-mcp-email-outreach` or `guzli-mcp-voice-campaigns` as needed.
Choose your host's configured skill root; common locations are:

| Host | Skill root |
| --- | --- |
| Codex | `~/.agents/skills` or project `.agents/skills` |
| Claude Code | `~/.claude/skills` or project `.claude/skills` |
| Cursor | `~/.cursor/skills` or project `.cursor/skills` |
| OpenClaw | `~/.openclaw/skills` |
| Hermes Agent | `~/.hermes/skills` |
| Muse, Grok or another Agent Skills host | Its configured skill import/search path |

For hosts with an import interface, import the complete skill folder rather than
only SKILL.md. Repository `.agents/skills` and `.claude/skills` links point to the
same source skills; preserve their targets when working from this clone.

## Connect and verify

1. Configure Guzli MCP at `https://mcp.guzli.com/mcp` in the host.
2. Complete the Guzli OAuth sign-in in your host.
3. Reload the host's skill discovery and invoke the selected skill by name.
4. Request read-only contact discovery and verify that Guzli tools are exposed.
   Installing skill files alone does not connect or authenticate MCP.

See [README.md](README.md) for offline validation and manual evaluation guidance.
