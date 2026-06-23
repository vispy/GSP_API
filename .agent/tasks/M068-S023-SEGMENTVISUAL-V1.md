# M068-S023-SEGMENTVISUAL-V1 - SegmentVisual v1

## Mission

M068

## Goal

Implement a line-segment family for independent start/end pairs with screen-space stroke width.

## Contract Starting Point

Suggested v1 fields:

```text
id
starts
ends
colors
widths
cap
coordinate_space
```

Validation rules:

- starts/ends finite float arrays, shape `(N, 2)` or `(N, 3)`;
- colors per segment;
- widths scalar or per segment, non-negative screen pixels;
- cap scalar per visual;
- zero-length segments rejected in v1 unless a later ADR defines dot behavior.

## Backend Mapping

- Matplotlib: `LineCollection`, with linewidth in points converted from pixel width via DPI.
- Datoviz v0.4: `dvz_segment(scene, flags)` plus `"position_start"`, `"position_end"`,
  `"color"`, `"stroke_width"`, and cap style helper if present.

## Acceptance

- Validation, Matplotlib, Datoviz fake-facade, and QA report tests pass.
- QA cases show width ramp, cap behavior, alpha overlap, and draw order.
- Datoviz unsupported reports identify exact missing symbols if segment/cap/capture is unavailable.

## Stop Conditions

- Stop if width units diverge from Point/Marker pixel diameter semantics.
- Stop if requested arrow/dash/vector features enter scope.
