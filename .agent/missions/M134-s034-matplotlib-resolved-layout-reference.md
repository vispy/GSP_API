# M134 - S034 Matplotlib resolved layout reference

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Implement the next P016/ANSWER slice after the protocol foundation: expose Matplotlib reference
layout geometry as a `ResolvedLayoutSnapshot` without treating native Matplotlib layout as the
abstract GSP contract.

## Deliverables

- `gsp_matplotlib.layout.resolve_matplotlib_layout_snapshot()`.
- Snapshot extraction for render target, panel rectangle, plot rectangle, title boxes, axis-label
  boxes, tick-label boxes, grid clip rectangle, z layers, and data-to-screen transform.
- Matplotlib guide/scoped query paths preserve `layout_snapshot_id` from query requests into query
  results.
- Matplotlib capability posture updated to `resolved_layout_produce="full"` while keeping
  `layout_strict=False` until render/query/readback are fully integrated.
- Tests proving snapshot extraction and query snapshot identity propagation.

## Acceptance

- Focused Matplotlib/layout tests pass.
- Full test suite remains green before closeout.
- No backend claims layout strictness from a visual artifact alone.

## Stop Condition

Stop before changing Datoviz strictness or promoting Matplotlib `layout_strict` until guide geometry
query/readback is complete and render APIs report the snapshot used.

## Result

Completed. Matplotlib can now produce a resolved layout snapshot from native artist geometry after a
draw, and guide/scoped query paths can echo the caller-supplied `layout_snapshot_id`.
