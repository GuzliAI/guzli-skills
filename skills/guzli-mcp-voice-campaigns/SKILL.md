---
name: guzli-mcp-voice-campaigns
description: >-
  Places phone calls and runs voice campaigns through Guzli MCP: one-call dialing,
  campaigns with call instructions and structured answer extraction, results and
  webhooks. Use when the task is outbound calling, voice campaign setup, or reading
  what a call captured. Do not use for email (see guzli-mcp-email-outreach).
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
    tags: [Guzli, MCP, Voice, Campaigns]
    related_skills: [guzli-mcp-core, guzli-mcp-email-outreach]
---

# Guzli MCP voice campaigns

Install and follow **`guzli-mcp-core`** first. Email is skill **`guzli-mcp-email-outreach`**. Tool map: [references/tool-map.md](references/tool-map.md).

Every voice campaign is a campaign like email: contacts or a segment as the audience, a revision with one voice step, caps, readiness, publish, enroll, run. The agent talks as itself, using the voice profile of the agent. Every call carries your call instructions, and optionally a list of answers to collect.

## What you need before any call

| Fact | How to get it |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| `number_pool_id` | `list_telephony_number_pools` → an active pool with at least one active member. There is no default pool. Without it readiness says `number_pool_missing` |
| `voice_profile_id` | `list_voice_profiles` → the agent's profile (ambience, voice, no reasoning). Set it on the campaign step so calls sound like the agent's inbound calls |
| Contact ids with real E.164 phones | `search_contacts` / `create_contact` |
| `cap_policy.maximum_daily_channel_units` | You choose it. Required to publish. Usually also `maximum_enrollments` |
| `admission_policy` | Two labels you choose, e.g. `{"subject_key":"organization","effect_key":"voice.dial:<campaign-name>"}` |
| User approval | Ask before the first live dial in a thread |

## Consent before any call (required)

Every campaign call is checked against a recorded permission for the contact, channel `voice_twilio` and purpose `marketing` (the purpose every voice campaign tool sets). Without one the attempt fails with `permission_missing` and no call is placed.

1. Check: `list_contact_permission_heads {"path": {"contact_id": "<contact uuid>"}}` → you need an item with `channel_key: "voice_twilio"`, `purpose: "marketing"`, `state: "active"`.
2. If missing, confirm the basis with the user and record it. Tested body (all fields required; `notice_text_digest` is the SHA-256 hex of the consent statement you are recording; the `*_ref`/`*_id` strings are your audit labels):
   ```json
   capture_operator_permission {
     "path": {"contact_id": "<contact uuid>"},
     "body": {
       "identifier_type": "phone", "identifier_value": "+12025550123",
       "channel_key": "voice_twilio", "purpose": "marketing",
       "basis_key": "existing_relationship",
       "captured_at": "2026-09-11T14:00:00Z", "expires_at": null,
       "source_ref": "operator confirmation in chat 2026-09-11",
       "notice_text_digest": "<64 hex chars>", "notice_version": "chat-v1",
       "tenant_compliance_profile_version": 1,
       "evidence_ref": "chat 2026-09-11 user message", "attribution_ref": "operator:<user email>",
       "causation_id": "consent-<contact uuid>", "correlation_id": "<campaign name>"
     }
   }
   ```
   `identifier_value` is the E.164 number the campaign will dial. Bases for marketing: `explicit_opt_in`, `existing_relationship` (`cold_b2b` only if the organisation allows it; the usual allowed set is `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`). For `call_phone_number` the contact is created from the number, so create or look up the contact first (`search_contacts` / `create_contact`) and record the permission on it before dialing.
3. Never record a permission the user did not confirm.

## Which path

Every call carries a script: `call_instructions` is required on `call_phone_number`, `call_contacts` and `call_segment`, and optional on `create_voice_campaign` (a draft; add it with `revise_campaign` before publishing). All four also take `initial_message` (optional opening line) and `post_call_extraction` (optional answer schema). Path A does the whole chain in one call; Path B builds it step by step when you want to inspect or edit the draft first.

