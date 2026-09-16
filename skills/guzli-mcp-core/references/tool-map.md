# Shared operations

Read the exposed schema before supplying arguments to the Guzli tools.

## Contacts and tags

- [ ] Use `guzli:find_contacts` and `guzli:lookup_contact` to resolve an existing
  contact before creating one. Confirm ambiguous matches with the user.
- [ ] Use `guzli:create_contact` only for supplied facts; supply source_reason_code.
  For changes, use `guzli:update_contact` with contact_id and reason_code.
- [ ] Keep custom_attributes scalar. Inspect existing fields through
  `guzli:search_contacts` and `guzli:get_segment_field_catalog` before reuse.
- [ ] Read back the contact; correct rejected fields and verify again.
- [ ] For tags, inspect `guzli:browse_tags`, use `guzli:add_tag` for a missing
  definition or `guzli:edit_tag` for a requested definition change, then use
  `guzli:mutate_contact_tag` for the requested contact association.
- [ ] Re-read the tag and contact facts to verify the association or change.

Do not invent an email address, phone number or permission basis. For lifecycle
changes, inspect `guzli:list_lifecycle_stages` and the contact's
`guzli:get_contact_lifecycle_stage` before `guzli:set_contact_lifecycle_stage`;
re-read to verify the requested transition.

## Segments

- [ ] Read `guzli:get_segment_field_catalog` for field keys and allowed operators.
- [ ] Define the requested audience and preview it with `guzli:preview_segment`.
  Inspect matches; correct the expression and preview again before creating it.
- [ ] Use `guzli:create_segment` with the approved expression. Each predicate
  carries a generated predicate_id; do not invent field keys or operators.
- [ ] Materialize the selected version with `guzli:materialize_segment`.
- [ ] Check `guzli:get_segment_readiness` and `guzli:list_segment_members`.
  Resolve failures and re-check before using the segment in a campaign.

Keep segment_id, segment_version_id and the materialization identifier distinct.
Reuse a matching segment rather than creating a duplicate for every contact list.

## Knowledge

- [ ] Confirm the agent and source. For a supplied URL, use
  `guzli:knowledge-ingest_url` with this argument shape after substituting facts:

```json
{"agent_id":"<agent UUID>","source":{"crawl_type":"single","urls":["<approved absolute URL>"]}}
```

- [ ] Retain the task_id and use `guzli:check_ingestion_status` for that task,
  supplying the fields in its exposed schema. Acceptance is not completion.
- [ ] On failure, inspect the returned error, correct its cause, and check state
  before submitting another ingestion. Do not broaden to a website crawl unasked.
- [ ] Once complete, use `guzli:knowledge_search` for a source-specific question;
  verify that the returned evidence supports the expected answer.

For a non-URL source, select the matching ingestion tool from the exposed schema
instead; preserve the same status and retrieval checks.

## Configuration and integrations

- [ ] Inspect `guzli:get_agent_tool_configuration` for a tool configuration request.
- [ ] For a system-prompt replacement, confirm the full requested text and agent;
  use `guzli:configure_agent_system_prompt` with agent_id and system_prompt.
- [ ] Follow its ask-first engine approval flow. A hold is not a saved change;
  verify the engine result before reporting completion.
- [ ] For an explicitly requested webhook, read `guzli:list_webhook_events`,
  confirm the destination and selected events, and inspect the schema of
  `guzli:create_webhook_integration` before creating it.
- [ ] Verify the returned integration details against the requested destination
  and events. Do not create another integration after an uncertain response.

## Conversations and issues

- [ ] Start catch-up with `guzli:list_customer_conversations`; select the relevant
  conversation before reading its messages or summary with the tools below.
- [ ] For an authorized bug report, collect observed behavior, expected behavior
  and reproduction context; exclude credentials and unnecessary contact data.
- [ ] Submit once through `guzli:report_issue` using its exposed schema.
- [ ] Report the returned outcome. If uncertain, investigate that submission;
  do not create duplicate reports to obtain a successful response.

| Read | Tool |
| --- | --- |
| Conversation messages | `read_conversation` |
| Conversation summary | `read_conversation_summary` |
