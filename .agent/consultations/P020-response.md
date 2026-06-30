## 1. Recommendation summary

This recommendation is based on the uploaded P020 consultation prompt and its stated constraints. 

* **Choose Option A + Option D for S036:** define a **static, camera-parameter-first, orthographic-only `View3D`** with deterministic projection math. Do **not** add public 3D navigation actions in S036.
* **Use `eye / target / up` as the public camera representation.** Do not accept arbitrary public view/projection matrices yet. Derived matrices may be reported in snapshots for diagnostics and conformance.
* **Support only strict orthographic projection in S036.** Perspective should be deferred until the orthographic path proves the coordinate, depth, query, and backend capability model.
* **Keep `CoordinateSpace.DATA` and `CoordinateSpace.NDC`.** Do not add `WORLD`, `MODEL`, `CLIP`, or `CAMERA` as public authoring spaces in S036.
* **Make `(N,3)` `MeshVisual` useful only through `View3D` capability-gated rendering.** `(N,3)` DATA meshes are projected by `View3D`; `(N,3)` NDC meshes are interpreted as panel NDC plus depth NDC.
* **Define a minimal opaque depth contract:** finite opaque triangles, no face culling by default, nearer fragments occlude farther fragments. Transparency, clipping strictness, materials, lights, normals, and advanced draw state remain deferred or adapted.
* **Define strict 3D query readback only for projection inverse / panel ray context, not mesh picking.** S036 should return coherent snapshot ids and a deterministic ray for `View3D`, while visual hit testing for 3D meshes returns structured unsupported diagnostics.
* **Allow interactive 3D demos only as adapted review paths.** Backend-native or VisPy2 demo orbit controls may exist, but their resulting state must be synchronized into canonical `View3D`; no public `View3DNavigationController` until S037.

---

## 2. Stage plan

| Stage                                       | Goal                                                                             | Public semantics added                                                                                             | Backend obligations                                                                                                                               | Fixtures                                                                                                   | Stop condition                                                                            |
| ------------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **S036.1 — Static `View3D` schema**         | Add the smallest valid 3D panel/view state                                       | `View3D`, `Camera3D`, `OrthographicProjection3D`, `DepthMode3D`, validation diagnostics, capability names          | Validate or reject with structured diagnostics; advertise capabilities explicitly                                                                 | Valid canonical camera; invalid eye/target/up; invalid projection bounds; unsupported perspective request  | Public schema and validation are frozen for orthographic static views                     |
| **S036.2 — Projection conformance**         | Make 3D-to-panel projection deterministic                                        | Normative `DATA -> camera -> NDC3` math; derived snapshot ids; optional derived matrices in snapshots              | Matplotlib and Datoviz must be able to compute identical projected NDC coordinates if they claim strict projection support                        | Cube vertex projection; reversed x/y bounds; off-axis orthographic bounds; panel center/corner ray inverse | Numeric projection fixtures pass independent of raster backend                            |
| **S036.3 — `(N,3)` `MeshVisual` rendering** | Make 3D mesh data renderable without a graphics-engine object model              | `(N,3)` DATA and NDC interpretation; opaque depth semantics; default no culling                                    | Datoviz should implement strict retained GPU rendering if capability is advertised; Matplotlib may be projection-reference or adapted render only | Opaque overlapping triangles with unambiguous depth; cube mesh; NDC-depth triangle                         | A backend can render static opaque 3D meshes or clearly report unsupported/adapted status |
| **S036.4 — Query/readback coherence**       | Preserve unified panel-query model without freezing picking                      | `View3DQueryContext`, panel NDC, near/far DATA points, ray direction, snapshot ids, unsupported 3D-hit diagnostics | Return coherent layout/view/projection snapshot ids; no hidden camera state                                                                       | Center ray; corner ray; stale snapshot rejection; 3D visual-hit unsupported result                         | Query results are deterministic and coherent even when 3D mesh picking is unsupported     |
| **S036.5 — Producer/API review examples**   | Let users exercise the feature safely                                            | VisPy2 public constructors/helpers for static `View3D`; no public 3D navigation controller                         | VisPy2 emits canonical protocol state; demos may update `View3D` directly                                                                         | Static cube, terrain-like mesh, NDC-depth fixture, unsupported-alpha fixture                               | Review examples cover useful 3D without adding navigation semantics                       |
| **S037 — Deferred 3D navigation**           | Define canonical orbit/pan/dolly/reset actions after static semantics are proven | Potential `View3DNavigationController`, `orbit_about`, `pan_in_view_plane`, `dolly`, `zoom_or_scale`, `reset_view` | Backends must return explicit updated `View3D`, never hidden native camera state                                                                  | Orbit determinism, retained update no buffer reupload, linked snapshot coherence                           | Requires a separate design review after S036 fixtures pass                                |

---

## 3. Minimal S036 public model

### 3.1 Public enums and dataclasses

```python
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional, Tuple


Float3 = Tuple[float, float, float]
Float2 = Tuple[float, float]


class Projection3DKind(str, Enum):
    ORTHOGRAPHIC = "orthographic"


class DepthMode3D(str, Enum):
    OPAQUE_LESS = "opaque_less"
```

