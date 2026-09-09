# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking.

# Guzli MCP — core / shared tools

Confirm live schemas on the connected server. Names are **remote** tool names.

## Connector

- MCP URL: `https://mcp.guzli.com/mcp`
- OAuth AS: `https://gateway.guzli.com`

## Contacts & lifecycle

| Remote name | Role |
|---|---|
| `create_contact` | Create or resolve contact |
| `update_contact` | Patch profile / custom attributes |
| `search_contacts` | Search |
| `lookup_contact` | Resolve by id or identifier |
| `list_contact_events` | Evidence events |
| `get_contact_lifecycle_stage` | Current stage |
| `set_contact_lifecycle_stage` | Move stage |
| `list_lifecycle_stages` | Profile, stages, edges |
| `contact_digest` | Bounded digest |

## Segments (shared)

| Remote name | Role |
|---|---|
| `get_segment_field_catalog` | Predicate catalog |
| `preview_segment` | Dry-run |
| `create_segment` / `create_segment_version` | Create |
| `publish_segment_version` | Publish version |
| `list_segments` / `get_segment` | Inventory |
| `materialize_segment` | Membership |
| `list_segment_members` | Members page |

## One-off email (not campaigns)

| Remote name | Role |
|---|---|
| `send_email` | Single plain-text email |
