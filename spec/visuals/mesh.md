# Mesh Visual - Accepted S025 Baseline

Status: accepted protocol baseline for S025. Static orthographic `View3D` semantics for `(N,3)`
mesh rendering are accepted separately by S036 in `spec/view3d.md`. S038 defines implicit
`unlit_rgba` material semantics in `spec/visuals/mesh_materials_s038.md`; S039 accepts only the
narrow flat Lambert face-normal extension in `spec/visuals/mesh_flat_lambert_s039.md`; S050 accepts
the unlit Texture2D/UV extension in `spec/visuals/mesh_texture2d_unlit_s050.md` and the
projected-NDC face-culling/alpha boundary in `spec/visuals/mesh_face_culling_alpha_s050.md`.

Semantic purpose: render explicit user-provided triangular meshes for filled 2D panel geometry and
capability-gated 3D geometry. S025 does not define a surface, volume, material, texture, instancing,
or external model protocol.

## Public model

S025 defines `MeshVisual` only. Geometry is inline and indexed.

| Attribute | Type | Required | Default | Semantics |
|---|---|---:|---|---|
| `id` | protocol id string | yes | none | Stable public visual id. |
| `positions` | float32/float64 `(N,2)` or `(N,3)` | yes | none | Vertex positions. `(N,2)` is the strict 2D path; `(N,3)` requires 3D view/backend capability. |
| `faces` | integer `(M,3)` | yes | none | Indexed triangles into `positions`; public v1 is triangle-only. |
| `coordinate_space` | `CoordinateSpace.NDC` or `.DATA` | yes | none | Existing coordinate-space semantics. |
| `color_mode` | `MeshColorMode` | no | inferred only when unambiguous | `uniform`, `face`, or optional `vertex`. |
| `color` | RGBA `(4,)`, `(M,4)`, or `(N,4)` | yes | none | Uniform, per-face, or per-vertex color according to `color_mode`. |
| `normal_mode` | `MeshNormalMode` | no | `none` | S039 accepts `face` only for flat Lambert; `vertex` remains deferred. |
| `normals` | float32/float64 `(M,3)` or `(N,3)` | no | none | S039 accepts `(M,3)` face normals only; `(N,3)` vertex normals remain deferred. |
| `normal_generation` | `MeshNormalGeneration` | no | `none` | S039 accepts deterministic `face_flat` generation for DATA-space 3D triangle faces. |
| `shading` | `MeshShading` | no | `flat` | Canonical spelling is `unlit_rgba`, `flat_lambert`, or `texture2d_unlit`; legacy enum values require normalization during implementation. |
| `texture2d_id` | protocol id string or `None` | no | `None` | S050 accepts a reference to a declared `Texture2D` only when `shading="texture2d_unlit"`. |
| `uv_mode` | `MeshUVMode` | no | `none` | S050 accepts `vertex` only for per-vertex UVs. |
| `uvs` | float32/float64 `(N,2)` or `None` | no | none | S050 accepts finite per-vertex UVs indexed by existing mesh faces. |
| `face_culling` | `FaceCulling` | no | `none` | `none`, optional/capability-gated `back`/`front`. For `(N,3)` strict paths, S050 classifies front/back by signed area after projection into panel NDC. |
| `depth_test` | `DepthMode` | no | `auto` | `auto`, `disabled`, or `enabled`. |
| `depth_write` | `DepthMode` | no | `auto` | `auto`, `disabled`, or `enabled`. |
| `order` | finite scalar | no | `0` | 2D painter/order hint when depth is disabled or unavailable. |
| `opacity_policy` | `OpacityPolicy` | no | `ordinary_alpha` | Ordinary alpha only; no OIT or face-sorting guarantee. |

Do not include public v1 fields for geometry resources, material objects, lights, textures, UVs,
wireframe/edge styling, mesh-local transforms, instance transforms, scalar colormaps, or external
model files.

## Enums

- `MeshColorMode`: `UNIFORM`, `FACE`; optional/capability-gated `VERTEX`.
- `MeshNormalMode`: `NONE`, `FACE`; `VERTEX` remains deferred after S039.
- `MeshNormalGeneration`: `NONE`, `FACE_FLAT`.
- `MeshShading`: canonical S039 protocol spelling is `UNLIT_RGBA` or `FLAT_LAMBERT`; legacy `FLAT`
  may alias `UNLIT_RGBA`, while legacy `LAMBERT` is non-canonical. S050 adds
  `TEXTURE2D_UNLIT`.
- `MeshUVMode`: `NONE`, `VERTEX`.
- `FaceCulling`: `NONE`, optional/capability-gated `BACK`, `FRONT`.
- `DepthMode`: `AUTO`, `DISABLED`, `ENABLED`.
- `OpacityPolicy`: `ORDINARY_ALPHA`.

No Datoviz slot names, material structs, or backend draw-state names are public protocol enums.

## Validation and units

- `positions`: rank 2, shape `(N,2)` or `(N,3)`, `N >= 3`, float32/float64, finite.
- `faces`: rank 2, shape `(M,3)`, `M >= 1`, integer dtype, every index `0 <= i < N`.
- Strict validation rejects empty geometry, object arrays, invalid indices, non-finite positions,
  invalid RGBA values, and ambiguous color mode/shape combinations.
- Strict validation should reject degenerate zero-area triangles. Permissive/adaptation mode may warn,
  skip, or deactivate degenerate triangles, but they are not query-conformance targets.
- Duplicate vertices are valid. Unreferenced vertices are allowed but should produce a non-fatal
  diagnostic.
