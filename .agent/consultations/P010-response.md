# Consultation Result: S025 Mesh/3D Protocol Semantics

## Executive recommendation

S025 should define **public `MeshVisual` v1 only**. Do **not** introduce public `GeometryResource`, `Material`, `SurfaceVisual`, or `VolumeVisual` in this stage. The first implementable slice should be a narrow triangular mesh visual with inline positions, triangle indices, RGBA colors, optional normals for capability-gated shaded rendering, conservative depth/culling controls, and mesh hit-query payloads where supported. This answers the uploaded P010 consultation request for S025 Mesh/3D protocol semantics.

The durable v1 contract should be:

* **Triangle-only indexed geometry**.
* **Inline NumPy arrays for in-process use**; NPZ sidecars remain fixture/debug/replay implementation detail.
* **No public reusable geometry resources yet**.
* **No public texture/UV protocol yet**.
* **No public general material or lighting system yet**.
* **No instancing yet**.
* **No surface-grid or volume concepts yet**.
* **2D mesh conformance first**, using NDC/DATA coordinates and Matplotlib `PolyCollection`.
* **3D mesh support as a capability-gated extension of `MeshVisual`**, not a separate visual family, using existing panel/view camera facilities only where accepted.
* **Flat RGBA color is required baseline**; per-face RGBA is required; per-vertex RGBA is optional/capability-gated; scalar colormap is deferred except a narrow optional grayscale convenience if the project already has accepted scalar color machinery.

This gives workers enough semantics for ADR/spec/test/backend work without freezing a full renderer, scene graph, material system, OBJ loader, or Datoviz-specific API surface.

## Protocol contract draft