S036 should define only one public projection kind. Do **not** add a public `PERSPECTIVE` enum value yet unless the implementation is prepared to support the exact semantics immediately.

```python
@dataclass(frozen=True)
class Camera3D:
    eye: Float3
    target: Float3
    up: Float3
```

```python
@dataclass(frozen=True)
class OrthographicProjection3D:
    kind: Literal[Projection3DKind.ORTHOGRAPHIC] = Projection3DKind.ORTHOGRAPHIC

    # Camera-plane horizontal and vertical bounds.
    # Reversed xlim/ylim are valid, matching View2D reversal precedent.
    xlim: Float2 = (-1.0, 1.0)
    ylim: Float2 = (-1.0, 1.0)

    # Forward distances from eye.
    # near_far[0] is the near distance, near_far[1] is the far distance.
    # Unlike xlim/ylim, this is not reversible.
    near_far: Float2 = (0.0, 1.0)
```

```python
@dataclass(frozen=True)
class View3D:
    id: str
    camera: Camera3D
    projection: OrthographicProjection3D
    depth_mode: DepthMode3D = DepthMode3D.OPAQUE_LESS

    # Retained semantic state revision.
    # Incremented by the server/session whenever this view state is replaced.
    revision: int = 0
```

Optional resolved snapshot object:

```python
@dataclass(frozen=True)
class View3DResolvedSnapshot:
    view_id: str
    view_revision: int
    layout_snapshot_id: str
    view_projection_snapshot_id: str

    eye: Float3
    target: Float3
    right: Float3
    true_up: Float3
    forward: Float3

    xlim: Float2
    ylim: Float2
    near_far: Float2

    # Optional diagnostic/conformance fields.
    # These are derived outputs, not public authoring inputs.
    data_to_camera_matrix_row_major: Optional[Tuple[float, ...]] = None
    camera_to_ndc_matrix_row_major: Optional[Tuple[float, ...]] = None
```

### 3.2 Validation rules

`Camera3D` is valid only if:

| Field                   | Rule                                                                 |
| ----------------------- | -------------------------------------------------------------------- |
| `eye`, `target`, `up`   | All components finite                                                |
| `eye`, `target`         | `eye != target`                                                      |
| `up`                    | finite nonzero vector                                                |
| `up` vs. view direction | `up` must not be parallel or anti-parallel to `target - eye`         |
| derived basis           | `right`, `true_up`, and `forward` must be finite after normalization |

Recommended degeneracy rule:

```text
forward_raw = target - eye
up_raw = up

reject if norm(forward_raw) <= camera_epsilon
reject if norm(up_raw) <= camera_epsilon
reject if norm(cross(normalize(forward_raw), normalize(up_raw))) <= camera_epsilon
```

Use a single documented implementation epsilon for validation, for example `1e-12` in double precision. The exact epsilon should be recorded in the spec so negative fixtures are deterministic.

`OrthographicProjection3D` is valid only if:

| Field           | Rule                                                                   |
| --------------- | ---------------------------------------------------------------------- |
| `xlim`          | both finite; endpoints must not be equal; reversed endpoints are valid |
| `ylim`          | both finite; endpoints must not be equal; reversed endpoints are valid |
| `near_far`      | both finite; `near >= 0`; `far > near`; reversed near/far is invalid   |
| projection kind | must be `"orthographic"` in S036                                       |

Do **not** require `target` to lie between `near` and `far`. That should be allowed, because `target` defines view direction; clipping range is a separate projection choice. Fixtures should nevertheless use a visible target to avoid surprise.

### 3.3 Coordinate conventions

S036 should define a GSP 3D normalized device coordinate convention independent of OpenGL, WebGPU, Matplotlib, or Datoviz internals:

```text
panel NDC x: -1 is panel left, +1 is panel right
panel NDC y: -1 is panel bottom, +1 is panel top
panel NDC z: -1 is near, +1 is far
smaller z_ndc is closer to the camera
```

The camera basis is derived as:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

This gives the intuitive canonical case:

```text
eye    = (0, 0, 1)
target = (0, 0, 0)
up     = (0, 1, 0)

forward = (0, 0, -1)
right   = (1, 0, 0)
true_up = (0, 1, 0)
```

For a DATA-space point `p = (x, y, z)`, camera coordinates are:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)
```

For orthographic projection:

```text
ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])

ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])

ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

where:

```text
near = near_far[0]
far  = near_far[1]
```

This intentionally mirrors the accepted `View2D` linear-limit style while extending it to a camera-plane basis and a forward depth interval.

### 3.4 Matrix policy

Public authoring input should be **camera-parameter-first only** in S036.

Do **not** accept this in the public S036 schema:

```python
View3D(view_matrix=..., projection_matrix=...)
```

Reasons:

* Matrices expose too many convention choices too early.
* They make query/readback harder to standardize.
* They allow non-invertible, skewed, or projective states that do not match the intended minimal camera model.
* They prematurely resemble backend draw state.

However, derived matrices are useful as readback and test artifacts. S036 may expose them in `View3DResolvedSnapshot` as optional diagnostic fields, provided the formulas above remain the normative contract.

