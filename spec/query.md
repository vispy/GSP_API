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

Statuses must distinguish miss from unsupported capability and backend/readback terminal states.

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

## M009 status semantics

`QueryStatus` is the terminal status for one query request:

| Status | Meaning | Payload rules |
|---|---|---|
| `hit` | A visual contribution was found. | `hit=True`; may include visual id, family, item/texel, coordinates, displayed color, and source value. |
| `miss` | Query coordinate is inside the panel but no visual contains it. | `hit=False`; no hit payload fields. |
| `outside-panel` | Query coordinate is outside the queried panel/viewport bounds. | `hit=False`; no hit payload fields. |
| `unsupported` | The backend/capability set cannot answer the requested query mode or payload. | `hit=False`; diagnostic required. |
| `stale` | A result exists but violates freshness policy, for example an old frame/result. | `hit=False`; diagnostic required. |
| `dropped` | The request was cancelled, superseded, or dropped from an async queue. | `hit=False`; diagnostic required. |
| `failed` | The backend attempted the query/readback but failed operationally. | `hit=False`; diagnostic required. |

Capabilities advertise coarse query support through `CapabilitySnapshot.query_modes`.
The v0.1 names currently used by conformance fixtures are:

- `panel-query`: backend can perform a point-in-panel query at all;
- `point-item`: backend can identify a point item;
- `image-texel`: backend can identify an image texel/source value.

Backends that do not advertise a mode must reject planning with a diagnostic or return
`unsupported` for direct query attempts. The Datoviz v0.4 adapter currently advertises no query
modes because Python cannot decode `DvzQueryResult`.
