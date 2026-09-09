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
  version: "1.4.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  hermes:
    tags: [Guzli, MCP, Voice, Campaigns]
    related_skills: [guzli-mcp-core, guzli-mcp-email-outreach]
---

# Guzli MCP voice campaigns

Install and follow **`guzli-mcp-core`**. Email sequences are skill **`guzli-mcp-email-outreach`**. Tool map: [references/tool-map.md](references/tool-map.md).

Same product shape as email (contacts, segments, standing campaigns, revisions, enrollments) — different channel tools and step config.

Use your host’s MCP tool caller against the connected Guzli server. Re-read voice schemas every time (payloads are large and versioned).

## How voice campaigns should run

1. **Few long-lived voice campaigns** per strategy; feed contacts or segments over time.
2. Do **not** open a new voice campaign per phone number.
3. Shared call strategy on the campaign; per-person details on the contact.
4. Flow: contacts → (optional segment) → `create_voice_campaign` → publish → enroll (if explicit) → `run_voice_campaign`.
5. **Audience → enrollment** (same rule as email):
   - **Segment audience:** segment automation enrolls members. Do not call `enroll_campaign_contacts`.
   - **Explicit audience:** after publish, `enroll_campaign_contacts`, then run.
6. Pass a real **`voice_profile_id`** on create when the user or product provides one. Do not invent profile, telephony, or number-pool ids.
7. First live publish/run in a thread needs explicit user approval. Summarize who will be dialed before running.

## Prerequisites

1. Guzli MCP connected; voice tools present (`create_voice_campaign`, `publish_voice_campaign`, `run_voice_campaign`, …).
2. Know **`agent_id`** (from `list_campaigns` or the user).
3. Real E.164 phone numbers only — never invent phones.
4. Prefer standing campaigns with ongoing audiences over one-shot dials.

## Canonical workflow

```
- [ ] 1. Core skill + list_campaigns / get_campaign as needed
- [ ] 2. Upsert contacts with real phones (omit custom_attributes unless allowed)
- [ ] 3. Segment if the audience is ongoing; otherwise explicit audience
- [ ] 4. create_voice_campaign (name + voice_profile_id when known)
- [ ] 5. Confirm draft via get_campaign / get_campaign_revision (lock_version, revision_id)
- [ ] 6. User approval → publish_voice_campaign
- [ ] 7. Explicit audience only: enroll_campaign_contacts
- [ ] 8. run_voice_campaign
- [ ] 9. Report campaign/revision ids and whether dials were queued
```

### Draft

`create_voice_campaign`: required `name`; optional `voice_profile_id`.

If the create call is slow to return, recover with `list_campaigns` by name, then `get_campaign` / `get_campaign_revision` for `campaign_id`, `draft_revision_id`, and `lock_version`.

Use `revise_campaign` when you need to replace the draft definition (caps, call copy, pinned identifier, destination permissions). Re-read the live schema; send a complete draft definition.

### Publish

`publish_voice_campaign` requires:

- `campaign_id`
- `revision_id`
- `expected_lock_version`
- `agent_id`

### Enroll & run

- Explicit: `enroll_campaign_contacts` on the **active published** campaign, then `run_voice_campaign` (`campaign_id`, `revision_id`).
- Segment: rely on segment enrollment; then `run_voice_campaign`.

## Hard rules

1. Do not use email campaign tools for phone outreach.
2. No invented phones or silent dial launches.
3. No one-campaign-per-number.
4. Keep private dial lists out of shared skill text.
5. OAuth: refresh tokens **single-flight** per session (see **guzli-mcp-core**).

## Verify

Draft and published ids known; enrollments match the intended audience; user approved the live dial; user gets campaign id, revision id, and whether dials were queued.

## Anti-patterns

Using `send_email` / `create_email_campaign` for phone outreach; one voice campaign per number; inventing `voice_profile_id` / telephony / number-pool ids; calling `enroll_campaign_contacts` on a segment-audience campaign.