### 3.5 Snapshot and revision rules

A strict S036 render involving `View3D` must report:

```python
@dataclass(frozen=True)
class Render3DSnapshotRefs:
    panel_id: str
    layout_snapshot_id: str
    view_id: str
    view_revision: int
    view_projection_snapshot_id: str
    strict_projection: bool
    strict_depth: bool
```

A strict or unsupported S036 query against a `View3D` panel must report the same categories:

```python
@dataclass(frozen=True)
class Query3DSnapshotRefs:
    panel_id: str
    layout_snapshot_id: str
    view_id: str
    view_revision: int
    view_projection_snapshot_id: str
```

The `view_projection_snapshot_id` should change when any of the following changes:

* `View3D.camera`
* `View3D.projection`
* `View3D.depth_mode`, if it affects render/query interpretation
* panel layout snapshot, if panel-coordinate resolution depends on it
* any future aspect policy that derives projection from panel size

Even though S036 orthographic bounds are explicit and not auto-aspect-adjusted, include `layout_snapshot_id` in the snapshot identity to preserve the same render/query coherence discipline as S035.

### 3.6 Diagnostics

Recommended diagnostic codes:

| Code                                  | Meaning                                                                                 |
| ------------------------------------- | --------------------------------------------------------------------------------------- |
| `view3d_not_supported`                | Backend does not support public `View3D`                                                |
| `view3d_projection_unsupported`       | Projection kind is not supported; in S036 this includes any non-orthographic projection |
| `view3d_invalid_camera_degenerate`    | `eye`, `target`, or `up` cannot form a valid basis                                      |
| `view3d_invalid_projection`           | Invalid orthographic bounds or near/far range                                           |
| `mesh3d_requires_view3d`              | `(N,3)` DATA mesh is used without a compatible `View3D`                                 |
| `mesh3d_coordinate_space_unsupported` | Backend cannot support `(N,3)` in the requested coordinate space                        |
| `mesh3d_transform_unsupported`        | A 2D affine visual transform was attached to `(N,3)` geometry                           |
| `mesh3d_depth_unsupported`            | Backend cannot provide opaque 3D depth semantics                                        |
| `mesh3d_depth_adapted`                | Backend rendered an approximate/adapted depth result                                    |
| `mesh3d_alpha_not_strict`             | Mesh uses alpha less than 1.0 in a path claiming strict 3D depth                        |
| `mesh3d_clipping_adapted`             | Geometry crosses clip bounds and backend clipping behavior is not strict                |
| `query_3d_visual_hit_deferred`        | 3D rendered-contribution hit testing is intentionally unsupported in S036               |
| `query_3d_snapshot_mismatch`          | Query could not be answered against the requested render/layout/view snapshot           |

---

## 4. MeshVisual `(N,3)` integration

### 4.1 Scope

S036 should enable only this 3D visual case:

```text
MeshVisual.positions shape == (N, 3)
MeshVisual.faces shape == (M, 3)
visual family == MeshVisual
projection == View3D orthographic
geometry == finite indexed triangles
fill == uniform or per-face RGBA
```

Do not use S036 to add 3D point clouds, 3D text, 3D image planes, volume rendering, surface materials, normals, lighting, model transforms, or scene graph nodes.

### 4.2 `(N,3)` with `CoordinateSpace.DATA`

Pipeline:

```text
source mesh vertex positions, shape (N, 3)
-> CoordinateSpace.DATA
-> View3D camera basis
-> View3D orthographic projection
-> panel NDC3
-> panel/framebuffer rasterization
-> opaque depth resolution, if strict depth is claimed
```

Interpretation:

* The vertex triples are in the panel’s `View3D` DATA coordinate system.
* This is not a new public `WORLD` or `MODEL` space.
* There is no mesh-local transform in S036.
* Existing 2D affine transforms do not apply to `(N,3)` positions.
* `(N,3)` DATA meshes require a panel with a compatible `View3D`.
* If the backend lacks `view3d.static.orthographic.v1`, it must not silently flatten or ignore z; it must return structured unsupported diagnostics.

### 4.3 `(N,3)` with `CoordinateSpace.NDC`

Pipeline:

```text
source mesh vertex positions, shape (N, 3)
-> CoordinateSpace.NDC
-> panel NDC3 directly
-> panel/framebuffer rasterization
-> opaque depth resolution, if strict depth is claimed
```

Interpretation:

```text
position[:, 0] is panel NDC x
position[:, 1] is panel NDC y
position[:, 2] is GSP NDC depth z
```

where:

```text
z = -1 means near
z = +1 means far
smaller z is closer
```

Rules:

* `(N,3)` NDC bypasses `View3D.camera` and `View3D.projection`.
* It still requires a backend capability for 3D mesh rasterization/depth if strict 3D rendering is claimed.
* In S036, restrict `(N,3)` NDC to panels participating in the 3D rendering path. Do not introduce mixed View2D/View3D depth composition semantics yet.
* `(N,2)` NDC mesh behavior remains unchanged from the accepted 2D baseline.

### 4.4 Depth and culling defaults

Strict S036 depth semantics should be:

```text
For fully opaque 3D mesh fragments in the same panel, the visible fragment is the valid fragment with the smallest ndc_z value.
```