| Field                 |                                              Type | Required |                                                                         Default | Semantics                                                                                                                                                                                                                       | Validation                                                                                                                                                                         |
| --------------------- | ------------------------------------------------: | -------: | ------------------------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                  |                         stable protocol visual id |      yes |                                                                            none | Unique visual identity used by scene graph, diagnostics, queries, and readback.                                                                                                                                                 | Non-empty stable id; uniqueness checked at scene/session level.                                                                                                                    |
| `family`              |          literal `"mesh"` or protocol family enum |      yes |                                                                        `"mesh"` | Declares this visual as `MeshVisual`.                                                                                                                                                                                           | Must equal accepted mesh family value.                                                                                                                                             |
| `positions`           | float32/float64 array, shape `(N, 2)` or `(N, 3)` |      yes |                                                                            none | Vertex positions. `(N, 2)` means planar panel coordinates in `coordinate_space`. `(N, 3)` means 3D coordinates in `coordinate_space`; projection/camera behavior is backend/view capability-dependent.                          | `N >= 3`; rank 2; second dimension 2 or 3; finite values only; dtype float32/float64 or safely castable with diagnostic policy.                                                    |
| `faces`               |                     integer array, shape `(M, 3)` |      yes |                                                                            none | Indexed triangles. Each row contains three vertex indices into `positions`. Public v1 supports triangles only.                                                                                                                  | `M >= 1`; rank 2; second dimension exactly 3; integer dtype; all indices `0 <= i < N`; no negative indices; no NaN because integer; reject object dtype.                           |
| `coordinate_space`    |                              enum `NDC` or `DATA` |      yes |           none, or inherited only if project already permits visual inheritance | Same cross-cutting meaning as existing accepted visuals. `NDC` positions are panel-normalized coordinates. `DATA` positions are in panel data coordinates and transformed by the view.                                          | Must be accepted `CoordinateSpace`.                                                                                                                                                |
| `color_mode`          |                                              enum |       no | `"uniform"` if `color` is scalar RGBA; otherwise inferred only when unambiguous | Selects how colors are associated with geometry. v1 required modes: `uniform`, `face`. Optional mode: `vertex`.                                                                                                                 | Must match supplied color field shapes. Ambiguous combinations are rejected.                                                                                                       |
| `color`               |                         RGBA scalar or RGBA array |      yes |                                                                            none | Display color. For `uniform`: shape `(4,)`. For `face`: shape `(M, 4)`. For `vertex`: shape `(N, 4)`. RGBA may be float `[0,1]` or uint8 `[0,255]`.                                                                             | Shape must match `color_mode`; finite if float; float values in `[0,1]`; uint8 values in `[0,255]`; alpha allowed.                                                                 |
| `values`              |             numeric array, shape `(M,)` or `(N,)` |       no |                                                                            none | Deferred for public v1 unless the project decides to include a narrow scalar-debug path. Not required for S025 conformance.                                                                                                     | If included experimentally, must be finite and must not imply broad colormap/colorbar semantics.                                                                                   |
| `colormap`            |                                       enum/string |       no |                                                                            none | Defer from public v1. Broad colormap registries and colorbars remain out of scope.                                                                                                                                              | Reject in public v1 unless accepted by a later scalar-color spec.                                                                                                                  |
| `clim`                |                             pair of finite floats |       no |                                                                            none | Defer from public v1 with `colormap`.                                                                                                                                                                                           | Same as above.                                                                                                                                                                     |
| `normals`             | float32/float64 array, shape `(N, 3)` or `(M, 3)` |       no |                                                                            none | Optional normals for capability-gated shaded rendering. `normal_mode` declares association. Normals do not change geometry. Missing normals imply flat unlit rendering, not hidden backend-specific lighting.                   | Rank 2; second dimension 3; finite; nonzero length after normalization tolerance; shape must match `normal_mode`; invalid normals rejected or shading deactivated with diagnostic. |
| `normal_mode`         |                     enum `none`, `vertex`, `face` |       no |                `"none"` if no normals, otherwise inferred only when unambiguous | Declares normal association. `vertex` means one normal per vertex. `face` means one normal per triangle.                                                                                                                        | Must match `normals` shape. `none` requires no `normals`.                                                                                                                          |
| `normal_generation`   |                          enum `none`, `face_flat` |       no |                                                                        `"none"` | Optional deterministic CPU-side generation policy. For v1, only `face_flat` may be allowed, producing geometric face normals for capability-gated shading or query readout. It must be explicit, never hidden.                  | Requires 3D positions. Degenerate triangles receive diagnostic and either no generated normal or fatal rejection according to validation profile.                                  |
| `shading`             |                   enum `flat`, optional `lambert` |       no |                                                                        `"flat"` | `flat` is required baseline and means no public light/material semantics. `lambert` may be capability-gated later using supplied/generated normals and a view-defined light policy, but should not be required for conformance. | Unsupported shading must produce structured diagnostic and either simplify to `flat` or reject according to adaptation policy.                                                     |
| `face_culling`        |                      enum `none`, `back`, `front` |       no |                                                                        `"none"` | Culling policy for oriented triangles. Meaningful mainly in 3D and depth-enabled rendering. Front/back are defined after projection/view orientation, not backend winding names.                                                | Backend unsupported culling requires diagnostic. Winding is not validated for consistency.                                                                                         |
| `depth_test`          |                enum `auto`, `disabled`, `enabled` |       no |                                                                        `"auto"` | Whether the mesh participates in depth testing. `auto` means 3D meshes use depth when backend/view supports it; 2D panel meshes may render by visual order unless depth is explicitly enabled and meaningful.                   | Unsupported explicit `enabled` requires fatal or deactivation diagnostic.                                                                                                          |
| `depth_write`         |                enum `auto`, `disabled`, `enabled` |       no |                                                                        `"auto"` | Whether rendered mesh updates depth buffer. `auto` follows `depth_test` and backend defaults.                                                                                                                                   | Unsupported explicit value requires diagnostic.                                                                                                                                    |
| `order`               |                           finite float or integer |       no |                                                                             `0` | 2D painter/order hint among visuals when depth is disabled or unavailable. Lower-to-higher ordering should follow existing visual ordering conventions.                                                                         | Finite scalar.                                                                                                                                                                     |
| `opacity_policy`      |                             enum `ordinary_alpha` |       no |                                                              `"ordinary_alpha"` | v1 only defines standard source-over alpha behavior where backend supports it. No order-independent transparency guarantee.                                                                                                     | Alpha values in `color` drive transparency. Backend limitations require diagnostic.                                                                                                |
| `wireframe`           |                                              bool |       no |                                                                         `false` | Defer as public semantic if possible. If included in S025, treat as optional/capability-gated overlay drawing of triangle edges. Recommended: keep out of strict v1 and implement QA as optional.                               | Unsupported wireframe requires diagnostic.                                                                                                                                         |
| `edge_color`          |                                       RGBA scalar |       no |                                                                            none | Defer from strict v1.                                                                                                                                                                                                           | Only valid if later `wireframe=true` is accepted.                                                                                                                                  |
| `edge_width`          |                               float screen pixels |       no |                                                                            none | Defer from strict v1.                                                                                                                                                                                                           | Positive finite screen-pixel width if later accepted.                                                                                                                              |
| `transform`           |                    affine transform object/matrix |       no |                                                                        identity | Defer from public v1 unless an accepted cross-cutting transform spec already exists. S025 must not invent a mesh-only transform system.                                                                                         | If accepted later: finite matrix, dimensionality consistent with positions.                                                                                                        |
| `instance_transforms` |                                 array of matrices |       no |                                                                            none | Defer. Datoviz may support it internally, but public v1 should not.                                                                                                                                                             | Reject in public S025.                                                                                                                                                             |
| `uv` / `texcoords`    |                              float array `(N, 2)` |       no |                                                                            none | Defer. Texture coordinate semantics require resource and color-space decisions beyond S025.                                                                                                                                     | Reject in public S025.                                                                                                                                                             |
| `texture`             |                         texture/image resource id |       no |                                                                            none | Defer. Mesh texture ownership and sampling are not part of v1.                                                                                                                                                                  | Reject in public S025.                                                                                                                                                             |
| `metadata`            |                              small JSON-like dict |       no |                                                                           empty | Non-rendering annotations only, if already permitted by cross-cutting protocol. Must not affect rendering semantics.                                                                                                            | Must be serializable where fixture path requires it.                                                                                                                               |

