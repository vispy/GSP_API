# M186 - S043 GSP Datoviz guide strict promotion

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Draft.

## Summary

Promote Datoviz guide rows from adapted to strict only where Datoviz provides full guide
layout/query/readback/all-rendered snapshot evidence.

## Deliverables

- Capability matrix updates for proven guide rows only.
- S031/S028-style review pack regeneration.
- Tests for guide identity, guide boxes, hit/readback payloads, contribution enumeration, and
  `layout_snapshot_id` equality.
- Row-specific diagnostics for remaining adapted guide cases.

## Acceptance

- Every promoted row has guide identity, guide box, hit/readback, contribution, and snapshot id
  evidence.
- Native grid clipping proof is credited without implying full guide strictness.
- Adapted rows remain adapted with precise blockers.

## Stop Conditions

- Stop if any promoted row lacks guide identity, guide box, hit/readback, contribution, or snapshot
  id.
- Stop if grid clipping proof depends on overlay masking.