Default policy:

```python
depth_mode = DepthMode3D.OPAQUE_LESS
```

Meaning:

* Depth testing is semantic, not a public OpenGL/WebGPU state object.
* Implementations may use a GPU depth buffer, CPU rasterization, triangle sorting where valid, or another method.
* The public contract is visible-surface ordering, not the backend mechanism.

Culling:

```text
Default face culling: none.
Triangles are two-sided filled surfaces.
```

This is important because S025 did not define normals, winding semantics, lighting, or materials. Introducing back-face culling now would create hidden dependence on winding order before the protocol has a public surface/material model.

Alpha:

```text
Strict S036 3D depth requires alpha == 1.0 for all rendered 3D mesh faces.
```

If any uniform or per-face RGBA color has alpha less than 1.0:

* the backend may render adapted output;
* the render result must not claim strict 3D depth;
* strict publication/conformance capture should reject or report `mesh3d_alpha_not_strict`.

Clipping:

For S036, strict fixtures should keep all triangles fully inside the view volume:

```text
-1 <= ndc_x <= +1
-1 <= ndc_y <= +1
-1 <= ndc_z <= +1
```

General clipping of triangles crossing near/far or side planes should be capability-gated or adapted in S036. Do not make full triangle clipping a release blocker for the first public `View3D`.

### 4.5 Without 3D capability

If a scene contains `(N,3)` `MeshVisual` data and the selected backend does not advertise compatible 3D support, the backend should return an unsupported diagnostic instead of flattening:

```json
{
  "code": "mesh3d_requires_view3d",
  "severity": "error",
  "message": "MeshVisual with positions shape (N,3) in CoordinateSpace.DATA requires a supported View3D."
}
```

or:

```json
{
  "code": "view3d_not_supported",
  "severity": "error",
  "message": "Backend does not support static orthographic View3D."
}
```

### 4.6 Remains unsupported in S036

* Perspective projection
* Orbit/trackball navigation semantics
* Public backend camera/controller objects
* Public matrices as authoring input
* Mesh-local 3D transforms
* Normals
* Lighting
* Materials
* Generated normals
* Back-face culling
* Per-vertex color, unless already separately capability-gated
* Transparency sorting
* Volume rendering
* Surface/terrain convenience visual
* External model loading
* Instancing
* LOD/chunked geometry
* 3D mesh picking / ray-triangle hit reporting
* Strict clipping of partially out-of-volume triangles, unless separately advertised

---

## 5. Query/readback policy

### 5.1 Recommendation

S036 should define **strict 3D projection inverse query context**, but **not strict 3D visual picking**.

That gives the protocol a coherent readback story without freezing ray/triangle intersection, tolerance, face identity, interpolated attributes, depth-buffer readback, or multi-layer hit behavior too early.

### 5.2 Public query result model

```python
@dataclass(frozen=True)
class View3DQueryContext:
    panel_id: str
    panel_logical_xy: Float2
    panel_ndc_xy: Float2

    layout_snapshot_id: str
    view_id: str
    view_revision: int
    view_projection_snapshot_id: str

    # DATA-space orthographic ray through this panel coordinate.
    ray_origin_data: Float3
    ray_direction_data: Float3
    near_point_data: Float3
    far_point_data: Float3

    inverse_status: Literal["ok"]
```

For a `View3D` orthographic query:

```text
ndc_x, ndc_y = resolved panel NDC coordinate

camera_x = xlim[0] + 0.5 * (ndc_x + 1) * (xlim[1] - xlim[0])
camera_y = ylim[0] + 0.5 * (ndc_y + 1) * (ylim[1] - ylim[0])

near_point = eye + near * forward + camera_x * right + camera_y * true_up
far_point  = eye + far  * forward + camera_x * right + camera_y * true_up

ray_origin_data    = near_point
ray_direction_data = forward
```

This is strict and easy to test.

### 5.3 Visual hit result in S036

The unified panel-query model asks, “what rendered scene contribution is under this panel coordinate?” In S036, the answer for 3D mesh contribution should be:

```python
@dataclass(frozen=True)
class Query3DVisualHit:
    status: Literal["unsupported"]
    visual_id: None
    source_index: None
    diagnostics: tuple
```

with diagnostic:

```json
{
  "code": "query_3d_visual_hit_deferred",
  "severity": "info",
  "message": "S036 defines View3D ray readback but not 3D mesh picking."
}
```

The full query result can still include `View3DQueryContext`, so users and tests can verify the camera/projection inverse.

### 5.4 Snapshot coherence

Every 3D query result, even unsupported visual-hit results, must carry:

```text
panel_id
layout_snapshot_id
view_id
view_revision
view_projection_snapshot_id
```

If the query is requested against a specific previous render snapshot and the backend cannot answer against that exact state, return:

```json
{
  "code": "query_3d_snapshot_mismatch",
  "severity": "error",
  "message": "The query could not be answered against the requested View3D/layout snapshot."
}
```

Do not answer from the current hidden backend camera if it differs from the canonical protocol `View3D`.

---

## 6. Backend mapping

### 6.1 Matplotlib