## Path A — one call with script and extraction

```json
call_phone_number {
  "name": "Survey Sept — one call",
  "agent_id": "<agent uuid>",
  "phone_number": "+12025550123",
  "number_pool_id": "<pool uuid>",
  "voice_profile_id": "<profile uuid>",
  "admission_policy": {"subject_key": "organization", "effect_key": "voice.dial:survey-sept"},
  "cap_policy": {"maximum_daily_channel_units": 2, "maximum_enrollments": 2},
  "call_instructions": "Ask the person, one question at a time, for their full name, the best phone number to reach them on, and their favourite colour. Confirm each answer briefly. Once you have all three and have recorded them, ask whether there is anything else you can help with. If not, thank them, say a proper goodbye, and end the call.",
  "post_call_extraction": {
    "is_enabled": true, "schema_name": "survey",
    "fields": [
      {"field_key": "full_name", "label": "Full name", "value_type": "text", "required": true},
      {"field_key": "phone_number", "label": "Best phone number", "value_type": "phone", "required": true},
      {"field_key": "favourite_colour", "label": "Favourite colour", "value_type": "text", "required": true}],
    "require_schema_validation": true, "allow_partial": true}
}
```

Response: `status: "queued"`, `campaign_id`, `campaign_revision_id`, `accepted_enrollment_ids`. `call_contacts` (`contact_ids`) and `call_segment` (`segment_id`) take the same fields. Leave out `post_call_extraction` when you only need the call and its automatic summary. A blank or missing `call_instructions` is refused with `invalid_workflow_request` before anything is created.

## Path B — step by step (tested sequence)

Use this when you want to review or edit the draft before it publishes. `create_voice_campaign` accepts `call_instructions`, `initial_message` and `post_call_extraction` directly; the edit step below is only needed when you left them out or want to change them.

1. **Create the draft**
   ```json
   create_voice_campaign {
     "name": "Survey Sept", "agent_id": "<agent uuid>",
     "audience_policy": {"kind": "explicit"},
     "number_pool_id": "<pool uuid>",
     "admission_policy": {"subject_key": "organization", "effect_key": "voice.dial:survey-sept"},
     "cap_policy": {"maximum_daily_channel_units": 50, "maximum_enrollments": 50}
   }
   ```
   Keep `campaign_id`, `revision_id` (this is the draft) and `lock_version`.

2. **Read the draft**: `get_campaign_revision {"path": {"campaign_id", "revision_id"}}` → `definition`.

3. **Edit `definition.steps[0].channel_config`** (it has `"channel": "voice"`):
   - `call_instructions`: plain prose. Tested wording: *"Ask the person, one question at a time, for their full name, the best phone number to reach them on, and their favourite colour. Confirm each answer briefly. Once you have all three and have recorded them, ask whether there is anything else you can help with. If not, thank them, say a proper goodbye, and end the call."*
   - `post_call_extraction`:
     ```json
     {"is_enabled": true, "schema_name": "survey",
      "fields": [
        {"field_key": "full_name", "label": "Full name", "value_type": "text", "required": true},
        {"field_key": "phone_number", "label": "Best phone number", "value_type": "phone", "required": true},
        {"field_key": "favourite_colour", "label": "Favourite colour", "value_type": "text", "required": true}],
      "require_schema_validation": true, "allow_partial": true}
     ```
     `value_type` is one of `text|number|boolean|date|datetime|email|phone|url|enum` (`enum` needs `enum_values`).
   - `voice_profile_id`: the agent's profile id.
   - **Delete** `extraction_schema_version_id` (server-owned).
   - Keep every step's `step_id` exactly as read. Never paste step ids from another revision.

4. **Revise — this also publishes**
   ```json
   revise_campaign {"campaign_id": "<id>", "source_revision_id": "<revision_id>",
                    "existing_draft_revision_id": "<revision_id>", "draft": <the edited definition>}
   ```
   Send only fields the tool schema declares (drop anything the schema rejects). The response carries `ready` and readiness `reasons`; `sending_identity_not_ready` as a *warning* is fine. **Do not call `publish_voice_campaign` after `revise_campaign`.** The revision is already published.