- RGBA follows existing validation: uint8 `[0,255]` or finite float `[0,1]`.
- `UNIFORM` color requires shape `(4,)`; `FACE` requires `(M,4)`; `VERTEX` requires `(N,4)`.
- S039 face normals must be finite, non-zero, and shaped `(M,3)`. Vertex normals remain deferred.
- S039 `FACE_FLAT` normal generation is deterministic for DATA-space 3D triangle faces using
  `cross(p1 - p0, p2 - p0)` and fails on degenerate triangles.
- S050 `texture2d_unlit` requires a declared RGBA8 `Texture2D`, `uv_mode="vertex"`, and finite
  `uvs.shape == (N,2)`. Separate UV indices, per-corner UVs, generated UVs, sampler fields, and
  color-space controls remain unsupported.
- `order` is a finite dimensionless visual-order scalar.

## Geometry, color, and material policy

Strict S025 conformance is flat filled triangles with uniform or per-face RGBA. Per-vertex RGBA is
optional because backends may differ in interpolation support. If a backend approximates vertex color
with face-averaged color, that must be opt-in and diagnosed.

Alpha is accepted through RGBA, but strict QA should use opaque colors. Partially transparent meshes
use ordinary backend alpha blending where supported; order-independent transparency, intersecting
transparent triangle correctness, and automatic face sorting are not guaranteed.

S038 names the unlit material boundary: existing RGBA mesh colors are implicit `unlit_rgba`, with
`output.rgb = base.rgb` and `output.a = base.a`. S039 accepts flat Lambert face-normal shading for
opaque DATA-space 3D triangle meshes. S050 accepts unlit RGBA8 texture sampling with per-vertex UVs
and fixed nearest/clamp/no-mipmap sampling. Public material objects, vertex normals, smooth Lambert,
samplers, Phong/specular/shininess, and backend material-struct fields remain deferred unless a
later ADR/spec accepts them.

S050 accepts only a strict face-culling boundary, not strict transparent rendering. For `(N,3)`
meshes, front/back classification is performed in projected panel NDC: counter-clockwise x/y winding
is front-facing, and `FaceCulling.BACK` or `.FRONT` suppresses triangles before depth, order, alpha
compositing, and query hit selection. Projected-degenerate triangles have no strict raster
contribution or strict pick hit. Non-opaque 3D mesh alpha remains outside strict opaque-depth and
strict mesh-triangle-pick paths.

## Transform, camera, and depth policy

`MeshVisual` does not define a camera or mesh-local transform. `(N,2)` positions are interpreted as
2D panel geometry in NDC or DATA and are the strict Matplotlib reference path. `(N,3)` positions are
valid protocol data and require an accepted 3D panel/view projection capability for rendering and
query. S036 defines the first accepted public 3D panel/view projection capability: static
orthographic `View3D`.

`depth_test=AUTO` should behave like ordered 2D rendering for 2D meshes and use depth for 3D meshes
when the view/backend supports it. Explicit unsupported depth or culling requests require structured
diagnostics.

## Query payload

Mesh query/readback is face-level and capability-gated. The strict Matplotlib/reference path supports
2D uniform and per-face RGBA face hits through `gsp.mesh-query@0.1`. A supported mesh hit should
include:

- `family="mesh"`;
- `visual_id`;
- `hit_kind="face"`;
- `face_index`;
- `vertex_indices` from `faces[face_index]`;
- `panel_xy`;
- `coordinate_space`;
- `displayed_rgba`;
- `depth` when available.

Recommended capability-gated fields include `barycentric`, hit `position`, `data_position`,
`ndc_position`, `color_source`, `interpolated_rgba`, `front_facing`, `normal`, and query diagnostics.
`instance_id`, scalar `value`, UV/texel/material ids, edge picking, and vertex picking are deferred.

## Backend mapping

Matplotlib is the strict reference backend for 2D filled triangles. Use a triangle collection such as
`PolyCollection`, support `UNIFORM` and `FACE` RGBA, NDC and DATA placement, visual `order`, and CPU
2D face hit testing. Matplotlib 3D output is optional QA only and must not be treated as strict
protocol authority.

Datoviz v0.4 support must be capability-gated against retained mesh APIs. Exact 2D adaptation to 3D
`z=0` is allowed when documented. Per-face color may be adapted to a per-vertex backend by duplicating
vertices only if original face identity remains recoverable or diagnostics report the adapted topology.
Hidden lighting/material defaults must not alter strict flat RGBA semantics.

## Strict QA cases

- `mesh_single_triangle_uniform_ndc_2d`;
- `mesh_indexed_square_uniform_ndc_2d`;
- `mesh_indexed_square_per_face_ndc_2d`;
- `mesh_data_coordinates_2d`;
- `mesh_order_overlap_2d`;
- `mesh_validation_invalid_index`;
- `mesh_validation_bad_color_shape`;
- `mesh_query_face_2d`.

Optional/capability-gated cases: vertex color interpolation, 3D cube depth/culling, projected-NDC
face culling, alpha overlap, 3D face query, and wireframe if later accepted. Normals, generated
normals, Lambert, Phong, and texture demonstrations are private/experimental until a later material
or texture ADR accepts them.

## Deferred

Public `GeometryResource`, public `Material`, `SurfaceVisual`, `VolumeVisual`, quads/polygons/holes,
triangle strips/fans, splats, subdivision, skeletal animation, morph targets, topology editing,
instancing, mesh-local transforms, PBR, public lights, shadows, clipping planes, advanced
transparency, UVs/textures/samplers/atlases, OBJ/PLY/STL loading, external model-file protocol,
remote mesh chunks, LOD, GPU-generated geometry, public Datoviz slot names/material structs/draw
calls, broad colormaps, colorbars, advanced normalization, normal/depth debug materials, edge/vertex
UV/texel/voxel picking, and guaranteed 3D Matplotlib conformance are out of S025 v1.
