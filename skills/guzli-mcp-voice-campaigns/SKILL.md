---
name: guzli-mcp-voice-campaigns
description: >-
  Creates and runs Guzli MCP voice campaigns (draft, publish, run) with shared
  contacts and segments. Use when the task is outbound or configured voice dialing,
  voice campaign setup, or voice campaign status via Guzli MCP. Do not use for
  email outreach (see guzli-mcp-email-outreach).
license: Apache-2.0
compatibility: >-
  Requires a host that supports Agent Skills (agentskills.io) and a connected
  Guzli MCP server at https://mcp.guzli.com/mcp (OAuth via gateway.guzli.com).
  Network access required. Works with Claude Code, Codex, Cursor, Grok, OpenClaw,
  Muse, Hermes Agent, and other compatible agents.
metadata:
  author: Guzli
  version: "1.1.2"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  hermes:
    tags: [Guzli, MCP, Voice, Campaigns]
    related_skills: [guzli-mcp-core, guzli-mcp-email-outreach]
---

# Guzli MCP voice campaigns

Install and follow **`guzli-mcp-core`**. Email sequences are skill **`guzli-mcp-email-outreach`**. Tool map: [references/tool-map.md](references/tool-map.md).

Same product ideas as email (contacts, segments, standing campaigns, revisions, enrollments) — different channel tools and config.

Use your host’s MCP tool caller against the connected Guzli server.

## Default model

1. **Few long-lived voice campaigns** per strategy; feed contacts/segments over time.
2. Do not open a new voice campaign per contact.
3. Personalization on the contact; campaign holds shared call strategy.
4. Draft → review → approve → publish → run.

## Prerequisites

1. Guzli MCP connected; voice tools present (`create_voice_campaign`, `publish_voice_campaign`, `run_voice_campaign`, …).
2. Know agent / voice profile ids (ask if missing — do not invent).
3. Never invent phone numbers.
4. First live publish/run in a thread needs explicit user approval.

## Workflow

```
Voice campaign:
- [ ] 1. Core skill + inventory existing campaigns when list tools exist
- [ ] 2. Upsert contacts with real phones
- [ ] 3. Segment if the audience is ongoing
- [ ] 4. create_voice_campaign (draft)
- [ ] 5. Complete revision/config per live schema
- [ ] 6. User approval → publish_voice_campaign → run_voice_campaign
- [ ] 7. Report campaign/revision ids and status
```

### Draft

`create_voice_campaign` with a clear strategy name. Attach required voice profile / agent fields from **current** schema. Prefer standing audience patterns when the product supports them.

### Publish & run

Summarize who will be dialed and which profile/limits apply. After approval: `publish_voice_campaign` (often needs `expected_lock_version`) then `run_voice_campaign`. Use enrollment/summary tools when available.

## Hard rules

1. Do not use email campaign tools for phone outreach.
2. No invented phones or silent dial launches.
3. Re-read voice schemas every time — payloads are large and versioned.
4. Keep private dial lists out of shared skill text.

## Verify

Draft ids known; publish/run only after approval; user gets campaign id, revision id, and whether dials were queued.

## Anti-patterns

Using `send_email` / `create_email_campaign` for phone outreach; one voice campaign per phone number; running before confirming voice profile and destination permissions.
