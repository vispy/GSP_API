# M068 - SegmentVisual v1

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Draft.

## Summary

Add independent screen-stroked line segment visual contract and backend mappings.

## Planned Deliverables

- `SegmentVisual` and `StrokeCap` enum.
- Producer API, likely `Axes.segments(...)`.
- Matplotlib LineCollection reference mapping.
- Datoviz v0.4 `dvz_segment` adapter using `"position_start"`, `"position_end"`, `"color"`, and
  `"stroke_width"`.
- QA cases for width, cap, alpha, and draw order.

## Acceptance

Segment width/cap/alpha cases render in Matplotlib and Datoviz or produce structured unsupported
reports.

## Stop Condition

Do not add arrows, dashes, gradients, vector heads, or zero-length cap-dot semantics in v1.
