# M068 - SegmentVisual v1

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Add independent screen-stroked line segment visual contract and backend mappings.

## Planned Deliverables

- `SegmentVisual` and `StrokeCap` enum.
- Producer API, likely `Axes.segments(...)`.
- Matplotlib LineCollection reference mapping.
- Datoviz v0.4 `dvz_segment` adapter using `"position_start"`, `"position_end"`, `"color"`, and
  `"stroke_width_px"`.
- QA cases for width, cap, alpha, and draw order.

## Completed

- Added `SegmentVisual` and `StrokeCap` to the formal protocol.
- Added `Axes.segments(...)` and top-level `vispy2.segments(...)`.
- Added Matplotlib `LineCollection` rendering with pixel-to-point stroke width conversion.
- Added Datoviz v0.4 retained segment rendering with `dvz_segment`, `dvz_segment_set_caps`, and dense
  `position_start`, `position_end`, `color`, and `stroke_width_px` uploads.
- Added S023 visual QA cases:
  - `segment/width_cap_ndc`
  - `segment/alpha_order_ndc`
- Regenerated `artifacts/visual_qa/s023/latest-local/contact_sheets/s023_all_cases.png`; both
  segment cases render in Matplotlib and Datoviz.

## Acceptance

Segment width/cap/alpha cases render in Matplotlib and Datoviz or produce structured unsupported
reports.

## Stop Condition

Do not add arrows, dashes, gradients, vector heads, or zero-length cap-dot semantics in v1.
