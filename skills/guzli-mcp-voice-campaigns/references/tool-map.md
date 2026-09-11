# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking. Confirm live schemas.

## One-call dial workflows (script required; extraction optional)

| Remote name | Role |
|---|---|
| `call_phone_number` | Create + publish + enroll + run for one E.164 number: `name`, `agent_id`, `phone_number`, `call_instructions` (required), `number_pool_id`, `admission_policy`, `cap_policy` (optional `initial_message`, `post_call_extraction`, `quiet_hours_policy`, `schedule_policy`, `voice_profile_id`) |
| `call_contacts` | Same for explicit `contact_ids` |
| `call_segment` | Same for a `segment_id` (materializes, creates, publishes, runs) |

## Step by step

| Remote name | Role |
|---|---|
| `create_voice_campaign` | Draft: `name`, `agent_id`, `audience_policy`, `number_pool_id`, `admission_policy`, `cap_policy` (optional `call_instructions`, `initial_message`, `post_call_extraction`, `quiet_hours_policy`, `schedule_policy`, `voice_profile_id`) → `campaign_id`, `revision_id`, `lock_version` |
| `get_campaign_revision` | Read the draft `definition` (operation) |
| `revise_campaign` | Replace the draft with the edited definition **and publish it**: `campaign_id`, `source_revision_id`, `existing_draft_revision_id` (= the draft), `draft`. Drop `extraction_schema_version_id`; keep the draft's own `step_id`s |
| `get_campaign_revision_readiness` | Readiness reasons (operation) |
| `publish_voice_campaign` | Publish a draft you did NOT revise (`campaign_id`, `revision_id`, `expected_lock_version`, `agent_id`). Never after `revise_campaign` |
| `enroll_campaign_contacts` | Explicit-audience campaigns: `campaign_id`, `contact_ids`, `requested_at` |
| `run_voice_campaign` | Start dialing: `campaign_id`, `revision_id` → `queued` |
| `list_campaign_call_attempts` / `get_campaign_call_attempt` | Dial attempts, outcomes, recording, and the automatic `post_event_summary` (operation) |
| `list_campaign_extraction_results` / `get_campaign_extraction_result` | Captured answers per call (operation) |
| `get_campaign_enrollment_summary` / `list_campaign_enrollments` | Enrollment dispositions |

## Permissions (operations; required before any run)

| Remote name | Role |
|---|---|
| `list_contact_permission_heads` | `{"path": {"contact_id"}}` → active permissions per channel and purpose |
| `capture_operator_permission` | `{"path": {"contact_id"}, "body": {...}}` → records one; body in SKILL.md "Consent before any call" |

## Discovery (operations)

| Remote name | Role |
|---|---|
| `list_telephony_number_pools` / `get_telephony_number_pool` | Caller-ID pools. Required for voice readiness; no default |
| `list_telephony_phone_numbers` | Owned numbers (pool members) |
| `list_voice_profiles` / `get_voice_profile` | Voice profiles; set the agent's on the campaign step |
| `search_managed_phone_numbers` / `buy_managed_phone_number` / `release_managed_phone_number` | Number inventory (costs money; confirm with the user) |

## Voice step `channel_config` keys you will use

`call_instructions` (prose), `post_call_extraction` (`is_enabled`, `schema_name`, `fields[]`, `require_schema_validation`, `allow_partial`), `voice_profile_id`, `number_pool_id`, `initial_message` (opening line, optional; none is spoken when unset), `end_call`, `voicemail_drop`, `ivr_mode`, `retry_policy`, `trust.call_reason`, `background_ambience`. `extraction_schema_version_id` is server-owned: never send it.

## Webhook

Event `voice_session_status` (subscribe an endpoint to it): `status`, `campaign_id`, `conversation_id`, `provider_call_id`, `duration_seconds`, `recording_url`, `prospect`, `post_call_extraction` {`structured_data`, `status`, `validation_errors`, `source`}.
