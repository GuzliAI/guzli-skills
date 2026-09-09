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
| `enroll_campaign_contacts` | Enroll into published **explicit** campaign |
| `list_campaign_enrollments` | Enrollment page |
| `get_campaign_enrollment_summary` | Counts + typed refusals |
| `campaign_measurement` | Metrics |
| `send_email` | Single message only — not lists |
| `list_segment_members` | Segment membership (`segment_id`, optional version, `limit`, `offset` only) |

## Operator notes

- Publish requires `cap_policy.maximum_daily_channel_units`.
- Segment predicates need a UUID `predicate_id`.
- `enroll_campaign_contacts` is for **explicit** audience campaigns only; segment campaigns use segment automation.
- Omit contact `custom_attributes` unless the org catalog allows keys.
