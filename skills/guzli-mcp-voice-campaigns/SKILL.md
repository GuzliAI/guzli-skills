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
  version: "1.3.0"
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
4. Draft → review → approve → publish → enroll (explicit) → run.

## Prerequisites

1. Guzli MCP connected; voice tools present (`create_voice_campaign`, `publish_voice_campaign`, `run_voice_campaign`, …).
2. Know **agent_id**. Optional `voice_profile_id` when the user/product provides one — do not invent. MCP has **no** `list_voice_profiles` / telephony / number-pool tools as of skill v1.3.0.
3. Never invent phone numbers.
4. First live publish/run in a thread needs explicit user approval.
5. **Hard gate (tracked P1):** MCP-created voice campaigns cannot publish yet. `publish_voice_campaign` returns `send_capability_not_registered` because the step’s **channel key does not match the engine’s voice send registry**. This is **not** a missing voice profile or number pool, and **no MCP call** can fix it today. `propose_agent_configuration_change` (`allow_in_voice`) does **not** clear it. Do not work around — wait for the engine fix.

## Workflow

```
Voice campaign:
- [ ] 1. Core skill + list_campaigns / get_campaign when available
- [ ] 2. Upsert contacts with real E.164 phones
- [ ] 3. Segment if the audience is ongoing; else keep explicit audience
- [ ] 4. create_voice_campaign (name + voice_profile_id when known)
- [ ] 5. If create times out, recover ids via list_campaigns + get_campaign_revision
- [ ] 6. Revise if needed (daily caps, pinned identifier, call copy) — see ops notes
- [ ] 7. User approval → publish_voice_campaign → enroll_campaign_contacts → run_voice_campaign
- [ ] 8. Report campaign/revision ids and whether dials queued
```

### Draft

`create_voice_campaign` requires `name`; optional `voice_profile_id`. Drafts may land with `voice_profile_id=null` and placeholder artifact digests; the current publish blocker is the **channel-key vs send registry** mismatch, not the missing profile.

**Create timeout:** the MCP call may hang for many minutes while the server still creates the draft. On timeout, `list_campaigns` by name and continue with recovered `campaign_id` / `draft_revision_id`.

### Publish & run

`publish_voice_campaign` needs `campaign_id`, `revision_id`, `expected_lock_version`, and `agent_id`.

After publish (lifecycle active), enroll explicit contacts with `enroll_campaign_contacts`, then `run_voice_campaign` (`campaign_id`, `revision_id`).

Summarize who will be dialed and which profile/limits apply before any live run.

## Live ops notes (2026-09)

Observed on connected Guzli MCP (~71 tools):

| Symptom | Handling |
|---|---|
| `publish_voice_campaign` → `readiness_blocked` / `send_capability_not_registered` | **Stop.** Tracked P1: step channel key ≠ engine voice send registry. **Not** missing profile/pool. No MCP workaround. Do not retry in a loop. |
| No inventory for `voice_profile_id` / number pool / telephony | Ask the user if needed later; do not invent. Prefer product MCP list tools when added. |
| `revise_campaign` → opaque `invalid_workflow_request` | Report as backend opacity; do not guess fields. Prefer structured validation errors from engine. |
| Contact phone **provisional**; step defaults to `verified_channel_identifier` | Schema allows `pinned_identifier` + `contact_identifier_id`. Prefer pin when revise works; document outcome. |
| `enroll_campaign_contacts` | Only on **active published** explicit-audience campaigns. |

## Hard rules

1. Do not use email campaign tools for phone outreach.
2. No invented phones or silent dial launches.
3. Re-read voice schemas every time — payloads are large and versioned.
4. Keep private dial lists out of shared skill text.
5. Do not treat Ability `allow_in_voice`, inventing a `voice_profile_id`, or adding a number pool as fixes for `send_capability_not_registered`.

## Verify

Draft ids known; publish readiness clear of `send_capability_not_registered`; real voice profile present when required; publish/run only after approval; user gets campaign id, revision id, and whether dials were queued.

## Anti-patterns

Using `send_email` / `create_email_campaign` for phone outreach; one voice campaign per phone number; inventing `voice_profile_id`; looping publish or “fixing” profile/pool for `send_capability_not_registered`.
