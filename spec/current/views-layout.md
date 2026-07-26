# Views, transforms, and layout

## Coordinate spaces

Visuals declare whether coordinates are data values or panel-normalized device coordinates. Conversion between spaces is defined by the associated view and transform records, not by backend convention.

| Space | Meaning |
|---|---|
| `DATA` | Values interpreted by the attached `View2D` or `View3D`. |
| `NDC` | Panel normalized device coordinates after data/view mapping; x and y use `[-1,+1]`. |
| logical pixels | Resolved panel/layout lengths with top-left screen origin where a screen coordinate is required. |

`GSP-VIEW-001`: a record declares its coordinate space. No implementation may guess DATA versus NDC
from numeric range, array rank, or backend defaults.

`GSP-VIEW-002`: DATA→NDC and inverse query mapping use the same accepted view/transform snapshot.
Screen/logical-pixel conversion uses the corresponding resolved layout and device-scale metadata.

## Affine transforms

The accepted 2D transform is finite and invertible. Inline and named transforms have equivalent semantics. Transform order is deterministic, and query results must report whether inverse mapping is exact, unavailable, or ambiguous.

### AffineTransform2D

| Field | Type | Required/default |
|---|---|---|
| `id` | identifier | named resource only |
| `matrix` | finite float `(3,3)` | required; homogeneous last row valid |
| `placement` | client/server/backend policy | negotiated; semantics unchanged |

Matrices act on homogeneous column vectors. Composition order is explicitly listed from source
coordinates toward the view. `GSP-VIEW-003`: singular matrices are invalid in the core invertible
contract. Inline and referenced matrices with equal values produce equal forward/inverse semantics.

## View2D

`View2D` defines finite non-degenerate x and y ranges. Reversed ranges are valid and reverse the corresponding mapping. Navigation is expressed through semantic pan, zoom-about, set-view, and reset actions. Input-device adapters may translate pointer events into those actions but do not define the navigation result.

### View2D

| Field | Type | Required/default |
|---|---|---|
| `id` | identifier | required |
| `panel_id` | panel identifier | required |
| `x_range`, `y_range` | two finite unequal numbers | default `(-1,+1)`; order preserved |
| `aspect_policy` | auto | fixed bounded core policy |
| `clip` | boolean | default true |

For x range `(x0,x1)`, `ndc_x = -1 + 2*(x-x0)/(x1-x0)`; y is analogous. Reversed ranges require no
special case beyond preserving denominator sign.

`GSP-VIEW-004`: navigation actions name the view, base revision, parameters, and expected snapshot
where applicable. An accepted action returns the new view and revision. Stale base revision rejects
without mutation.

| Action | Parameters |
|---|---|
| pan | finite data or normalized delta under the action schema |
| zoom-about | positive finite scale and anchor |
| set-view | complete valid ranges |
| reset | accepted initial view identity/revision |

## View3D

`View3D` associates a camera with an orthographic or perspective projection. Camera basis vectors and ranges must pass degeneracy and finite-value checks. Navigation actions include orbit, pan, zoom, camera replacement, projection replacement, and reset with explicit snapshot freshness.

Strict opaque depth applies only to advertised supported mesh and view combinations. Partially clipped triangles, arbitrary transparency, and backend-native camera behavior are not implicitly strict.

### Camera3D

| Field | Type | Validation |
|---|---|---|
| `eye` | finite vec3 | distinct from target |
| `target` | finite vec3 | defines forward direction with eye |
| `up` | finite vec3 | non-zero and not collinear with forward |

The canonical basis is derived deterministically from eye, target, and up. `GSP-VIEW-005`: camera
records are values, not mutable native controllers. Backend-native interaction must either emit
canonical actions/state or remain explicitly non-canonical review behavior.

### Projections

| Projection | Fields | Validation |
|---|---|---|
| orthographic | x/y bounds, near/far | finite non-degenerate bounds; ordered near/far |
| perspective | vertical FOV degrees, near/far, optional authored aspect | `0 < fov < 180`; positive ordered clipping range; authored aspect positive when present |

`GSP-VIEW-006`: a view projection snapshot ID changes when camera, projection, relevant layout, or
coordinate mapping changes. Query rays and mesh picking name the snapshot they use.

For perspective projection, an omitted authored aspect is resolved as
`plot_rect_px.width / plot_rect_px.height`. The projection snapshot records that effective value
and whether it came from the authored projection or the resolved layout. The effective aspect and
resolved plot rectangle are projection identity inputs. An old caller that supplies only a layout
snapshot ID cannot prove the plot geometry; an implementation may preserve that call shape only as
a diagnosed compatibility path, not as layout-strict resolution.

### View3D navigation

Orbit, pan, center-dolly zoom, set-camera, set-projection, and reset are canonical actions. Orbit
preserves the accepted target and camera distance unless its action explicitly changes them. Center
dolly moves eye along the eye-target line while preserving target, up, FOV, and clipping range.

