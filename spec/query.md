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

Datoviz v0.4-dev implementation is active for the bounded data-scope slice when the Python facade
exposes decodable `DvzQueryResult` fields. The current live offscreen smoke proves queue, frame,
poll, and decode to a `hit` result, but Datoviz still leaves some richer live payload fields unset
(`visual_family`, `item_id`, `texel`, displayed color, value) in the tested runtime artifact.

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
`unsupported` for direct query attempts. The Datoviz v0.4 adapter advertises these modes only when
the imported v0.4 facade exposes the queue/poll functions and decodable `DvzQueryResult` fields.

## M011 tiled-source query payload

`QueryResult` can carry a typed extension payload on hit results:

- `extension_payload_kind`
- `extension_payload`

For `gsp.tiled-image@0.1`, the payload is `TiledImageQueryPayload` and reports:

- source id;
- level;
- tile x/y;
- tile-local texel x/y;
- level-local source x/y;
- optional UV coordinate;
- source value.

Non-hit query results must not include extension payload fields.

## S015 unified query scopes

`QueryRequest` now carries an explicit `scope`:

| Scope | Meaning |
|---|---|
| `data` | Query user data visuals and data-scoped extension visuals. This is the default for compatibility. |
| `guides` | Query semantic GSP guide contributions such as axes, ticks, spines, grid, labels, titles, and panel text guides. |
| `all-rendered` | Query eligible data and guide contributions merged in final rendered order. |

`all-rendered` is a strict semantic request. It is not inferred from separate `data` and `guides`
support. If a backend cannot prove global rendered ordering across eligible contributions, it must
return `unsupported` with a diagnostic.

`QueryResult.hits` is the canonical hit list. Existing top-level fields such as `visual_id`,
`visual_family`, `item_id`, `texel`, `displayed_rgba`, `value`, and extension payload fields remain
as compatibility mirrors of `hits[0]`.

For `hit_policy=frontmost`, `hits` contains the frontmost hit. For `hit_policy=all`, `hits` contains
all eligible hits sorted front-to-back once a backend advertises that support.

Direct query execution does not return partial results. Unsupported requested scope, hit policy,
payload, extension payload, or guide-provider behavior returns `unsupported`, not an adapted hit or
miss.

## S015 Matplotlib scoped reference routing

The Matplotlib/reference path routes scoped queries as follows:

- `data` uses the existing deterministic point/image query path and ignores guides;
- `guides` uses bounded semantic `AxisGuide` query support and ignores data visuals;
- `all-rendered` merges queryable data and guide hits using the bounded reference `z_order` fields
  as the comparable render-order key;
- `hit_policy=frontmost` returns the first front-to-back hit;
- `hit_policy=all` returns all eligible hits front-to-back in `QueryResult.hits`;
- `all-rendered` with guide entries requires a `View2D`, otherwise it returns `unsupported`.

This is a reference/conformance route, not a claim that every backend can support `all-rendered`.

## M023 scoped extension query payloads

The Matplotlib/reference scoped query path also accepts data-scoped extension query entries. These
entries expose their supported extension payload kinds and participate in `data` and `all-rendered`
queries as data contributions.

For the built-in tiled-image proof, `TILED_IMAGE_QUERY_PAYLOAD_KIND` is
`gsp.tiled-image@0.1.query`. Scoped tiled-image hits carry the same `TiledImageQueryPayload` used by
the direct M011 tiled-source query helper.

Reference behavior:

- `data` scope can return extension hits and extension payloads;
- `all-rendered` merges extension hits with core data and guide hits using bounded reference
  `z_order`;
- requests for unsupported extension payload kinds return `unsupported` with a diagnostic;
- requested extension payload kinds limit direct reference routing to entries that can satisfy
  those payloads rather than returning a core visual hit without the requested extension payload.


## S024 TextVisual query payload

Text query/readback is item-level and capability-gated. A text hit payload uses `kind="text"`,
`visual_id`, and `item_index`, and may include `text`, original `position`, `coordinate_space`,
resolved anchors, `bounds_px`, `distance_px`, and `z_order`. Glyph-level hit testing is deferred.
Guide labels and titles remain guide-query payloads, not public `TextVisual` hits.