Matplotlib’s S036 role should be **projection reference / diagnostic publication path**, not necessarily strict 3D raster authority.

Mandatory Matplotlib responsibilities:

| Area                   | Responsibility                                                                  |
| ---------------------- | ------------------------------------------------------------------------------- |
| Schema                 | Accept, validate, or reject `View3D` objects                                    |
| Projection             | Compute canonical `DATA -> NDC3` projection using the normative formulas        |
| Snapshots              | Return `layout_snapshot_id`, `view_revision`, and `view_projection_snapshot_id` |
| Query                  | Return strict `View3DQueryContext` ray readback                                 |
| Unsupported 3D picking | Return `query_3d_visual_hit_deferred`                                           |
| Diagnostics            | Clearly distinguish strict projection from adapted rendering                    |

Optional/adapted Matplotlib responsibilities:

| Area                     | Policy                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Static 3D mesh rendering | May render projected triangles for review/publication if it can report whether depth is strict or adapted      |
| Depth                    | Should not claim strict general 3D depth unless implemented against the S036 depth rule                        |
| mplot3d                  | May be used only as adapted/diagnostic output if its projection/depth behavior is not exactly the GSP contract |

Recommended implementation path:

* Implement the projection math in backend-independent code used by Matplotlib tests.
* For publication review, Matplotlib may draw projected 2D triangles.
* Strict image comparison should be limited to fixtures where the implementation genuinely satisfies the S036 depth rule.
* If Matplotlib cannot provide strict depth, it should still pass numeric projection/readback fixtures.

### 6.2 Datoviz v0.4

Datoviz should be the first meaningful runtime backend for S036 3D.

Mandatory Datoviz responsibilities if it advertises `view3d.static.orthographic.v1`:

| Area              | Responsibility                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------- |
| View state        | Map canonical `View3D` to retained backend camera/projection state without leaking Datoviz object names |
| Mesh rendering    | Render `(N,3)` DATA `MeshVisual` through canonical orthographic projection                              |
| NDC rendering     | Render `(N,3)` NDC `MeshVisual` as panel NDC plus depth                                                 |
| Depth             | Provide strict opaque nearer-fragment-wins behavior for supported fixtures                              |
| Retained updates  | Updating `View3D` must not reupload unchanged mesh buffers                                              |
| Snapshots         | Report canonical view/layout/projection snapshot ids                                                    |
| Query             | Return canonical ray readback; return unsupported diagnostic for mesh picking                           |
| Capability gating | Reject or adapt unsupported alpha, clipping, perspective, picking, and transforms explicitly            |

Datoviz must not expose public protocol fields such as:

```text
Datoviz camera type
Datoviz slot names
Datoviz material structs
Datoviz draw-state identifiers
Datoviz interaction/controller objects
```

Backend-native interaction may be used only experimentally, and only if the resulting camera state is synchronized back into canonical `View3D`.

### 6.3 VisPy2 producer API

VisPy2 should provide ergonomic construction of canonical S036 state, not a separate camera object model.

Suggested public API shape:

```python
view = gsp.View3D(
    id="main_3d",
    camera=gsp.Camera3D(
        eye=(3.0, 3.0, 3.0),
        target=(0.0, 0.0, 0.0),
        up=(0.0, 1.0, 0.0),
    ),
    projection=gsp.OrthographicProjection3D(
        xlim=(-2.0, 2.0),
        ylim=(-2.0, 2.0),
        near_far=(0.1, 10.0),
    ),
)
```

Possible convenience helper:

```python
view = gsp.view3d_ortho(
    id="main_3d",
    eye=(3, 3, 3),
    target=(0, 0, 0),
    up=(0, 1, 0),
    xlim=(-2, 2),
    ylim=(-2, 2),
    near_far=(0.1, 10),
)
```

VisPy2 should:

* validate camera and projection parameters before emission;
* preserve canonical field names;
* expose capability discovery results to users;
* make `(N,3)` `MeshVisual` construction straightforward;
* not expose public orbit/trackball controller semantics in S036;
* allow examples that programmatically replace `View3D` state for review.

Allowed adapted demo:

```text
drag mouse -> demo computes new eye/target/up -> emits canonical View3D replacement
```

Not allowed as public S036 semantics:

```text
backend_native_trackball = True
controller = DatovizArcball(...)
event = RawMouseDrag(...)
```

---

## 7. Required conformance fixtures and negative fixtures

### 7.1 Positive fixtures

