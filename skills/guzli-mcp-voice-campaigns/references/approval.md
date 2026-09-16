# Approval and uncertain outcomes

- [ ] Inspect the returned outcome before declaring a mutation complete.
- [ ] For held_for_approval or any pending approval, report that approval is
  pending. Do not poll for status or repeat the action to bypass the hold.
- [ ] Retain the returned held_call_id and any engine-provided approval facts.
  Use the host's approval flow; report an unresolved hold as pending.
- [ ] Re-read the affected object after an uncertain mutation when a read tool
  exists. If outcome remains unresolved, stop and report it rather than repeat.

A completed operation_id is not a held_call_id; do not poll completed sends or
resubmit them for status.
