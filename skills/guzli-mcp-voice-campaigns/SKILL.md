---
name: guzli-mcp-voice-campaigns
description: >-
  Creates and runs Guzli MCP voice campaigns (one-call dial workflows or
  draft, publish, run) with shared contacts and segments, including the voice
  profile, caller-ID number pool and readiness rules. Use when the task is outbound
  or configured voice dialing, voice campaign setup, or voice campaign status via
  Guzli MCP. Do not use for email outreach (see guzli-mcp-email-outreach).
license: Apache-2.0
compatibility: >-
  Requires a host that supports Agent Skills (agentskills.io) and a connected
  Guzli MCP server at https://mcp.guzli.com/mcp (OAuth via gateway.guzli.com).
  Network access required. Works with Claude Code, Codex, Cursor, Grok, OpenClaw,
  Muse, Hermes Agent, and other compatible agents.
metadata:
  author: Guzli
  version: "1.5.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine MCP registry, 2026-09-10 (release 1.0.7 live; 1.0.8 pending)"
  hermes:
    tags: [Guzli, MCP, Voice, Campaigns]
    related_skills: [guzli-mcp-core, guzli-mcp-email-outreach]
---

# Guzli MCP voice campaigns

Install and follow **`guzli-mcp-core`**. Email sequences are skill **`guzli-mcp-email-outreach`**. Tool map: [references/tool-map.md](references/tool-map.md).

Same product shape as email (contacts, segments, standing campaigns, revisions, enrollments) on the same campaign engine: caps, quiet hours, schedule and admission labels mean the same thing. Different channel tools and step config.

## Release check first

On the live server, list the tools and read `create_voice_campaign`'s input schema:

- If it lists `cap_policy` and `number_pool_id`, you are on **1.0.8 or later**: voice campaigns can publish through MCP. Follow this skill as written.
- If it lists only `name` and `voice_profile_id`, you are on **1.0.7**: `publish_voice_campaign` fails with `send_capability_not_registered` for every voice campaign authored through MCP (engine defect: the hosted tools wrote a channel key the send registry does not recognise). No profile, pool or capability on your side fixes it. Tell the user, and stop before dialing.

## Two ways to dial

| Path | Tools | When |
|---|---|---|
| **One call** (create + publish + run) | `call_phone_number` (one E.164 number), `call_contacts` (contact ids), `call_segment` (a segment) | The audience is known and the user has approved dialing |
| **Step by step** | `create_voice_campaign` → `get_campaign_revision_readiness` → `publish_voice_campaign` → (`enroll_campaign_contacts` for explicit audiences) → `run_voice_campaign` | The user wants to review the draft, caps or schedule first |

Both paths need the same facts below. Never open a new voice campaign per phone number; feed contacts or segments into few standing campaigns.

## Required facts before you dial

| Fact | Source | Notes |
|---|---|---|
| `agent_id` | `list_campaigns` (any row) or the user | Required by every voice tool (1.0.8: also on `create_voice_campaign`) |
| **`number_pool_id`** | `list_telephony_number_pools` → pick an active pool with at least one active member (`get_telephony_number_pool`, `list_telephony_phone_numbers`) | **Required for readiness.** There is **no default pool** by design; omitting it yields `number_pool_missing` |
| `voice_profile_id` | `list_voice_profiles`, or omit | Optional: the agent's default profile applies when omitted |
| `cap_policy.maximum_daily_channel_units` | You set it | **Required for publish** (`campaign_daily_missing` otherwise). Usually also `maximum_enrollments` |
| `admission_policy` | You set it | Labels, not identities (see the email skill for the 1.0.7 caveat) |
| Phones | Real E.164 numbers on contacts | Never invent |
| User approval | The thread | Required before the first live dial |

## Canonical workflow (step by step)

```
- [ ] 1. Core skill: agent_id, contacts with real phones (omit custom_attributes unless allowed)
- [ ] 2. list_telephony_number_pools → number_pool_id with an active member; list_voice_profiles if a specific voice is wanted
- [ ] 3. Segment if the audience is ongoing; otherwise explicit audience
- [ ] 4. create_voice_campaign (name, agent_id, audience_policy, number_pool_id, cap_policy.maximum_daily_channel_units, optional voice_profile_id)
- [ ] 5. get_campaign / get_campaign_revision (campaign_id, revision_id, lock_version)
- [ ] 6. get_campaign_revision_readiness → fix every reason → user approval
- [ ] 7. publish_voice_campaign (campaign_id, revision_id, expected_lock_version, agent_id)
- [ ] 8. Explicit audience only: enroll_campaign_contacts; segment audience: segment automation enrolls
- [ ] 9. run_voice_campaign (campaign_id, revision_id)
- [ ] 10. Report campaign/revision ids, who will be dialed, and the attempt state (list_campaign_call_attempts)
```

### Draft

If `create_voice_campaign` is slow to return, recover with `list_campaigns` by name, then `get_campaign` / `get_campaign_revision` for `campaign_id`, `draft_revision_id`, and `lock_version`.

`revise_campaign` replaces the draft (caps, pool, profile, call copy, permissions). Send a **complete** draft and remove server-owned fields from any read you started from (`extraction_schema_version_id`). Re-read the live schema; voice payloads are large and versioned.

### Readiness codes

| Code | Meaning | Fix |
|---|---|---|
| `number_pool_missing` | No caller-ID pool on the step | `revise_campaign` with `number_pool_id`, or recreate with it |
| `campaign_daily_missing` | Daily channel cap unset | Set `cap_policy.maximum_daily_channel_units` |
| `sending_identity_not_ready` | Pool inactive or has no active member | Pick another pool (`list_telephony_number_pools`) or fix it in the dashboard |
| `send_capability_not_registered` | 1.0.7 defect (see Release check) | Wait for 1.0.8 |
| `send_platform_unavailable` / `send_platform_integration_mismatch` / `send_platform_ambiguous` (1.0.8) | The agent has no voice integration, the wrong one, or several | Fix the agent's voice integration in the dashboard |

### Publish, enroll, run

- `publish_voice_campaign` requires `campaign_id`, `revision_id`, `expected_lock_version`, `agent_id`.
- Explicit audience: `enroll_campaign_contacts` on the **active published** campaign, then `run_voice_campaign`.
- Segment audience: segment automation enrolls (publish-time sweep of the pinned materialization, then entry facts); do **not** call `enroll_campaign_contacts` (`campaign_enrollment_explicit_audience_required` is intended). Then `run_voice_campaign`.

## Hard rules

1. Do not use email campaign tools for phone outreach.
2. No invented phones, profiles, pools or ids. Discover them with the operations above.
3. No silent dial launches: summarize who will be dialed and get approval first.
4. No one-campaign-per-number.
5. Call `get_campaign_revision_readiness` before every publish.
6. Keep private dial lists out of shared skill text.
7. OAuth: refresh tokens single-flight per session (see **guzli-mcp-core**).

## Verify

Readiness returned no reasons; draft and published ids known; enrollments match the intended audience; the user approved the live dial; the user gets campaign id, revision id, and the attempt state.

## Anti-patterns

Publishing without a `number_pool_id`; omitting the daily cap; calling `enroll_campaign_contacts` on a segment-audience campaign; round-tripping `extraction_schema_version_id` into `revise_campaign`; inventing pool or profile ids instead of listing them; using `send_email` / `create_email_campaign` for phone outreach; one voice campaign per number; retrying `publish_voice_campaign` on 1.0.7 hoping the channel-key defect goes away.
