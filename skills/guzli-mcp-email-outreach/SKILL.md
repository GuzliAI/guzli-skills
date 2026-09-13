---
name: guzli-mcp-email-outreach
description: >-
  Sends email through Guzli MCP: one-off messages with send_email and list
  outreach with campaigns fed by contacts or segments, including readiness,
  publish, enroll, run, replies and the unsubscribe footer. Use for any email
  task through Guzli MCP. Do not use for phone calls (see guzli-mcp-voice-campaigns).
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
    tags: [Guzli, MCP, Email, Campaigns, Outreach]
    related_skills: [guzli-mcp-core, guzli-mcp-voice-campaigns]
---
# Guzli MCP email outreach

Install and follow **`guzli-mcp-core`** first. Phone calls are skill **`guzli-mcp-voice-campaigns`**. Tool map: [references/tool-map.md](references/tool-map.md).

Two ways to send email. A **one-off** message goes through `send_email`. **List outreach** goes through a campaign: contacts or a segment as the audience, one email step, caps, readiness, publish, enroll, run. Prefer campaigns over looping `send_email`.

## One-off email: `send_email`

```json
send_email {"to": "person@example.com", "subject": "Your appointment", "body_text": "Plain text body."}
```

The sender is the agent's configured address. The result is a structured outcome, not the message bytes. If the agent's policy holds outbound email for approval, the result says `held_for_approval`; a human approves it in the dashboard and it is sent as written. The served copilot schema does not accept `idempotency_key`; the package workflow schema does require it. Read the exposed schema: supply a stable key only where declared, and do not blindly repeat a send with an uncertain outcome.

### HTML and independent text

`send_email`, `create_email_campaign`, `email_contacts` and `email_segment` accept required `body_text` and optional independent `body_html`. `revise_campaign` accepts them in the email step’s `channel_config`. Always supply the plain-text part; HTML does not replace it. One optional `link` accepts HTTP or HTTPS. For example, the one-off input can add `"body_html":"<p>Your appointment is confirmed.</p>"` alongside the text.

Sanitizer refusals are typed: `email_html_disallowed`, `email_macro_location_invalid`, `email_content_too_long`, or `email_content_validation_unavailable`. Inspect `reason_code`, `field`, `phase`, `rule`, `instance_path` and any `actual_characters` / `limit_characters`; correct the named content instead of retrying unchanged. When an unsubscribe token is emitted, it remains valid for 180 days from send.

A completed one-off `operation_id` is not pollable. Only approval-held results with `held_call_id` use `get_operation_status`; follow core’s held-operation section.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json; contracts/mcp-registry/generated/package-workflows.json (email workflows, revise_campaign); channels/email/content/contracts.py (typed sanitizer refusals); channels/email/campaign_unsubscribe.py and tests/channels/email/test_unsubscribe_validity.py (180 days from send). -->

## What you need before a campaign

| Fact | How to get it |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| `tenant_postal_address` | The organisation's mailing address (required campaign input for footer mechanics) |
| `purpose` | `marketing` or `transactional` |
| `admission_policy` | Two labels you choose, e.g. `{"subject_key":"organization","effect_key":"email.send:<campaign-name>"}` |
| `cap_policy.maximum_daily_channel_units` | You choose it. Required to publish. Usually also `maximum_enrollments` |
| Contact ids with real emails | `search_contacts` / `create_contact` |
| A verified sender | Readiness tells you if the agent's sending identity is not ready; fix it in the dashboard |

## Consent for permission-required email campaigns

Email campaign permission is optional by default. A step with `permission_requirement: "required"` checks recorded permission for channel `email` and the campaign’s `purpose`; without it the attempt fails with `permission_missing`. Follow the check below for required steps. `send_email` (one-off) is not a campaign and is not checked this way.

