# Voice campaign checklist

Substitute verified facts for placeholders and the latest lock for
the illustrative lock value. Caps must reflect the user's approved limits.

## Prepare and create

- [ ] Resolve recipients through `guzli:find_contacts` and `guzli:lookup_contact`.
  Confirm agent, script, purpose, audience and daily cap.
- [ ] Read `guzli:list_telephony_number_pools` and `guzli:get_telephony_number_pool`.
  Select an active caller-ID pool with an active member; there is no default.
  Read `guzli:list_voice_profiles` for the intended voice_profile_id.
- [ ] Capture call authorization and complete the permission checklist linked
  from SKILL.md for every permission-required recipient before enroll or run.
- [ ] Create the draft with `guzli:create_voice_campaign`:

```json
{
  "name":"Requested follow-up calls", "agent_id":"<agent UUID>",
  "audience_policy":{"kind":"explicit"},
  "number_pool_id":"<active pool UUID>", "voice_profile_id":"<profile UUID>",
  "purpose":"transactional", "permission_requirement":"required",
  "call_instructions":"Ask whether the requested follow-up resolved their question. Confirm the answer and close the call.",
  "admission_policy":{"subject_key":"organization","effect_key":"voice.dial:follow-up"},
  "cap_policy":{"maximum_daily_channel_units":50,"maximum_enrollments":50}
}
```

- [ ] Retain campaign_id, revision_id and lock_version; verify the saved draft
  with `guzli:get_campaign_revision` using campaign_id and revision_id.

The sample explicitly requires permission. Use the approved purpose and policy,
not a weaker requirement to bypass a failure. Voice creation accepts purpose
marketing or transactional, and permission_requirement required or optional.

## Edit without publishing

- [ ] Read the draft's step_id and lock_version with `guzli:get_campaign_revision`.
- [ ] Patch only the requested fields with `guzli:update_campaign_draft_step`:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<draft UUID>","step_id":"<draft step UUID>","expected_lock_version":1,"patch":{"call_instructions":"Ask for the preferred callback number, confirm it, and close the call."}}
```

- [ ] Re-read and verify the saved script. For structured answers, include
  post_call_extraction as described in the results reference linked from SKILL.md.
  On a stale lock or uncertain response, re-read and reconcile before another
  patch. Use the latest lock for publish; the patch does not publish.

## Readiness, publish, enroll, run

- [ ] Verify the saved script, audience, pool, profile and daily cap.
- [ ] When publication is authorized, use `guzli:publish_voice_campaign`:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<draft UUID>","expected_lock_version":1,"agent_id":"<agent UUID>"}
```

- [ ] Establish readiness only from the publish workflow's result. Fix the
  failures it reports, re-read saved state with `guzli:get_campaign_revision`,
  then publish again with the latest lock. For an uncertain result, resolve saved
  state before retrying; stop if unresolved. Proceed only after readiness passes
  and publication is confirmed. A hold remains pending; do not poll for approval.
- [ ] For an explicit audience, call `guzli:enroll_campaign_contacts`:

```json
{"campaign_id":"<campaign UUID>","contact_ids":["<approved contact UUID>"],"requested_at":"<current ISO timestamp>"}
```

- [ ] Verify enrollments with `guzli:get_campaign_enrollment_summary`. For a
  segment audience, skip explicit enroll and verify automation's results.
- [ ] Re-check required permission and authorization, then use `guzli:run_voice_campaign`:

```json
{"campaign_id":"<campaign UUID>","revision_id":"<published UUID>"}
```

- [ ] Inspect status and accepted_enrollment_ids. Queued is not completed. Read
  `guzli:list_campaign_call_attempts` and extraction results instead of running
  again while calls are pending. Report failures and holds without bypassing them.
