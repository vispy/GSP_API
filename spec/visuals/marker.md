# Marker Visual - Draft

Semantic purpose: shaped point-like marks for categorical scatter plots and oriented annotations.

`gsp.protocol.MarkerVisual` is the S023 marker-family model. It is distinct from `PointVisual`:
points remain simple high-volume filled discs, while markers add shape, angle, and stroke styling.

## Fields

- `id`: stable protocol visual id.
- `positions`: finite float32/float64 array with shape `(N, 2)` or `(N, 3)`.
- `shape`: either one `MarkerShape` or one `MarkerShape` per marker.
- `fill_colors`: per-marker RGBA array with shape `(N, 4)`, as uint8 `[0, 255]` or float `[0, 1]`.
- `sizes`: scalar or per-marker rendered screen-pixel diameter.
- `angle`: scalar or per-marker screen-space rotation in radians.
- `stroke_color`: one RGBA color for marker edges.
- `stroke_width`: rendered screen-pixel edge width.
- `coordinate_space`: `ndc` or `data`.

The v1 shape vocabulary is intentionally conservative: `disc`, `square`, `triangle`, `diamond`,
and `cross`. Custom symbols, SVG/SDF/MSDF assets, and broader Datoviz symbol-set semantics are out
of scope for M067.

## Backend Notes

Matplotlib maps these shapes to native marker paths and converts protocol pixel diameters to
Matplotlib scatter area units using figure DPI.

Datoviz v0.4 maps markers to `dvz_marker()` when the facade exposes marker style helpers. It uploads
`position`, `color`, `diameter_px`, `angle`, and `shape`. Missing marker facade functions must be
reported as structured unsupported diagnostics, not approximated with `PointVisual`.
