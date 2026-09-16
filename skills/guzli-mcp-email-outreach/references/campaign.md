# Email campaign checklist

Replace angle-bracket placeholders with verified facts.
Numeric examples are illustrative: use the approved cap and latest lock value.

## Prepare and create

- [ ] Resolve contacts with `guzli:find_contacts` and `guzli:lookup_contact`.
  Confirm the agent, audience, sender, purpose, postal address and cap with the
  user. Do not infer the agent from an unrelated campaign.
- [ ] Capture send authorization and complete the permission checklist linked
  from SKILL.md. For required permission, re-check every recipient before enroll.
- [ ] Create the draft with `guzli:create_email_campaign`:

```json
{
  "name":"Requested follow-up", "agent_id":"<agent UUID>",
  "audience_policy":{"kind":"explicit"},
  "subject":"Your requested information", "body_text":"Here is your follow-up.",
  "body_html":"<p>Here is your follow-up.</p>",
  "tenant_postal_address":"<confirmed mailing address>", "purpose":"transactional",
  "permission_requirement":"required", "unsubscribe_requirement":"required",
  "admission_policy":{"subject_key":"organization","effect_key":"email.send:follow-up"},
  "cap_policy":{"maximum_daily_channel_units":50,"maximum_enrollments":50}
}
```

- [ ] Keep campaign_id, revision_id and lock_version. Read the draft with
  `guzli:get_campaign_revision` using campaign_id and revision_id. Verify its
  audience, plain text, HTML, purpose and policies before publish.

The sample selects permission and unsubscribe requirements explicitly; it does
not describe a server default. Use the user's approved policy, never a weaker
policy to bypass a failure. Purpose is marketing or transactional. Preserve
independent body_text when supplying body_html; author HTML inside the tool input.

## Edit a draft without publishing

- [ ] Read the draft with `guzli:get_campaign_revision`; use its step_id and lock.
- [ ] Call `guzli:update_campaign_draft_step` for only the requested fields:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<draft UUID>","step_id":"<draft step UUID>","expected_lock_version":1,"patch":{"subject":"Updated follow-up","body_text":"Updated information.","body_html":"<p>Updated information.</p>"}}
```

- [ ] Re-read and verify the saved draft. On a stale lock or uncertain response,
  re-read, reconcile the requested edit with the saved state, then retry only
  the remaining change using the latest lock. Editing does not publish.

## Readiness, publish, enroll, run

- [ ] Check the saved draft against the confirmed audience, content and cap.
- [ ] When publication is authorized, call `guzli:publish_email_campaign`:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<draft UUID>","expected_lock_version":1}
```

- [ ] Establish readiness only from the publish workflow's result. Fix the
  failures it reports, re-read saved state with `guzli:get_campaign_revision`,
  then publish again with the latest lock. For an uncertain result, resolve saved
  state before retrying; stop if unresolved. Proceed only after readiness passes
  and publication is confirmed. A hold remains pending; do not poll for approval.
- [ ] For an explicit audience, use `guzli:enroll_campaign_contacts`:

```json
{"campaign_id":"<campaign UUID>","contact_ids":["<approved contact UUID>"],"requested_at":"<current ISO timestamp>"}
```

- [ ] Verify accepted enrollments with `guzli:get_campaign_enrollment_summary`.
  Resolve discrepancies before run. For a segment audience, skip explicit enroll;
  inspect automation's enrollment results instead.
- [ ] Run only the approved enrollments with `guzli:run_email_campaign`:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<published UUID>","enrollment_ids":["<accepted enrollment UUID>"]}
```

- [ ] Use all_active:true instead of enrollment_ids only when the user authorizes
  all active enrollments; never supply both. Inspect accepted_enrollment_ids and
  status. Queued is not delivered; read campaign results rather than run again.
