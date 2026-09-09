# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking.

# Guzli MCP — voice campaign tools

Confirm live schemas. Shared contact/segment tools: [core tool map](../../guzli-mcp-core/references/tool-map.md).

| Remote name | Role |
|---|---|
| `create_voice_campaign` | Create draft voice campaign (`name`, optional `voice_profile_id`) |
| `publish_voice_campaign` | Readiness check + publish (`campaign_id`, `revision_id`, `expected_lock_version`, `agent_id`) |
| `run_voice_campaign` | Start published revision |
| `revise_campaign` | Replace draft definition (re-read schema; send a complete draft) |
| `list_campaigns` / `get_campaign` / `get_campaign_revision` | Inventory / inspect |
| `enroll_campaign_contacts` | Enroll into **active published** explicit-audience campaign |
| `get_campaign_enrollment_summary` / `list_campaign_enrollments` | Enrollment dispositions |
| `campaign_measurement` | Measurement when applicable |

Voice step config (profile, dial permissions, voicemail, IVR, etc.) lives on revision/channel payloads — always re-read the tool schema.
