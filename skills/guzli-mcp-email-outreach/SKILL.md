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
  Muse, Hermes Agent, and other compatible agents.
metadata:
  author: Guzli
  version: "1.4.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  hermes:
    tags: [Guzli, MCP, Email, Campaigns, Outreach]
    related_skills: [guzli-mcp-core, guzli-mcp-voice-campaigns]
---
# Guzli MCP email outreach

Install and follow **`guzli-mcp-core`** first. Tool map: [references/tool-map.md](references/tool-map.md).

Run outbound **email** as **standing campaigns** fed by **segments** and **contacts**. Prefer campaigns over looping `send_email` for list work.

Use your host’s MCP tool caller against the connected Guzli server. Prefer **remote tool names**. Re-read each tool’s input schema before calling.

## How campaigns should run

1. **One standing segment per cohort** (strategy name, not a batch id). Prefer durable predicates (domain, lifecycle, tags) over one-off address lists when the cohort is ongoing.
2. **One standing campaign per strategy** with audience `kind: segment` and `enroll_on_segment_entry: true`. Keep feeding matching contacts into the segment over time.
3. **Few campaigns total** — never one campaign per contact or per CSV drop.
4. **Personalization on the contact**, only with configured custom-attribute keys. **Omit `custom_attributes`** on create/update unless the org catalog (or a tool refusal) names an allowed key. An empty configured-key set means the org has none — do not invent keys.
5. **`send_email` is one-off only** (a single verify or hot reply). Not for list outreach.
6. **Audience → enrollment split:**
   - **Segment audience:** populated by segment automation (publish-time sweep of the pinned materialization, then later segment-entry facts). Do **not** call `enroll_campaign_contacts`.
   - **Explicit audience:** after publish, call `enroll_campaign_contacts` with the contact ids.
7. **Pacing:** set `cap_policy.maximum_daily_channel_units` before publish (required). Usually also set `maximum_enrollments`.
8. **Queue:** after publish and enrollments are in place, call `run_email_campaign` to queue sends. Report ids and status to the user.

## Required facts before create

| Fact | Source |
|---|---|
| `agent_id` | Existing `list_campaigns` row, or the user’s Guzli agent id |
| `tenant_postal_address` | Org mailing address |
| `admission_policy` | Typically `subject_key: organization`, `effect_key: email.send` |
| `purpose` | `marketing` or `transactional` |
| Caps | **`maximum_daily_channel_units`** (required) and usually `maximum_enrollments` |

## Canonical workflow (segment-fed)

```
- [ ] 1. search / create contacts (real emails only; omit custom_attributes unless allowed)
- [ ] 2. get_segment_field_catalog
- [ ] 3. create_segment (publish=true) with a valid expression
- [ ] 4. materialize_segment → confirm matched count; keep segment_materialization_id
- [ ] 5. create_email_campaign with audience kind=segment + daily channel units
- [ ] 6. publish_email_campaign (expected_lock_version from create)
- [ ] 7. Confirm enrollments via list_campaign_enrollments / get_campaign_enrollment_summary
- [ ] 8. run_email_campaign (campaign_id + revision_id; all_active or enrollment_ids)
- [ ] 9. Report campaign/revision ids and whether mail was queued
```

### Explicit-audience variant

Use audience `{ "kind": "explicit" }`, publish, then `enroll_campaign_contacts` (`contact_ids`, `requested_at`, optional `request_id`), then `run_email_campaign`.

## Segment expressions

- Call `get_segment_field_catalog` first; only use listed `field_key` + `allowed_operators`.
- Every predicate needs a **client-generated** `predicate_id` (UUID).
- Value shape must match the field type, e.g. email `in`:

```json
{
  "kind": "predicate",
  "predicate_id": "<uuid>",
  "field_key": "contact.email",
  "operator": "in",
  "value": { "kind": "text_set", "value": ["person@example.com"] }
}
```

### Materialize

`materialize_segment` with `segment_id` + `segment_version_id`. Check `counts.matched`. Save the materialization `id`.

### Segment audience payload

```json
{
  "kind": "segment",
  "segment_version_id": "<version uuid>",
  "materialization_selection": "exact",
  "segment_materialization_id": "<materialization uuid>",
  "maximum_age_seconds": 300,
  "enroll_on_segment_entry": true,
  "unenroll_on_segment_exit": false
}
```

Use `current_at_publish` when you want whatever is current at publish instead of a pinned materialization.

### Publish

`publish_email_campaign`: `campaign_id`, `revision_id`, `expected_lock_version` (from create `lock_version`).

### Inspecting segment membership

`list_segment_members`: only declared arguments — `segment_id`, optional version, `limit`, `offset`. Do not pass undeclared fields such as `campaign_id`.

### Run

`run_email_campaign`: `campaign_id` + `revision_id`, and either `all_active: true` or `enrollment_ids`.

## Hard rules

1. No one-campaign-per-contact.
2. No invented contact data.
3. No silent live sends without user intent for that thread.
4. Prefer reuse of standing segments and campaigns.
5. Voice dialing → **`guzli-mcp-voice-campaigns`**.
6. Keep private lists and goals out of shared skill text.
7. OAuth: refresh tokens **single-flight** per session (see **guzli-mcp-core**).

## Verify checklist

- Segment matched count matches the intended cohort.
- Campaign is published / ready.
- Enrollment summary shows the expected contacts (segment automation or explicit enroll).
- User knows whether mail was queued via `run_email_campaign` or sent as a one-off via `send_email`.

## Anti-patterns

- Skipping `maximum_daily_channel_units`.
- Calling `enroll_campaign_contacts` on a segment-audience campaign.
- Passing undeclared arguments to `list_segment_members`.
- Omitting `predicate_id` on segment predicates.
- Stuffing unconfigured custom attribute keys onto contacts.
- Using `send_email` for list outreach.
- One campaign per contact or per batch file.
