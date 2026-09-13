---
name: guzli-mcp-core
description: >-
  Connects to and operates Guzli MCP for shared product concepts: the two tool
  layers, discovery of ids (agents, voice profiles, number pools, phone numbers),
  contacts, lifecycle stages, readiness checks, and connector hygiene. Use when
  setting up Guzli MCP, listing or debugging tools, creating or searching
  contacts, or before any campaign work. Do not use for the channel runbooks
  themselves (see guzli-mcp-email-outreach and guzli-mcp-voice-campaigns).
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
    tags: [Guzli, MCP, Contacts, CRM]
    related_skills: [guzli-mcp-email-outreach, guzli-mcp-voice-campaigns]
---

# Guzli MCP core

Portable foundation for Guzli MCP on any Agent Skills host. Channel runbooks:

- Email (one-off and campaigns) → skill **`guzli-mcp-email-outreach`**
- Phone calls and voice campaigns → skill **`guzli-mcp-voice-campaigns`**

Tool cheat sheet: [references/tool-map.md](references/tool-map.md).

## Host setup

1. Connect Guzli MCP (`https://mcp.guzli.com/mcp`, OAuth via gateway.guzli.com).
2. List the server's tools in your host; call them by **remote name** (example `search_contacts`). Hosts may prefix names; match on the suffix.
3. Read a tool's **input schema** before calling it. The server rejects undeclared arguments with `invalid_workflow_request` and the path of the offending field.

## The two tool layers

| Layer | What it is | Examples |
|---|---|---|
| **Workflows** | One call that does several engine steps | `send_email`, `create_email_campaign`, `email_segment`, `call_phone_number`, `create_voice_campaign`, `revise_campaign`, `run_voice_campaign`, `enroll_campaign_contacts` |
| **Operations** | Direct reads and writes, named `verb_object` | `list_campaigns`, `get_campaign_revision`, `get_campaign_revision_readiness`, `list_telephony_number_pools`, `list_voice_profiles`, `list_campaign_extraction_results` |

Use a workflow to act, an operation to find an id or check state. These layers are distinct from the authorization surfaces below.

### Copilot vs tenant surfaces

Authorize all four scopes: `guzli:read`, `guzli:write`, `guzli:copilot:read`, `guzli:copilot:act`. Copilot authorization exposes about 80 tools (81 in the served fixture), including `create_contact`, `update_contact`, `call_contact_now`, `send_email` and campaign workflows. Only `guzli:read` / `guzli:write` exposes the tenant operations plane (about 144 operations); workflow-backed operations carry `_primitive` names and contact write tools are absent. If `tools/list` shows about 144 tools and no `update_contact`, re-authorize with the copilot scopes. Counts are diagnostic hints; names and schemas decide availability.

Copilot tools use flat arguments (`get_campaign {"campaign_id":"<id>"}`), not tenant transport envelopes. Tools such as `get_campaign_revision_readiness`, `list_campaign_revisions` and `list_telephony_phone_numbers` are registry operations absent from the served copilot fixture. Use them only when exposed; read their schema for `path`, `query` and `headers`. Otherwise use the dashboard or the workflow’s built-in readiness check; do not invent a copilot tool. The tool map lists both surfaces.

<!-- Sources at 704e0b48e: contracts/mcp-registry/classification-seed.json; contracts/mcp-registry/generated/primitive-identities.json; tests/fixtures/copilot_schema_budget/current_served_catalog.json; engine/model_first/hosted_mcp/bundle_composition.py (scope routing). -->

## Where ids come from

