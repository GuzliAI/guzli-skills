# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking. Guzli serves **workflow** tools (one call, several steps) and **operation** tools (`verb_object`, direct engine reads/writes). Confirm live schemas on the connected server.

## Connector

- MCP URL: `https://mcp.guzli.com/mcp`
- OAuth AS: `https://gateway.guzli.com`

## Contacts & lifecycle

| Remote name | Layer | Role |
|---|---|---|
| `create_contact` | operation | Create or resolve contact |
| `update_contact` | operation | Patch profile / allowed custom attributes |
| `search_contacts` / `list_contacts` | operation | Find contacts |
| `lookup_contact` | operation | Resolve by id or identifier |
| `list_contact_events` | operation | Evidence events |
| `get_contact_lifecycle_stage` / `set_contact_lifecycle_stage` | operation | Stage read / move |
| `list_lifecycle_stages` | operation | Profile, stages, edges |
| `contact_digest` | operation | Bounded digest |
| `list_contact_tags` / `apply_contact_tag` / `remove_contact_tag` | operation | Tags |

## Segments (shared)

| Remote name | Layer | Role |
|---|---|---|
| `get_segment_field_catalog` | operation | Predicate catalog |
| `preview_segment` | operation | Dry run |
| `create_segment` / `create_segment_version` / `publish_segment_version` | operation | Author + publish |
| `list_segments` / `get_segment` / `list_segment_versions` | operation | Inventory |
| `materialize_segment` | operation | Compute membership (returns the materialization id) |
| `get_segment_readiness` | operation | Is the version usable |
| `list_segment_members` | operation | Current members page: `segment_id`, optional version, `limit`, `offset` only |
| `list_segment_entry_facts` | operation | Entry facts (what segment automation enrolls from) |

## Campaign inspection (shared by email and voice)

| Remote name | Layer | Role |
|---|---|---|
| `list_campaigns` / `get_campaign` | operation | Inventory; a source of `agent_id` |
| `get_campaign_revision` / `list_campaign_revisions` | operation | Revision definition, `lock_version` |
| `get_campaign_revision_readiness` | operation | **Blocking reasons before publish** |
| `get_campaign_enrollment_summary` / `list_campaign_enrollments` | operation | Enrollment dispositions and typed refusals |
| `list_campaign_revision_attempts` / `list_campaign_call_attempts` | operation | Send / call attempts |
| `pause_campaign` / `resume_campaign` | operation | Pause and resume |
| `campaign_measurement` | operation | Metrics |
| `revise_campaign` | workflow | Replace the draft (send a complete draft; drop server-owned fields such as `extraction_schema_version_id`) |
| `enroll_campaign_contacts` | workflow | Explicit-audience campaigns only |

## Telephony & voice discovery

| Remote name | Layer | Role |
|---|---|---|
| `list_voice_profiles` / `get_voice_profile` | operation | Voice profiles (the agent default applies when a voice tool omits `voice_profile_id`) |
| `list_telephony_number_pools` / `get_telephony_number_pool` | operation | **Caller-ID pools; required for voice publish; no default** |
| `list_telephony_phone_numbers` | operation | Owned numbers (pool members) |
| `search_managed_phone_numbers` / `buy_managed_phone_number` / `release_managed_phone_number` | workflow | Buy or release numbers (confirm with the user; these cost money) |

## One-off email (not campaigns)

| Remote name | Layer | Role |
|---|---|---|
| `send_email` | workflow | Single plain-text email |
