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
  version: "1.7.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine 1.0.16 (704e0b48e)"
  hermes:
    tags: [Guzli, MCP, Voice, Campaigns]
    related_skills: [guzli-mcp-core, guzli-mcp-email-outreach]
---

# Guzli MCP voice campaigns

Install and follow **`guzli-mcp-core`** first. Email is skill **`guzli-mcp-email-outreach`**. Tool map: [references/tool-map.md](references/tool-map.md).

Every voice campaign is a campaign like email: contacts or a segment as the audience, a revision with one voice step, caps, readiness, publish, enroll, run. The agent talks as itself, using the voice profile of the agent. Every call carries your call instructions, and optionally a list of answers to collect.

## One-off call: `call_contact_now`

For an operator-directed call to one recipient, use `call_contact_now`. Supply exactly one of `contact_id` or E.164 `phone_number`, required nonblank `call_instructions` and required stable `idempotency_key`; optional fields are `initial_message`, `post_call_extraction`, `caller_number`.

```json
call_contact_now {"phone_number":"+12025550123","call_instructions":"Follow up on the information the person requested. Answer their questions and end the call when finished.","idempotency_key":"<stable key for this call>"}
```

Like `send_email`, this uses automatic posture with a tenant override that may hold for approval. It is operator-directed only, is not offered on customer chat, and refuses a missing operator principal with `initiating_principal_required` and `required.initiating_principal_kind: "operator"`. A held result is not completion; use core’s approval polling guidance.

It bypasses campaign pacing, quiet hours, campaign daily caps and campaign permission rows. Voice balance, plan entitlement (`calls_per_minute`, `calls_per_hour`, `calls_per_day`, `calls_per_month` and concurrency), destination restrictions and duplicate protection still apply. Keep the same key for the same intended call; inspect uncertain results rather than generating a new key.

Caller selection is an explicit eligible owned `caller_number`, otherwise the agent’s single eligible number. With none or several, the refusal is `caller_number_required`; an invalid explicit selection returns `caller_number_not_owned`. Both return `required.owned_numbers` as facts for choosing a caller. A number pool is a campaign requirement, not an argument to this tool.

Read the returned `call_id` with `get_call {"call_id":"<call id>"}` for outcome, summary and extraction, or `list_calls {"limit":50}` for the agent’s calls. Call-read refusals are `call_attempt_not_found` (404) and `one_off_call_result_missing` (503); report the typed result. Do not treat dispatch acceptance as a completed conversation.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json (call_contact_now/get_call/list_calls); engine/model_first/internal_mcp/call_contact_now_tool.py; engine/model_first/internal_mcp/call_contact_now.py; engine/model_first/internal_mcp/builtin_registrations.py (posture); campaigns/calls/one_off_refusal_contracts.py; tests/api/test_call_route_typed_refusals.py. -->

## What you need before a campaign call

| Fact | How to get it |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| `number_pool_id` | `list_telephony_number_pools` → an active pool with at least one active member. There is no default pool. Without it readiness says `number_pool_missing` |
| `voice_profile_id` | `list_voice_profiles` → the agent's profile (ambience, voice, no reasoning). Set it on the campaign step so calls sound like the agent's inbound calls |
| Contact ids with real E.164 phones | `search_contacts` / `create_contact` |
| `cap_policy.maximum_daily_channel_units` | You choose it. Required to publish. Usually also `maximum_enrollments` |
| `admission_policy` | Two labels you choose, e.g. `{"subject_key":"organization","effect_key":"voice.dial:<campaign-name>"}` |
| User approval | Ask before the first live dial in a thread |

## Consent before a permission-required campaign call

Voice campaign steps require recorded permission by default for channel `voice_twilio` and their `purpose` (`marketing` by default; `transactional` is also supported). Explicit `permission_requirement: "optional"` disables that campaign permission-row requirement. When permission is required, a missing record fails with `permission_missing` and no call is placed.

1. Check: `list_contact_permission_heads {"contact_id": "<contact uuid>"}` → you need an item with `channel_key: "voice_twilio"`, `purpose` matching the campaign, `state: "active"`.
2. If missing, confirm the basis with the user and record it. Flat copilot arguments (`expires_at` is optional; `notice_text_digest` is the SHA-256 hex of the consent statement you are recording; the `*_ref`/`*_id` strings are your audit labels):
   ```json
   capture_operator_permission {
     "contact_id": "<contact uuid>",
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
   ```
   `identifier_value` is the E.164 number the campaign will dial. Bases for marketing: `explicit_opt_in`, `existing_relationship` (`cold_b2b` only if the organisation allows it; the usual allowed set is `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`). For `call_phone_number` the contact is created from the number, so create or look up the contact first (`search_contacts` / `create_contact`) and record the permission on it before dialing.
3. Never record a permission the user did not confirm.

### Creation policy knobs

`create_voice_campaign`, `call_phone_number`, `call_contacts` and `call_segment` accept optional `permission_requirement` (`"required"` / `"optional"`) and `purpose` (`"marketing"` / `"transactional"`, default `"marketing"`). Omitted permission inherits the voice manifest’s **required** setting. Use the consent runbook for required steps and match its permission purpose to the campaign. Voice creation tools do not expose `unsubscribe_requirement`. These creation overrides are optional, not a claim that voice permission defaults off.

<!-- Sources at 704e0b48e: contracts/mcp-registry/generated/package-workflows.json; tests/fixtures/copilot_schema_budget/current_served_catalog.json; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py. -->

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

