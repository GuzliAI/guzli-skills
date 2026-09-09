# Guzli skills

Public [Agent Skills](https://agentskills.io) for [Guzli](https://guzli.com) MCP (`https://mcp.guzli.com/mcp`).

These skills follow the **agentskills.io** `SKILL.md` standard so the same folders work across hosts that load Agent Skills — including **Claude Code**, **OpenAI Codex / ChatGPT skills**, **Cursor**, **Grok Bot**, **OpenClaw**, **Muse Code**, **Hermes Agent** (Nous Research), and other compatible agents.

Each skill is a directory with:

- `SKILL.md` — required YAML frontmatter (`name`, `description`) + instructions
- `references/` — optional detail loaded on demand
- `agents/openai.yaml` — optional Codex / ChatGPT desktop metadata + Guzli MCP dependency hint

## Skills

| Folder | Skill `name` | Use when |
|---|---|---|
| [`skills/guzli-mcp-core`](skills/guzli-mcp-core/) | `guzli-mcp-core` | Connect Guzli MCP, contacts, lifecycle, shared concepts |
| [`skills/guzli-mcp-email-outreach`](skills/guzli-mcp-email-outreach/) | `guzli-mcp-email-outreach` | Standing **email** campaigns + segments |
| [`skills/guzli-mcp-voice-campaigns`](skills/guzli-mcp-voice-campaigns/) | `guzli-mcp-voice-campaigns` | **Voice** campaigns (create / publish / run) |

Install **core** plus whichever channel skill(s) you need. Channel skills assume core concepts; they do not require a monorepo-relative path at runtime.

## Install

See [INSTALL.md](INSTALL.md) for host-specific paths (Claude, Codex, Cursor, Grok, OpenClaw, Muse, Hermes, generic clone).

Quick pattern (any host that scans a skills directory):

```bash
git clone https://github.com/GuzliAI/guzli-skills.git
# copy one skill folder so SKILL.md is at <skills-root>/<name>/SKILL.md
cp -R guzli-skills/skills/guzli-mcp-core <skills-root>/guzli-mcp-core
```

## MCP prerequisite

Skills describe **how** to use Guzli tools. Your host must still expose Guzli as an MCP server:

- **URL:** `https://mcp.guzli.com/mcp`
- **Auth:** OAuth 2.0 via `https://gateway.guzli.com` (authorization code + PKCE)

How you add that connector differs by product (Claude connectors, Codex/ChatGPT apps, Cursor MCP, Grok connectors, OpenClaw MCP config, etc.). Skills stay connector-UI agnostic: discover tools from the connected Guzli server, then call them by **remote name** (for example `list_campaigns`).

## Authoring rules (portability)

- Frontmatter `name` is lowercase kebab-case and **matches the folder name**.
- Descriptions are third person: what + when + when not.
- No host-private paths, chat ids, or org secrets in skill text.
- Intra-skill links stay one level deep (`references/...`). Cross-skill deps are by **skill name**, not fragile relative paths after install.

## License

Apache-2.0 — see [LICENSE](LICENSE).
