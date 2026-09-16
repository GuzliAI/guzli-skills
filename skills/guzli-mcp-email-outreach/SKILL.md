---
name: guzli-mcp-email-outreach
description: >-
  Sends Guzli email and prepares, edits, publishes and monitors email campaigns
  for contacts or segments. Applies to one-off email, HTML content, outreach,
  permission checks, enrollment and email results. Routes outbound phone calls
  to guzli-mcp-voice-campaigns and shared connection, contact, knowledge or number
  administration to guzli-mcp-core.
license: Apache-2.0
compatibility: Requires a host with Agent Skills support and the Guzli MCP server at https://mcp.guzli.com/mcp.
metadata:
  author: Guzli
---

# Guzli email outreach

The server is named guzli in plugin configurations; the fully qualified form is guzli:<tool>.
Complete the Guzli OAuth sign-in in your host.
Read exposed schemas before supplying arguments to the Guzli tools.

## Terms

- Permission: the contact's recorded permission for a channel and purpose.
- Authorization: the user's go-ahead for an action the agent takes.
- Approval: the engine's hold/approve flow for ask-first tools.
- Draft: an unpublished campaign revision; publish: make a draft available for enrollment; enroll: admit contacts; run: dispatch campaign work; tool: an MCP tool; argument: a tool input field.

## One recipient

- [ ] Resolve the recipient and preview the subject and content. Capture the
  user's authorization before sending; a contact record is not permission.
- [ ] Use `guzli:send_email` with required plain text and optional
  independent HTML. Write real markup directly in the body_html tool argument,
  not escaped tags or merely HTML pasted into the chat response.

```json
{"to":"person@example.com","subject":"Appointment confirmation","body_text":"Your appointment is confirmed.","body_html":"<h2>Appointment confirmed</h2><p>Thank you.</p>"}
```

- [ ] Check the exposed schema for idempotency_key before calling: supply a
  stable key if declared and required; do not add undeclared arguments.
- [ ] Inspect the result. A hold is pending, not sent. Do not resend an uncertain
  message or poll a completed operation identifier to manufacture confirmation.
  Use [approval handling](references/approval.md) for a hold.

## Contact-list outreach

Use a campaign rather than looping one-off sends. Follow
[the campaign checklist](references/campaign.md) for creation, readiness,
publish, enroll and run. For a draft-only request, stop after saving and verifying
the draft. Read [permission capture](references/permission.md) before any
permission-required campaign enrollment or send.

- [ ] Confirm audience, content, purpose, sender, postal address and daily cap.
- [ ] Check and capture permission, then re-check; never invent evidence or
  change permission to optional merely to get past a refusal.
- [ ] Create or edit the draft; validate the saved content.
- [ ] When authorized, publish through the readiness-gated workflow. Fix reported
  failures and publish again; only its result establishes readiness.
- [ ] Verify publication, enroll the authorized explicit audience, then run.
- [ ] Read enrollment and campaign results; queued does not mean delivered.

| Task | Tool |
| --- | --- |
| Resolve contacts | `guzli:find_contacts`, `guzli:lookup_contact` |
| Read and edit draft | `guzli:get_campaign_revision`, `guzli:update_campaign_draft_step` |
| Create and publish | `guzli:create_email_campaign`, `guzli:publish_email_campaign` |
| Enroll and run | `guzli:enroll_campaign_contacts`, `guzli:run_email_campaign` |
| Inspect outcomes | `guzli:get_campaign_enrollment_summary`, `guzli:campaign_measurement` |

For a segment audience, follow [segment preparation](references/segments.md);
do not explicitly enroll contacts into a segment campaign. For pause, resume,
replies and result reading, use [the tool map](references/tool-map.md).
