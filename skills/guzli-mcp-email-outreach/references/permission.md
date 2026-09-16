# Permission before a campaign send

Never invent user authorization or recorded contact permission.
For a one-off send, capture the user's send authorization; do not pretend that
it is a campaign enrollment with a campaign permission-row check.

- [ ] Read the campaign step's permission_requirement and purpose. If permission
  is required, check every recipient before enrollment or sending.
- [ ] Use `guzli:list_contact_permission_heads`:

```json
{"contact_id":"<contact UUID>"}
```

- [ ] Require active permission for channel_key email and the exact campaign
  purpose, with the identifier the campaign will use and a basis allowed by the
  organization's policy. Inspect returned facts, not merely the existence of a row.
- [ ] If missing or inactive, ask the user for the actual permission basis and
  evidence. Do not assume a relationship, fabricate evidence or lower the policy.
- [ ] Capture confirmed evidence with `guzli:capture_operator_permission`:

```json
{
  "contact_id":"<contact UUID>",
  "identifier_type":"email", "identifier_value":"<recipient email>",
  "channel_key":"email", "purpose":"transactional",
  "basis_key":"existing_relationship", "captured_at":"<evidence capture ISO timestamp>",
  "source_ref":"<source of confirmed evidence>",
  "notice_text_digest":"<SHA-256 hex of the actual permission notice>",
  "notice_version":"<actual notice identifier>",
  "tenant_compliance_profile_version":1,
  "evidence_ref":"<evidence reference>", "attribution_ref":"<confirming operator reference>",
  "causation_id":"<capture action identifier>", "correlation_id":"<campaign correlation identifier>"
}
```

Replace every placeholder and the illustrative compliance profile value with
actual evidence. The example's purpose and basis are not defaults: set them to
the confirmed facts. If required evidence or the policy identifier is unknown,
obtain it before capture. Use expires_at only when supported by the evidence.

- [ ] Re-read `guzli:list_contact_permission_heads` and verify the channel,
  purpose and active state. Correct rejected evidence only from confirmed facts,
  then re-check. Do not send while the permission check remains unresolved.
- [ ] On permission_missing, permission_inactive or permission_basis_not_allowed,
  resolve the returned reason and re-check instead of retrying the same send.

Permission bases accepted by the schema include explicit_opt_in,
existing_relationship, legitimate_interest, cold_b2b, recipient_requested,
contract_or_service and legal_obligation. Schema membership does not establish
that a basis is allowed for this organization, purpose or recipient.
