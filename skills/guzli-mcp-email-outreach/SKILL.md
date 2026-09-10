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
  version: "1.5.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine MCP registry, 2026-09-10 (release 1.0.7 live; 1.0.8 pending)"
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
8. **Readiness first:** call `get_campaign_revision_readiness` before `publish_email_campaign`; it names every blocker (`campaign_daily_missing`, identity, artifact). Fix, then publish.
9. **Queue:** after publish and enrollments are in place, call `run_email_campaign` (`campaign_id`, `revision_id`, and exactly one of `all_active: true` or `enrollment_ids`). **On 1.0.7 this tool rejects every valid request with `invalid_workflow_request`** (engine defect, fixed in 1.0.8). Do not retry with other shapes; tell the user the queue step needs 1.0.8 and that `email_contacts` / `email_segment` are the one-call alternatives when they are authored fresh.
10. **One-call alternatives:** `email_contacts` (explicit contact ids) and `email_segment` (a materialized segment) create, publish and queue in a single call. Prefer them for a fresh cohort; prefer the step-by-step path when the user wants to review the draft first.

## Required facts before create

| Fact | Source |
|---|---|
| `agent_id` | Existing `list_campaigns` row, or the user’s Guzli agent id |
| `tenant_postal_address` | Org mailing address |
| `admission_policy` | `subject_key` and `effect_key` are **labels**, not identities. On 1.0.7 use a **unique `effect_key` per campaign** (for example `email.send:<campaign-name>`): two campaigns sharing a label collide at publish (`storage_operation_failed` on `campaign_revision_publish`). From 1.0.8 the engine namespaces the key per revision and any label works |
| `purpose` | `marketing` or `transactional` |
| Caps | **`maximum_daily_channel_units`** (required) and usually `maximum_enrollments` |

## Canonical workflow (segment-fed)

```
- [ ] 1. search / create contacts (real emails only; omit custom_attributes unless allowed)
- [ ] 2. get_segment_field_catalog
- [ ] 3. create_segment (publish=true) with a valid expression
- [ ] 4. materialize_segment → confirm matched count; keep segment_materialization_id
- [ ] 5. create_email_campaign with audience kind=segment + daily channel units + a unique effect_key label (1.0.7)
- [ ] 6. get_campaign_revision_readiness → no blockers → publish_email_campaign (expected_lock_version from create)
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

**1.0.7 caveat for pinned (`exact`) audiences:** a contact re-evaluated by segment automation between your materialization and the publish can be skipped by the publish sweep (engine defect, fixed in 1.0.8). Workaround on 1.0.7: materialize immediately before publishing, and check `get_campaign_enrollment_summary` against the segment's matched count; if a member is missing, prefer `current_at_publish` for that campaign.

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
- Calling `enroll_campaign_contacts` on a segment-audience campaign (the typed refusal `campaign_enrollment_explicit_audience_required` is intended).
- Round-tripping a revision read into `revise_campaign` without removing server-owned fields (`extraction_schema_version_id`).
- Reusing one `effect_key` label across campaigns on 1.0.7.
- Passing undeclared arguments to `list_segment_members`.
- Omitting `predicate_id` on segment predicates.
- Stuffing unconfigured custom attribute keys onto contacts.
- Using `send_email` for list outreach.
- One campaign per contact or per batch file.