| Need | Tool |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| Contacts | `search_contacts`, `lookup_contact`, `create_contact` |
| Voice profile | `list_voice_profiles` (the agent's profile) |
| Caller-ID number pool | `list_telephony_number_pools` (an active pool with an active member; there is no default) |
| Campaign state, `lock_version`, draft `definition` | `get_campaign`, `get_campaign_revision`, `list_campaign_revisions` |
| Readiness before publish | `get_campaign_revision_readiness` |
| Segments | `get_segment_field_catalog`, `create_segment`, `materialize_segment`, `get_segment_readiness`, `list_segment_members` |
| Call outcomes and captured answers | `list_campaign_call_attempts`, `list_campaign_extraction_results`, `get_campaign_extraction_result` |

## The campaign shape (same for email and voice)

`create_*_campaign` → (optional `get_campaign_revision` → edit → `revise_campaign`, which publishes) → or `get_campaign_revision_readiness` → `publish_*_campaign` → `enroll_campaign_contacts` (explicit audiences only) → `run_*_campaign` → check attempts / results. One-call shortcuts (`email_contacts`, `email_segment`, `call_phone_number`, `call_contacts`, `call_segment`) do the whole chain for a fresh cohort. The voice ones take the call script (`call_instructions`, required) and answer extraction directly.

## Consent for permission-required campaign sends

When a campaign step resolves `permission_requirement` to `"required"`, it checks recorded permission for the contact, channel and purpose; no record fails with `permission_missing`. Email inherits `"optional"`; voice inherits `"required"`. For required steps, before enrolling anyone:

1. `list_contact_permission_heads {"contact_id": "<contact uuid>"}` → `items[]` with `channel_key`, `purpose`, `basis_key`, `state`. You need an item with `state: "active"`, the channel you will use (`email`, or `voice_twilio` for calls) and the purpose of your campaign.
2. If there is none, ask the user on what basis this person may be contacted, then record it with `capture_operator_permission` (exact body in the email and voice skills). Bases: `explicit_opt_in`, `existing_relationship` (either purpose); `recipient_requested`, `contract_or_service`, `legal_obligation` (transactional only); `cold_b2b` (marketing only); `legitimate_interest`. The organisation's allowed bases are set in the dashboard; the usual set is `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`. A basis outside that set fails the send with `permission_basis_not_allowed`.
3. Never record a permission the user did not confirm. The record names who vouched for it.

## Codes you will meet

| Code | Meaning | What to do |
|---|---|---|
| `campaign_daily_missing` | `cap_policy.maximum_daily_channel_units` unset | Set it (create or `revise_campaign`) |
| `number_pool_missing` | Voice step has no caller-ID pool | Pass `number_pool_id` |
| `sending_identity_not_ready` | As an error: sender/pool unusable. As a warning on a voice campaign: informational | Fix the sender or pool in the dashboard; warnings do not block |
| `campaign_enrollment_explicit_audience_required` | `enroll_campaign_contacts` on a segment campaign | Intended; segment automation enrolls |
| `pacing.recipient_rolling_cap` | A recipient was already called/emailed in the last 24 h | Product rule; the attempt is held with a retry time |
| `invalid_workflow_request` | Arguments rejected against the schema; `schema_path` names the field | Fix that field; do not retry blindly |
| `invalid_contact_patch` with `invalid_attribute_keys` | Invalid custom attribute names or nested values | Correct the listed keys or use scalar values |
| `held_for_approval` | The agent's policy holds outbound actions for a human | Tell the user; a reviewer approves in the dashboard |
| `permission_missing` / `permission_inactive` / `permission_basis_not_allowed` | No active permission for this contact, channel and purpose, or its basis is outside the organisation's allowed set | Record one with `capture_operator_permission` (see the consent section); do not retry the same run |

## Held operations and status polling

A completed `send_email` result with `operation_id: "api-operation:<digest>"` is final. Do not poll that id or send the email again merely to obtain status. Only `status: "held_for_approval"` supplies a `held_call_id` for approval polling; a held result with `side_effect_complete: false` is not done.

Call `get_operation_status` with the returned **held-call value**. Its registry transport schema names the input `path.operation_id`, even though the value must be `held_call_id`:

```json
get_operation_status {"path":{"operation_id":"<held_call_id from held result>"},"query":{},"headers":{}}
```

Passing an `api-operation:` id returns `status: "denied"`, `reason_code: "held_call_id_required"`, `may_have_executed: false`, `retryable: false`, the supplied `operation_id`, `conversation_id: null`, `held_call_id: null`, and `required: {"id_field":"held_call_id","result_status":"held_for_approval"}`. There is no message text to parse. Report held status to the user and use the returned approval facts.

<!-- Sources at 704e0b48e: contracts/mcp-registry/generated/engine-primitives.json, engine.get-operation-status input; contracts/mcp-registry/generated/package-workflows.json, held_result_grammar. The package send_email polling recipe is stale: v2/api/operation_status.py and tests/engine/model_first/public_operations/test_status_denial_sequence.py establish the exact held-only denial and completed invocation behavior. -->

## Contacts

`search_contacts` / `lookup_contact` before create. `create_contact` with a real `source_reason_code` (lowercase snake_case). Use scalar `custom_attributes`; unknown valid keys are defined on first write. Never invent email, phone, or name. Phones are E.164.

### Self-serve custom attributes

`create_contact` takes `source_reason_code`; `update_contact` takes `contact_id` and `reason_code`. Both accept `custom_attributes` with scalar values. An unknown valid key defines an organization attribute on first non-null write: boolean → `boolean`, number → `number`, valid `YYYY-MM-DD` → `date`, other strings → `text`. The label comes from the key. `null` on an unknown key defines nothing; existing attributes keep their type. Keys must match `^[a-z][a-z0-9_]{0,63}$`. Bad names or nested values are refused with `invalid_contact_patch` and `invalid_attribute_keys` (a served schema can reject nested values before mutation). Correct the values; do not discard valid unknown keys.

`search_contacts` returns `schema`; inspect it for existing types. `get_segment_field_catalog` lists defined attributes and supported operators before segment authoring. Omitted update fields stay unchanged; explicit null retracts an existing fact.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json, create_contact/update_contact/search_contacts/get_segment_field_catalog; contacts/attribute_definition.py; contacts/service.py; contacts/tool_mutations/contracts.py; tests/contacts/test_self_serve_attributes_postgres.py. -->

## Lifecycle

`list_lifecycle_stages`, `get_contact_lifecycle_stage`, `list_contact_events` (evidence ids), `set_contact_lifecycle_stage` only with real `to_stage_id`, `evidence_event_ids`, `reason_codes`.

## Editing a draft: `revise_campaign`

Read the draft with `get_campaign_revision`, edit `definition`, send it back with `existing_draft_revision_id` set to that draft. Send only fields the schema declares, keep the draft's own `step_id`s, and never send server-owned fields (`extraction_schema_version_id`; email `artifact_ref` and `artifact_digest`). `revise_campaign` publishes the revision; do not call `publish_*_campaign` afterwards.

## OAuth and parallel calls

The engine rotates refresh tokens once and rejects reuse. Refresh single-flight per session, then reuse the rotated tokens for parallel calls.

## Release compatibility

| Behaviour | 1.0.7 (historical) | 1.0.8 (historical) | 1.0.16 (current) |
|---|---|---|---|
| `run_email_campaign` | Rejects every valid request (`invalid_workflow_request`) | Fixed | Supported; exactly one of `all_active` / `enrollment_ids` |
| Voice publish | Blocked by `send_capability_not_registered` | Fixed | Supported; readiness still applies |
| Voice tools accept `cap_policy`, quiet hours, schedule, admission label, `number_pool_id` | No | Yes; `create_voice_campaign` also requires `agent_id` and `audience_policy` | Supported; number pool and daily cap needed for publish |
| Second segment campaign with the same `admission_policy.effect_key` | Publish fails (identity collision) | Fixed; the key is a label | Key remains a namespace label |
| Pinned segment publish | Can miss a member re-evaluated after the pin | Fixed | Historical fix retained |

Historical columns preserved from the repository’s 1.5.0 runbook; they are not live test results from this docs update. Use the current exposed schema.

<!-- Sources: guzli-skills commit 29ecc31, skills/guzli-mcp-core/SKILL.md (historical columns); engine 704e0b48e contracts/mcp-registry/generated/package-workflows.json and tests/fixtures/copilot_schema_budget/current_served_catalog.json (current workflow inputs, publish and effect-key label). -->

## Hard rules

1. No fabricated contact data.
2. No silent sending or dialing: confirm with the user before the first live send or dial in a thread.
3. Readiness before every publish; a permission record for each recipient when the step requires it.
4. On a schema error, report the tool and the field; do not guess.
5. Channel details live in the sibling skills.

## Verify

A harmless read succeeds (`list_lifecycle_stages`, `search_contacts`, or `list_campaigns`) and the returned ids are reusable in the channel skills.

<!-- Engine 704e0b48e audit: tests/fixtures/copilot_schema_budget/current_served_catalog.json (served names and flat inputs); contracts/mcp-registry/generated/package-workflows.json (workflow inputs and composition); contracts/mcp-registry/generated/engine-primitives.json (operation names and transport schemas). Permission defaults: tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py. Legacy codes absent from generated schemas were checked in pinned implementation/tests; full token inventory is in the release RESULT artifact. -->

## Changelog

- **1.7.0 (2026-09-13)** — Audits served flat inputs and permission defaults; distinguishes copilot/tenant authorization, held-only status polling and self-serve attributes; restores historical compatibility with 1.0.16 current.