1. Check: `list_contact_permission_heads {"contact_id": "<contact uuid>"}`. You need an item with `channel_key: "email"`, `purpose` equal to your campaign's purpose and `state: "active"`.
2. If missing, confirm the basis with the user and record it. Flat copilot arguments (`expires_at` is optional; `captured_at` is now in ISO-8601; `notice_text_digest` is the SHA-256 hex of the consent statement you are recording, for example the user's sentence granting it; the `*_ref`/`*_id` strings are your own audit labels):
   ```json
   capture_operator_permission {
     "contact_id": "<contact uuid>",
       "identifier_type": "email", "identifier_value": "<the contact's email address>",
       "channel_key": "email", "purpose": "transactional",
       "basis_key": "existing_relationship",
       "captured_at": "2026-09-11T14:00:00Z", "expires_at": null,
       "source_ref": "operator confirmation in chat 2026-09-11",
       "notice_text_digest": "<64 hex chars>", "notice_version": "chat-v1",
       "tenant_compliance_profile_version": 1,
       "evidence_ref": "chat 2026-09-11 user message", "attribution_ref": "operator:<user email>",
       "causation_id": "consent-<contact uuid>", "correlation_id": "<campaign name>"
   }
   ```
   Response: `permission_record_id`, `state: "active"`, `channel_key`, `purpose`, `basis_key`. Use `purpose: "marketing"` with `explicit_opt_in` or `existing_relationship` for marketing mail; `recipient_requested`, `contract_or_service`, `legal_obligation` are transactional only; `cold_b2b` is marketing only. The organisation's allowed bases (dashboard) are usually `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`; another basis fails the send with `permission_basis_not_allowed`.
3. One record per contact, per channel, per purpose. `identifier_value` must be the address the campaign will send to.

### Creation policy knobs

`create_email_campaign`, `email_contacts` and `email_segment` accept optional `permission_requirement` and `unsubscribe_requirement`, each `"required"` or `"optional"`. Omission inherits the email manifest’s `"optional"` defaults; these are string choices, not booleans. Keep `purpose` explicit. To require recorded permission and the unsubscribe mechanism, pass `"permission_requirement":"required","unsubscribe_requirement":"required"` at creation and use the consent runbook above. On a complete revision draft these fields belong on the send step, outside `channel_config`.

<!-- Sources at 704e0b48e: contracts/mcp-registry/generated/package-workflows.json (create_email_campaign/email_contacts/email_segment); tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py; tests/campaigns/phase4b/test_email_campaign_execution_contract.py. -->

## Path A — one call for a fresh cohort

- `email_contacts` (explicit contact ids) or `email_segment` (a materialized segment): creates, publishes, enrolls and queues in one call. Required: `name`, `agent_id`, `subject`, `body_text`, `tenant_postal_address`, `purpose`, `admission_policy`, `request_id` (uuid), `requested_at` (ISO time), plus `contact_ids` or `segment_id` + `segment_version_id` + `maximum_age_seconds`. Add `cap_policy`, `link`, `description` as needed.
- Response: `status: "queued"`, `campaign_id`, `campaign_revision_id`, `accepted_enrollment_ids`.

## Path B — step by step (tested sequence)

Field-only braces below are argument shorthand, not copy-ready JSON. Copilot inputs are flat. `get_campaign_revision_readiness` is a tenant registry operation absent from the served copilot fixture: use it only when exposed, or rely on the publish workflow’s built-in readiness check and fix its returned reasons.

1. `create_email_campaign {"name","agent_id","audience_policy":{"kind":"explicit"},"subject","body_text","tenant_postal_address","purpose","admission_policy","cap_policy":{"maximum_daily_channel_units":100,"maximum_enrollments":100}}` → `campaign_id`, `revision_id`, `lock_version`. Optional `link` (appended to the body as a typed link), `description`, `quiet_hours_policy`, `schedule_policy`.
2. `get_campaign_revision_readiness {"path":{"campaign_id":"<campaign uuid>","revision_id":"<revision uuid>"},"query":{},"headers":{}}` → fix every error reason.
3. `publish_email_campaign {"campaign_id","revision_id","expected_lock_version"}`.
4. Explicit audience: `enroll_campaign_contacts {"campaign_id","contact_ids":[…],"requested_at"}`. Segment audience: skip this; segment automation enrolls.
5. `run_email_campaign {"campaign_id","revision_id","enrollment_ids":[…]}` or `{"campaign_id","revision_id","all_active":true}` (exactly one of the two) → `status: "queued"`.
6. Check with `list_campaign_enrollments` / `get_campaign_enrollment_summary` and the campaign's activity.

### Changing a draft before publish: `revise_campaign`

`get_campaign_revision` → edit `definition` → `revise_campaign {"campaign_id","source_revision_id","existing_draft_revision_id": <the draft>, "draft": <definition>}`. Send only fields the schema declares; keep the draft’s own `step_id`s and remove email `artifact_ref` / `artifact_digest`, `email_content_policy_id`, `email_renderer_id`, `email_content_digest_version`, plus `extraction_schema_version_id`. **`revise_campaign` publishes the revision.** Do not call `publish_email_campaign` afterwards.

Common edit: make the unsubscribe footer optional for a campaign — set the email step's `unsubscribe_requirement` to `"optional"` at the step level in the draft (`"optional"` is the email manifest default). Choose this explicitly to match the user’s campaign requirements.

### Patch one draft step without publishing

Read `get_campaign_revision` for the draft’s `step_id` and `lock_version`, then call:

```json
update_campaign_draft_step {"campaign_id":"<campaign uuid>","revision_id":"<draft uuid>","step_id":"<step uuid>","expected_lock_version":1,"patch":{"subject":"Updated subject","body_text":"Updated text."}}
```

Use the version just read, not the illustrative `1`. Email patch fields are `subject`, `body_text`, `body_html`, `link`, `tenant_postal_address`, `permission_requirement`, `unsubscribe_requirement`. This tool **never publishes**. A stale version returns `campaign_revision_version_conflict` with `expected_lock_version`, `current_lock_version` and `required_action: "reread_revision"`; reread and reconcile before submitting another patch. Retain the returned new lock version for publish. An uncertain write must be reread. `revise_campaign` still replaces a complete draft and publishes it.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json, update_campaign_draft_step/CampaignStepFieldPatch; contracts/mcp-registry/generated/package-workflows.json; campaigns/revisions/step_patch_refusals.py; campaigns/revisions/step_patch_manager.py. -->

## Per-contact campaign merge fields

Write real per-contact content with `update_contact` before enrollment. Unknown valid scalar keys self-define, using the type and key rules in core; nested values or bad names produce `invalid_contact_patch` / `invalid_attribute_keys`. `search_contacts.schema` and `get_segment_field_catalog` expose defined attributes.

```json
update_contact {"contact_id":"<contact uuid>","reason_code":"operator_outreach_copy","custom_attributes":{"outreach_subject":"Your requested follow-up","outreach_body":"Here is the information you requested."}}
```

Create and publish the campaign with `subject: "{{member_metadata.outreach_subject}}"` and `body_text: "{{member_metadata.outreach_body}}"`, then enroll the contacts and run it. Macro-referenced attributes are snapshotted from the contact **at enrollment**; later contact edits do not change that enrollment’s snapshot. Set the macros before enrollment. Missing values fail with `merge_field_missing`.

Snapshot values are non-null scalars; strings must be plain text, at most 18,000 characters each, and the per-contact metadata must fit 32 KiB (32,768 bytes), at most 50 keys. `body_html` can reference these scalar values as text; do not store HTML fragments in contact attributes for insertion as markup. Use the segment field catalog’s defined attribute keys and operators to select the audience.

<!-- Sources at 704e0b48e: tests/fixtures/copilot_schema_budget/current_served_catalog.json (update_contact and enrollment inputs); contracts/mcp-registry/generated/package-workflows.json (enroll_campaign_contacts); contacts/attribute_definition.py; supabase/migrations/20260912_221550_campaign_html_member_metadata_snapshot.sql (macro-referenced snapshot including subject/text/HTML); campaigns/member_metadata_contracts.py (limits); campaigns/execution/merge_fields.py (merge_field_missing). -->

## Segments

- `get_segment_field_catalog` first; use only listed `field_key` + `allowed_operators`.
- `create_segment` (`publish: true`) with an expression; every predicate needs a client-generated `predicate_id` (uuid). Example predicate:
  ```json
  {"kind":"predicate","predicate_id":"<uuid>","field_key":"contact.email","operator":"in","value":{"kind":"text_set","value":["person@example.com"]}}
  ```
- `materialize_segment` (`segment_id`, `segment_version_id`) → `counts.matched`; keep the materialization `id`.
- Segment audience payload: `{"kind":"segment","segment_version_id":"…","materialization_selection":"exact","segment_materialization_id":"…","maximum_age_seconds":300,"enroll_on_segment_entry":true,"unenroll_on_segment_exit":false}` (`current_at_publish` instead of `exact` to take whatever is current at publish).
- `list_segment_members`: only `segment_id`, optional version, `limit`, `offset`.

## Replies

Every campaign message carries a message id and a per-thread reply address. A reply is matched to the campaign message and lands in the agent's inbox as a conversation; the campaign step does not advance because of a reply. Read replies through the conversation tools, not the campaign tools.

## Rules that save you a round trip

- `permission_missing` on a send attempt: the recipient has no active permission for `email` with the campaign's `purpose`. This applies to either purpose when permission is required. Record it (section above) and run again; do not retry the same run.
- Readiness before publish; `campaign_daily_missing` means the daily cap is unset.
- Explicit audience → you enroll. Segment audience → automation enrolls; `enroll_campaign_contacts` is refused with `campaign_enrollment_explicit_audience_required`.
- `run_email_campaign` takes exactly one of `all_active` or `enrollment_ids`.
- `revise_campaign` publishes; no second publish.
- Contacts: use scalar `custom_attributes` with valid keys; never invent addresses.
- Few standing segments and campaigns; never one campaign per contact or per file.

## Verify

For permission-required steps, every recipient has active `email` permission for the campaign’s purpose; readiness had no error reasons; the campaign is published; the enrollment summary matches the intended audience; the run returned `queued`; the user has campaign id, revision id and the outcome.

## Anti-patterns

Running a permission-required campaign before checking permissions; recording a permission the user did not confirm; skipping the daily cap; enrolling contacts on a segment campaign; a second publish after `revise_campaign`; pasting server-owned fields (`extraction_schema_version_id`; email `artifact_ref` and `artifact_digest`) or foreign `step_id`s into a draft; undeclared arguments on `list_segment_members`; missing `predicate_id`; looping `send_email` for a list; one campaign per contact.

<!-- Engine 704e0b48e audit: tests/fixtures/copilot_schema_budget/current_served_catalog.json (served names and flat inputs); contracts/mcp-registry/generated/package-workflows.json (workflow inputs and composition); contracts/mcp-registry/generated/engine-primitives.json (operation names and transport schemas). Permission defaults: tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py; tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py. Legacy codes absent from generated schemas were checked in pinned implementation/tests; full token inventory is in the release RESULT artifact. -->

## Changelog

- **1.7.0 (2026-09-13)** — Corrects send_email inputs and consent defaults; documents independent HTML/text, unsubscribe validity, per-contact merge snapshots, creation knobs and nonpublishing draft-step patches.

<!-- Email full-draft cleanup source at 704e0b48e: campaigns/revisions/steps.py, email_policy_tuple and compile_email_artifact; campaigns/revisions/step_patch_merge.py. -->
