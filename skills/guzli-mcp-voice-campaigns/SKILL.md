---
name: guzli-mcp-voice-campaigns
description: >-
  Creates and runs Guzli MCP voice campaigns (draft, publish, run) with shared
  contacts and segments. Use when the task is outbound or configured voice
  dialing, voice campaign setup, or voice campaign status via Guzli MCP. Do not
  use for email outreach (see guzli-mcp-email-outreach) or one-off chat tools.
---

# Guzli MCP voice campaigns

Requires [guzli-mcp-core](../guzli-mcp-core/SKILL.md). Email sequences are a **different** skill: [guzli-mcp-email-outreach](../guzli-mcp-email-outreach/SKILL.md). Tool map: [references/tool-map.md](references/tool-map.md).

Same product ideas as email (contacts, segments, standing campaigns, revisions, enrollments) — different channel tools and config (voice profile, dial policy, voicemail, etc.).

## Default model

1. **Few long-lived voice campaigns** per strategy; feed contacts/segments over time.
2. Do not open a new voice campaign per contact.
3. Personalization on the contact; campaign holds shared call strategy.
4. Draft → review → approve → publish → run.

## Prerequisites

1. Guzli MCP connected; voice tools present (`create_voice_campaign`, `publish_voice_campaign`, `run_voice_campaign`, etc.).
2. Know which **agent** / **voice profile** the org wants (ask if missing — do not invent ids).
3. Never invent phone numbers. Skip contacts without a usable phone identifier.
4. First live `publish_voice_campaign` / `run_voice_campaign` in a thread needs explicit user approval.

## Workflow

```
Voice campaign:
- [ ] 1. Read core skill; inventory existing voice campaigns if list tools exist
- [ ] 2. Upsert contacts with real phones
- [ ] 3. Segment if the audience is ongoing
- [ ] 4. create_voice_campaign (draft)
- [ ] 5. Complete revision/config per schema (voice profile, dial limits, etc.)
- [ ] 6. User approval → publish_voice_campaign → run_voice_campaign
- [ ] 7. Report campaign/revision ids and status
```

### Gather

- Confirm tool schemas (voice create/publish/run differ from email).
- Reuse contacts/segments from core patterns.
- If email `list_campaigns` mixes channels, filter carefully by what get/revision returns — do not assume every listed campaign is voice.

### Draft

- `create_voice_campaign` with a clear strategy name.
- Attach required voice profile / agent fields from schema.
- Prefer standing audience (segment or enroll-later) over one-off blasts when the product supports it.

### Publish & run

- Summarize who will be dialed, which profile, and caps/limits you set.
- After approval: `publish_voice_campaign` (often needs `expected_lock_version`) then `run_voice_campaign`.
- Use enrollment/summary tools when available to verify who was accepted vs refused.

## Hard rules

1. Separate from email outreach — do not overload email campaign tools for voice.
2. No invented phones or silent dial launches.
3. Read schemas every time; voice revision payloads are large and versioned.
4. Keep private dial lists out of shared skill text.

## Verify

- Draft campaign exists with known ids.
- Publish/run only after approval.
- User gets campaign id, revision id, and whether dials were queued.

## Anti-patterns

- Using `send_email` or `create_email_campaign` for phone outreach.
- One voice campaign per phone number.
- Running before confirming voice profile and destination permissions.