| Fixture                          | Purpose                                               | Required expected output                                                                     |
| -------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Canonical camera basis**       | Validate `eye/target/up` basis derivation             | `forward`, `right`, `true_up` exactly as specified within tolerance                          |
| **Cube projection**              | Validate DATA `(N,3)` projection                      | Expected NDC3 vertex coordinates                                                             |
| **Reversed xlim**                | Match View2D precedent for reversed horizontal limits | Mirrored `ndc_x`                                                                             |
| **Reversed ylim**                | Match View2D precedent for reversed vertical limits   | Mirrored `ndc_y`                                                                             |
| **Off-axis orthographic bounds** | Ensure x/y bounds are explicit and not auto-centered  | Target need not project to panel center                                                      |
| **NDC3 triangle**                | Validate `(N,3)` `CoordinateSpace.NDC` interpretation | x/y/z used directly as panel NDC3                                                            |
| **Opaque depth overlap**         | Validate nearer-fragment-wins                         | Near triangle visible over far triangle at unambiguous sample point                          |
| **No face culling**              | Validate two-sided default                            | Reversed winding triangle still renders                                                      |
| **Center ray query**             | Validate panel center inverse                         | Correct near/far DATA points and direction                                                   |
| **Corner ray query**             | Validate non-center inverse                           | Correct x/y camera offsets in near/far DATA points                                           |
| **Snapshot coherence**           | Validate render/query state identity                  | Render and query carry matching layout/view/projection snapshot ids                          |
| **Retained view update**         | Especially for Datoviz                                | Changing `View3D` updates camera/projection state without reuploading unchanged mesh buffers |

Example canonical ray fixture:

```text
eye = (0, 0, 5)
target = (0, 0, 0)
up = (0, 1, 0)
xlim = (-2, 2)
ylim = (-2, 2)
near_far = (1, 10)

forward = (0, 0, -1)
right = (1, 0, 0)
true_up = (0, 1, 0)

panel_ndc = (0, 0)

near_point = (0, 0, 4)
far_point  = (0, 0, -5)
ray_direction = (0, 0, -1)
```

Corner fixture:

```text
panel_ndc = (1, 1)

camera_x = 2
camera_y = 2

near_point = (2, 2, 4)
far_point  = (2, 2, -5)
ray_direction = (0, 0, -1)
```

### 7.2 Negative fixtures

| Fixture                                                         | Expected diagnostic                                             |
| --------------------------------------------------------------- | --------------------------------------------------------------- |
| `eye == target`                                                 | `view3d_invalid_camera_degenerate`                              |
| zero `up` vector                                                | `view3d_invalid_camera_degenerate`                              |
| `up` parallel to `target - eye`                                 | `view3d_invalid_camera_degenerate`                              |
| non-finite camera component                                     | `view3d_invalid_camera_degenerate`                              |
| `xlim[0] == xlim[1]`                                            | `view3d_invalid_projection`                                     |
| `ylim[0] == ylim[1]`                                            | `view3d_invalid_projection`                                     |
| `near < 0`                                                      | `view3d_invalid_projection`                                     |
| `far <= near`                                                   | `view3d_invalid_projection`                                     |
| non-orthographic projection in public S036 schema               | `view3d_projection_unsupported` or schema validation error      |
| `(N,3)` DATA mesh on `View2D` panel                             | `mesh3d_requires_view3d`                                        |
| `(N,3)` DATA mesh with no 3D backend capability                 | `view3d_not_supported` or `mesh3d_coordinate_space_unsupported` |
| `(N,3)` mesh with 2D affine transform                           | `mesh3d_transform_unsupported`                                  |
| alpha less than 1.0 in strict 3D capture                        | `mesh3d_alpha_not_strict`                                       |
| triangle crossing clipping boundary without clipping capability | `mesh3d_clipping_adapted`                                       |
| query requesting 3D mesh hit                                    | `query_3d_visual_hit_deferred`                                  |
| query against stale/unavailable snapshot                        | `query_3d_snapshot_mismatch`                                    |

---

## 8. Explicit deferrals

S036 should explicitly defer:

1. **Public 3D navigation**

   * no `View3DNavigationController`
   * no public orbit, arcball, trackball, dolly, roll, fly, first-person, or gesture semantics
   * no raw mouse/wheel/key/touch event protocol

2. **Perspective projection**

   * no public FOV/aspect/film-back semantics
   * no perspective divide fixtures
   * no depth precision contract for perspective

3. **Matrix-first authoring**

   * no public arbitrary view matrix
   * no public arbitrary projection matrix
   * no custom clip-space transforms

4. **Additional coordinate spaces**

   * no `WORLD`
   * no `MODEL`
   * no `CAMERA`
   * no `CLIP`
   * no `SCREEN`
   * no geospatial/date/categorical/log 3D scales

5. **Scene graph / model system**

   * no nodes
   * no hierarchical transforms
   * no mesh-local 3D affine transform
   * no instancing
   * no external model loading

6. **Materials and lighting**

   * no normals
   * no generated normals
   * no Lambert/Phong/PBR
   * no lights
   * no public material records
   * no texture/UV semantics

7. **Advanced rendering**

   * no strict transparency sorting
   * no order-independent transparency
   * no strict clipping for partially clipped triangles unless separately advertised
   * no advanced culling
   * no wireframe conformance
   * no antialiasing/pixel-coverage contract beyond existing backend policies

8. **3D picking**

   * no ray-triangle visual hit
   * no depth-buffer readback
   * no interpolated barycentric/source attributes
   * no nearest-surface selection
   * no multi-hit stack

9. **Non-mesh 3D visual families**

   * no 3D markers
   * no 3D text
   * no 3D images
   * no volume rendering
   * no isosurfaces or surface convenience visual

---

## 9. Risks and mitigations

