# Voice results and extraction

All tools here use copilot. Inspect exposed schemas before supplying arguments.

| Need | Tool |
| --- | --- |
| Calls | `list_calls`, `get_call` |
| Campaign attempts | `list_campaign_call_attempts`, `get_campaign_call_attempt` |
| Captured answers | `list_campaign_extraction_results`, `get_campaign_extraction_result` |
| Campaign state | `get_campaign`, `get_campaign_enrollment_summary`, `campaign_measurement` |
| Pause or resume | `pause_campaign_now`, `resume_campaign_now` |
| Webhook setup | `list_webhook_events`, `create_webhook_integration` |

## Configure structured answers

- [ ] Identify only the answers the user needs and their types. Example input:
  "Capture the person's preferred callback number."
- [ ] Add this post_call_extraction object to campaign creation or the draft-step
  patch; keep call_instructions aligned with the question:

```json
{
  "is_enabled":true, "schema_name":"callback",
  "fields":[{"field_key":"callback_number","label":"Preferred callback number","value_type":"phone","required":true}],
  "require_schema_validation":true, "allow_partial":true
}
```

- [ ] Re-read the draft through `guzli:get_campaign_revision`; verify instructions
  and extraction before publish. Correct mismatches and re-read after saving.

The example allows a partial result so an unanswered question is distinguishable
from a completed answer; set that choice to the user's requirement. Supported
value_type choices are text, number, boolean, date, datetime, email, phone, url
and enum. For enum, supply enum_values. Do not send server-owned extraction ids.

## Read outcomes

- [ ] Inspect `guzli:list_campaign_call_attempts` for the campaign. Read a selected
  attempt with `guzli:get_campaign_call_attempt`; do not equate queue acceptance
  with a completed conversation.
- [ ] Read `guzli:list_campaign_extraction_results` and the selected
  `guzli:get_campaign_extraction_result` for actual captured values and status.
- [ ] Compare results to the requested fields. Report missing or partial answers
  explicitly; do not invent values or place another call to fill them unasked.

## Pause, resume or add a webhook

- [ ] For an authorized pause or resume, resolve the campaign and use
  `guzli:pause_campaign_now` or `guzli:resume_campaign_now` with the exposed schema.
- [ ] Re-read `guzli:get_campaign` and verify the requested state. Inspect an
  uncertain result before any repeat mutation.
- [ ] For a requested webhook, inspect `guzli:list_webhook_events`; confirm the
  destination and selected event from its returned catalog.
- [ ] Use `guzli:create_webhook_integration` with the exposed argument shape;
  verify returned destination and event selection. Do not create a duplicate
  integration after an uncertain response or call a recipient as a webhook test.
