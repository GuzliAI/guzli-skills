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

Every voice campaign is a campaign like email: contacts or a segment as the audience, a revision with one voice step, caps, readiness, publish, enroll, run. The agent talks as itself, using the voice profile of the agent. You can give it call instructions and a list of answers to collect.

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

## Path A — one call, no script: `call_phone_number`

Creates, publishes, enrolls and runs a one-recipient campaign in one call. The agent just talks as itself. There are **no call instructions and no answer extraction** on this path.

```json
call_phone_number {
  "name": "Call Jane",
  "agent_id": "<agent uuid>",
  "phone_number": "+12025550123",
  "number_pool_id": "<pool uuid>",
  "admission_policy": {"subject_key": "organization", "effect_key": "voice.dial:call-jane"},
  "cap_policy": {"maximum_daily_channel_units": 2, "maximum_enrollments": 2}
}
```

Response: `status: "queued"`, `campaign_id`, `campaign_revision_id`, `accepted_enrollment_ids`. `call_contacts` (contact ids) and `call_segment` (a segment) are the same shape for more than one recipient.

## Path B — campaign with instructions and answer extraction (tested sequence)

Use this when the agent must ask specific things and you want the answers back as structured data.

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

- No opening line is spoken unless the campaign selects one. The agent starts from your instructions.
- The agent asks, confirms, and records the answers with its capture tool as it goes (live collection, on by default).
- The agent ends the call itself: it says goodbye in its own words and calls the end tool. The goodbye is played in full before the hang-up.
- Tested result: a 2-minute call, three answers captured exactly as spoken, "anything else?" asked, goodbye spoken, call ended by the agent.

## Reading the answers

- `list_campaign_extraction_results {"path": {"campaign_id"}}` and `get_campaign_extraction_result` → `status`, `extraction_results` (your field keys → values), `schema_name`, `voice_session_id`, `campaign_call_attempt_id`.
- Webhook: subscribe an endpoint to the `voice_session_status` event. After the call completes you receive `status`, `campaign_id`, `provider_call_id`, `duration_seconds`, `recording_url`, `prospect`, and `post_call_extraction` with `structured_data` (same values), `status`, `validation_errors`, `source`.

## Rules that save you a round trip

- One call per recipient per 24 hours. A second attempt is held with reason `pacing.recipient_rolling_cap` and a retry time. This is a product rule, not an error.
- `revise_campaign` publishes. Calling `publish_voice_campaign` afterwards is a mistake.
- Explicit audience → you enroll. Segment audience → segment automation enrolls; `enroll_campaign_contacts` is refused with `campaign_enrollment_explicit_audience_required`.
- Readiness codes: `number_pool_missing` (add the pool), `campaign_daily_missing` (set the daily cap), `sending_identity_not_ready` as an error (pool inactive or no active member: pick another pool), `send_platform_unavailable` / `send_platform_integration_mismatch` / `send_platform_ambiguous` (the agent's voice integration needs fixing in the dashboard).
- Path A for a quick call; Path B whenever the call has a script or answers to collect.
- Few standing campaigns, many enrollments. Never one campaign per phone number.

## Verify

Readiness had no error reasons; the run returned `queued` with your enrollment id; the call attempt reached `completed`; the extraction result holds the answers; the user has campaign id, revision id and the outcome.

## Anti-patterns

Publishing without `number_pool_id`; omitting the daily cap; a second publish after `revise_campaign`; pasting `extraction_schema_version_id` or foreign `step_id`s into a draft; expecting `call_phone_number` to follow a script; enrolling contacts on a segment campaign; inventing pool, profile or contact ids; using email tools for calls; retrying a dial that is held by the 24-hour cap.
