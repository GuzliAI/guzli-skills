# Approval and uncertain outcomes

- [ ] Inspect the returned outcome before declaring a mutation complete.
- [ ] For held_for_approval, report that approval is pending. Do not send, buy,
  publish or run again through another tool to bypass the hold.
- [ ] Retain the returned held_call_id and any engine-provided approval facts.
- [ ] If the user requests status and tenant-operations is authorized and exposed,
  use `guzli:get_operation_status` with the held-call value:

```json
{"path":{"operation_id":"<returned held_call_id>"},"query":{},"headers":{}}
```

- [ ] Otherwise use the host's approval flow and report the unresolved hold.
  Do not request tenant-operations solely to avoid the approval flow.
- [ ] Re-read the affected object after an uncertain mutation when a read tool
  exists. If outcome remains unresolved, stop and report it rather than repeat.

The status tool is tenant-operations, not copilot. A completed operation_id is
not a held_call_id; do not poll completed sends or resubmit them for status.
