# M138 - S034 layout-aware guide query

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Add a Matplotlib/reference guide query path over `ResolvedLayoutSnapshot` geometry so guide hits can
be resolved in logical panel pixels and report the same layout snapshot id.

## Deliverables

- `gsp_matplotlib.layout_query.query_resolved_layout_guides()`.
- Hit testing for title, axis-label, tick-label, legend, and colorbar boxes present in a resolved
  layout snapshot.
- Query results with `GuideQueryPayload` and `layout_snapshot_id`.
- Matplotlib capability posture updated to advertise guide layout query support while keeping
  all-rendered layout query pending.
- Tests for title-box query, overlapping guide boxes with `hit_policy=ALL`, and capability posture.

## Acceptance

- Layout guide queries require panel logical-pixel coordinates.
- Hits report the `ResolvedLayoutSnapshot.snapshot_id`.
- Matplotlib still does not claim full `layout_strict`.
- Focused tests pass.

## Stop Condition

Stop before Datoviz guide query, all-rendered layout query integration, or full layout-strict
promotion.

## Result

Completed. Matplotlib/reference can query resolved guide geometry from snapshots and preserve
snapshot identity in query results.
