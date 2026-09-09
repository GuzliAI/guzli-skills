---
name: guzli-mcp-core
description: >-
  Connects to and operates Guzli MCP for shared product concepts—tool discovery,
  contacts, lifecycle stages, and connector hygiene. Use when setting up Guzli
  MCP, listing or debugging tools, creating or searching contacts, reading
  lifecycle stages, or before email/voice campaign skills. Do not use alone for
  full outreach campaign runs (see guzli-mcp-email-outreach or
  guzli-mcp-voice-campaigns).
---

# Guzli MCP core

Foundation skill for any Guzli MCP work. Campaign-specific flows live in sibling skills:

- Email outreach → [guzli-mcp-email-outreach](../guzli-mcp-email-outreach/SKILL.md)
- Voice campaigns → [guzli-mcp-voice-campaigns](../guzli-mcp-voice-campaigns/SKILL.md)

Tool name cheat sheet: [references/tool-map.md](references/tool-map.md).

## Prerequisites

1. Guzli remote MCP URL: `https://mcp.guzli.com/mcp` (OAuth via `https://gateway.guzli.com`).
2. Confirm the connector is **connected** and list tools from its namespace (install name varies).
3. Read each tool’s **input schema** before calling — required fields change across releases.
4. Prefer the tool’s **remote name** (e.g. `search_contacts`) in notes and reports.

## Shared concepts

| Concept | Meaning |
|---|---|
| **Contact** | One person / primary inbox. Personalization → custom attributes, not duplicate contacts. |
| **Lifecycle** | Stage profile + stages + allowed edges. Read stages before moving anyone. |
| **Segment** | Reusable audience (expression → version → materialize). |
| **Campaign / revision** | Strategy container + versioned definition. Email and voice are different campaign families. |
| **Enrollment** | Contact membership in a campaign; summaries expose typed refusal reasons. |

## Workflow

### 1. Discover

- List MCP tools for the Guzli connector.
- If auth fails, fix OAuth / reconnect — do not invent a second API.

### 2. Contacts

- `search_contacts` / `lookup_contact` before create (avoid duplicates).
- `create_contact` with a real `source_reason_code` (lowercase snake_case).
- `update_contact` for profile patches and custom attributes.
- Never invent email, phone, or name. Skip incomplete rows.

### 3. Lifecycle

- `list_lifecycle_stages` → know profile id, stage ids/keys, edges.
- `get_contact_lifecycle_stage` to read current stage.
- `list_contact_events` when you need evidence ids.
- `set_contact_lifecycle_stage` only with real `to_stage_id`, `evidence_event_ids`, and `reason_codes`.

### 4. Hand off

- Email list / sequence work → **guzli-mcp-email-outreach**.
- Voice dialer / voice campaign work → **guzli-mcp-voice-campaigns**.
- Single ad-hoc plain email → `send_email` only when the user asked for one message, not a list.

## Hard rules

1. No fabricated contact data.
2. No silent destructive or sending actions — confirm when unsure.
3. Do not stuff campaign runbooks into this skill; keep it shared primitives only.
4. If a tool returns schema/validation errors, report tool + error; do not guess fields.

## Verify

- Connector shows tools; a harmless read (`list_campaigns` or `list_lifecycle_stages` or `search_contacts`) succeeds.
- Contact create/search returns stable ids you can reuse in campaign skills.