Field-only braces below are argument shorthand, not copy-ready JSON. Copilot inputs are flat. `get_campaign_revision_readiness` is a tenant registry operation absent from the served copilot fixture: use it only when exposed, or rely on the publish workflow’s built-in readiness check and fix its returned reasons.

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

2. **Read the draft**: `get_campaign_revision {"campaign_id", "revision_id"}` → `definition`.

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

6. **Run**: `run_voice_campaign {"campaign_id", "revision_id"}` → `status: "queued"`, `accepted_enrollment_ids`. Queued is not proof of a completed call; inspect the attempt.

7. **Watch**: `list_campaign_call_attempts {"campaign_id"}` → `in_progress` → `completed` with `duration_seconds`.

### Patch one draft step without publishing

Read `get_campaign_revision` and use its draft `step_id` and current `lock_version`:

```json
update_campaign_draft_step {"campaign_id":"<campaign uuid>","revision_id":"<draft uuid>","step_id":"<step uuid>","expected_lock_version":1,"patch":{"call_instructions":"Ask whether the requested follow-up resolved their question."}}
```

Replace the illustrative `1` with the version read. For voice content, use `call_instructions`, `initial_message`, `post_call_extraction`, and the step’s `permission_requirement`. The shared patch schema also exposes step-level `unsubscribe_requirement`; voice creation workflows do not. The tool never publishes; use its new lock version for the later publish. Stale input returns `campaign_revision_version_conflict`, `expected_lock_version`, `current_lock_version`, and `required_action: "reread_revision"`. Reread and reconcile; also reread after an uncertain write. Use `revise_campaign` for a complete-draft replacement that publishes, including changes beyond these patch fields.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json, update_campaign_draft_step/CampaignStepFieldPatch; contracts/mcp-registry/generated/package-workflows.json; campaigns/revisions/step_patch_refusals.py; campaigns/revisions/step_patch_manager.py; campaigns/revisions/step_patch.py; campaigns/revisions/step_patch_merge.py. -->

## What happens on the call

- No opening line is spoken unless the campaign selects one. The agent starts from your instructions.
- The agent asks, confirms, and records the answers with its capture tool as it goes (live collection, on by default).
- The agent ends the call itself: it says goodbye in its own words and calls the end tool. The goodbye is played in full before the hang-up.

## Reading the answers

- `list_campaign_extraction_results {"campaign_id"}` and `get_campaign_extraction_result` → `status`, `extraction_results` (your field keys → values), `schema_name`, `voice_session_id`, `campaign_call_attempt_id`.
- Webhook: subscribe an endpoint to the `voice_session_status` event. After the call completes you receive `status`, `campaign_id`, `provider_call_id`, `duration_seconds`, `recording_url`, `prospect`, and `post_call_extraction` with `structured_data` (same values), `status`, `validation_errors`, `source`.

## Call summary (automatic)

Every call also gets a written summary without any setup: after the call the engine writes `post_event_summary` onto the call attempt with `headline`, `topic`, `intent`, `situation`, `customer_ask`, `outcome`, `outcome_tag`. Read it with `list_campaign_call_attempts` / `get_campaign_call_attempt`. It is produced shortly after the call ends, so it is not part of the `voice_session_status` webhook payload; poll the attempt if you need it. Do not add a "summary" extraction field to get one.

## Rules that save you a round trip

- Campaign pacing: one call per recipient per 24 hours. A second attempt is held with reason `pacing.recipient_rolling_cap` and a retry time. This is a product rule, not an error.
- `revise_campaign` publishes. Calling `publish_voice_campaign` afterwards is a mistake.
- Explicit audience → you enroll. Segment audience → segment automation enrolls; `enroll_campaign_contacts` is refused with `campaign_enrollment_explicit_audience_required`.
- Readiness codes: `number_pool_missing` (add the pool), `campaign_daily_missing` (set the daily cap), `sending_identity_not_ready` as an error (pool inactive or no active member: pick another pool), `send_platform_unavailable` / `send_platform_integration_mismatch` / `send_platform_ambiguous` (the agent's voice integration needs fixing in the dashboard).
- Permission-required steps need active `voice_twilio` permission matching the campaign purpose before the run (section above).
- Few standing campaigns, many enrollments. Never one campaign per phone number.

## Verify

For permission-required steps, every recipient has active `voice_twilio` permission matching the campaign purpose; readiness had no error reasons; the run returned `queued` with your enrollment id; the call attempt reached `completed`; the extraction result holds the answers; the user has campaign id, revision id and the outcome.

## Anti-patterns

Publishing without `number_pool_id`; omitting the daily cap; a second publish after `revise_campaign`; pasting `extraction_schema_version_id` or foreign `step_id`s into a draft; running a permission-required campaign before its permission check; recording a permission the user did not confirm; enrolling contacts on a segment campaign; inventing pool, profile or contact ids; using email tools for calls; retrying a dial that is held by the 24-hour cap.

<!-- Engine 704e0b48e audit: tests/fixtures/copilot_schema_budget/current_served_catalog.json (served names and flat inputs); contracts/mcp-registry/generated/package-workflows.json (workflow inputs and composition); contracts/mcp-registry/generated/engine-primitives.json (operation names and transport schemas). Permission defaults: tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py. Legacy codes absent from generated schemas were checked in pinned implementation/tests; full token inventory is in the release RESULT artifact. -->

## Changelog

- **1.7.0 (2026-09-13)** — Adds operator-directed call_contact_now, caller selection, call reads and typed refusals; distinguishes campaign controls and purpose/permission knobs; documents nonpublishing draft-step patches.
