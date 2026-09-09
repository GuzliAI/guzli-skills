# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking.

# Guzli MCP — voice campaign tools

Confirm live schemas. Shared contact/segment tools: [core tool map](../../guzli-mcp-core/references/tool-map.md).

| Remote name | Role |
|---|---|
| `create_voice_campaign` | Create draft voice campaign |
| `publish_voice_campaign` | Readiness check + publish revision |
| `run_voice_campaign` | Start published revision |
| `revise_campaign` | May apply when revising definitions (confirm schema) |
| `list_campaigns` / `get_campaign` / `get_campaign_revision` | Inventory / inspect when available |
| `enroll_campaign_contacts` | Enroll into published campaign when supported |
| `get_campaign_enrollment_summary` | Enrollment dispositions |
| `campaign_measurement` | Measurement when applicable |

Voice step config (profile overrides, dial permissions, voicemail, IVR, etc.) lives on revision/channel payloads — always re-read the tool schema; do not copy stale field lists from memory.
