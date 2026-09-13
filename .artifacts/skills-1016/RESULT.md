# RESULT — Guzli skills for engine 1.0.16

Updated the three portable skills to version **1.7.0**, verified against **Guzli engine 1.0.16 (704e0b48e)**. Work is docs-only on `skills/engine-1.0.16`; no pushes, live sends, calls, installs, or engine mutations were performed.

Authority bundle verification was the first action and returned `PASS`.

## Sections changed and registry citations

All engine paths below refer to commit `704e0b48e`, not the current engine worktree tip. Supplemental runtime sources are identified separately because the generated registry does not contain all requested reason codes or behavior.

| Skill | Sections changed | Registry / served-fixture citations |
|---|---|---|
| `guzli-mcp-core` | Metadata; The two tool layers → Copilot vs tenant surfaces; Consent for permission-required campaign sends; Codes you will meet; Held operations and status polling; Contacts → Self-serve custom attributes; Editing a draft; Release compatibility; Hard rules; Changelog; reference tool map and surface availability | `contracts/mcp-registry/classification-seed.json`; `contracts/mcp-registry/generated/primitive-identities.json`; `contracts/mcp-registry/generated/engine-primitives.json` (`get_operation_status`, readiness transport schemas); `contracts/mcp-registry/generated/package-workflows.json` (workflow inputs/composition, held grammar); `tests/fixtures/copilot_schema_budget/current_served_catalog.json` (`create_contact`, `update_contact`, `search_contacts`, flat inputs) |
| `guzli-mcp-email-outreach` | Metadata; One-off email → HTML and independent text; campaign prerequisites; Consent → Creation policy knobs; Path B and full-draft cleanup; Patch one draft step without publishing; Per-contact campaign merge fields; Rules; Verify; Anti-patterns; Changelog; reference tool map | `tests/fixtures/copilot_schema_budget/current_served_catalog.json` (`send_email`, contact mutations, email creation workflows, `update_campaign_draft_step`); `contracts/mcp-registry/generated/package-workflows.json` (email workflows, `revise_campaign`, enrollment and patch composition); `contracts/mcp-registry/generated/engine-primitives.json` (operation transport schemas) |
| `guzli-mcp-voice-campaigns` | Metadata; One-off call; campaign prerequisites; Consent → Creation policy knobs; Path B; Patch one draft step without publishing; What happens on the call (removed unsupported historical test anecdote); Rules; Verify; Anti-patterns; Changelog; reference tool map | `tests/fixtures/copilot_schema_budget/current_served_catalog.json` (`call_contact_now`, `get_call`, `list_calls`, voice workflows, `update_campaign_draft_step`); `contracts/mcp-registry/generated/package-workflows.json` (voice creation, publish, run and patch composition); `contracts/mcp-registry/generated/engine-primitives.json` (operation transport schemas) |
| README | 1.7.0 changelog, engine target and current compatibility status | Same pinned registry and served fixture; per-skill comments contain section-level citations |

## Supplemental citation table

| Claim / correction | Pinned source evidence |
|---|---|
| Copilot scopes and tenant routing | `engine/model_first/hosted_mcp/bundle_composition.py`; `engine/model_first/hosted_mcp/operation_manifest.py` |
| Completed operation is final; exact held-only denial with no prose | `v2/api/operation_status.py`; `tests/engine/model_first/public_operations/test_status_denial_sequence.py` |
| Self-serve types, valid key pattern, unknown null, existing types and refusal fields | `contacts/attribute_definition.py`; `contacts/service.py`; `contacts/tool_mutations/contracts.py`; `tests/contacts/test_self_serve_attributes_postgres.py` |
| Contact merge snapshot at enrollment, subject/text/HTML macro scanning | `supabase/migrations/20260912_221550_campaign_html_member_metadata_snapshot.sql` |
| 18,000-character / 32-KiB metadata limits and missing-field code | `campaigns/member_metadata_contracts.py`; `campaigns/execution/merge_fields.py` |
| HTML sanitizer fields / codes; 180-day unsubscribe validity | `channels/email/content/contracts.py`; `channels/email/campaign_unsubscribe.py`; `tests/channels/email/test_unsubscribe_validity.py` |
| One-off caller selection, operator principal and bypass of campaign controls | `engine/model_first/internal_mcp/call_contact_now.py`; `engine/model_first/internal_mcp/call_contact_now_tool.py` |
| Automatic posture, channel availability, billing / destination / duplicate refusal codes | `engine/model_first/internal_mcp/builtin_registrations.py`; `campaigns/calls/one_off_refusal_contracts.py` |
| Call-read 404 / 503 typed refusals | `tests/api/test_call_route_typed_refusals.py` |
| Patchable fields, lock conflict and reread requirement | `campaigns/revisions/step_patch.py`; `campaigns/revisions/step_patch_refusals.py`; `campaigns/revisions/step_patch_manager.py`; `campaigns/revisions/step_patch_merge.py` |
| Server-owned email fields removed from full-draft round trips | `campaigns/revisions/steps.py`; `campaigns/revisions/step_patch_merge.py` |
| Email optional vs voice required permission; creation overrides and voice purpose | `tests/engine/model_first/internal_mcp/test_campaign_workflow_permission_defaults.py`; `tests/engine/model_first/internal_mcp/test_campaign_workflow_create_knobs.py`; `tests/campaigns/phase4b/test_email_campaign_execution_contract.py` |
| Historical 1.0.7/1.0.8 compatibility columns | Guzli-skills commit `29ecc31`, `skills/guzli-mcp-core/SKILL.md`; historical columns restored because the branch baseline had removed the table |

