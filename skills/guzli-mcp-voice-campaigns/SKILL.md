---
name: guzli-mcp-voice-campaigns
description: >-
  Places Guzli outbound calls and prepares, edits, publishes and monitors voice
  campaigns with call instructions and structured answer extraction. Use when the user
  mentions Guzli and wants to call a contact or phone number once with follow-up
  instructions, prepare a permission-required voice campaign or survey, edit a draft,
  add a required preferred callback number to answer extraction, select a caller ID
  pool or daily cap, inspect captured answers, or check an uncertain call before retrying.
  Routes email to guzli-mcp-email-outreach and shared connection,
  contact, knowledge or number administration to guzli-mcp-core.
license: Apache-2.0
compatibility: Requires a host with Agent Skills support and the Guzli MCP server at https://mcp.guzli.com/mcp.
metadata:
  author: Guzli
---

# Guzli voice campaigns

The server is named guzli in plugin configurations; the fully qualified form is guzli:<tool>.
Complete the Guzli OAuth sign-in in your host.
Read exposed schemas before supplying arguments to the Guzli tools.

## Terms

- Permission: the contact's recorded permission for a channel and purpose.
- Authorization: the user's go-ahead for an action the agent takes.
- Approval: the engine's hold/approve flow for ask-first tools.
- Draft: an unpublished campaign revision; publish: make a draft available for enrollment; enroll: admit contacts; run: dispatch campaign work; tool: an MCP tool; argument: a tool input field.

## One operator-directed call

- [ ] Resolve the intended contact or E.164 phone number and the call instructions.
  Capture the user's authorization for this call before dialing.
- [ ] Inspect `guzli:list_owned_phone_numbers` for eligible caller selection.
  Resolve ambiguity rather than inventing a caller number.
- [ ] Call `guzli:call_contact_now` with exactly one of contact_id or
  phone_number, nonblank call_instructions, and a stable idempotency_key:

```json
{"contact_id":"<contact UUID>","call_instructions":"Ask whether the requested follow-up resolved their question, then close the call.","idempotency_key":"<stable key for this intended call>"}
```

- [ ] Supply caller_number only when selecting an eligible owned number. This
  tool does not take a campaign number_pool_id.
- [ ] Inspect the outcome before any retry. Preserve the same key for the same
  intended call; an uncertain dispatch is not a reason to dial with a new key.
- [ ] Read the returned call with `guzli:get_call`; use `guzli:list_calls` for
  discovery. Dispatch acceptance is not a completed conversation.
  Use [approval handling](references/approval.md) for a hold.

## Voice campaign

Use [the campaign checklist](references/campaign.md) for a reusable campaign.
Read [permission capture](references/permission.md) before a permission-required
enrollment or call. Read [results and extraction](references/tool-map.md) for
structured answers and requested webhooks.

- [ ] Confirm audience, script, purpose, daily cap, caller-ID pool and profile.
- [ ] Check and capture permission, then re-check. Do not invent evidence or
  lower the permission requirement to get past a refusal.
- [ ] Create or edit the draft and verify the saved instructions and extraction.
- [ ] When authorized, publish through the readiness-gated workflow. Fix reported
  failures and publish again; only its result establishes readiness.
  A draft-only request stops before publish.
- [ ] Verify publication, enroll the authorized explicit audience, then run.
- [ ] Inspect call attempts and extraction; report actual outcomes and pending work.

| Task | Tool |
| --- | --- |
| Resolve recipients | `guzli:find_contacts`, `guzli:lookup_contact` |
| Discover caller-ID pool and profile | `guzli:list_telephony_number_pools`, `guzli:list_voice_profiles` |
| Read and edit draft | `guzli:get_campaign_revision`, `guzli:update_campaign_draft_step` |
| Create and publish | `guzli:create_voice_campaign`, `guzli:publish_voice_campaign` |
| Enroll and run | `guzli:enroll_campaign_contacts`, `guzli:run_voice_campaign` |
| Read calls and answers | `guzli:list_campaign_call_attempts`, `guzli:list_campaign_extraction_results` |

For a segment audience, follow [segment preparation](references/segments.md);
segment automation owns enrollment. Number purchase and release belong to the
general skill, not to a call request.