Recommended strict S025 subset:

```text
MeshVisual(
    id,
    positions,
    faces,
    coordinate_space,
    color,
    color_mode = uniform | face,
    order = 0,
    depth_test = auto,
    depth_write = auto,
    face_culling = none,
    shading = flat,
)
```

Recommended optional/capability-gated S025 fields:

```text
color_mode = vertex
normals
normal_mode
normal_generation = face_flat
shading = lambert
mesh query/readback
3D camera-backed rendering
alpha blending
face_culling != none
```

Recommended deferred fields:

```text
GeometryResource
Material
SurfaceVisual
VolumeVisual
values/colormap/colorbar
UVs/textures
wireframe/edge styling as required conformance
transforms/instancing
external model loading
LOD/chunking
```

## Enums and units

| Enum                   | Values                               |                               Required in v1? | Semantics                                                                                                                                                  |
| ---------------------- | ------------------------------------ | --------------------------------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CoordinateSpace`      | `NDC`, `DATA`                        |                                           yes | Same accepted cross-cutting values as Point/Marker/Segment/Path/Image/Text.                                                                                |
| `MeshColorMode`        | `uniform`, `face`, optional `vertex` | `uniform`, `face` required; `vertex` optional | `uniform`: one RGBA for the visual. `face`: one RGBA per triangle. `vertex`: one RGBA per vertex, interpolated across triangles where backend supports it. |
| `MeshNormalMode`       | `none`, `face`, `vertex`             |                                      optional | Declares normal association. Normals are only meaningful for capability-gated shaded rendering and query payloads.                                         |
| `MeshNormalGeneration` | `none`, `face_flat`                  |                                      optional | Explicit deterministic generation only. No hidden backend normal generation should affect conformance.                                                     |
| `MeshShading`          | `flat`, optional `lambert`           |                               `flat` required | `flat` means colors are used directly without public light/material semantics. `lambert` may be capability-gated but should not be required for S025.      |
| `FaceCulling`          | `none`, `back`, `front`              |                                           yes | Conservative culling. `none` required. `back`/`front` capability-gated.                                                                                    |
| `DepthTest`            | `auto`, `disabled`, `enabled`        |                                           yes | `auto` follows dimensionality/view/backend support; explicit values require diagnostics if unsupported.                                                    |
| `DepthWrite`           | `auto`, `disabled`, `enabled`        |                                           yes | Controls whether mesh contributes to depth buffer when depth is active.                                                                                    |
| `OpacityPolicy`        | `ordinary_alpha`                     |                                           yes | Alpha is ordinary source-over where supported. No OIT, sorting guarantee, or physically based transparency.                                                |

Units:

* `positions`: NDC coordinates or DATA coordinates, depending on `coordinate_space`.
* `faces`: integer indices into `positions`.
* `color`: RGBA float `[0,1]` or uint8 `[0,255]`.
* `order`: dimensionless visual ordering scalar.
* `edge_width`, if later accepted: logical screen pixels, matching existing stroke-width semantics.
* `normals`: unitless direction vectors; implementations may normalize after validation.
* `depth`: query/readback depth should be reported in normalized panel depth where available, plus backend-specific raw depth only as diagnostic/private data.

No Datoviz slot names, material struct names, Vulkan/OpenGL state names, mplot3d names, or shader-stage concepts should appear in public protocol fields.

## Geometry and resource policy

`MeshVisual` v1 should own its geometry inline:

* `positions` is the authoritative vertex array.
* `faces` is the authoritative triangle-index array.
* There is no public `GeometryResource` in S025.
* There is no external model-file concept in S025.
* There is no OBJ/PLY/STL loading protocol in S025.
* There is no topology-editing protocol in S025.
* There is no remote mesh-chunk protocol in S025.
* There is no LOD protocol in S025.

Rationale:

* A reusable geometry-resource layer is likely needed later for huge datasets, shared meshes, instancing, streaming, caching, and remote renderers.
* Introducing it now would force premature decisions about lifetime, mutability, buffer identity, server ownership, invalidation, slicing, transport, and query mapping.
* Inline arrays match the existing accepted visual-family pattern and preserve the fast in-process path.

Geometry constraints:

* Public v1 is **triangles only**.
* Quads, polygons, triangle strips, fans, indexed lines, mixed primitives, holes, and tessellation are deferred.
* `faces` must be indexed; unindexed triangles can be represented by sequential positions plus generated faces by producer APIs, but the protocol object should still contain explicit `faces`.
* Duplicate vertices are allowed.
* Unreferenced vertices are allowed but should generate non-fatal validation diagnostics because they increase memory and can confuse query expectations.
* Degenerate triangles should be detected. Recommended policy:

  * In strict validation mode: reject zero-area triangles.
  * In permissive/adaptation mode: accept with warning, render backend-dependent or skip, and exclude from required query guarantees.
* Winding is not globally validated because valid scientific meshes can contain inconsistent orientation. However:

  * culling requires winding to matter;
  * if `face_culling != none`, inconsistent winding should produce a warning if cheaply detectable;
  * conformance fixtures should use consistent counter-clockwise winding in projected view.

Normals:

* Normals should be optional.
* `normal_mode = face` or `vertex` must be explicit or unambiguously inferred from shape.
* Missing normals must not imply hidden Phong/Lambert shading.
* Generated normals, if supported, must be explicit through `normal_generation = face_flat`.
* Normal generation should require 3D positions; for `(N, 2)` positions, generation is either rejected or defined as constant `+Z` only if the spec explicitly accepts that. Recommendation: reject normal generation for 2D in v1 to avoid accidental 2D/3D mixing.

Textures and UVs:

* Defer public `uv`, `texture`, sampler, color-space, atlas, and texture-resource semantics.
* Datoviz texture support may be recorded as backend evidence, not public v1 behavior.

Instancing:

* Defer public instancing despite Datoviz support.
* Query payload should reserve an optional `instance_id` field but return `null`/absent for S025.

## Material, lighting, and color policy

The v1 material policy should be deliberately minimal:

### Required baseline

`shading = flat`

This means:

* The mesh is rasterized as colored triangles.
* `color` is the semantic displayed color source.
* No public light source exists.
* No public material object exists.
* No ambient/diffuse/specular/shininess fields exist.
* No depth-derived or normal-derived debug material is public v1.
* Matplotlib and Datoviz should both be able to produce deterministic reference images for the strict subset.

### Required color modes

`color_mode = uniform`

* One RGBA color for all triangles.
* Required for all backends.

`color_mode = face`

* One RGBA color per triangle.
* Required for v1 because it gives deterministic scientific labeling and Matplotlib reference behavior.
* Query can return `face_index` and displayed face color without interpolation ambiguity.

### Optional color mode

`color_mode = vertex`

* One RGBA color per vertex.
* Interpolated across each triangle where backend supports it.
* Capability-gated because Matplotlib reference support is limited and different renderers may vary in interpolation and antialiasing.
* If unsupported:

  * allowed adaptation: convert to per-face color by averaging vertex colors, with warning, only when the caller permits simplification;
  * otherwise reject with fatal diagnostic.

### Deferred color modes

Defer from public S025 v1:

* scalar `values` plus arbitrary colormap;
* broad colormap registries;
* colorbars;
* nonlinear normalization;
* categorical palettes;
* transfer functions;
* texture sampling;
* material-driven color;
* normal/depth debug colors as public materials.

A narrow grayscale scalar mode is tempting, but it would entangle MeshVisual with colorbar/normalization decisions that the project has explicitly deferred. Better to keep scalar mesh coloring out of strict v1 unless an accepted cross-cutting scalar-color spec already exists.

### Alpha/transparency

Alpha should be accepted in RGBA because all accepted visual families already use RGBA. But S025 should only guarantee:

* alpha values are part of the color payload;
* fully opaque alpha behaves deterministically;
* partially transparent alpha uses ordinary backend alpha blending where supported;
* no correct order-independent transparency guarantee;
* no guarantee for intersecting transparent triangles;
* no automatic face sorting.

For conformance, strict visual QA should use opaque meshes. Alpha-overlap tests should be optional/capability-gated with manual review.

### Lighting

Do not include public lights in S025.

Optional `shading = lambert` may be recorded as an experimental/capability-gated path only if the team wants an early Datoviz 3D demonstration. It should not be part of strict v1 conformance unless the project first accepts a narrow light convention such as:

```text
single view-space directional light
fixed direction
fixed ambient factor
no specular
no shadows
```

Recommendation: keep `lambert` out of strict S025; include it only as a backend capability note or optional QA case.

## Transform, camera, and depth policy

S025 must avoid creating a parallel 3D scene graph. Mesh positions should be interpreted through existing panel/view concepts only.

### 2D mesh behavior

For `positions.shape == (N, 2)`:

* The mesh is a panel-space/data-space filled-triangle visual.
* `coordinate_space = NDC` means vertices are in the same NDC coordinate system used by existing visual QA fixtures.
* `coordinate_space = DATA` means vertices are transformed by the panel’s accepted data transform.
* No camera is involved.
* Depth defaults to visual `order` unless explicitly enabled by a backend/view that supports meaningful depth.
* This is the **strict Matplotlib reference/conformance path**.

### 3D mesh behavior

For `positions.shape == (N, 3)`:

* The mesh is a 3D data-space or NDC-space geometry visual.
* Rendering requires an accepted panel/view 3D projection policy.
* If no accepted 3D camera/view exists yet, S025 should define only a **QA-local provisional camera fixture**, not a general public camera protocol.

Recommended safe 3D policy:

* Public `MeshVisual` may contain `(N, 3)` positions.
* The visual spec says 3D positions require a panel/view with 3D projection capability.
* The mesh spec does **not** define camera fields inside `MeshVisual`.
* Backend conformance for 3D is capability-gated until a cross-cutting camera/view spec is accepted.
* QA may use a fixed internal reference camera for contact sheets, but this must be marked as QA fixture behavior, not protocol authority.

### Transform policy

Do not add mesh-local model transforms in strict v1.

Reasons:

* Transform semantics are cross-cutting, not mesh-specific.
* Adding transforms only to MeshVisual creates divergence from Point/Text/Path/Image.
* Datoviz instance transforms should remain backend implementation detail until a general transform/resource/instancing ADR exists.

If a transform spec already exists by implementation time, MeshVisual may opt into that cross-cutting transform. Otherwise S025 should use pre-transformed positions.

### Depth policy

Depth should be controlled conservatively:

* `depth_test = auto` default.
* For 2D meshes, `auto` should usually behave like ordered 2D rendering.
* For 3D meshes, `auto` should enable depth testing when the panel/view/backend supports it.
* `depth_test = enabled` requires backend support; otherwise fatal diagnostic or visual deactivation with diagnostic, depending on session adaptation policy.
* `depth_write = auto` follows depth testing.
* `order` remains relevant for 2D rendering, transparent rendering, and unsupported depth.

### Culling policy

* `face_culling = none` is required baseline.
* `back` and `front` are optional/capability-gated.
* Culling depends on orientation after projection/view transformation.
* The protocol should not expose backend culling constants.
* If culling is requested but unsupported, report structured diagnostic.

## Query/readback contract

Mesh query should fit the unified panel-query model.

### Required when mesh query is supported

A mesh hit result should include:

| Field              |        Required? | Semantics                                                                                                      |
| ------------------ | ---------------: | -------------------------------------------------------------------------------------------------------------- |
| `visual_id`        |              yes | Stable id of the `MeshVisual`.                                                                                 |
| `family`           |              yes | `"mesh"`.                                                                                                      |
| `hit_kind`         |              yes | `"face"` for S025. Vertex/edge hits are deferred.                                                              |
| `face_index`       |              yes | Row index into `faces`.                                                                                        |
| `vertex_indices`   |              yes | The three indices from `faces[face_index]`.                                                                    |
| `panel_xy`         |              yes | Queried panel coordinate in the unified query coordinate convention.                                           |
| `depth`            | yes if available | Normalized depth/order value used to rank hits. If unavailable, omit with diagnostic or set explicit `null`.   |
| `displayed_rgba`   |              yes | RGBA displayed at hit point after color association and alpha policy, before display color-management details. |
| `coordinate_space` |              yes | `NDC` or `DATA`, matching the visual.                                                                          |

### Strongly recommended when feasible

| Field               | Status                                      | Semantics                                                                                                               |
| ------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `barycentric`       | capability-gated but recommended            | Three finite barycentric coordinates relative to the hit triangle. Should sum to approximately 1.                       |
| `position`          | recommended                                 | Interpolated position in visual coordinates, shape `(2,)` or `(3,)`.                                                    |
| `data_position`     | recommended for `DATA`                      | Position in data coordinates if distinguishable from visual coordinates.                                                |
| `ndc_position`      | recommended for `NDC` or projected readback | NDC hit position if available.                                                                                          |
| `color_source`      | recommended                                 | `uniform`, `face`, or `vertex`.                                                                                         |
| `interpolated_rgba` | recommended                                 | For vertex-color mode, interpolated RGBA at barycentric hit. For face/uniform, same as displayed color before blending. |
| `front_facing`      | optional                                    | Whether the selected triangle was front-facing after projection.                                                        |
| `normal`            | optional                                    | Interpolated or face normal if normals are available/generated.                                                         |
| `diagnostics`       | recommended                                 | Query-specific notes, especially for approximated picking.                                                              |

### Optional/reserved

| Field          | Status            | Semantics                                                                                      |
| -------------- | ----------------- | ---------------------------------------------------------------------------------------------- |
| `instance_id`  | reserved/deferred | Always absent or `null` in S025 because instancing is deferred.                                |
| `value`        | deferred          | Scalar value readback if scalar mesh coloring is later accepted.                               |
| `uv`           | deferred          | Texture coordinate readback.                                                                   |
| `texel`        | deferred          | Texture texel identity/readback.                                                               |
| `material_id`  | deferred          | Public materials are deferred.                                                                 |
| `edge_index`   | deferred          | Edge picking is not part of S025.                                                              |
| `vertex_index` | deferred          | Vertex picking is not part of S025 MeshVisual; existing PointVisual covers point-like picking. |

Query semantics:

* Query returns the top visible mesh contribution under a panel coordinate, consistent with the unified panel-query model.
* If backend picking is unavailable, CPU reference picking may be used for 2D strict fixtures.
* For 3D, query requires accepted projection/depth information; otherwise report `query_unsupported`.
* Degenerate triangles are not required to be queryable.
* Transparent triangle hit ordering is not guaranteed beyond backend capability reports.
* For per-face color, `displayed_rgba = color[face_index]`, subject to alpha/composition caveats.
* For uniform color, `displayed_rgba = color`.
* For per-vertex color, `displayed_rgba` should use barycentric interpolation if supported; otherwise report simplification.

## Backend guidance

### Matplotlib reference backend

Matplotlib should be the strict reference backend for the **2D filled-triangle subset**.

Recommended implementation mapping:

* For `(N, 2)` positions:

  * use `PolyCollection` or equivalent filled polygon collection;
  * construct one triangle polygon per `faces` row;
  * support uniform RGBA and per-face RGBA strictly;
  * support `coordinate_space = NDC` for QA fixtures over `[-1, +1]`;
  * support `coordinate_space = DATA` through normal axes/data transforms where existing backend conventions allow;
  * use visual `order` / z-order for layering;
  * keep antialiasing behavior deterministic where possible.

Strict Matplotlib conformance should include:

* uniform-color triangle;
* indexed square made of two triangles;
* per-face-colored square;
* DATA vs NDC placement;
* simple 2D query/readback using CPU triangle hit testing.

Matplotlib should **not** be required to provide strict 3D conformance in S025.

For `(N, 3)` positions:

* `mplot3d` may be used for optional visual QA/contact sheets only.
* It should not be treated as pixel-accurate protocol authority.
* Acceptable diagnostics:

  * `mesh_3d_reference_limited`;
  * `mesh_depth_order_approximate`;
  * `mesh_culling_unsupported`;
  * `mesh_vertex_color_interpolation_unsupported`;
  * `mesh_query_3d_unsupported`.

Per-vertex color in Matplotlib:

* Not required for strict conformance.
* If approximated by per-face averaged color, this must emit a simplification diagnostic.
* The adaptation must be opt-in.

Alpha in Matplotlib:

* Opaque alpha is strict.
* Partial alpha is optional/manual review.
* No strict guarantee for interpenetrating transparent triangles.

### Datoviz v0.4 backend

Datoviz should be the flagship GPU backend for mesh, but GSP must use semantic capability gates.

Required Datoviz capability checks:

| Capability                          |                Required for strict S025? | Diagnostic if missing                        |
| ----------------------------------- | ---------------------------------------: | -------------------------------------------- |
| retained mesh visual creation       |             yes for Datoviz mesh support | `datoviz_mesh_visual_unavailable`            |
| indexed triangle geometry upload    |                                      yes | `datoviz_mesh_indexed_geometry_unavailable`  |
| vertex positions `(N,3)`            |                               yes for 3D | `datoviz_mesh_position3_unavailable`         |
| 2D positions or 2D-to-3D adaptation |                        yes for 2D subset | `datoviz_mesh_position2_requires_adaptation` |
| uniform color                       |                                      yes | `datoviz_mesh_uniform_color_unavailable`     |
| per-face color                      | required for strict parity if advertised | `datoviz_mesh_face_color_unavailable`        |
| per-vertex color                    |                                 optional | `datoviz_mesh_vertex_color_unavailable`      |
| depth test/write controls           |                   optional but important | `datoviz_mesh_depth_control_unavailable`     |
| face culling                        |                                 optional | `datoviz_mesh_culling_unavailable`           |
| normals upload                      |                                 optional | `datoviz_mesh_normals_unavailable`           |
| shaded material path                |                                 optional | `datoviz_mesh_shading_unavailable`           |
| texture path                        |                                 deferred | `datoviz_mesh_texture_deferred`              |
| query/picking                       |                optional/capability-gated | `datoviz_mesh_query_unavailable`             |
| instance transforms                 |                                 deferred | `datoviz_mesh_instancing_deferred`           |

Datoviz adaptation rules:

* Do not expose Datoviz slot names as public protocol fields.
* Do not expose Datoviz material structs as public protocol fields.
* Do not silently convert color association if it changes visual semantics.
* For 2D MeshVisual, adaptation to 3D positions with `z=0` is acceptable if explicitly documented and diagnostic-free only when semantically exact.
* For per-face color on a backend that only supports per-vertex color:

  * exact adaptation is possible by duplicating vertices per face;
  * this is allowed if query mapping preserves original `face_index` and `vertex_indices` or reports adapted topology clearly;
  * memory increase should be reported for large meshes if capability diagnostics support performance warnings.
* For per-vertex color on a backend that only supports per-face color:

  * averaging is not exact;
  * require opt-in simplification diagnostic or reject.
* For flat shading:

  * disable or bypass public lighting/material effects;
  * backend default lighting must not alter strict conformance colors unless explicitly accepted.
* For normals:

  * upload only when requested and supported;
  * do not let missing normals trigger hidden backend normal generation that affects output.
* For alpha:

  * report lack of blending, sorting, or known transparency limitations.

Required structured diagnostic fields should include at least:

```text
code
severity = info | warning | error | fatal
visual_id
field
requested_semantics
backend
backend_capability
action = accepted | simplified | deactivated | rejected
message
```

Recommended Datoviz stop conditions:

* Stop if only v0.3-style APIs are available.
* Stop if retained mesh API evidence contradicts planned implementation.
* Stop if indexed geometry cannot preserve face identity for queries.
* Stop if flat color cannot be rendered without hidden material/lighting changes.
* Stop if adaptation would change public color/depth/culling semantics without diagnostic.

## Visual QA plan

S025 visual QA should produce deterministic fixtures, Matplotlib reference images, Datoviz images where supported, contact sheets, structured capability reports, and manual review notes.

### Strict QA cases

| Case                                  | Purpose                           | Required backend behavior                                                                      |
| ------------------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------- |
| `mesh_single_triangle_uniform_ndc_2d` | Minimal geometry/color smoke test | One opaque triangle in NDC with uniform RGBA.                                                  |
| `mesh_indexed_square_uniform_ndc_2d`  | Indexed faces and shared vertices | Two triangles forming a square; no cracks; stable winding.                                     |
| `mesh_indexed_square_per_face_ndc_2d` | Per-face color semantics          | Two triangles with distinct face colors; visible diagonal.                                     |
| `mesh_data_coordinates_2d`            | DATA coordinate behavior          | Triangle/square placed using panel data limits.                                                |
| `mesh_order_overlap_2d`               | Visual ordering without depth     | Two overlapping 2D meshes with different `order`.                                              |
| `mesh_validation_invalid_index`       | Deterministic validation          | Out-of-bounds index rejected.                                                                  |
| `mesh_validation_bad_color_shape`     | Deterministic validation          | Wrong color shape rejected.                                                                    |
| `mesh_query_face_2d`                  | Readback semantics                | Query inside triangle returns visual id, face index, vertex indices, displayed RGBA, position. |

### Optional/capability-gated QA cases

| Case                         | Purpose                                | Gate                                     |
| ---------------------------- | -------------------------------------- | ---------------------------------------- |
| `mesh_vertex_color_triangle` | Per-vertex color interpolation         | `mesh.vertex_color`                      |
| `mesh_cube_3d_depth`         | 3D depth/projection sanity             | accepted 3D panel/camera + backend depth |
| `mesh_cube_3d_culling`       | Face culling orientation               | culling support                          |
| `mesh_alpha_overlap`         | Ordinary alpha behavior                | blending support; manual review          |
| `mesh_normals_flat_shading`  | Optional normal/shading path           | normals + shading capability             |
| `mesh_lambert_optional`      | Optional shaded material demonstration | explicit `lambert` support if accepted   |
| `mesh_query_3d_face`         | GPU or CPU 3D picking                  | 3D query support                         |
| `mesh_wireframe_optional`    | Edge overlay if later accepted         | wireframe capability                     |

### Manual review criteria

For strict cases:

* Geometry appears in expected NDC/DATA location.
* Triangle boundaries match reference within established image tolerance.
* Per-face colors are not interpolated across face boundary.
* Opaque RGBA colors match accepted tolerance.
* Visual ordering is deterministic.
* Query returns the expected face id and color for known sample points.

For optional cases:

* Capability report must clearly say whether the case was run, simplified, skipped, or rejected.
* Datoviz output should not be silently compared against Matplotlib where semantics differ.
* 3D cases should be reviewed for gross correctness: orientation, depth visibility, culling, and stable camera fixture.

### Required artifacts

* Protocol fixture files for strict cases.
* Sidecar NPZ arrays only for debug/replay fixtures, not mandatory runtime path.
* Matplotlib reference PNGs.
* Datoviz PNGs where capability gates pass.
* Contact sheet comparing available backends.
* JSON or YAML capability/diagnostic report.
* Query/readback expected-result files for deterministic 2D hit points.
* Manual review markdown notes documenting limitations.

## Explicit deferrals

The following must not be included in S025 public v1:

* `GeometryResource` as public protocol object.
* `Material` as public protocol object.
* `SurfaceVisual`.
* `VolumeVisual`.
* Quads, polygons, holes, triangle strips, fans, mixed primitive meshes.
* Surface grids as a special protocol family.
* Splats, impostors, glyph meshes, tessellation, subdivision.
* Skeletal animation, morph targets, topology editing.
* Instancing and per-instance transforms.
* Mesh-local model transforms unless a cross-cutting transform spec already exists.
* PBR materials.
* Public Phong/Blinn/specular/shininess material fields.
* Public lights.
* Shadows.
* Clipping planes.
* Advanced transparency, order-independent transparency, automatic face sorting.
* Texture resources, UVs, samplers, texture atlases, normal maps.
* OBJ/PLY/STL loading as protocol semantics.
* External model files as conformance inputs.
* Remote mesh chunks.
* LOD.
* GPU-side generated geometry.
* Compute-generated meshes.
* Public Datoviz slot names.
* Public Datoviz material structs.
* Public backend draw calls or retained API names.
* Broad colormap registries.
* Colorbars.
* Advanced normalization.
* Normal/depth debug materials as public protocol modes.
* Edge, vertex, UV, texel, voxel picking.
* Guaranteed 3D Matplotlib reference conformance.

## Recommended mission sequence

1. **M083 ADR/spec conversion**

   * Save the consultation as `.agent/consultations/P010-response.md`.
   * Create ADR for S025 MeshVisual scope.
   * Create `spec/visuals/mesh.md`.
   * Update visual-family index, cross-cutting rules, backend capabilities, QA harness, VisPy2 API notes, and Datoviz backend boundary notes.
   * **Stop condition:** any conflict with `PROJECT_CHARTER`, `ARCHITECTURE`, accepted specs, or accepted ADRs.

2. **MeshVisual validation model**

   * Add frozen dataclass/protocol object.
   * Implement deterministic validation for `positions`, `faces`, `coordinate_space`, `color`, `color_mode`, depth/order/culling fields.
   * Include invalid-fixture tests for shape, dtype, finite checks, out-of-bounds indices, empty arrays, invalid RGBA, and ambiguous color modes.
   * **Stop condition:** need for transforms, materials, resources, scalar colormaps, or texture semantics.

3. **Matplotlib strict 2D reference backend**

   * Implement only strict 2D subset first.
   * Use filled triangle collections.
   * Support uniform and per-face RGBA.
   * Implement visual ordering.
   * Implement CPU 2D face query.
   * **Stop condition:** 3D camera/projection uncertainty blocks reference semantics; proceed with 2D only rather than inventing camera protocol.

4. **Visual QA strict fixtures**

   * Build strict NDC/DATA 2D fixtures.
   * Generate Matplotlib references.
   * Add query expected outputs.
   * Produce contact sheets and manual review notes.
   * **Stop condition:** image tolerances are unstable or backend-specific antialiasing dominates comparisons.

5. **Datoviz v0.4 capability probe**

   * Gather retained mesh API evidence against current v0.4-dev.
   * Implement capability report before renderer behavior.
   * Check indexed triangle geometry, color association, depth, culling, query, normals, and texture deferrals.
   * **Stop condition:** API evidence is v0.3-only, ambiguous, or incompatible with accepted protocol.

6. **Datoviz strict mesh renderer**

   * Implement strict subset with exact adaptation only.
   * Preserve face identity for query where possible.
   * Support 2D adaptation to 3D `z=0` only if semantically exact.
   * Emit structured diagnostics for unsupported optional fields.
   * **Stop condition:** backend requires hidden lighting/material defaults that alter flat RGBA semantics.

7. **VisPy2 producer API**

   * Add simple high-level mesh creation API that emits accepted `MeshVisual`.
   * Producer may accept convenience unindexed triangles, but must serialize/produce explicit `faces`.
   * Keep textures, materials, OBJ loading, and surface grids out of public v1 producer API or mark as private examples.
   * **Stop condition:** producer API starts exposing deferred protocol concepts.

8. **Optional/capability-gated extensions**

   * Add per-vertex color if both validation and backend diagnostics are settled.
   * Add normals and optional flat-normal generation only if needed for Datoviz shaded QA.
   * Add 3D contact-sheet fixtures using a clearly non-authoritative QA camera or an accepted camera spec.
   * **Stop condition:** any optional path requires public material, lighting, transform, or texture semantics.

9. **Query/readback hardening**

   * Finalize 2D CPU reference query.
   * Add Datoviz query only if face identity, barycentric coordinates or equivalent hit position, depth, and displayed color can be reported faithfully.
   * **Stop condition:** backend query only returns backend object ids without reliable face mapping.

10. **Acceptance review**

* Confirm specs, ADRs, validation tests, Matplotlib references, Datoviz reports, QA artifacts, and VisPy2 API all align.
* Explicitly list all deferred features in the acceptance record.
* **Stop condition:** any implementation behavior exists without corresponding accepted spec semantics.
