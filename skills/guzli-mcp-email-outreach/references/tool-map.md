# Host note

Tool names below are **remote** Guzli MCP names. Your agent host may show a namespace or prefix; match on these remote names when invoking.

# Guzli MCP — email campaign tools

Confirm live schemas. See also [guzli-mcp-core tool map](../../guzli-mcp-core/references/tool-map.md).

| Remote name | Role |
|---|---|
| `list_campaigns` | List campaigns |
| `get_campaign` | Campaign + revision ids |
| `get_campaign_revision` | Full revision |
| `create_email_campaign` | Draft email campaign |
| `revise_campaign` | Draft/replace definition |
| `publish_email_campaign` | Publish revision |
| `run_email_campaign` | Queue published revision |
| `email_contacts` | Create+queue for explicit contacts |
| `email_segment` | Create+queue for materialized segment |
| `enroll_campaign_contacts` | Enroll into published campaign |
| `list_campaign_enrollments` | Enrollment page |
| `get_campaign_enrollment_summary` | Counts + typed refusals |
| `campaign_measurement` | Metrics |
| `send_email` | Single message only — not lists |


## Ops notes (live)

- Publish requires `maximum_daily_channel_units` in `cap_policy` or readiness returns `campaign_daily_missing`.
- Segment predicates need a UUID `predicate_id`.
- `enroll_campaign_contacts` is for **explicit** audience campaigns only.
- Segment campaigns enroll via `enroll_on_segment_entry` / segment_entry facts.
- `run_email_campaign` queues enrollments; if it returns `invalid_workflow_request`, report upstream — do not invent success.
