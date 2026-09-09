---
name: guzli-mcp-email-outreach
description: >-
  Runs outbound email outreach through Guzli MCP using standing campaigns,
  segments, and contacts—not one-off sends. Use when Guzli MCP is available for
  email outreach, email campaigns, segment-fed enrollments, or turning a researched
  lead list into Guzli email campaigns. Do not use for voice campaigns (see
  guzli-mcp-voice-campaigns) or a single transactional email outside a campaign.
license: Apache-2.0
compatibility: >-
  Requires a host that supports Agent Skills (agentskills.io) and a connected
  Guzli MCP server at https://mcp.guzli.com/mcp (OAuth via gateway.guzli.com).
  Network access required. Works with Claude Code, Codex, Cursor, Grok, OpenClaw,
  Muse, and other compatible agents.
metadata:
  author: Guzli
  version: "1.1.1"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
---

# Guzli MCP email outreach

Install and follow **`guzli-mcp-core`** first. Tool map: [references/tool-map.md](references/tool-map.md).

Run outbound **email** as **standing campaigns** fed by **segments** and **contacts**. Prefer campaigns over looping `send_email`.

Use your host’s MCP tool caller against the connected Guzli server. Prefer **remote tool names**.

## Default model (non-negotiable)

1. **Few long-lived campaigns** per strategy — not one campaign per contact or batch.
2. **Keep feeding contacts** into the segment (or enroll into a published campaign).
3. **Personalization on the contact**; shared template on the campaign.
4. **`send_email` is one-off only**, never list outreach.

## Prerequisites

1. Guzli MCP connected; core skill available.
2. Permission to create contacts / segments / email campaigns.
3. Never invent emails, phones, or names.
4. Draft freely; **publish / run / email_*** that can deliver only with explicit approval for the first live send in a thread.

## Workflow

```
Email outreach:
- [ ] 1. Inventory campaigns / segments (reuse when possible)
- [ ] 2. Upsert contacts
- [ ] 3. Segment + version + materialize
- [ ] 4. Create or revise standing email campaign (draft)
- [ ] 5. Review revision; get approval before publish/run
- [ ] 6. Publish, enroll or segment-feed, verify enrollments
- [ ] 7. Report ids and whether anything was queued
```

### Gather

`list_campaigns`, `list_segments`, `list_lifecycle_stages`, `search_contacts` / `lookup_contact`.

### Contacts & segments

Create/update contacts with real `source_reason_code`.  
`get_segment_field_catalog` → `preview_segment` → create/publish version → `materialize_segment`.  
Prefer **segment audience** for ongoing intake; **explicit** for a fixed one-time set.

### Campaign draft

`create_email_campaign` or `revise_campaign`. Strategy-oriented names. Typical required shape: agent id, audience policy, subject, body, tenant postal address, purpose (`marketing` | `transactional`), admission policy. Caps + quiet hours for cold-ish outreach. Save `campaign_id` and `revision_id`.

### Review → publish → verify

`get_campaign` + `get_campaign_revision`. Summarize for the user. After approval: publish, enroll, then `get_campaign_enrollment_summary` / `list_campaign_enrollments`. Fix typed **not_enrolled** reasons.

## Hard rules

1. No one-campaign-per-contact.
2. No invented contact data.
3. No silent live sends.
4. Prefer reuse over near-duplicate campaigns/segments.
5. Voice dialing → skill **`guzli-mcp-voice-campaigns`**, not this skill.
6. Keep private lists/goals out of shared notes.

## Verify

Standing campaign visible via `list_campaigns`; segment members look right; enrollment counts match intent; user knows **draft only** vs **queued/sent**.

## Anti-patterns

`send_email` loops over a CSV; new campaign per daily batch; publish before revision review; using this skill for voice.
