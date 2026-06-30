# P021 - View3D Legacy 3D Reuse, Datoviz Binding, Navigation, Materials, and Textures

## Use

Paste the full prompt below into ChatGPT Pro.

## Prompt

You are advising on architecture for `GSP_API`, a Python visualization protocol/library with
Matplotlib and Datoviz v0.4 backends plus a VisPy2-style producer API. We need a high-reasoning
architecture decision after completing a bounded static 3D baseline.

Please answer as a protocol/API architect. Keep the answer implementation-sized and explicit.

### Project authority and constraints

Authority order in this repo is:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

Existing code is implementation material, not automatically authoritative. If legacy code conflicts
with accepted specs, specs win.

The current public protocol is intentionally backend-neutral. It must not expose backend-native
Datoviz camera objects, draw-state names, material structs, controller objects, or Matplotlib artist
objects as public GSP API.

### Current state after S036

S036, “Static View3D, Orthographic Projection, and 3D Mesh Baseline”, is complete.

Accepted public S036 concepts:

- `Camera3D(eye, target, up)`.
- `OrthographicProjection3D(xlim, ylim, near_far)`.
- `View3D(id, panel_id, camera, projection, depth_mode=opaque_less, revision=...)`.
- Orthographic only.
- Static only.
- `MeshVisual.positions` accepts `(N,2)` and `(N,3)`.
- `(N,3)` + `CoordinateSpace.DATA` projects through `View3D`.
- `(N,3)` + `CoordinateSpace.NDC` is interpreted as panel NDC3 directly.
- Existing 2D affine transforms do not apply to `(N,3)` mesh geometry.
- `View3DProjectionSnapshot` provides deterministic projection snapshot IDs.
- `View3DQueryPayload` with payload kind `gsp.view3d-query@0.1` provides panel xy, panel NDC xy,
  near/far DATA points, ray direction, view id, view revision, layout snapshot id, and
  view/projection snapshot id.
- 3D mesh face picking is intentionally deferred and returns `query_3d_visual_hit_deferred`.

Accepted S036 capability strings:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
```

Accepted S036 diagnostics:

```text
view3d_not_supported
view3d_projection_unsupported
view3d_invalid_camera_degenerate
view3d_invalid_projection
mesh3d_requires_view3d
mesh3d_coordinate_space_unsupported
mesh3d_transform_unsupported
mesh3d_depth_unsupported
mesh3d_depth_adapted
mesh3d_alpha_not_strict
mesh3d_clipping_adapted
query_3d_visual_hit_deferred
query_3d_snapshot_mismatch
```

### Current backend behavior

Matplotlib:

- Implements strict validation, projection math, snapshot identity, and ray readback.
- Renders `(N,3)` meshes by projecting them to 2D and using `PolyCollection`.
- Has an adapted face-order fixture: opaque, non-intersecting triangles are sorted far-to-near by
  average panel-NDC z so nearer faces draw last.
- Does NOT claim strict fragment-depth semantics.
- Rejects translucent 3D mesh colors from that adapted opaque-depth path with
  `mesh3d_alpha_not_strict`.
- Keeps partially clipped 3D triangles adapted/unverified.

Datoviz v0.4:

- Current public `(N,3)` MeshVisual attempts fail with:

```text
datoviz: unsupported (DatovizV04Unsupported: mesh3d_coordinate_space_unsupported:
Datoviz v0.4 MeshVisual strict adapter is limited to 2D positions until public View3D camera
binding is implemented)
```

- This is intentional after S036: the adapter refuses to silently flatten z or expose backend-native
  camera/draw-state names.
- Existing Datoviz 2D mesh path uses retained `dvz_mesh`, `position`, `color`, direct index upload,
  and `dvz_visual_set_depth_test(False)` for bounded 2D cases.
- Lower internal payload formatting can already format 3D positions, but public `View3D` binding is
  missing.

### Legacy 3D code found in the repo

There is older/legacy GSP_API code that rendered 3D objects, lighting, depth, and textures. It is not
authoritative public API, but it may contain useful implementation techniques.

Relevant legacy files:

- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_depth.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_normal.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_phong.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_textured.py`
- `src/gsp_matplotlib/utils/renderer_utils.py`
- `src/gsp/materials/mesh_basic_material.py`
- `src/gsp/materials/mesh_depth_material.py`
- `src/gsp/materials/mesh_normal_material.py`
- `src/gsp/materials/mesh_phong_material.py`
- `src/gsp/materials/mesh_textured_material.py`
- `src/gsp/lights/*`
- `src/gsp/core/camera.py`

Key legacy techniques:

1. Legacy mesh renderer computes MVP:

```python
mvp_matrix = MathUtils.compute_mvp_matrix(model_matrix_numpy, view_matrix_numpy, projection_matrix_numpy)
_, vertices_ndc = MathUtils.apply_transform_matrix(vertices_numpy, mvp_matrix)
faces_vertices_ndc = vertices_ndc[geometry_indices_numpy].reshape(-1, 3, 3)
faces_vertices_2d = faces_vertices_ndc[..., :2]
```

2. It computes view-space and world-space vertices:

```python
view_model_matrix = view_matrix_numpy @ model_matrix_numpy
vertices_view_numpy, _ = MathUtils.apply_transform_matrix(vertices_numpy, view_model_matrix)
vertices_world_numpy, _ = MathUtils.apply_transform_matrix(vertices_numpy, model_matrix_numpy)
camera_position_world = (np.linalg.inv(view_matrix_numpy) @ np.array([0.0, 0.0, 0.0, 1.0]))[:3]
```

