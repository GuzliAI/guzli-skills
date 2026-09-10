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
  version: "1.5.0"
  website: https://guzli.com
  mcp_url: https://mcp.guzli.com/mcp
  standard: agentskills.io
  verified_against: "Guzli engine MCP registry, 2026-09-10 (release 1.0.7 live; 1.0.8 pending)"
  hermes:
    tags: [Guzli, MCP, Contacts, CRM]
    related_skills: [guzli-mcp-email-outreach, guzli-mcp-voice-campaigns]
---

# Guzli MCP core

Portable foundation for Guzli MCP on any Agent Skills host. Channel runbooks:

- Email outreach → skill **`guzli-mcp-email-outreach`**
- Voice campaigns → skill **`guzli-mcp-voice-campaigns`**

Tool cheat sheet: [references/tool-map.md](references/tool-map.md).

## Host setup (all agents)

1. Connect Guzli MCP in your product UI or config (`https://mcp.guzli.com/mcp`).
2. Confirm tools from that server are callable (list/search tools in your host).
3. Call tools by **remote name** (example: `search_contacts`). Hosts may prefix names; match on the remote/suffix name.
4. Re-read each tool's **input schema** before calling. Required fields change across releases, and the server rejects undeclared arguments.

Do not assume Cursor-, Claude-, or Codex-specific tool APIs. Use whatever MCP invocation your host provides.

## The two tool layers

Guzli serves two kinds of tools from the same connection. Both are discoverable with your host's tool listing; if you do not see a tool named below, list again with a search filter before concluding it is absent.

| Layer | What it is | Examples |
|---|---|---|
| **Workflows** (about 25) | One-call operations that do several engine steps for you | `create_email_campaign`, `email_segment`, `call_phone_number`, `run_voice_campaign`, `send_email`, `enroll_campaign_contacts` |
| **Operations** (about 140) | Direct reads and writes on the engine, named `verb_object` | `list_campaigns`, `get_campaign_revision_readiness`, `list_telephony_number_pools`, `list_voice_profiles`, `list_telephony_phone_numbers`, `search_contacts`, `list_segment_members` |

Rule of thumb: use a **workflow** to act, and an **operation** to discover an id or to check state before acting.

## Discovery: where ids come from

| Need | Tool | Notes |
|---|---|---|
| `agent_id` | `list_campaigns` (any row) or ask the user | Required by every campaign-creating tool |
| Voice profile | `list_voice_profiles` / `get_voice_profile` | Optional on voice tools: the agent's default profile applies when omitted |
| Caller-ID number pool | `list_telephony_number_pools` / `get_telephony_number_pool` | **Required** for voice publish readiness. There is no default pool by design |
| Owned phone numbers | `list_telephony_phone_numbers` | Pool members are phone numbers |
| Campaign state | `get_campaign`, `get_campaign_revision`, `list_campaign_revisions` | `lock_version` for publish comes from here |
| **Publish readiness** | `get_campaign_revision_readiness` | Call it **before** `publish_*`; it names every blocking reason (see codes below) |
| Segment state | `get_segment_readiness`, `list_segment_members`, `list_segment_entry_facts` | Members list is current membership only |

## Readiness and refusal codes you will meet

| Code | Meaning | What to do |
|---|---|---|
| `campaign_daily_missing` | `cap_policy.maximum_daily_channel_units` is not set | Set it on create or with `revise_campaign`, then publish |
| `number_pool_missing` | Voice step has no caller-ID pool | Pass `number_pool_id` (list with `list_telephony_number_pools`) |
| `sending_identity_not_ready` | Email identity or voice pool not usable | Read the readiness detail; fix the pool or sender in the dashboard |
| `send_capability_not_registered` | Step channel key is not a registered send platform | Engine defect on 1.0.7 for voice (fixed in 1.0.8). Nothing on the client side fixes it |
| `campaign_enrollment_explicit_audience_required` | `enroll_campaign_contacts` on a segment-audience campaign | Intended. Segment campaigns are populated by their segment automation |
| `invalid_workflow_request` | Arguments rejected at admission | Re-read the schema; on 1.0.7 `run_email_campaign` returns this for **valid** requests (fixed in 1.0.8) |
| `invalid_contact_patch` with `configured_attribute_keys: []` | Unknown custom attribute keys | Omit `custom_attributes`; the org has none configured |

## Contacts

- `search_contacts` / `lookup_contact` before create.
- `create_contact` with a real `source_reason_code` (lowercase snake_case).
- **Omit `custom_attributes`** unless a refusal or the configured catalog names an allowed key. `configured_attribute_keys: []` means none are configured; unknown keys are rejected, never silently dropped.
- `update_contact` for profile or allowed custom attributes only.
- Never invent email, phone, or name. Phones are E.164.

## Lifecycle

- `list_lifecycle_stages`
- `get_contact_lifecycle_stage`
- `list_contact_events` for evidence ids
- `set_contact_lifecycle_stage` only with real `to_stage_id`, `evidence_event_ids`, and `reason_codes`

## Revising a draft (`revise_campaign`)

`revise_campaign` takes a **complete draft**. When you build it from a `get_campaign_revision` read, **remove server-owned fields** before sending, in particular `extraction_schema_version_id`. Sending them back is rejected as `invalid_workflow_request`.

## OAuth / parallel calls

The engine rotates refresh tokens once and rejects reuse. Refresh **single-flight** per session: complete one refresh, then reuse those tokens for parallel tool calls. "Sibling already rotated tokens" means your client raced itself.

## Release compatibility (read this once per session)

| Behaviour | 1.0.7 (live) | 1.0.8 (pending) |
|---|---|---|
| `run_email_campaign` | Rejects every valid request (`invalid_workflow_request`) | Fixed |
| Voice publish | Blocked by `send_capability_not_registered` | Fixed |
| Voice tools accept `cap_policy`, quiet hours, schedule, admission label, `number_pool_id` | No | Yes; `create_voice_campaign` also requires `agent_id` and `audience_policy` |
| Second segment campaign with the same `admission_policy.effect_key` | Publish fails (identity collision) | Fixed; the key is a label |
| Pinned segment publish | Can miss a member re-evaluated after the pin | Fixed |

Check the live server's tool schemas to tell which release you are on: on 1.0.8 `create_voice_campaign` lists `cap_policy` and `number_pool_id`.

## Hard rules

1. No fabricated contact data.
2. No silent sending or dialing. Confirm with the user before the first live send or dial in a thread.
3. Keep this skill to shared primitives; channel details live in sibling skills.
4. On schema or validation errors, report the tool and the error; do not guess fields.
5. Call `get_campaign_revision_readiness` before every publish.

## Verify

A harmless read succeeds (`list_lifecycle_stages`, `search_contacts`, or `list_campaigns`), and returned ids are reusable in channel skills.