## Existing-surface audit

[IDENTIFIER-AUDIT.md](IDENTIFIER-AUDIT.md) records every pre-edit snake-case tool, field and code token across the three skills and their maps, with literal registry/fixture/docs matches or supplemental pinned-source matches. Skill metadata and illustrative extraction keys are explicitly classified. Contextual schema inspection additionally found and corrected:

- Copilot operations use flat arguments; legacy `path` / `body` permission examples were invalid on that surface. Registry-only readiness/status retain transport envelopes.
- `send_email.body` became `body_text`; served copilot excludes an input idempotency key while the package workflow requires one.
- Unknown valid contact custom attributes are self-serve, not rejected for being unconfigured.
- Email permission and unsubscribe checks default optional; voice campaign permission remains required.
- Voice purpose is configurable, not always marketing.
- Email round trips remove artifact and policy fields owned by the server.
- Tool-layer counts are not authorization-surface counts; registry-only operations are not promised on copilot.
- Removed unsupported call-timing and historical call-result guarantees.

## Assumptions

1. **Pinned target overrides moving checkout.** The engine checkout was at `789135617001b0de73aa2ce41224e9a3fd6b963e`, rather than the contract’s `704e0b48e`. Authoritative checks used `git show 704e0b48e:<path>` / `git grep ... 704e0b48e`; no checkout or write occurred there.
2. **Registry coverage is incomplete.** Requested codes including `held_call_id_required`, `invalid_attribute_keys` and one-off refusal details are absent from the specified registry/fixture/docs set. Existing codes also have gaps. Following the no-stop rule, exact pinned implementation/tests supplement those paths; the result does not claim every behavior is present in generated registry JSON. The package `send_email` recipe still polls the resulting operation id; the pinned status implementation and explicit regression test supersede that stale recipe.
3. **Surface schema wins for calls.** The served copilot fixture omits `idempotency_key` from `send_email`, while the package workflow requires it. Skills document both and require using only exposed fields. The fixture also omits some registry reads such as readiness and owned-number inventory. These remain conditional operations with explicit availability guidance.
4. **“Off by default” means optional overrides, not all channel defaults.** Omitted creation knobs inherit manifests: email permission/unsubscribe are optional; voice permission is required, voice purpose defaults marketing. This is directly asserted in pinned tests. No instruction silently turns required voice permission off.
5. **Creation and HTML naming.** The served copilot tools are `create_email_campaign` and `create_voice_campaign`, not generic `create_campaign`. The HTML surface consists of `send_email`, three email creation/cohort workflows and email content inside `revise_campaign`; publish/run tools do not accept bodies. The docs name those exact supported tools rather than inventing a fourth email creation workflow.
6. **Historical compatibility is historical evidence.** The 1.0.7/1.0.8 columns come from the prior repository runbook, with 1.0.16 marked current. No old-release live testing was performed.
7. **Preserved portable frontmatter.** The bundled Codex quick validator predates the repository’s existing `compatibility` key and rejects it. Preserved the key and reran the validator with only that allowlist addition in memory. No script was edited; the raw failures are recorded rather than hidden.
8. **Verification scope.** No verification script exists in repository `scripts/`; its installer was inspected, not executed. This docs task uses pinned-schema/example checks and source inspection, not the engine test suite or production tool execution. Illustrative UUIDs, timestamps, addresses and custom field names are examples, not production data.

## Verification output

Full output and interpretation: [VERIFICATION.md](VERIFICATION.md).

```text
authority-bundle: PASS
repository scripts/: install-skill.sh only; no verification script present
bundled quick_validate: exit 1 for all three (pre-existing compatibility key unsupported)
compatibility-aware validator: 3/3 PASS
name/version/verified_against/compatibility checks: 3/3 PASS
concrete tool examples: 10/10 PASS (pinned input schemas, including formats)
complete-draft pseudocode: 1 schematic; not counted as parsed JSON
intra-skill reference links: PASS
pinned citation paths: 31 PASS
git diff --check: PASS
changed file scope: docs only PASS
```

## Commits

The required phases were committed separately; review corrections and verification evidence have their own commits. This RESULT is force-added in the final result commit.

```text
59296ff Merge PR #1: Skills v1.6.0 clean runbooks
2c2e444 Merge PR #2: consent/permission runbook + voice one-call fields
862b40f docs: audit existing skill schemas and correct engine drift
70bb178 docs: add engine 1.0.16 contact email and call runbooks
9365caf docs: release skills 1.7.0 verified against engine 1.0.16
3fce0b2 docs: resolve verification findings and clarify readiness surfaces
6bd237f docs: complete draft cleanup and source precision
a9b8788 docs: record engine 1.0.16 skill verification output
```

The result commit is the branch tip reported in the final handoff. Clean-tree verification is performed after that commit; no push is authorized or performed.
