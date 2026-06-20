# Point Visual - Draft

Semantic purpose: screen-space or world/data-positioned point markers.

First-slice attributes:

| Attribute | Type | Required | Notes |
|---|---|---:|---|
| position | float32/float64 Nx2 or Nx3 | yes | coordinate interpretation from attachment/panel |
| color | rgba8 or transformed scalar/category | yes | final color or color transform source |
| size | float32 N or scalar | yes | screen pixels initially |

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
- `sizes` as a scalar or float array `(N,)`, interpreted as Matplotlib-compatible screen marker area for the reference slice;
- `coordinate_space`, initially `ndc` or `data`.
