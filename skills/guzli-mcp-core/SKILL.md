---
name: guzli-mcp-core
description: >-
  Connects to and operates Guzli MCP for shared product concepts—tool discovery, contacts, lifecycle stages, and connector hygiene. Use when setting up Guzli MCP, listing or debugging tools, creating or searching contacts, reading lifecycle stages, or before email/voice campaign skills. Do not use alone for full outreach campaign runs (see guzli-mcp-email-outreach or guzli-mcp-voice-campaigns).
license: Apache-2.0
compatibility: >-
  Requires a host that supports Agent Skills (agentskills.io) and a connected
  Guzli MCP server at https://mcp.guzli.com/mcp (OAuth via gateway.guzli.com).
  Network access required. Works with Claude Code, Codex, Cursor, Grok, OpenClaw,
  Muse, Hermes Agent, and other compatible agents.
metadata:
  author: Guzli
  version: "1.4.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  hermes:
    tags: [Guzli, MCP, Contacts, CRM]
    related_skills: [guzli-mcp-email-outreach, guzli-mcp-voice-campaigns]
---

# Guzli MCP core

Portable foundation for Guzli MCP on any Agent Skills host. Channel runbooks:

- Email outreach → skill **`guzli-mcp-email-outreach`** (install beside this skill)
- Voice campaigns → skill **`guzli-mcp-voice-campaigns`**

Tool cheat sheet: [references/tool-map.md](references/tool-map.md).

## Host setup (all agents)

1. Connect Guzli MCP in your product UI or config (`https://mcp.guzli.com/mcp`).
2. Confirm tools from that server are callable (list/search tools in your host).
3. Call tools by **remote name** (example: `search_contacts`). Hosts may prefix names; match on the remote/suffix name when needed.
4. Re-read each tool’s **input schema** before calling — required fields change across releases.

Do not assume Cursor-, Claude-, or Codex-specific tool APIs. Use whatever MCP invocation your host provides.

## Shared concepts

| Concept | Meaning |
|---|---|
| **Contact** | One person / primary inbox. Personalization → custom attributes. |
| **Lifecycle** | Stage profile + stages + edges. Read before moving contacts. |
| **Segment** | Reusable audience (expression → version → materialize). |
| **Campaign / revision** | Strategy container + versioned definition (email and voice differ). |
| **Enrollment** | Membership in a campaign; summaries may expose typed refusal reasons. |

## Workflow

### 1. Discover

List Guzli MCP tools. Discover a usable `agent_id` from `list_campaigns` (or the user) before creating campaigns. If auth fails, fix the host connector — do not invent a parallel HTTP API.

### 2. Contacts

- `search_contacts` / `lookup_contact` before create.
- `create_contact` with a real `source_reason_code` (lowercase snake_case).
- **Omit `custom_attributes`** unless a refusal or the configured catalog names an allowed key. If the org has no configured keys, leave custom attributes off.
- `update_contact` for profile / allowed custom attributes only.
- Never invent email, phone, or name.

### 3. Lifecycle

- `list_lifecycle_stages`
- `get_contact_lifecycle_stage`
- `list_contact_events` for evidence ids
- `set_contact_lifecycle_stage` only with real `to_stage_id`, `evidence_event_ids`, and `reason_codes`

### 4. Hand off

- List/sequence **email** → **`guzli-mcp-email-outreach`**
- **Voice** dial campaigns → **`guzli-mcp-voice-campaigns`**
- Single ad-hoc email → `send_email` only when the user asked for one message

## OAuth / parallel calls

Refresh tokens **single-flight** per session: complete one refresh, then reuse those tokens for parallel tool calls. Do not run concurrent refreshes that compete for the same rotated handle.

## Hard rules

1. No fabricated contact data.
2. No silent sending or dialing — confirm when unsure.
3. Keep this skill to shared primitives; channel details live in sibling skills.
4. On schema/validation errors, report the tool + error; do not guess fields.

## Verify

A harmless read succeeds (`list_lifecycle_stages`, `search_contacts`, or `list_campaigns`), and returned ids are reusable in channel skills.
