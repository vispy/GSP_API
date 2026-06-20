# GSP Query - Draft

Use a unified panel query:

> What rendered scene contribution is under this panel coordinate?

First-slice QueryRequest:

- request id;
- panel id;
- coordinate;
- coordinate space;
- hit policy;
- requested payload;
- freshness policy.

First-slice QueryResult:

- request id;
- status;
- hit/miss;
- panel/framebuffer coordinate;
- visual id;
- visual family;
- item/texel id where applicable;
- visual/data coordinate where available;
- displayed RGBA;
- optional scalar/vector/category/text value.

Statuses must distinguish miss from unsupported capability.

## M005 reference proof

The first concrete query models live in `gsp.protocol.query`.

The Matplotlib/reference proof lives in `gsp_matplotlib.protocol_query` and evaluates `PointVisual`
and `ImageVisual` models directly. It is intentionally CPU-side and deterministic; it proves the
schema and reference semantics, not the Datoviz GPU backend.

First-slice behavior:

- `QueryRequest` carries request id, panel id, coordinate, coordinate space, hit policy, requested
  payload, and freshness policy.
- `QueryResult` distinguishes `hit`, `miss`, `outside-panel`, and `unsupported`.
- Point hits report visual id, visual family, item id, coordinate, and displayed RGBA.
- Image hits report visual id, visual family, texel `(row, col)`, data/visual coordinate,
  displayed RGBA, and source value.
- When multiple visuals contain the coordinate, the reference proof chooses the highest `z_order`
  entry as the frontmost result.

Datoviz implementation remains deferred until `DvzQueryResult` fields are available to Python or a
decoded helper API exists in `../datoviz/`.
