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
  version: "1.2.0"
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

Use your host’s MCP tool caller against the connected Guzli server. Prefer **remote tool names**.

## Default model (how outreach should run)

1. **One standing segment per cohort** (strategy name, not “batch-17”). Expression usually matches emails / domains / lifecycle — not a pasted one-off ID list in the campaign.
2. **One standing campaign per strategy**, audience `kind: segment`, `enroll_on_segment_entry: true`. Keep feeding contacts that match the segment; rematerialize as the list grows.
3. **Few campaigns total** — never one campaign per contact or per daily CSV.
4. **Personalization on the contact** when the org has configured custom attribute keys. If `create_contact` / `update_contact` returns `invalid_contact_patch` with `unknown_key_count`, this org has **no** custom attributes configured — omit them (or configure keys in product first).
5. **`send_email` is for a single explicit one-off** (verify path, hot reply). Not for list outreach.

## Required facts before create

| Fact | How to get it |
|---|---|
| `agent_id` | From an existing `list_campaigns` row, or the user’s Guzli agent id |
| `tenant_postal_address` | Org mailing address (e.g. country + city/region) |
| `admission_policy` | Typically `subject_key: organization`, `effect_key: email.send` |
| `purpose` | `marketing` or `transactional` |
| Caps | Set **`maximum_daily_channel_units`** (required for publish in practice) and usually `maximum_enrollments` |

Publish fails with `readiness_blocked` / `cap_not_ready` / `campaign_daily_missing` if daily channel units are unset.

## Segment workflow (canonical)

```
Segment → campaign:
- [ ] 1. search/create contacts (real emails only)
- [ ] 2. get_segment_field_catalog
- [ ] 3. create_segment (publish=true) with valid expression
- [ ] 4. materialize_segment → confirm matched count
- [ ] 5. create_email_campaign with audience kind=segment
- [ ] 6. publish_email_campaign (lock_version from create)
- [ ] 7. Verify enrollments (segment entry and/or explicit enroll)
- [ ] 8. run_email_campaign when the engine accepts it; else report error
```

### Expression rules

- Call `get_segment_field_catalog` first; only use listed `field_key` + `allowed_operators`.
- Every predicate needs a **client-generated** `predicate_id` (UUID).
- Value shape must match type, e.g. email `in` → `{ "kind": "text_set", "value": ["a@x.com", "b@x.com"] }`.
- Example cohort (exact inboxes):

```json
{
  "kind": "predicate",
  "predicate_id": "<uuid>",
  "field_key": "contact.email",
  "operator": "in",
  "value": { "kind": "text_set", "value": ["person@example.com"] }
}
```

For ongoing outreach, prefer durable predicates (domain `contains`, lifecycle stage, tags) over editing the segment for every new address when possible — or version the segment when the allowlist grows.

### Materialize

- `materialize_segment` with `segment_id` + `segment_version_id`.
- Check `counts.matched`. Save `id` as `segment_materialization_id`.

### Campaign audience

Segment audience (standing):

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

`current_at_publish` is an alternative when you want “whatever is current at publish” instead of a pinned materialization.

Explicit audience (fixed set / ops twin):

```json
{ "kind": "explicit" }
```

Then `enroll_campaign_contacts` after publish. **`enroll_campaign_contacts` fails with `campaign_enrollment_explicit_audience_required` on segment-audience campaigns** — that is expected.

### Publish

`publish_email_campaign` needs `campaign_id`, `revision_id`, `expected_lock_version` (from create: `lock_version`).

### Enrollments after publish

- Segment campaigns: members enroll via **segment_entry** when `enroll_on_segment_entry` is true. Not every pre-existing matched contact always appears immediately — rematerialize and re-check `list_campaign_enrollments` / `get_campaign_enrollment_summary`.
- Explicit campaigns: `enroll_campaign_contacts` with `contact_ids`, `requested_at`, optional `request_id`.

### Run / queue

`run_email_campaign` requires `campaign_id` + `revision_id`, and either `all_active: true` or `enrollment_ids`.

If the tool returns `invalid_workflow_request` or `email_segment` returns `storage_operation_failed`, **do not pretend mail queued** — report the reason code, leave the published campaign + enrollments in place, and use `send_email` only if the user asked for a one-off verify. Escalation belongs with Guzli backend/Integrations.

## Hard rules

1. No one-campaign-per-contact.
2. No invented contact data.
3. No silent live sends without user intent for that thread.
4. Prefer reuse of standing segments/campaigns.
5. Voice dialing → **`guzli-mcp-voice-campaigns`**.
6. Keep private lists/goals out of shared skill text.

## Verify checklist

- Segment `matched` count equals intended cohort size.
- Campaign `state` is `published` (`ready: true`).
- Enrollment summary / list shows expected contacts (`disposition: enrolled` or segment_entry source).
- User knows whether mail was **provider_accepted** (send_email) vs **queued via run** vs **draft/published only**.

## Anti-patterns

- Skipping `maximum_daily_channel_units`.
- Calling `enroll_campaign_contacts` on a segment-audience campaign.
- Omitting `predicate_id` on segment predicates.
- Treating `run_email_campaign` success as delivery completion (it only queues).
- Stuffing unconfigured custom attribute keys onto contacts.
