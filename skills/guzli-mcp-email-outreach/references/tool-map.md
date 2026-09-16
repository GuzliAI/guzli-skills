# Email monitoring and personalization

All tools here use copilot. Read their exposed input schemas.

| Need | Tool |
| --- | --- |
| Campaign inventory and state | `list_campaigns`, `get_campaign` |
| Enrollment details | `list_campaign_enrollments`, `get_campaign_enrollment_summary` |
| Measurement | `campaign_measurement` |
| Pause or resume | `pause_campaign_now`, `resume_campaign_now` |
| Replies | `list_customer_conversations`, `read_conversation` |
| Contact fields | `update_contact`, `search_contacts`, `get_segment_field_catalog` |

## Monitor or pause

- [ ] Resolve the campaign and read `guzli:get_campaign` plus
  `guzli:get_campaign_enrollment_summary` and `guzli:campaign_measurement`.
- [ ] Distinguish accepted enrollment, queued dispatch, held work and completed
  results. Report the returned facts; do not infer delivery from a queue result.
- [ ] For an authorized pause or resume, use `guzli:pause_campaign_now` or
  `guzli:resume_campaign_now`, respectively, with the exposed argument shape.
- [ ] Re-read campaign state. Resolve a refusal or uncertain response before
  repeating the mutation; do not resume an approval-held send through another tool.

## Per-contact content

- [ ] Inspect `guzli:search_contacts` and `guzli:get_segment_field_catalog` for
  existing attribute definitions. Use scalar custom_attributes for per-contact
  text and `guzli:update_contact` with contact_id and reason_code.
- [ ] Read back the values before enrollment. Keep markup in body_html, not in
  contact attributes intended as plain text.
- [ ] Use only merge fields supported by the exposed campaign schema. Confirm
  personalized content before publish and enrollment; do not assume later
  contact edits update content already attached to an enrollment.

## Replies

- [ ] Use `guzli:list_customer_conversations` to locate relevant conversations.
- [ ] Read the selected conversation with `guzli:read_conversation` and report
  the actual reply. Do not infer a reply from campaign enrollment state.
