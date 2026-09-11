---
name: guzli-mcp-core
description: >-
  Connects to and operates Guzli MCP for shared product concepts: the two tool
  layers, discovery of ids (agents, voice profiles, number pools, phone numbers),
  contacts, lifecycle stages, readiness checks, and connector hygiene. Use when
  setting up Guzli MCP, listing or debugging tools, creating or searching
  contacts, or before any campaign work. Do not use for the channel runbooks
  themselves (see guzli-mcp-email-outreach and guzli-mcp-voice-campaigns).
license: Apache-2.0
compatibility: >-
  Requires a host that supports Agent Skills (agentskills.io) and a connected
  Guzli MCP server at https://mcp.guzli.com/mcp (OAuth via gateway.guzli.com).
  Network access required. Works with Claude Code, Codex, Cursor, Grok, OpenClaw,
  Muse, Hermes Agent, and other compatible agents.
metadata:
  author: Guzli
  version: "1.6.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine release 1.0.8 (live-tested end to end)"
  hermes:
    tags: [Guzli, MCP, Contacts, CRM]
    related_skills: [guzli-mcp-email-outreach, guzli-mcp-voice-campaigns]
---

# Guzli MCP core

Portable foundation for Guzli MCP on any Agent Skills host. Channel runbooks:

- Email (one-off and campaigns) → skill **`guzli-mcp-email-outreach`**
- Phone calls and voice campaigns → skill **`guzli-mcp-voice-campaigns`**

Tool cheat sheet: [references/tool-map.md](references/tool-map.md).

## Host setup

1. Connect Guzli MCP (`https://mcp.guzli.com/mcp`, OAuth via gateway.guzli.com).
2. List the server's tools in your host; call them by **remote name** (example `search_contacts`). Hosts may prefix names; match on the suffix.
3. Read a tool's **input schema** before calling it. The server rejects undeclared arguments with `invalid_workflow_request` and the path of the offending field.

## The two tool layers

| Layer | What it is | Examples |
|---|---|---|
| **Workflows** (about 25) | One call that does several engine steps | `send_email`, `create_email_campaign`, `email_segment`, `call_phone_number`, `create_voice_campaign`, `revise_campaign`, `run_voice_campaign`, `enroll_campaign_contacts` |
| **Operations** (about 140) | Direct reads and writes, named `verb_object` | `list_campaigns`, `get_campaign_revision`, `get_campaign_revision_readiness`, `list_telephony_number_pools`, `list_voice_profiles`, `list_campaign_extraction_results` |

Use a workflow to act, an operation to find an id or check state.

## Where ids come from

