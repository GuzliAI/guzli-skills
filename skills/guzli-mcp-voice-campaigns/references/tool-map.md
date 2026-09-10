# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking. Confirm live schemas. Shared contact/segment/campaign tools: [core tool map](../../guzli-mcp-core/references/tool-map.md).

## One-call dial workflows

| Remote name | Role |
|---|---|
| `call_phone_number` | Create + publish + run for one E.164 number (`name`, `agent_id`, `phone_number`; 1.0.8: `number_pool_id`, `cap_policy`, `quiet_hours_policy`, `schedule_policy`, `admission_policy`, optional `voice_profile_id`) |
| `call_contacts` | Same for explicit `contact_ids` |
| `call_segment` | Same for a `segment_id` (materializes, creates, publishes, runs) |

## Step-by-step voice tools

| Remote name | Role |
|---|---|
| `create_voice_campaign` | Draft (1.0.7: `name`, optional `voice_profile_id`; 1.0.8: also `agent_id`, `audience_policy`, `number_pool_id`, `cap_policy`, `quiet_hours_policy`, `schedule_policy`, `admission_policy`) |
| `get_campaign_revision_readiness` | Blocking reasons before publish (operation) |
| `publish_voice_campaign` | Readiness check + publish (`campaign_id`, `revision_id`, `expected_lock_version`, `agent_id`) |
| `run_voice_campaign` | Start the published revision (`campaign_id`, `revision_id`) |
| `revise_campaign` | Replace the draft (complete draft; drop `extraction_schema_version_id`) |
| `enroll_campaign_contacts` | Explicit-audience campaigns only |
| `list_campaign_call_attempts` / `get_campaign_call_attempt` | Dial attempts and outcomes (operation) |
| `get_campaign_enrollment_summary` / `list_campaign_enrollments` | Enrollment dispositions |

## Discovery (operations)

| Remote name | Role |
|---|---|
| `list_telephony_number_pools` / `get_telephony_number_pool` | Caller-ID pools. **Required** for voice readiness; no default |
| `list_telephony_phone_numbers` | Owned numbers (pool members) |
| `list_voice_profiles` / `get_voice_profile` | Voice profiles (agent default applies when omitted) |
| `search_managed_phone_numbers` / `buy_managed_phone_number` / `release_managed_phone_number` | Number inventory (costs money; confirm with the user) |

Voice step config (profile, pool, dial permissions, voicemail, IVR) lives on the revision's step `channel_config`; always re-read the tool schema.
