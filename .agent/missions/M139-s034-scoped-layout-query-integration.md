# M139 - S034 scoped layout query integration

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Integrate resolved layout guide queries into the Matplotlib scoped query router, including
`all-rendered` guide contributions, while preserving existing semantic axis-query behavior.

## Deliverables

- `query_scoped_scene(..., layout_snapshot=...)`.
- Guide-scope routing to `query_resolved_layout_guides()` when a snapshot is provided.
- All-rendered routing that can merge resolved guide-box hits with existing data/extension hits.
- Matplotlib capability posture updated to advertise all-rendered guide query support from layout
  snapshots.
- Tests for guide-only and all-rendered layout snapshot queries.

## Acceptance

- Existing semantic guide query tests continue to pass.
- Layout-snapshot guide hits carry `layout_snapshot_id`.
- Matplotlib still does not claim full `layout_strict`; render-result snapshot reporting remains a
  separate requirement.

## Stop Condition

Stop before Datoviz guide query or backend layout-strict promotion.

## Result

Completed. The Matplotlib scoped query router can now use resolved layout snapshots for guide and
all-rendered guide contributions.
