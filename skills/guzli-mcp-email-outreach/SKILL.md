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
  version: "1.6.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine release 1.0.8 (live-tested end to end)"
  hermes:
    tags: [Guzli, MCP, Email, Campaigns, Outreach]
    related_skills: [guzli-mcp-core, guzli-mcp-voice-campaigns]
---
# Guzli MCP email outreach

Install and follow **`guzli-mcp-core`** first. Phone calls are skill **`guzli-mcp-voice-campaigns`**. Tool map: [references/tool-map.md](references/tool-map.md).

Two ways to send email. A **one-off** message goes through `send_email`. **List outreach** goes through a campaign: contacts or a segment as the audience, one email step, caps, readiness, publish, enroll, run. Prefer campaigns over looping `send_email`.

## One-off email: `send_email`

```json
send_email {"to": "person@example.com", "subject": "Your appointment", "body": "Plain text body.", "idempotency_key": "<uuid you generate>"}
```

The sender is the agent's configured address. The result is a structured outcome, not the message bytes. If the agent's policy holds outbound email for approval, the result says `held_for_approval`; a human approves it in the dashboard and it is sent as written. Reuse the same `idempotency_key` when you retry; a new key is a new email.

## What you need before a campaign

| Fact | How to get it |
|---|---|
| `agent_id` | `list_campaigns` (any row) or the user |
| `tenant_postal_address` | The organisation's mailing address (required by law in the footer) |
| `purpose` | `marketing` or `transactional` |
| `admission_policy` | Two labels you choose, e.g. `{"subject_key":"organization","effect_key":"email.send:<campaign-name>"}` |
| `cap_policy.maximum_daily_channel_units` | You choose it. Required to publish. Usually also `maximum_enrollments` |
| Contact ids with real emails | `search_contacts` / `create_contact` |
| A verified sender | Readiness tells you if the agent's sending identity is not ready; fix it in the dashboard |

## Consent for email campaigns (optional by default)

Email campaigns do not require a recorded consent by default: the email channel's consent requirement is `optional`, and campaigns created through these tools inherit it. A step becomes consent-checked only when its `permission_requirement` is set to `"required"` (through `revise_campaign`). A required step with no matching permission record fails with `permission_missing` and nothing is sent. Voice campaigns are always required (see the voice skill). `send_email` (one-off) is not a campaign and is not checked this way.

When a step is required, or the user asks you to record consent:

1. Check: `list_contact_permission_heads {"path": {"contact_id": "<contact uuid>"}}`. You need an item with `channel_key: "email"`, `purpose` equal to your campaign's purpose and `state: "active"`.
2. If missing, confirm the basis with the user and record it. Tested body (every field is required; `captured_at` is now in ISO-8601; `notice_text_digest` is the SHA-256 hex of the consent statement you are recording, for example the user's sentence granting it; the `*_ref`/`*_id` strings are your own audit labels):
   ```json
   capture_operator_permission {
     "path": {"contact_id": "<contact uuid>"},
     "body": {
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
   }
   ```
   Response: `permission_record_id`, `state: "active"`, `channel_key`, `purpose`, `basis_key`. Use `purpose: "marketing"` with `explicit_opt_in` or `existing_relationship` for marketing mail; `recipient_requested`, `contract_or_service`, `legal_obligation` are transactional only; `cold_b2b` is marketing only. The organisation's allowed bases (dashboard) are usually `explicit_opt_in`, `existing_relationship`, `recipient_requested`, `contract_or_service`; another basis fails the send with `permission_basis_not_allowed`.
3. One record per contact, per channel, per purpose. `identifier_value` must be the address the campaign will send to.

## Path A — one call for a fresh cohort

- `email_contacts` (explicit contact ids) or `email_segment` (a materialized segment): creates, publishes, enrolls and queues in one call. Required: `name`, `agent_id`, `subject`, `body_text`, `tenant_postal_address`, `purpose`, `admission_policy`, `request_id` (uuid), `requested_at` (ISO time), plus `contact_ids` or `segment_id` + `segment_version_id` + `maximum_age_seconds`. Add `cap_policy`, `link`, `description` as needed.
- Response: `status: "queued"`, `campaign_id`, `campaign_revision_id`, `accepted_enrollment_ids`.

## Path B — step by step (tested sequence)

1. `create_email_campaign {"name","agent_id","audience_policy":{"kind":"explicit"},"subject","body_text","tenant_postal_address","purpose","admission_policy","cap_policy":{"maximum_daily_channel_units":100,"maximum_enrollments":100}}` → `campaign_id`, `revision_id`, `lock_version`. Optional `link` (appended to the body as a typed link), `description`, `quiet_hours_policy`, `schedule_policy`.
2. `get_campaign_revision_readiness {"path":{"campaign_id","revision_id"}}` → fix every error reason.
3. `publish_email_campaign {"campaign_id","revision_id","expected_lock_version"}`.
4. Explicit audience: `enroll_campaign_contacts {"campaign_id","contact_ids":[…],"requested_at"}`. Segment audience: skip this; segment automation enrolls.
5. `run_email_campaign {"campaign_id","revision_id","enrollment_ids":[…]}` or `{"campaign_id","revision_id","all_active":true}` (exactly one of the two) → `status: "queued"`.
6. Check with `list_campaign_enrollments` / `get_campaign_enrollment_summary` and the campaign's activity.

### Changing a draft before publish: `revise_campaign`

`get_campaign_revision` → edit `definition` → `revise_campaign {"campaign_id","source_revision_id","existing_draft_revision_id": <the draft>, "draft": <definition>}`. Send only fields the schema declares; keep the draft's own `step_id`s. **`revise_campaign` publishes the revision.** Do not call `publish_email_campaign` afterwards.

Common edit: make the unsubscribe footer optional for a campaign — set the email step's `unsubscribe_requirement` to `"optional"` in the draft (`"required"` is what the create tools write). Only do this for mail that is not marketing, or when the user asks for a test. Exact sequence, one call per step, no re-planning between them:

1. `create_email_campaign` (draft) → keep `campaign_id`, `revision_id`.
2. `get_campaign_revision {"path": {"campaign_id", "revision_id"}}` → `definition`.
3. Set `definition.steps[0].unsubscribe_requirement = "optional"`; delete `extraction_schema_version_id` if present; keep every `step_id`.
4. `revise_campaign {"campaign_id", "source_revision_id": revision_id, "existing_draft_revision_id": revision_id, "draft": definition}` → this publishes; do not call `publish_email_campaign`.
5. `enroll_campaign_contacts` → 6. `run_email_campaign` with the returned `enrollment_ids`.

Look up the contact once and reuse its id. Do not refresh the tool list or search the contact again between steps.

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

- `permission_missing` on a send attempt: the step is `permission_requirement: "required"` and the recipient has no active permission for `email` with the campaign's `purpose`. Record it (section above) and run again; do not retry the same run.
- Subject and body: use plain ASCII (no curly quotes, em dashes, arrows or emoji) in `subject` and `body_text` for `email_contacts`, `email_segment` and `create_email_campaign` until the HTML email release; non-ASCII text is refused at create with `campaign content digest must equal expected digest`.
- Refusals arrive as an error result whose text is JSON with `reason_code` and the facts you need (`required`, `details`, `engine_status`). Read the JSON; it names the fix. A host-side "structured content does not match the output schema" message is a host bug, not a Guzli refusal.
- Readiness before publish; `campaign_daily_missing` means the daily cap is unset.
- Explicit audience → you enroll. Segment audience → automation enrolls; `enroll_campaign_contacts` is refused with `campaign_enrollment_explicit_audience_required`.
- `run_email_campaign` takes exactly one of `all_active` or `enrollment_ids`.
- `revise_campaign` publishes; no second publish.
- Contacts: omit `custom_attributes` unless the org has configured keys; never invent addresses.
- Few standing segments and campaigns; never one campaign per contact or per file.

## Verify

Readiness had no error reasons; the campaign is published; the enrollment summary matches the intended audience; the run returned `queued`; the user has campaign id, revision id and the outcome.

## Anti-patterns

Recording a permission the user did not confirm; re-searching the contact or re-listing tools between steps; skipping the daily cap; enrolling contacts on a segment campaign; a second publish after `revise_campaign`; pasting server-owned fields (`extraction_schema_version_id`) or foreign `step_id`s into a draft; undeclared arguments on `list_segment_members`; missing `predicate_id`; looping `send_email` for a list; one campaign per contact.