| Risk                                         | Why it matters                                                   | Mitigation                                                                                                                                            |
| -------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orthographic-only feels too small            | Users often expect perspective for 3D                            | Allow adapted demos privately, but keep public strict S036 orthographic; schedule perspective for a later ADR after projection/readback fixtures pass |
| Camera conventions become controversial      | Handedness, z range, and y orientation differ across backends    | Define formulas as normative; treat matrices as derived diagnostics only                                                                              |
| Matplotlib cannot be strict 3D authority     | mplot3d behavior may not match GSP depth/projection exactly      | Make Matplotlib strict for validation/projection/readback; mark 3D raster as adapted unless it satisfies fixtures                                     |
| Datoviz implementation details leak          | Datoviz is likely first runtime 3D backend                       | Capability names and public schema must remain semantic; no Datoviz object names in public protocol                                                   |
| Depth semantics overfreeze draw state        | Graphics APIs differ in depth conventions                        | Define only visible result: nearer opaque fragment wins; do not expose depth buffer functions beyond semantic `OPAQUE_LESS`                           |
| Query model feels incomplete                 | GSP treats query/readback as first-class                         | Return strict ray/projection context and explicit unsupported visual-hit diagnostics                                                                  |
| Transparent meshes produce misleading images | Alpha blending in 3D requires ordering policy                    | Do not claim strict depth for alpha < 1; require diagnostics                                                                                          |
| Clipping is harder than expected             | Correct triangle clipping can become a large implementation task | S036 strict fixtures keep geometry inside the view volume; clipped triangles are adapted/capability-gated                                             |
| Navigation semantics get designed too early  | Orbit, pan, dolly, target, roll, and zoom conventions are sticky | Defer public navigation to S037; allow demos that emit canonical `View3D` replacements                                                                |

---

## 10. ADR/spec skeleton

````markdown
# ADR S036: Minimal Static View3D, Orthographic Camera, Projection, and 3D Mesh Semantics

## Status

Accepted / Proposed

## Context

GSP currently has a coherent static 2D API and retained `View2D` navigation. `MeshVisual` already permits positions with shape `(N,3)`, but public 3D camera, projection, depth, and query semantics are deferred. S036 defines the smallest public 3D semantic surface needed to render `(N,3)` meshes without importing backend-specific graphics engine models.

## Decision

S036 adds a static `View3D` with:

- `Camera3D(eye, target, up)`
- `OrthographicProjection3D(xlim, ylim, near_far)`
- `DepthMode3D.OPAQUE_LESS`
- deterministic DATA-to-camera and camera-to-NDC projection math
- `(N,3)` `MeshVisual` integration for `CoordinateSpace.DATA` and `CoordinateSpace.NDC`
- strict query readback for panel-to-DATA ray context
- explicit unsupported diagnostics for 3D visual picking

S036 does not add public 3D navigation, perspective projection, matrix-first authoring, materials, lighting, scene graph nodes, or 3D picking.

## Public Types

```python
class Projection3DKind(str, Enum):
    ORTHOGRAPHIC = "orthographic"

class DepthMode3D(str, Enum):
    OPAQUE_LESS = "opaque_less"

@dataclass(frozen=True)
class Camera3D:
    eye: Float3
    target: Float3
    up: Float3

@dataclass(frozen=True)
class OrthographicProjection3D:
    kind: Literal["orthographic"]
    xlim: Float2
    ylim: Float2
    near_far: Float2

@dataclass(frozen=True)
class View3D:
    id: str
    camera: Camera3D
    projection: OrthographicProjection3D
    depth_mode: DepthMode3D = DepthMode3D.OPAQUE_LESS
    revision: int = 0
````

## Coordinate Convention

Panel NDC:

```text
x: -1 left, +1 right
y: -1 bottom, +1 top
z: -1 near, +1 far
```

Camera basis:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

DATA point projection:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)

ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])
ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

## Validation

Reject:

* non-finite camera or projection values
* `eye == target`
* zero `up`
* `up` parallel or anti-parallel to `target - eye`
* equal x or y bounds
* `near < 0`
* `far <= near`
* non-orthographic public projection in S036

Reversed `xlim` and `ylim` are valid. Reversed near/far is invalid.

## MeshVisual Integration

For positions shape `(N,3)`:

* `CoordinateSpace.DATA`: vertices are in `View3D` DATA coordinates and are projected by `View3D`.
* `CoordinateSpace.NDC`: vertices are already panel NDC3.
* Existing 2D affine transforms do not apply.
* Strict S036 depth applies only to opaque meshes.
* Default culling is none.

## Depth Semantics

For fully opaque 3D mesh fragments, the visible fragment is the one with the smallest `ndc_z`.

Equal-depth overlaps, transparency, clipping of partially out-of-volume triangles, and advanced culling are not strict S036 behavior.

## Query Semantics

S036 query returns:

* panel logical coordinate
* panel NDC coordinate
* layout snapshot id
* view id and revision
* view/projection snapshot id
* near and far DATA points
* DATA-space ray direction

S036 does not return 3D mesh hit identity. Such requests return `query_3d_visual_hit_deferred`.

## Backend Requirements

### Matplotlib

* strict validation and projection math
* strict query ray readback
* adapted or unsupported 3D raster unless exact S036 depth semantics are satisfied

### Datoviz

* retained static orthographic `View3D`
* `(N,3)` DATA and NDC mesh rendering
* strict opaque depth for supported fixtures
* no public leakage of Datoviz object model
* no unchanged mesh-buffer reupload on view updates

### VisPy2

* emit canonical `View3D` objects
* validate authoring inputs
* expose capability diagnostics
* no public 3D navigation controller in S036

## Capabilities

Recommended capability names:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
```

