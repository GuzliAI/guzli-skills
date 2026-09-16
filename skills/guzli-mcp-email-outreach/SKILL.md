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

The server is named guzli in the plugin configurations. Invoke tools with the
guzli: prefix, as in `guzli:send_email`; tables use bare tool names.
Default to copilot (scopes guzli:copilot:read and guzli:copilot:act).
Tenant-operations is a separate surface under guzli:read and guzli:write, only on
request. Read exposed schemas before supplying arguments.

## One recipient

- [ ] Resolve the recipient and preview the subject and content. Capture the
  user's authorization before sending; a contact record is not permission.
- [ ] Use `guzli:send_email` on copilot with required plain text and optional
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
- [ ] Create or edit the draft; validate the saved content and readiness.
- [ ] Publish only through the readiness-gated workflow when authorized.
- [ ] Verify publication, enroll the approved explicit audience, then run.
- [ ] Read enrollment and campaign results; queued does not mean delivered.

| Task | Tool | Surface |
| --- | --- | --- |
| Resolve contacts | `find_contacts`, `lookup_contact` | copilot |
| Read and edit draft | `get_campaign_revision`, `update_campaign_draft_step` | copilot |
| Create and publish | `create_email_campaign`, `publish_email_campaign` | copilot |
| Enroll and run | `enroll_campaign_contacts`, `run_email_campaign` | copilot |
| Inspect outcomes | `get_campaign_enrollment_summary`, `campaign_measurement` | copilot |
| Readiness preflight when separately authorized | `get_campaign_revision_readiness` | tenant-operations |

For a segment audience, follow [segment preparation](references/segments.md);
do not explicitly enroll contacts into a segment campaign. For pause, resume,
replies and result reading, use [the tool map](references/tool-map.md).
