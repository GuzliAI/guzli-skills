---
name: guzli-mcp-email-outreach
description: >-
  Runs outbound email outreach through Guzli MCP using standing campaigns,
  segments, and contacts—not one-off sends. Use when the Guzli MCP connector is
  available and the task is email outreach, email campaigns, segment-fed
  enrollments, or turning a researched lead list into Guzli email campaigns.
  Do not use for voice campaigns (see guzli-mcp-voice-campaigns), website copy,
  SEO, directory submissions, or a single transactional email outside a campaign.
---

# Guzli MCP email outreach

Requires shared primitives from [guzli-mcp-core](../guzli-mcp-core/SKILL.md). Tool map: [references/tool-map.md](references/tool-map.md).

Run outbound **email** through Guzli MCP as **standing campaigns** fed by **segments** and **contacts**. Prefer the campaign system over looping `send_email`.

## Default model (non-negotiable)

1. **Few long-lived campaigns** per strategy — not one campaign per contact or per batch.
2. **Keep feeding contacts** into the segment (or enroll into an already-published campaign). The campaign owns caps, quiet hours, and send policy.
3. **Personalization lives on the contact** (custom attributes / supported macros). Campaign body stays shared template text.
4. **`send_email` is for a single explicit one-off**, never for list outreach.

## Prerequisites

1. Guzli MCP connected; read [guzli-mcp-core](../guzli-mcp-core/SKILL.md) first if needed.
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

- `list_campaigns`, `list_segments`, `list_lifecycle_stages`
- `search_contacts` / `lookup_contact` — avoid duplicates

### Contacts & segments

- Create/update contacts with real `source_reason_code`.
- `get_segment_field_catalog` → `preview_segment` → `create_segment` / version → publish → `materialize_segment`.
- Prefer **segment audience** for ongoing intake; **explicit** audience for a fixed one-time set.

### Campaign draft

- `create_email_campaign` or `revise_campaign`.
- Strategy-oriented names (not “batch-17”).
- Typical required shape: agent id, audience policy, subject, body, tenant postal address, purpose (`marketing` | `transactional`), admission policy.
- Cap enrollments / daily units; enable quiet hours for cold-ish outreach.
- Save `campaign_id` and `revision_id`.

### Review → publish → verify

- `get_campaign` + `get_campaign_revision`.
- Summarize for the user: who, subject, segment vs explicit, send risk.
- After approval: publish, enroll (`enroll_campaign_contacts` and/or segment entry), then `get_campaign_enrollment_summary` / `list_campaign_enrollments`.
- Fix typed **not_enrolled** reasons (missing identifier, channel mismatch, etc.).

## Hard rules

1. No one-campaign-per-contact.
2. No invented contact data.
3. No silent live sends.
4. Prefer reuse over near-duplicate campaigns/segments.
5. Keep org-private lists and goals out of shared notes.

## Verify

Standing campaign visible via `list_campaigns`; segment members look right; enrollment counts match intent; user knows **draft only** vs **queued/sent**.

## Anti-patterns

- `send_email` in a loop over a CSV.
- New campaign per daily batch.
- Publish before revision review.
- Using this skill for voice dial campaigns.
