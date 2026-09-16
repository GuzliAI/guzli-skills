---
name: guzli-mcp-core
description: >-
  Manages the Guzli connection, contacts, tags, segments, knowledge base,
  phone numbers, agent configuration and bug reports. Use when the user
  mentions Guzli and wants to find or update contacts, add or edit tags, build
  segments, ingest a URL or file into the knowledge base, check ingestion
  status, buy, list or release phone numbers, view or change an agent's system
  prompt or tool configuration, or report a bug. Routes email sending to
  guzli-mcp-email-outreach and phone calls to guzli-mcp-voice-campaigns.
license: Apache-2.0
compatibility: Requires a host with Agent Skills support and the Guzli MCP server at https://mcp.guzli.com/mcp.
metadata:
  author: Guzli
---

# Guzli MCP core

The server is named guzli in plugin configurations; the fully qualified form is guzli:<tool>.
Complete the Guzli OAuth sign-in in your host.
Read exposed schemas before supplying arguments to the Guzli tools.

## Terms

- Permission: the contact's recorded permission for a channel and purpose.
- Authorization: the user's go-ahead for an action the agent takes.
- Approval: the engine's hold/approve flow for ask-first tools.
- Tool: an MCP tool; argument: a tool input field.

## Connect and discover

- [ ] Connect the host to https://mcp.guzli.com/mcp.
- [ ] Inspect the Guzli tools and their argument schemas.
- [ ] Resolve identifiers from returned facts or the user, not from unrelated records.
- [ ] If a tool is absent, reconnect and re-list before acting.

Read [the tool map](references/tool-map.md) for contact, tag, segment, knowledge,
configuration, conversation and issue workflows. Read
[managed numbers](references/managed-numbers.md) before a purchase or release.
Read [approval handling](references/approval.md) when a tool returns a hold.

## Select the operation

| Request | Tool |
| --- | --- |
| Find contacts | `guzli:find_contacts`, `guzli:lookup_contact` |
| Write contact facts | `guzli:create_contact`, `guzli:update_contact` |
| Read or change tags | `guzli:browse_tags`, `guzli:add_tag`, `guzli:edit_tag`, `guzli:mutate_contact_tag` |
| Inspect an agent's tools | `guzli:get_agent_tool_configuration` |
| Ingest a URL and check progress | `guzli:knowledge-ingest_url`, `guzli:check_ingestion_status` |
| Search, buy, inspect, release numbers | `guzli:search_managed_phone_numbers`, `guzli:buy_managed_phone_number`, `guzli:list_owned_phone_numbers`, `guzli:release_managed_phone_number` |
| Report a product bug | `guzli:report_issue` |

## Bound mutations

- [ ] Establish the requested object, change and scope before a write.
- [ ] For spending, sending or releasing a number, obtain explicit authorization
  covering that action. Contact creation alone does not establish permission to send.
- [ ] Respect engine approval and denial. System-prompt configuration and number
  release are ask-first actions; chat authorization does not bypass engine approval.
- [ ] Read back changed state. Correct a rejected argument before retrying; inspect an
  uncertain result before any repeat mutation. Stop if its outcome cannot be resolved.
- [ ] Report identifiers and observed outcome, including anything still pending.

For email or voice work, select the matching sibling skill. Do not send through
another channel or tool to bypass a permission failure or approval hold.
