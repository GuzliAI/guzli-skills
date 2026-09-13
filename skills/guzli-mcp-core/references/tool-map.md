# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking. Guzli serves **workflow** tools (one call, several steps) and **operation** tools (`verb_object`, direct engine reads/writes). Confirm live schemas on the connected server. This map covers both copilot and tenant surfaces. Copilot inputs are flat; registry-only operations require their exposed transport schema.

## Connector

- MCP URL: `https://mcp.guzli.com/mcp`
- OAuth AS: `https://gateway.guzli.com`

## Contacts & lifecycle

| Remote name | Layer | Role |
|---|---|---|
| `create_contact` | operation | Create or resolve contact |
| `update_contact` | operation | Patch profile / self-serve scalar custom attributes |
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
| `update_campaign_draft_step` | workflow | Patch one draft step with `expected_lock_version`; never publishes |
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
| `send_email` | workflow | Single email with required text |

<!-- Engine 704e0b48e audit: tests/fixtures/copilot_schema_budget/current_served_catalog.json (served names and flat inputs); contracts/mcp-registry/generated/package-workflows.json (workflow inputs and composition); contracts/mcp-registry/generated/engine-primitives.json (operation names and transport schemas). Permission defaults: tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py. Legacy codes absent from generated schemas were checked in pinned implementation/tests; full token inventory is in the release RESULT artifact. -->

## One-off calls and held status

| Remote name | Role |
|---|---|
| `call_contact_now` | One operator-directed recipient; required `call_instructions`, `idempotency_key` |
| `get_call` / `list_calls` | One-off and campaign call outcomes |
| `get_operation_status` | Poll only the `held_call_id` from `held_for_approval`; registry input is `path.operation_id` |

<!-- Additions verified at 704e0b48e against tests/fixtures/copilot_schema_budget/current_served_catalog.json and contracts/mcp-registry/generated/package-workflows.json. Runtime details and their supplemental source citations are in the corresponding SKILL.md sections. -->

## Registry-only availability in this snapshot

Absent from the served copilot fixture: `apply_contact_tag`, `buy_managed_phone_number`, `call_instructions`, `get_campaign_revision_readiness`, `get_operation_status`, `list_campaign_revision_attempts`, `list_campaign_revisions`, `list_contact_tags`, `list_contacts`, `list_telephony_phone_numbers`, `pause_campaign`, `release_managed_phone_number`, `remove_contact_tag`, `resume_campaign`, `search_managed_phone_numbers`. Use only if tools/list exposes them; do not infer availability from this map.
