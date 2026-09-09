# Guzli skills

Public [Agent Skills](https://agentskills.io) for [Guzli](https://guzli.com) MCP (`https://mcp.guzli.com/mcp`).

Each skill is a folder with a `SKILL.md` (YAML frontmatter + instructions) and optional `references/`. Compatible with Cursor / Grok Bot style skill loading and the agentskills.io progressive-disclosure model.

## Skills

| Skill | Use when |
|---|---|
| [`guzli-mcp-core`](skills/guzli-mcp-core/) | Connecting to Guzli MCP, discovering tools, contacts, lifecycle, shared concepts |
| [`guzli-mcp-email-outreach`](skills/guzli-mcp-email-outreach/) | Outbound **email** via standing campaigns + segments (not one-off `send_email` loops) |
| [`guzli-mcp-voice-campaigns`](skills/guzli-mcp-voice-campaigns/) | Outbound / configured **voice** campaigns (separate from email outreach) |

## Layout

```
skills/<skill-id>/
  SKILL.md
  references/   # optional, loaded on demand
```

## Install

- **Cursor / Grok Bot:** copy or submodule a skill folder into your skills/workflows directory, or clone this repo and point your agent at `skills/`.
- Keep org-specific secrets, lead lists, and private goals out of these files — they are meant to be shared.

## License

Apache-2.0
