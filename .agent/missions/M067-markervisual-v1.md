# M067 - MarkerVisual v1

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Add the Marker visual family with formal protocol contract, producer API, Matplotlib reference
renderer, Datoviz v0.4 `dvz_marker` mapping, and visual QA cases.

## Planned Deliverables

- `MarkerVisual` and `MarkerShape` enum.
- Validation for positions, fill colors, sizes, angle, stroke color, stroke width, and coordinate
  space.
- VisPy2/GSP producer API, likely `Axes.markers(...)`.
- Matplotlib mapping to supported marker shapes.
- Datoviz v0.4 mapping to `"symbol"` or `"shape"`, `"diameter"`, `"angle"`, style descriptor, and
  dense uploads.
- QA cases for supported shapes, fill/stroke, angle, and size ramp.

## Acceptance

Supported symbols render in Matplotlib. Datoviz renders or reports missing `dvz_marker`, style, or
symbol capabilities. Stroke/fill cases produce contact sheets.

## Stop Condition

Do not add custom marker symbols, SVG/SDF/MSDF marker assets, or Matplotlib-only shapes without
capability gates.

## Completion Notes

- Added `MarkerVisual` and conservative `MarkerShape` values: `disc`, `square`, `triangle`,
  `diamond`, and `cross`.
- Added validation for marker positions, scalar/per-item shape, fill colors, sizes, angle,
  stroke color, stroke width, and coordinate space.
- Added VisPy2 `Axes.markers(...)` and top-level `vispy2.markers(...)`.
- Added Matplotlib reference rendering with protocol pixel-diameter conversion.
- Added Datoviz v0.4 retained marker rendering with `dvz_marker()`, marker style, and dense
  uploads for `position`, `color`, `diameter_px`, `angle`, and `shape`.
- Added S023 visual QA cases `marker/shapes_ndc` and `marker/angle_size_stroke_ndc`.
- Regenerated `artifacts/visual_qa/s023/latest-local`; both marker cases render in Matplotlib and
  Datoviz.
