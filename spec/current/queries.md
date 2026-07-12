# Queries and readback

## Panel-query model

A query asks what semantic or rendered contribution exists at a panel coordinate. The request declares panel, coordinate space, scope, hit policy, and desired payloads.

Scopes distinguish data visuals, guides, and all rendered contributions. A backend may support one scope without supporting another.

### QueryRequest

| Field | Type | Required/default |
|---|---|---|
| `id` | identifier | required request identity |
| `panel_id` | panel identifier | required |
| `coordinate` | finite pair | required |
| `coordinate_space` | panel logical pixels or panel NDC | required; no guessing |
| `scope` | data/guides/all-rendered | default data |
| `hit_policy` | frontmost/all | default frontmost |
| `payloads` | non-empty set of payload kinds | default identity |
| `expected_scene_revision` | non-negative integer or null | recommended for rendered queries |
| `expected_layout_snapshot_id` | identifier or null | required for layout-aware queries |
| `expected_view_snapshot_id` | identifier or null | required for inverse/view-dependent payloads |

| Rule | Requirement |
|---|---|
| `GSP-QUERY-001` | Query support is negotiated independently from rendering. A rendered visual does not imply identity, value, coordinate, color, depth, or primitive payload support. |
| `GSP-QUERY-002` | Query coordinates and their coordinate space are explicit. Outside-panel detection occurs against the named resolved panel rectangle. |
| `GSP-QUERY-003` | Requested payloads are planned before execution. Missing required payload capability returns unsupported, not a partial hit with silently omitted fields. |

## Result states

| Status | Meaning |
|---|---|
| Hit | A supported contribution satisfies the request. |
| Miss | The request was valid and supported, but no contribution matched. |
| Outside panel | The coordinate is outside the target region. |
| Unsupported | Required scope, policy, or payload capability is unavailable. |
| Stale | The request references an obsolete scene, view, or layout snapshot. |
| Invalid | The request itself violates the contract. |

Unsupported, stale, and invalid states must not be encoded as misses.

The complete core status vocabulary is `hit`, `miss`, `outside-panel`, `unsupported`, `stale`,
`invalid`, `dropped`, and `failed`. `dropped` is permitted only under an advertised bounded async
query policy. `failed` identifies execution failure after a valid supported request.

### QueryResult

| Field | Type | Required/default |
|---|---|---|
| `request_id` | identifier | required |
| `status` | query status | required |
| `hit` | boolean | required; true iff status is hit |
| `panel_coordinate` | finite pair | required echo/canonical coordinate |
| `hits` | ordered tuple of `QueryHit` | empty unless hit |
| `snapshot_ids` | scene/layout/view/resource identities | as required by payload |
| `diagnostics` | structured diagnostics | required for unsupported/stale/invalid/dropped/failed |

`GSP-QUERY-004`: result invariants are strict. `hit=true` requires at least one hit. Miss/outside
results have no fabricated hit. Unsupported/stale/invalid/dropped/failed results carry diagnostics.

## Payloads

Common payloads include visual identity, item or primitive index, visual/data/UV coordinates, displayed RGBA, scalar source and normalized values, depth/order, guide identity, and optional extension data. Only requested and supported fields may be returned.

### QueryHit common fields

| Field | Meaning |
|---|---|
| `contribution_kind` | data or guide |
| `visual_id` / `guide_id` | public semantic identity; exactly as applicable |
| `visual_family` | registered family for data hits |
| `item_index` | public item identity when defined |
| `primitive_index` | face/segment/glyph/texel identity when capability-gated |
| `order` / `depth` | ordering values under the advertised guarantee |
| `payloads` | typed payload records requested and supported |

`GSP-QUERY-005`: `frontmost` returns at most one contribution under the advertised ordering model.
`all` returns a deterministically ordered tuple and requires a separate ordering guarantee. Draw
order, depth order, and guide composition order must not be conflated.

### Typed payloads

| Payload | Minimum fields |
|---|---|
| identity | public entity and item/primitive identity |
| coordinate | visual/data/NDC/UV values plus inverse status |
| color | displayed RGBA and declared color-space role |
| scalar value | source value, normalized value, color-scale ID |
| guide | guide role, axis dimension, tick/label identity as available |
| View3D ray | canonical origin/direction and view projection snapshot |
| mesh pick | visual ID, public face/triangle ID, hit/miss state |
| mesh geometry | barycentric, data-space position, panel-NDC depth |
| mesh facing | projected front-facing classification and culling context |

`GSP-QUERY-006`: displayed color payload means the contribution color defined by the advertised
query profile. It is not automatically a final composited framebuffer pixel or scientific source
value; those require distinct payloads/capabilities.

Mesh-triangle picking is limited to advertised opaque DATA-space triangle scopes. Geometry payloads may add barycentric coordinates, data-space hit position, panel-NDC depth, and projected facing. Base identity-only payloads remain valid independently.

`GSP-QUERY-007`: identity-only, geometry, and facing mesh-pick capabilities are siblings. Geometry
or facing support does not mutate the base payload contract. Public face identity must correspond to
the protocol mesh topology, not a backend-expanded triangle index.

`GSP-QUERY-008`: culling, clipping, projection, and opaque depth used for picking match the rendered
snapshot. CPU reference picking may be strict only for its explicitly bounded accepted scope and
tolerance; otherwise it reports adaptation.

## Coherence

Queries that depend on view, projection, resource, or resolved-layout state carry the relevant snapshot identity. Implementations must reject stale queries rather than combining state from different frames.

`GSP-QUERY-009`: freshness comparison happens before returning semantic hit data. A stale request
returns the current and expected public snapshot/revision identities in a redacted diagnostic.

`GSP-QUERY-010`: query execution never mutates scene state. Internal caches are allowed but cannot
change public revisions, ordering, or subsequent rendering semantics.
