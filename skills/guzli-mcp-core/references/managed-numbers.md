# Managed numbers

Substitute discovered identifiers into the JSON;
read the exposed schema before invoking each tool.

## Purchase

- [ ] Resolve the intended agent, telephony account and country from the user's
  configuration or supplied facts. Use `guzli:list_owned_phone_numbers` to check
  whether an already owned number meets the request.
- [ ] Search with `guzli:search_managed_phone_numbers`:

```json
{"telephony_account_id":"<account UUID>","iso_country":"US"}
```

- [ ] Present one selected number and the returned purchase details, including
  price when supplied. If cost is not supplied, establish the applicable cost
  before purchase. Obtain explicit spending authorization for this selection.
- [ ] Call `guzli:buy_managed_phone_number` once with the selected number:

```json
{"telephony_account_id":"<account UUID>","e164":"<selected number>","agent_id":"<agent UUID>"}
```

- [ ] Verify the exact number and assignment with `guzli:list_owned_phone_numbers`.
  An uncertain response is not authorization to buy again. Inspect inventory and
  the returned outcome; stop and report uncertainty if ownership is unresolved.
- [ ] Report the owned number and returned identifier only after verification.

The optional voice_profile_id must identify the intended profile; discover it
with `guzli:list_voice_profiles`. Owning a number does not establish a campaign
number pool: campaign configuration belongs to the voice skill.

## Release

- [ ] Read `guzli:list_owned_phone_numbers` and confirm the exact number to release.
- [ ] Obtain authorization for that release and invoke
  `guzli:release_managed_phone_number`:

```json
{"phone_number_id":"<owned number UUID>"}
```

- [ ] Respect the ask-first engine approval flow. Do not substitute another tool
  to bypass a hold or denial.
- [ ] After completion, re-read inventory and verify the number is no longer
  owned. If the result is uncertain, inspect state rather than repeating release.