Explicitly not implied:

```text
view3d.perspective
view3d.navigation
meshvisual.positions3d.picking
meshvisual.positions3d.transparent_strict
meshvisual.positions3d.clipping_strict
```

## Consequences

Positive:

* `(N,3)` mesh data becomes a real protocol feature.
* Projection and query are deterministic.
* Datoviz can provide useful GPU 3D without leaking backend concepts.
* Matplotlib can remain a reference for projection/readback even if strict 3D raster is limited.

Negative:

* No public perspective yet.
* No public orbit/trackball navigation yet.
* No strict 3D picking yet.
* Some useful 3D rendering cases remain adapted.

## Deferrals

* Perspective projection
* `View3DNavigationController`
* 3D picking
* matrix-first authoring
* materials/lights/normals
* scene graph/model transforms
* transparency sorting
* strict clipping
* non-mesh 3D visual families

````

---

## 11. Mission Control recommendation

### Mission 1 — Spec and validation

**Goal:** Add public `View3D` schema, validation, capabilities, and diagnostics.

**Dependencies:** Accepted S027 transform/view/query baseline; accepted S025 `MeshVisual`.

**Stop condition:**

- Valid and invalid `View3D` fixtures pass.
- No backend silently accepts degenerate cameras.
- Unsupported projection requests produce structured diagnostics.

**Needs another Pro consultation:** No.

---

### Mission 2 — Projection and snapshot conformance

**Goal:** Implement backend-independent projection math and snapshot identity.

**Dependencies:** Mission 1.

**Stop condition:**

- Canonical cube, reversed bounds, off-axis bounds, and query ray fixtures pass.
- Render/query results carry matching `layout_snapshot_id`, `view_revision`, and `view_projection_snapshot_id`.

**Needs another Pro consultation:** No.

---

### Mission 3 — MeshVisual `(N,3)` DATA and NDC rendering path

**Goal:** Make `(N,3)` `MeshVisual` renderable through `View3D` where capability is advertised.

**Dependencies:** Mission 2.

**Stop condition:**

- Datoviz renders static opaque `(N,3)` DATA meshes through canonical `View3D`.
- Datoviz renders `(N,3)` NDC meshes as panel NDC3.
- Backends without support return structured diagnostics.
- Existing `(N,2)` mesh behavior is unchanged.

**Needs another Pro consultation:** No, unless Datoviz v0.4 exposes an unavoidable camera/depth limitation that would force public semantic changes.

---

### Mission 4 — Opaque depth fixture

**Goal:** Establish the minimal strict 3D depth contract.

**Dependencies:** Mission 3.

**Stop condition:**

- Unambiguous overlapping opaque triangles render with the nearer triangle visible.
- Reversed winding still renders.
- Alpha less than 1.0 prevents strict-depth claims.
- Clipping-edge cases are diagnosed as adapted unless separately implemented.

**Needs another Pro consultation:** Possibly only if strict depth cannot be implemented without exposing backend draw-state concepts.

---

### Mission 5 — Query ray readback

**Goal:** Preserve first-class query/readback coherence without adding picking.

**Dependencies:** Mission 2.

**Stop condition:**

- Center and corner ray fixtures pass.
- 3D visual hit requests return `query_3d_visual_hit_deferred`.
- Stale snapshot queries fail with `query_3d_snapshot_mismatch`.

**Needs another Pro consultation:** No.

---

### Mission 6 — Review examples and adapted interactive demo

**Goal:** Provide useful user-facing examples while keeping public semantics static.

**Dependencies:** Missions 1–5.

**Examples:**

- static cube mesh
- simple terrain-like mesh
- two overlapping opaque triangles
- NDC-depth triangle
- alpha-not-strict negative example
- optional adapted orbit demo that emits canonical `View3D` replacements

**Stop condition:**

- Examples demonstrate useful 3D rendering.
- Any interactive demo is labeled adapted/experimental.
- No public `View3DNavigationController` or backend-native controller object appears in protocol semantics.

**Needs another Pro consultation:** No for demos. Yes before promoting orbit/pan/dolly/reset actions into S037 public semantics.

---

## Final decision

S036 should be a **small, strict, static 3D stage**:

```text
Static View3D
+ eye/target/up camera
+ orthographic projection
+ DATA/NDC interpretation for (N,3) MeshVisual
+ opaque depth capability
+ projection/ray readback
- no perspective
- no public navigation
- no matrix-first authoring
- no 3D picking
- no materials/lights/scene graph
````

That is the smallest releaseable step that turns `(N,3)` `MeshVisual` from protocol data into a useful visual feature while preserving GSP’s core commitments: semantic contracts, backend independence, capability discovery, explicit adaptation, and render/query/readback coherence.
