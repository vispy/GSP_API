# Point Visual - Draft

Semantic purpose: screen-space or world/data-positioned point markers.

First-slice attributes:

| Attribute | Type | Required | Notes |
|---|---|---:|---|
| position | float32/float64 Nx2 or Nx3 | yes | coordinate interpretation from attachment/panel |
| color | rgba8 or transformed scalar/category | yes | final color or color transform source |
| size | float32 N or scalar | yes | rendered screen-pixel diameter |

Query payload first slice:

- visual id;
- item id;
- data/visual coordinate if available;
- displayed RGBA.

## M003 first protocol model

`gsp.protocol.PointVisual` is the first formal point model.

It requires:

- `id`;
- `positions` as float32/float64 `(N, 2)` or `(N, 3)`;
- `colors` as rgba8 `(N, 4)` or float color `(N, 4)` in `[0, 1]`;
- `sizes` as a scalar or float array `(N,)`, interpreted as rendered screen-pixel diameters;
- `coordinate_space`, initially `ndc` or `data`.

## M066 size-unit decision

`PointVisual.sizes` is protocol-owned and means canvas/reference-pixel diameter. Backends must not
expose their native marker-size units through this field. The Matplotlib reference renderer converts
diameter pixels to `scatter(s=...)` area units using the resolved canvas contract. The Datoviz v0.4
adapter scales values by `ResolvedCanvas.framebuffer_per_canvas_px` before uploading to the point
visual's `diameter_px` attribute.

Point positions must be finite float32/float64 arrays with shape `(N, 2)` or `(N, 3)`. Sizes must be
finite, non-negative float32/float64 values, either scalar or per-point. Colors are per-point RGBA,
using either uint8 `[0, 255]` values or finite float `[0.0, 1.0]` values.