3. It sorts faces by NDC depth:

```python
faces_depth = RendererUtils.compute_face_depths_ndc(faces_vertices_ndc)
depth_sorted_indices = np.argsort(-faces_depth)
faces_vertices_2d = faces_vertices_2d[depth_sorted_indices]
face_colors_numpy = face_colors_numpy[depth_sorted_indices]
```

The current S036 Matplotlib adapted face ordering already mirrors this idea.

4. It computes screen-space face culling:

```python
faces_edges_2d_a = faces_vertices_2d[:, 1] - faces_vertices_2d[:, 0]
faces_edges_2d_b = faces_vertices_2d[:, 2] - faces_vertices_2d[:, 0]
faces_cross_z = faces_edges_2d_a[:, 0] * faces_edges_2d_b[:, 1] - faces_edges_2d_a[:, 1] * faces_edges_2d_b[:, 0]
```

5. It computes face normals:

```python
faces_vertices = vertices[geometry_indices]
edge_a = faces_vertices[:, 1] - faces_vertices[:, 0]
edge_b = faces_vertices[:, 2] - faces_vertices[:, 0]
face_normals = np.cross(edge_a, edge_b)
face_normals = face_normals / norm
```

6. Legacy Phong material computes flat per-face Lambert + Phong specular lighting:

```python
view_dirs = camera_position_world[np.newaxis, :] - face_centroids_world
cos_theta = np.maximum(0.0, np.sum(face_normals_world * light_dirs, axis=1))
diffuse_term = diffuse_per_face * scaled_light[np.newaxis, :] * cos_theta[:, np.newaxis]
halfway = light_dirs + view_dirs
spec_cos = np.maximum(0.0, np.sum(face_normals_world * halfway, axis=1))
specular_term = specular_per_face * scaled_light[np.newaxis, :] * np.power(spec_cos, shininess)[:, np.newaxis]
face_rgb += diffuse_term + specular_term
```

7. Legacy textured material renders one Matplotlib `AxesImage` per triangle, using UVs and affine
warp:

```python
faces_uvs = uvs_numpy[geometry_indices]
texture_hwc = texture_pixels.reshape(texture_height, texture_width, 4).astype(np.float32) / 255.0
texture_region = texture_hwc[y_min:y_max, x_min:x_max, :3] * face_color_rgb
matrix_wrap = RendererMeshTextured._texture_coords_wrap(face_uvs, face_vertices_2d)
transform = matrix_wrap + mpl_axes.transData
```

This may be useful internally but is much more public-contract-heavy because S036 has no public
texture, UV, material, or light semantics.

### User request

The user wants us to “do all of that”:

- reuse legacy 3D rendering techniques where appropriate;
- add or plan Matplotlib 3D lighting/textured examples if safe;
- fix or plan Datoviz 3D rendering so `(N,3)` examples do not just say unsupported;
- define whether and how public View3D navigation should be opened;
- provide a ChatGPT Pro consultation packet before implementation because it may take a while.

### Decision questions

Please answer these questions:

1. Which legacy Matplotlib 3D techniques should be reused immediately inside the S036/S037
   implementation without changing public API?
2. Which legacy techniques must remain deferred until new public protocol fields are accepted?
3. What is the minimal public material/light/texture model, if any, that should follow S036?
4. Should lighting/texturing be part of S037, or should S037 be only View3D navigation + Datoviz
   View3D binding?
5. What public View3D navigation model should GSP expose, if any? It must preserve canonical
   `View3D` state, revisions, and snapshot freshness.
6. What is the safest Datoviz v0.4 implementation plan for `(N,3)` `MeshVisual`?
   - What public GSP state should lower into Datoviz?
   - What backend evidence is required before claiming support?
   - What diagnostics should remain if the needed Datoviz binding is missing?
7. How should strict/ adapted capability claims be worded for:
   - Matplotlib projected mesh rendering;
   - Matplotlib face sorting/depth;
   - Datoviz retained 3D mesh rendering;
   - future lighting;
   - future textured meshes?
8. What exact next mission breakdown should we use after S036?

### Expected output format

Return a structured answer with exactly these sections:

1. `Executive Decision`
   - 5-10 bullets stating what to do now vs defer.
2. `Legacy Reuse Matrix`
   - Table with columns: `Legacy technique`, `Reuse now?`, `Public API impact`, `Reason`, `Tests needed`.
3. `Datoviz View3D Binding Plan`
   - Ordered implementation plan.
   - Required evidence.
   - Diagnostics if unsupported.
4. `Public View3D Navigation Contract`
   - Proposed public action/event/state model.
   - Snapshot/revision/freshness rules.
   - What remains private/backend-native.
5. `Materials Lights Textures`
   - Decide whether to defer or introduce a minimal model.
   - If introducing, give field names and capability names.
   - If deferring, give exact diagnostics and review examples allowed meanwhile.
6. `Capability Wording`
   - Exact capability strings and strict/adapted wording to use.
7. `Mission Plan`
   - Concrete missions M161+ with title, purpose, deliverables, stop condition.
8. `Risks And Non-Goals`
   - Concise list of pitfalls to avoid.

Do not assume attached files. Base your answer only on the facts embedded in this prompt.
