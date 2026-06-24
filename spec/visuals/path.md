# Path Visual - Draft

Semantic purpose: ordered open polylines with continuous joins across vertices.

`gsp.protocol.PathVisual` is the S023 path-family model. It is distinct from
`SegmentVisual`: segments are independent start/end pairs, while paths preserve ordered vertices and
join semantics within each subpath.

## Fields

- `id`: stable protocol visual id.
- `positions`: finite float32/float64 array with shape `(N, 2)` or `(N, 3)`.
- `path_lengths`: non-empty tuple partitioning `positions` into open subpaths; every entry is at
  least 2 and the sum equals `N`.
- `colors`: per-subpath RGBA array with shape `(P, 4)`, as uint8 `[0, 255]` or float `[0, 1]`.
- `widths`: scalar or per-subpath rendered screen-pixel stroke width.
- `cap`: one `StrokeCap` for all subpath endpoints: `butt`, `round`, or `square`.
- `join`: one `StrokeJoin` for interior vertices: `miter`, `round`, or `bevel`.
- `miter_limit`: non-negative finite miter limit.
- `coordinate_space`: `ndc` or `data`.

Closed paths, fills, holes, Beziers, dashes, polygons, and per-vertex styling are out of scope for
M069. A producer may duplicate the first vertex to create a closed-looking open polyline, but there
is no `closed` protocol field in S023.

## Backend Notes

Matplotlib maps each subpath to an open `PathPatch`, converts protocol pixel widths to point
linewidths using figure DPI, and applies cap/join styles.

Datoviz v0.4 maps paths to `dvz_path()` when the facade exposes `dvz_path_set_subpaths`,
`dvz_path_set_caps`, and `dvz_path_set_join`. Per-subpath colors and widths are expanded to
per-vertex arrays before upload as `position`, `color`, and `stroke_width_px`.
