# Static View3D, Orthographic Projection, and 3D Mesh Semantics

Status: accepted S036 baseline for schema and validation; projection/render/query implementation is
staged across S036 missions.

Semantic purpose: define the smallest public 3D view state needed for `(N, 3)` `MeshVisual` data
without accepting a full graphics-engine object model.

## Scope

Accepted S036 concepts:

| Concept | Status | Semantics |
|---|---:|---|
| `Camera3D` | accepted | Camera parameters `eye`, `target`, `up`. |
| `OrthographicProjection3D` | accepted | Explicit camera-plane x/y bounds and near/far distances. |
| `View3D` | accepted | Static 3D view attached to one panel. |
| Orthographic projection | accepted | Deterministic DATA-to-panel NDC3 mapping. |
| `(N, 3)` DATA mesh | capability-gated | Mesh vertices projected through `View3D`. |
| `(N, 3)` NDC mesh | capability-gated | Mesh vertices interpreted as panel NDC x/y/z. |
| Opaque depth | capability-gated | Nearer opaque fragment wins where strict support is claimed. |
| Ray readback | accepted target | Query returns projection-inverse ray context. |
| 3D visual picking | deferred | Query hit identity for 3D mesh faces is unsupported in S036. |

Deferred concepts include public 3D navigation, perspective projection, matrix-first authoring,
materials/lights/normals, scene graphs, mesh-local 3D transforms, transparency sorting, strict
clipping of partially clipped triangles, external model loading, instancing, and non-mesh 3D visual
families.

## Public Model

`Camera3D` fields:

| Field | Required | Semantics |
|---|---:|---|
| `eye` | yes | Finite DATA-space camera position. |
| `target` | yes | Finite DATA-space point defining view direction with `eye`. |
| `up` | yes | Finite nonzero up hint not parallel to `target - eye`. |

`OrthographicProjection3D` fields:

| Field | Required | Semantics |
|---|---:|---|
| `kind` | no | Must be `orthographic` in S036. |
| `xlim` | yes | Camera-plane horizontal bounds; reversed bounds are valid. |
| `ylim` | yes | Camera-plane vertical bounds; reversed bounds are valid. |
| `near_far` | yes | Forward distances from `eye`; must satisfy `near >= 0` and `far > near`. |

`View3D` fields:

| Field | Required | Semantics |
|---|---:|---|
| `id` | yes | Stable view id. |
| `panel_id` | yes | Target panel id. |
| `camera` | yes | `Camera3D`. |
| `projection` | yes | `OrthographicProjection3D`. |
| `depth_mode` | no | `opaque_less` only in S036. |
| `kind` | no | `VIEW3D_CAMERA`. |
| `revision` | no | Non-negative semantic state revision. |

## Validation

Camera validation rejects:

- non-finite `eye`, `target`, or `up` components;
- `eye == target`;
- zero `up`;
- `up` parallel or anti-parallel to `target - eye`.

S036 uses `CAMERA3D_EPSILON = 1e-12` in double precision for degeneracy checks.

Projection validation rejects:

- non-finite x/y/near/far bounds;
- equal `xlim` or `ylim` endpoints;
- `near < 0`;
- `far <= near`;
- non-orthographic projection kind.

Reversed `xlim` and `ylim` are valid. Reversed `near_far` is invalid.

## Coordinate Convention

Camera basis:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

Panel NDC:

```text
x: -1 left, +1 right
y: -1 bottom, +1 top
z: -1 near, +1 far
smaller z is closer
```

For a DATA-space point `p`:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)

ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])
ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

Derived matrices may be reported later in snapshots for diagnostics and fixtures. They are not
public authoring input in S036.

## Projection Snapshot

Strict S036 projection support uses a resolved projection snapshot for one `View3D` and one layout
snapshot. The snapshot records:

- view id;
- panel id;
- view revision;
- layout snapshot id;
- view/projection snapshot id;
- camera `eye` and `target`;
- derived `right`, `true_up`, and `forward` basis vectors;
- projection `xlim`, `ylim`, and `near_far`;
- depth mode.

The `view_projection_snapshot_id` must change when canonical projection inputs change, including
camera state, projection bounds, view revision, layout snapshot id, or depth mode. It must remain
stable for repeated resolution of the same state.

## MeshVisual Integration

For `MeshVisual.positions.shape == (N, 3)` and `coordinate_space == DATA`:

```text
source vertices
-> View3D camera basis
-> orthographic projection
-> panel NDC3
-> rasterization/depth where supported
```

For `MeshVisual.positions.shape == (N, 3)` and `coordinate_space == NDC`:

```text
source x/y/z
-> panel NDC3 directly
-> rasterization/depth where supported
```

Existing `(N, 2)` mesh behavior remains unchanged. Existing 2D affine visual transforms do not apply
to `(N, 3)` geometry in S036.

Backends without compatible support must report structured unsupported diagnostics rather than
silently flattening z.

## Capabilities

Recommended capability names:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
```

These do not imply support for:

```text
view3d.perspective
view3d.navigation
meshvisual.positions3d.picking
meshvisual.positions3d.transparent_strict
meshvisual.positions3d.clipping_strict
```

## Diagnostics

Accepted S036 diagnostic vocabulary:

| Code | Meaning |
|---|---|
| `view3d_not_supported` | Backend does not support public `View3D`. |
| `view3d_projection_unsupported` | Projection kind is not supported. |
| `view3d_invalid_camera_degenerate` | `eye`, `target`, or `up` cannot form a valid basis. |
| `view3d_invalid_projection` | Invalid orthographic bounds or near/far range. |
| `mesh3d_requires_view3d` | `(N, 3)` DATA mesh is used without compatible `View3D`. |
| `mesh3d_coordinate_space_unsupported` | Backend cannot support requested 3D coordinate space. |
| `mesh3d_transform_unsupported` | A 2D affine transform was attached to `(N, 3)` geometry. |
| `mesh3d_depth_unsupported` | Backend cannot provide opaque 3D depth semantics. |
| `mesh3d_depth_adapted` | Backend rendered approximate/adapted depth. |
| `mesh3d_alpha_not_strict` | Alpha is below 1.0 in a strict-depth path. |
| `mesh3d_clipping_adapted` | Clipping behavior is adapted/unverified. |
| `query_3d_visual_hit_deferred` | 3D mesh picking is intentionally unsupported in S036. |
| `query_3d_snapshot_mismatch` | Query could not be answered for requested snapshots. |

## Query Boundary

S036 query/readback should return a deterministic projection-inverse ray context:

- panel logical coordinate;
- panel NDC coordinate;
- layout snapshot id;
- view id and revision;
- view/projection snapshot id;
- near and far DATA points;
- DATA-space ray direction.

S036 does not return strict 3D mesh face hit identity. Such requests return
`query_3d_visual_hit_deferred`.

## Backend Mapping

Matplotlib is strict for validation, projection math, and ray readback. 3D raster output is adapted
unless it satisfies the accepted S036 depth rules.

Datoviz is the intended first runtime 3D backend, but support must be capability-gated. It must not
leak Datoviz camera, material, slot, draw-state, or controller names into public protocol fields.

VisPy2 may provide ergonomic constructors/helpers that emit canonical `View3D` state. It must not
expose a public 3D navigation controller in S036.