`GSP-VIEW-007`: non-blocking/native controllers do not redefine replay semantics. Canonical actions
are deterministic from their inputs within documented floating-point tolerance.

## Resolved layout

Resolved layout records concrete logical-pixel rectangles for panels, plot regions, and guides. The same snapshot identity must be used by rendering and layout-aware queries. Device scale and output DPI are explicit metadata. Grid lines are clipped to the plot rectangle when strict layout behavior is advertised.

### ResolvedLayoutSnapshot

| Field | Type | Meaning |
|---|---|---|
| `id` | identifier | Snapshot identity. |
| `canvas_logical_size` | positive width/height | Reference layout space. |
| `device_scale` | positive finite x/y scale | Logical→framebuffer conversion. |
| `output_dpi` | positive finite value or null | Output metadata where meaningful. |
| `panel_rects` | panel ID→logical-pixel rectangle | Presentation/query regions. |
| `plot_rects` | panel ID→logical-pixel rectangle | Clipped data region. |
| `guide_boxes` | guide ID→resolved box/role | Exact guide geometry where supported. |
| `revision_inputs` | scene/view/guide revisions | Coherence inputs. |

Logical rectangles use `(x, y, width, height)` with nonnegative extent and an explicit pixel-origin
enum. `GSP-VIEW-008`: render, hit testing, guide geometry, and screen-coordinate queries use the
same snapshot rather than independently recomputed layout.

`Panel.viewport_rect` allocates the outer panel in the render target. In a resolved snapshot,
`panel_rect_px` is the complete panel presentation and guide-query region, while `plot_rect_px` is
the contained visual/data viewport remaining after guide and layout allocation. Both rectangles
must be finite and nonnegative, lie inside the render target, and the plot rectangle must be
contained by the panel rectangle. The outer panel must have positive area. A degenerate plot
contains no data; coordinate conversion, navigation, and aspect helpers reject it.

The authored viewport intent itself contains four finite normalized components. Its x/y origin is
nonnegative, width/height are positive, and closed containment requires `x + width <= 1` and
`y + height <= 1`. For logical target size `(W,H)`, outer-panel resolution is exactly
`(x*W, y*H, width*W, height*H)`. `RenderTarget.pixel_origin` must be a valid `PixelOrigin` enum
value (or be explicitly coerced from that enum's string value); an unknown string or other type is
invalid protocol state.

`GSP-VIEW-011`: DATA and panel-NDC visual positions map through `plot_rect_px`. Data queries,
View3D rays, mesh picking, and layout-dependent navigation use that same rectangle. A logical
coordinate inside `panel_rect_px` but outside `plot_rect_px` cannot hit a data visual; guide boxes
in that outer-panel space remain independently queryable.

Public logical pointer/query coordinates are absolute render-target logical coordinates. Panel NDC
maps through the closed `plot_rect_px`: with top-left origin, plot top-left is `(-1,+1)` and
bottom-right is `(+1,-1)`; bottom-left origin reverses y. Exact edges participate in geometric
round trips, while backend raster sample ownership may be half-open.

The typed routing classification is outside outer panel, panel guide lane, or data plot. Supported
DATA queries in a guide lane return MISS; GUIDE and ALL_RENDERED queries may hit guide boxes. Rays,
mesh picks, and navigation anchors never clamp or extrapolate a guide-lane coordinate into the
plot. Layout-dependent pan/zoom deltas use plot width and height.

View2D layout-aware navigation also uses the snapshot pixel origin. A minimum-logical-y-edge zoom
anchor preserves `y_max` for top-left logical coordinates and `y_min` for bottom-left logical
coordinates. Equal positive logical `dy_px` therefore produces opposite signed data pan under those
two origins.
Rect-only helper calls retain their established compatibility behavior but cannot claim
layout-strict origin resolution.

`GSP-VIEW-012`: layout-strict and cross-backend comparison consumes one produced
`ResolvedLayoutSnapshot` in every backend. A backend that cannot render a `PanelTextGuide` still
uses the snapshot's plot rectangle and reports the missing guide; it does not reclaim the guide
lane or change visual scale. Semantic-only rendering may resolve layout per backend when it reports
the applicable diagnostics.

The core snapshot is single-panel. Aggregate/multi-panel layout snapshots and a public
multi-panel authoring API are deferred.

`GSP-VIEW-009`: canvas sizing policies distinguish pixel-exact output from reference-pixel physical
intent. A backend reports resolved logical, framebuffer, device-scale, and DPI values; it does not
silently reinterpret one policy as another.

`GSP-VIEW-010`: strict guides require plot-rectangle grid clipping and deterministic explicit tick
placement. Backend-native auto ticks are adapted unless they realize the accepted GSP tick values
and labels exactly.
