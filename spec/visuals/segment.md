# Segment Visual - Accepted S023 Baseline

Semantic purpose: independent stroked line segments for connections, edges, and vector-like marks.

`gsp.protocol.SegmentVisual` is distinct from `PathVisual`: each segment has independent start and
end vertices and no interior join semantics.

## Fields

- `id`: stable protocol visual id.
- `start_positions`: finite float32/float64 array with shape `(N, 2)` or `(N, 3)`.
- `end_positions`: finite float32/float64 array with matching shape.
- `colors`: per-segment RGBA array with shape `(N, 4)`, as uint8 `[0, 255]` or float `[0, 1]`.
- `widths`: scalar or per-segment rendered screen-pixel stroke width.
- `cap`: one `StrokeCap` for all segment endpoints: `butt`, `round`, or `square`.
- `coordinate_space`: `ndc` or `data`.

Arrows, dashes, gradients, vector heads, and zero-length cap-dot semantics are out of scope for
S023.

## Backend Notes

Matplotlib maps segments to `LineCollection` and converts protocol pixel widths to point linewidths
using figure DPI.

Datoviz v0.4 maps segments to `dvz_segment()` when the facade exposes segment helpers. It uploads
`position_start`, `position_end`, `color`, and `stroke_width_px`, and configures caps when
`dvz_segment_set_caps` is available.
