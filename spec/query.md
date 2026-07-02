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

## S028 guide query and View2D

Guide-scoped query and guide contributions in `all-rendered` consume the same `View2D` snapshot as
guide rendering:

- x-axis guide ticks use the query/render snapshot's `xlim`;
- y-axis guide ticks use the query/render snapshot's `ylim`;
- reversed `View2D` limits are valid and reverse spatial placement, not tick identity;
- auto tick values are generated over the finite numeric interval spanned by the limit pair;
- explicit tick values and labels are preserved exactly;
- hit payloads report semantic tick values and labels, not backend pixel labels or locator output;
- a backend without the exact guide/View2D snapshot required for the query must return
  `unsupported`, not `miss`.

S028 does not change the S015 requirement that `all-rendered` support is explicit and not inferred
from separate data and guide query capabilities.

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

## S029/S034 layout snapshot identity

Layout-aware guide query uses the same `ResolvedLayoutSnapshot` as rendering. Query requests and
results may carry `layout_snapshot_id`; a backend that advertises layout-strict guide query or
all-rendered guide contributions must report the snapshot used. If a backend renders native guide
decorations but cannot query them or cannot report their layout snapshot, it must return an explicit
unsupported/adapted diagnostic rather than silent misses.

## S025 MeshVisual query payload

Mesh query/readback is face-level for the strict 2D reference subset. The Matplotlib/reference path
supports `MeshVisual` face hits for 2D uniform and per-face RGBA meshes. A mesh hit reports
`visual_family="mesh"`, uses `item_id` as the face index, and carries extension payload kind
`gsp.mesh-query@0.1`.

The typed `MeshQueryPayload` reports:

- `visual_id`;
- `hit_kind="face"`;
- `face_index`;
- `vertex_indices` copied from `faces[face_index]`;
- `panel_xy`;
- `coordinate_space`;
- `displayed_rgba`.

Vertex-colored mesh readback, edge/vertex picking, 3D mesh query, barycentric coordinates,
front-facing state, normals, depth, and interpolated RGBA remain capability-gated/deferred.

## S026 scalar color query payload

Scalar/color-mapped visual hits use extension payload kind `gsp.scalar-color-query@0.1`. The payload
reports the semantic scalar source and displayed color:

- `visual_id`;
- `item_kind`: `texel`, `point`, `marker`, or capability-gated `face`;
- item identity such as texel coordinates, point index, marker index, or face index;
- `color_slot`: `image`, `color`, `fill`, or capability-gated `face_color`;
- `color_scale_id`;
- `colormap_id`;
- `source_value`;
- `normalized_value_raw`;
- `normalized_value_clipped`;
- `range_class`: `under`, `in_range`, or `over`;
- `lut_index`;
- `displayed_rgba`.

Colorbar ramp query uses extension payload kind `gsp.colorbar-query@0.1` when guide-query capability
supports it. Framebuffer readback is not the authority for scalar semantics; exact results may be
computed from protocol scene data.

## S027 transformed query inverse payload

Transformed visual hits use extension payload kind `gsp.transform-query@0.1` when the backend claims
strict S027 transform query support. The payload reports the coordinate chain used for readback:
panel/framebuffer coordinate, panel NDC, declared visual coordinate space, declared-space coordinate,
source/local coordinate when invertible, DATA coordinate for DATA visuals, transform identity,
`View2D` identity for DATA visuals, inverse status, and diagnostics.

Strict support requires exact inverse semantics within numeric tolerance. A backend that can render a
transform but cannot provide inverse coordinates must report `unsupported` or include
`GSP_QUERY_INVERSE_UNSUPPORTED`; it must not silently return an untransformed coordinate.

## S036 View3D ray payload

S036 adds projection-inverse View3D ray readback without 3D visual picking. A successful ray context
uses extension payload kind `gsp.view3d-query@0.1` and carries:

- `view_id`;
- `view_revision`;
- `layout_snapshot_id`;
- `view_projection_snapshot_id`;
- panel logical `panel_xy`;
- panel NDC `panel_ndc`;
- near and far DATA points;
- normalized DATA-space `ray_direction`.

The query consumes panel coordinates and the current `View3DProjectionSnapshot`. If a request names
a stale `layout_snapshot_id` or `view_snapshot_id`, the result is `stale` with
`query_3d_snapshot_mismatch`. `MeshVisual` face picking for `(N, 3)` positions remains deferred and
returns `unsupported` with `query_3d_visual_hit_deferred`. Datoviz v0.4 support for
`query.view3d.ray_readback.v1` is canonical ray-context payload generation from public `View3D`
state, not GPU visual hit picking for 3D meshes.

## S044 View3D mesh triangle picking

S044 accepts backend-neutral `query.view3d.mesh_triangle_pick.v1` for the first strict 3D visual-hit
query. This is distinct from ray readback: it identifies the frontmost visible supported opaque
DATA-space `MeshVisual` triangle at a panel point.

Strict v1 responses report public `visual_id`, `visual_type="MeshVisual"`,
`primitive_kind="triangle"`, public canonical `primitive_index`, layout/view/projection snapshot
ids, and `pick_scene_snapshot_id`. Unsupported, stale, invalid, and miss states must remain
distinct.

Full semantics live in `spec/view3d_mesh_triangle_picking.md`.
