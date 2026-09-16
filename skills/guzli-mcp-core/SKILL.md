---
name: guzli-mcp-core
description: >-
  Manages Guzli MCP connection, contact discovery, tags, segments, knowledge,
  managed phone numbers, agent configuration and issue reports. Applies when
  users request these shared operations or troubleshoot Guzli tools. Routes
  email sending to guzli-mcp-email-outreach and outbound calls to
  guzli-mcp-voice-campaigns; does not own either channel's campaign runbook.
license: Apache-2.0
compatibility: Requires a host with Agent Skills support and the Guzli MCP server at https://mcp.guzli.com/mcp.
metadata:
  author: Guzli
---

# Guzli MCP core

The server is named guzli in plugin configurations; the fully qualified form is guzli:<tool>.
Complete the Guzli OAuth sign-in in your host.
Read exposed schemas before supplying arguments to the Guzli tools.

## Connect and discover

- [ ] Connect the host to https://mcp.guzli.com/mcp.
- [ ] Inspect the Guzli tools and their input schemas.
- [ ] Resolve identifiers from returned facts or the user, not from unrelated records.
- [ ] If a tool is absent, check authorization and reconnect; re-list before acting.

Read [the tool map](references/tool-map.md) for contact, tag, segment, knowledge,
configuration, conversation and issue workflows. Read
[managed numbers](references/managed-numbers.md) before a purchase or release.
Read [approval handling](references/approval.md) when a tool returns a hold.

## Select the operation

| Request | Tool |
| --- | --- |
| Find contacts | `find_contacts`, `lookup_contact` |
| Write contact facts | `create_contact`, `update_contact` |
| Read or change tags | `browse_tags`, `add_tag`, `edit_tag`, `mutate_contact_tag` |
| Inspect an agent's tools | `get_agent_tool_configuration` |
| Ingest a URL and check progress | `knowledge-ingest_url`, `check_ingestion_status` |
| Search, buy, inspect, release numbers | `search_managed_phone_numbers`, `buy_managed_phone_number`, `list_owned_phone_numbers`, `release_managed_phone_number` |
| Report a product bug | `report_issue` |

## Bound mutations

- [ ] Establish the requested object, change and scope before a write.
- [ ] For spending, sending or releasing a number, obtain explicit authorization
  covering that action. Contact creation alone does not establish permission to send.
- [ ] Respect engine approval and denial. System-prompt configuration and number
  release are ask-first actions; chat authorization does not bypass engine approval.
- [ ] Read back changed state. Correct a rejected input before retrying; inspect an
  uncertain result before any repeat mutation. Stop if its outcome cannot be resolved.
- [ ] Report identifiers and observed outcome, including anything still pending.

For email or voice work, select the matching sibling skill. Do not send through
another channel or tool to bypass a permission failure or approval hold.
