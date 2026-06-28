# M136 - S034 Datoviz guide capability audit

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Make the current Datoviz guide/layout posture explicit after the P016 resolved-layout decision. This
mission does not promote Datoviz guide rows; it hardens capability diagnostics so adapted review
artifacts cannot be mistaken for layout-strict support.

## Deliverables

- S034 Datoviz guide-layout audit in capability snapshot metadata.
- Explicit diagnostics for adapted panel title handling, missing resolved layout snapshots, partial
  axis style mapping, missing grid clipping guarantee, missing guide query, and missing
  all-rendered guide contributions.
- Backend spec update documenting the conservative Datoviz S034 posture.
- Tests asserting the audit fields and diagnostics.

## Acceptance

- Datoviz still advertises `layout_strict=False`.
- Datoviz still advertises no resolved layout production or consumption.
- Capability metadata names the native axis style fields the adapter may map for review output.
- Missing layout/query semantics are machine-readable diagnostics.

## Stop Condition

Stop before implementing or claiming Datoviz grid clipping, guide query, all-rendered guide query,
or layout-strict conformance.

## Result

Completed. Datoviz guide/layout support is explicitly semantic/adapted with S034 diagnostics and a
machine-readable axis-style field audit.
