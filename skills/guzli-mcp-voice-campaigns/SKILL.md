---
name: guzli-mcp-voice-campaigns
description: >-
  Places Guzli outbound calls and prepares, edits, publishes and monitors voice
  campaigns with call instructions and structured answer extraction. Applies to
  one-off dialing, voice surveys, caller-ID pools, call results and captured
  answers. Routes email to guzli-mcp-email-outreach and shared connection,
  contact, knowledge or number administration to guzli-mcp-core.
license: Apache-2.0
compatibility: Requires a host with Agent Skills support and the Guzli MCP server at https://mcp.guzli.com/mcp.
metadata:
  author: Guzli
---

# Guzli voice campaigns

The server is named guzli in the plugin configurations. Invoke tools with the
guzli: prefix, as in `guzli:call_contact_now`; tables use bare tool names.
Default to copilot (scopes guzli:copilot:read and guzli:copilot:act).
Tenant-operations is a separate surface under guzli:read and guzli:write, only on
request. Read exposed schemas before supplying arguments.

## One operator-directed call

- [ ] Resolve the intended contact or E.164 phone number and the call instructions.
  Capture the user's authorization for this call before dialing.
- [ ] Inspect `guzli:list_owned_phone_numbers` for eligible caller selection.
  Resolve ambiguity rather than inventing a caller number.
- [ ] Call `guzli:call_contact_now` on copilot with exactly one of contact_id or
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
- [ ] Fix readiness failures; publish only through the readiness-gated workflow
  when authorized. A draft-only request stops before publish.
- [ ] Verify publication, enroll the approved explicit audience, then run.
- [ ] Inspect call attempts and extraction; report actual outcomes and pending work.

| Task | Tool | Surface |
| --- | --- | --- |
| Resolve recipients | `find_contacts`, `lookup_contact` | copilot |
| Discover caller-ID pool and profile | `list_telephony_number_pools`, `list_voice_profiles` | copilot |
| Read and edit draft | `get_campaign_revision`, `update_campaign_draft_step` | copilot |
| Create and publish | `create_voice_campaign`, `publish_voice_campaign` | copilot |
| Enroll and run | `enroll_campaign_contacts`, `run_voice_campaign` | copilot |
| Read calls and answers | `list_campaign_call_attempts`, `list_campaign_extraction_results` | copilot |
| Readiness preflight when separately authorized | `get_campaign_revision_readiness` | tenant-operations |

For a segment audience, follow [segment preparation](references/segments.md);
segment automation owns enrollment. Number purchase and release belong to the
general skill, not to a call request.
