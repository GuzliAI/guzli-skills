# Host note

Tool names below are **remote** Guzli MCP names. Your host may prefix them; match on the remote name. Confirm live schemas.

## One-off

| Remote name | Role |
|---|---|
| `send_email` | One email from the agent's address: `to`, `subject`, `body_text`. May return `held_for_approval` under the agent's approval policy |

## One-call campaign workflows

| Remote name | Role |
|---|---|
| `email_contacts` | Create + publish + enroll + queue for explicit `contact_ids` |
| `email_segment` | Same for `segment_id` + `segment_version_id` + `maximum_age_seconds` (materializes first) |

## Step by step

| Remote name | Role |
|---|---|
| `create_email_campaign` | Draft: `name`, `agent_id`, `audience_policy`, `subject`, `body_text`, `tenant_postal_address`, `purpose`, `admission_policy`, `cap_policy` (+ `link`, `description`, `quiet_hours_policy`, `schedule_policy`, `sending_identity`) → `campaign_id`, `revision_id`, `lock_version` |
| `get_campaign_revision_readiness` | Readiness reasons (operation) |
| `publish_email_campaign` | `campaign_id`, `revision_id`, `expected_lock_version` |
| `revise_campaign` | Replace the draft and publish it (`campaign_id`, `source_revision_id`, `existing_draft_revision_id`, `draft`) |
| `enroll_campaign_contacts` | Explicit audiences: `campaign_id`, `contact_ids`, `requested_at` |
| `run_email_campaign` | `campaign_id`, `revision_id`, and exactly one of `all_active: true` / `enrollment_ids` |
| `list_campaign_enrollments` / `get_campaign_enrollment_summary` | Enrollment dispositions |
| `get_campaign_activity` | What was sent / queued / held |

## Permissions (operations; when the step requires permission)

| Remote name | Role |
|---|---|
| `list_contact_permission_heads` | `{"contact_id"}` → active permissions per channel and purpose |
| `capture_operator_permission` | `{"contact_id", ...permission fields}` → records one; body in SKILL.md consent section |

## Segments and contacts (operations)

`get_segment_field_catalog`, `create_segment`, `materialize_segment`, `get_segment_readiness`, `list_segment_members`, `search_contacts`, `lookup_contact`, `create_contact`, `update_contact`, `list_campaigns`, `get_campaign`, `get_campaign_revision`.

## Email step `channel_config` / step keys you will use

`subject`, `body_text`, `link`, `unsubscribe_requirement` (`required` or `optional`; email manifest default is `optional`), `sending_identity` (`{"selection":"agent_default"}`), `permission_requirement`. Server-owned fields are never sent back.

<!-- Engine 704e0b48e audit: tests/fixtures/copilot_schema_budget/current_served_catalog.json (served names and flat inputs); contracts/mcp-registry/generated/package-workflows.json (workflow inputs and composition); contracts/mcp-registry/generated/engine-primitives.json (operation names and transport schemas). Permission defaults: tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py. Legacy codes absent from generated schemas were checked in pinned implementation/tests; full token inventory is in the release RESULT artifact. -->
