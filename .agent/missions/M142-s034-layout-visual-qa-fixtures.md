# M142 - S034 layout visual QA fixtures

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Add initial resolved-layout visual QA fixtures and Matplotlib report metadata so review artifacts can
check layout snapshot identity, plot rectangles, guide boxes, and grid clipping.

## Deliverables

- `S034_SUITE` extending the existing visual QA case registry.
- Layout cases for scatter title/axis/grid geometry and reversed explicit tick-label boxes.
- Scene JSON serialization of axis and panel text guide style fields.
- Matplotlib QA report rows with `layout_snapshot_id` and compact `layout_snapshot` summaries for
  guide/layout scenes.
- Tests for S034 registry ordering, scene serialization, and snapshot report consistency.

## Acceptance

- S034 Matplotlib QA runs produce rendered artifacts and contact sheets.
- Layout report rows expose plot rectangle, grid clip rectangle, title boxes, axis-label boxes, and
  tick-label box counts.
- `grid_clip_rect_px` matches the resolved `plot_rect_px` for the Matplotlib reference path.

## Stop Condition

Stop before treating these fixtures as full layout-strict promotion. Datoviz-native layout proofs,
resized viewport fixtures, non-1.0 device-scale fixtures, legend layout, and readback remain separate
work.

## Result

Completed. The S034 visual QA suite now has initial layout-focused fixtures and Matplotlib snapshot
metadata in the review report.
