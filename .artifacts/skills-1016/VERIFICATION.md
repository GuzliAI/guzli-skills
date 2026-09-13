# Verification

Target: Guzli engine 1.0.16 (`704e0b48e`), accessed with read-only git show.

```text
authority-bundle: PASS (first action, before reads or edits)
repository scripts/: install-skill.sh only; no verification script present; installer not executed
guzli-mcp-core: bundled quick_validate exit 1: Unexpected key(s) in SKILL.md frontmatter: compatibility. Allowed properties are: allowed-tools, description, license, metadata, name
guzli-mcp-core: compatibility-aware validator PASS; name/version/target/compatibility length PASS
guzli-mcp-email-outreach: bundled quick_validate exit 1: Unexpected key(s) in SKILL.md frontmatter: compatibility. Allowed properties are: allowed-tools, description, license, metadata, name
guzli-mcp-email-outreach: compatibility-aware validator PASS; name/version/target/compatibility length PASS
guzli-mcp-voice-campaigns: bundled quick_validate exit 1: Unexpected key(s) in SKILL.md frontmatter: compatibility. Allowed properties are: allowed-tools, description, license, metadata, name
guzli-mcp-voice-campaigns: compatibility-aware validator PASS; name/version/target/compatibility length PASS
guzli-mcp-core: get_operation_status concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-email-outreach: send_email concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-email-outreach: capture_operator_permission concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-email-outreach: update_campaign_draft_step concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-email-outreach: update_contact concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-voice-campaigns: call_contact_now concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-voice-campaigns: capture_operator_permission concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-voice-campaigns: call_phone_number concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-voice-campaigns: create_voice_campaign concrete example PASS (required/type/enum/unknown-field/format checks)
guzli-mcp-voice-campaigns: update_campaign_draft_step concrete example PASS (required/type/enum/unknown-field/format checks)
concrete fenced tool examples: 10 PASS; complete-draft pseudocode: 1 schematic, not parsed as JSON
intra-skill reference links: PASS
pinned citation paths: 31 PASS
git diff --check: PASS
changed file scope: docs only PASS
```

## Validator interpretation

The bundled validator was run unchanged and rejects the existing `compatibility` key. A second execution changed only its top-level allowed-properties set in memory to include `compatibility`, preserving the repository’s portable frontmatter. No script or installed skill was changed. YAML, folder/name agreement, version, target, description, compatibility length and scaffold checks passed. This is not a claim that the unmodified bundled validator passed.

Examples use illustrative placeholders; validation substitutes shape-valid dummy values only in memory. No tool was invoked, no live email/call was sent, and no engine test suite was run. Schema validation does not establish delivery behavior. Runtime claims were inspected in pinned sources/tests, with gaps recorded in RESULT.