| Need | Tool |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| Contacts | `search_contacts`, `lookup_contact`, `create_contact` |
| Voice profile | `list_voice_profiles` (the agent's profile) |
| Caller-ID number pool | `list_telephony_number_pools` (an active pool with an active member; there is no default) |
| Campaign state, `lock_version`, draft `definition` | `get_campaign`, `get_campaign_revision`, `list_campaign_revisions` |
| Readiness before publish | `get_campaign_revision_readiness` |
| Segments | `get_segment_field_catalog`, `create_segment`, `materialize_segment`, `get_segment_readiness`, `list_segment_members` |
| Call outcomes and captured answers | `list_campaign_call_attempts`, `list_campaign_extraction_results`, `get_campaign_extraction_result` |

## The campaign shape (same for email and voice)

`create_*_campaign` → (optional `get_campaign_revision` → edit → `revise_campaign`, which publishes) → or `get_campaign_revision_readiness` → `publish_*_campaign` → `enroll_campaign_contacts` (explicit audiences only) → `run_*_campaign` → check attempts / results. One-call shortcuts (`email_contacts`, `email_segment`, `call_phone_number`, `call_contacts`, `call_segment`) do the whole chain for a fresh cohort. The voice ones take the call script (`call_instructions`, required) and answer extraction directly.

## Consent before any campaign send (required)

Voice campaign sends are always checked against a recorded permission for that contact, channel `voice_twilio` and purpose `marketing`; email campaign sends are checked only when the step's `permission_requirement` is `"required"` (the email default is optional). No record on a checked step means the attempt fails with `permission_missing`. Before enrolling anyone into a checked campaign:

1. `list_contact_permission_heads {"path": {"contact_id": "<contact uuid>"}}` → `items[]` with `channel_key`, `purpose`, `basis_key`, `state`. You need an item with `state: "active"`, the channel you will use (`email`, or `voice_twilio` for calls) and the purpose of your campaign.
2. If there is none, ask the user on what basis this person may be contacted, then record it with `capture_operator_permission` (exact body in the email and voice skills). Bases: `explicit_opt_in`, `existing_relationship` (either purpose); `recipient_requested`, `contract_or_service`, `legal_obligation` (transactional only); `cold_b2b` (marketing only); `legitimate_interest`. The organisation's allowed bases are set in the dashboard; the usual set is `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`. A basis outside that set fails the send with `permission_basis_not_allowed`.
3. Never record a permission the user did not confirm. The record names who vouched for it.

## How refusals look

A refused call returns an error result. Its text is JSON: `{"reason_code": "…", …facts…}` such as `required`, `details`, `schema_path` or `engine_status`. That JSON is the whole answer; the fix is the named field. Do one corrected call, not a loop.

## Codes you will meet

| Code | Meaning | What to do |
|---|---|---|
| `campaign_daily_missing` | `cap_policy.maximum_daily_channel_units` unset | Set it (create or `revise_campaign`) |
| `number_pool_missing` | Voice step has no caller-ID pool | Pass `number_pool_id` |
| `sending_identity_not_ready` | As an error: sender/pool unusable. As a warning on a voice campaign: informational | Fix the sender or pool in the dashboard; warnings do not block |
| `campaign_enrollment_explicit_audience_required` | `enroll_campaign_contacts` on a segment campaign | Intended; segment automation enrolls |
| `pacing.recipient_rolling_cap` | A recipient was already called/emailed in the last 24 h | Product rule; the attempt is held with a retry time |
| `invalid_workflow_request` | Arguments rejected against the schema; `schema_path` names the field | Fix that field; do not retry blindly |
| `invalid_contact_patch` with `configured_attribute_keys: []` | Unknown custom attribute keys | Omit `custom_attributes` |
| `held_for_approval` | The agent's policy holds outbound actions for a human | Tell the user; a reviewer approves in the dashboard |
| `pacing.recipient_rolling_cap` (held) | The recipient was contacted on this channel in the last 24 h | Product rule; wait for the retry time or use another recipient |
| Any refusal | Comes back as an error result whose text is JSON with `reason_code` + facts | Read the JSON and act on the named field; never retry blindly |
| `permission_missing` / `permission_inactive` / `permission_basis_not_allowed` | No active permission for this contact, channel and purpose, or its basis is outside the organisation's allowed set | Record one with `capture_operator_permission` (see "Consent before any campaign send"); do not retry the same run |

## Contacts

`search_contacts` / `lookup_contact` before create. `create_contact` with a real `source_reason_code` (lowercase snake_case). Omit `custom_attributes` unless the org has configured keys. Never invent email, phone, or name. Phones are E.164.

## Lifecycle

`list_lifecycle_stages`, `get_contact_lifecycle_stage`, `list_contact_events` (evidence ids), `set_contact_lifecycle_stage` only with real `to_stage_id`, `evidence_event_ids`, `reason_codes`.

## Editing a draft: `revise_campaign`

Read the draft with `get_campaign_revision`, edit `definition`, send it back with `existing_draft_revision_id` set to that draft. Send only fields the schema declares, keep the draft's own `step_id`s, and never send server-owned fields (`extraction_schema_version_id`). `revise_campaign` publishes the revision; do not call `publish_*_campaign` afterwards.

## OAuth and parallel calls

The engine rotates refresh tokens once and rejects reuse. Refresh single-flight per session, then reuse the rotated tokens for parallel calls.

## Hard rules

1. No fabricated contact data.
2. No silent sending or dialing: confirm with the user before the first live send or dial in a thread.
3. Readiness before every publish; a permission record for every recipient of a consent-checked campaign (voice always; email when the step says required).
4. On a schema error, report the tool and the field; do not guess.
5. Channel details live in the sibling skills.

## Verify

A harmless read succeeds (`list_lifecycle_stages`, `search_contacts`, or `list_campaigns`) and the returned ids are reusable in the channel skills.
