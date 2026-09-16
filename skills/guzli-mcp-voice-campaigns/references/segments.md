# Segment audience preparation

Use the explicit-audience campaign checklist by
default; use this branch when the user requests a segment audience.

- [ ] Read `guzli:get_segment_field_catalog` for fields and allowed operators.
- [ ] Preview the intended expression with `guzli:preview_segment`; inspect
  matches and correct the expression until it reflects the requested audience.
- [ ] Create the approved segment with `guzli:create_segment`, supplying a
  predicate_id for each predicate and using its exposed schema for publication.
- [ ] Materialize its selected version with `guzli:materialize_segment` and retain
  the returned identifier. Check `guzli:get_segment_readiness` and
  `guzli:list_segment_members`; fix failures and re-check before campaign use.
- [ ] Substitute this audience_policy into the campaign creation input:

```json
{"kind":"segment","segment_version_id":"<segment version UUID>","materialization_selection":"exact","segment_materialization_id":"<materialization UUID>","maximum_age_seconds":300,"enroll_on_segment_entry":true,"unenroll_on_segment_exit":false}
```

The example tolerates a five-minute-old materialization; choose the age from the
user's freshness requirement. Entry and exit behavior must match their request.

- [ ] Complete permission checks for the selected recipients before sending.
- [ ] After publish, inspect `guzli:get_campaign_enrollment_summary`. Segment
  automation owns enrollment; do not call `guzli:enroll_campaign_contacts` for
  this campaign or create duplicate explicit enrollments when automation is pending.
- [ ] Run only within the approved scope after verifying readiness and enrollment.