5. **Enroll**: `enroll_campaign_contacts {"campaign_id", "contact_ids": ["<contact uuid>"], "requested_at": "<ISO time>"}` → `disposition: "enrolled"`.

6. **Run**: `run_voice_campaign {"campaign_id", "revision_id"}` → `status: "queued"`, `accepted_enrollment_ids`. The dial happens within about a minute.

7. **Watch**: `list_campaign_call_attempts {"path": {"campaign_id"}}` → `in_progress` → `completed` with `duration_seconds`.

## What happens on the call

- Your `call_instructions` are placed in the agent's system prompt as a "Campaign call instructions" section; the agent follows them from the first turn. Write them as instructions to the agent ("You are calling on behalf of … Ask …"), not as a description.
- No opening line is spoken unless the campaign selects one. The agent starts from your instructions.
- The agent asks, confirms, and records the answers with its capture tool as it goes (live collection, on by default).
- The agent ends the call itself: it says goodbye in its own words and calls the end tool. The goodbye is played in full before the hang-up.
- Tested result: a 2-minute call, three answers captured exactly as spoken, "anything else?" asked, goodbye spoken, call ended by the agent.

## Reading the answers

- `list_campaign_extraction_results {"path": {"campaign_id"}}` and `get_campaign_extraction_result` → `status`, `extraction_results` (your field keys → values), `schema_name`, `voice_session_id`, `campaign_call_attempt_id`.
- Webhook: subscribe an endpoint to the `voice_session_status` event. After the call completes you receive `status`, `campaign_id`, `provider_call_id`, `duration_seconds`, `recording_url`, `prospect`, and `post_call_extraction` with `structured_data` (same values), `status`, `validation_errors`, `source`.

## Call summary (automatic)

Every call also gets a written summary without any setup: after the call the engine writes `post_event_summary` onto the call attempt with `headline`, `topic`, `intent`, `situation`, `customer_ask`, `outcome`, `outcome_tag`. Read it with `list_campaign_call_attempts` / `get_campaign_call_attempt`. It is produced shortly after the call ends, so it is not part of the `voice_session_status` webhook payload; poll the attempt if you need it. Do not add a "summary" extraction field to get one.

## Rules that save you a round trip

- One call per recipient per 24 hours. A second attempt is held with reason `pacing.recipient_rolling_cap` and a retry time. This is a product rule, not an error; do not poll it — use another consented recipient or wait for the retry time.
- `revise_campaign` publishes. Calling `publish_voice_campaign` afterwards is a mistake.
- Explicit audience → you enroll. Segment audience → segment automation enrolls; `enroll_campaign_contacts` is refused with `campaign_enrollment_explicit_audience_required`.
- Readiness codes: `number_pool_missing` (add the pool), `campaign_daily_missing` (set the daily cap), `sending_identity_not_ready` as an error (pool inactive or no active member: pick another pool), `send_platform_unavailable` / `send_platform_integration_mismatch` / `send_platform_ambiguous` (the agent's voice integration needs fixing in the dashboard).
- Every recipient needs an active `voice_twilio` / `marketing` permission before the run (section above).
- Few standing campaigns, many enrollments. Never one campaign per phone number.

## Verify

Every recipient has an active `voice_twilio` marketing permission; readiness had no error reasons; the run returned `queued` with your enrollment id; the call attempt reached `completed`; the extraction result holds the answers; the user has campaign id, revision id and the outcome.

## Anti-patterns

Publishing without `number_pool_id`; omitting the daily cap; a second publish after `revise_campaign`; pasting `extraction_schema_version_id` or foreign `step_id`s into a draft; dialing before the permission check; recording a permission the user did not confirm; enrolling contacts on a segment campaign; inventing pool, profile or contact ids; using email tools for calls; retrying a dial that is held by the 24-hour cap.
