# MeshVisual Flat Lambert Shading - S039

Status: accepted S039 protocol boundary. S050 later accepts unlit Texture2D/UV semantics separately
in `spec/visuals/mesh_texture2d_unlit_s050.md`; that does not change S039 Lambert behavior.

Semantic purpose: add the smallest deterministic diffuse lighting model after S038 while preserving
backend neutrality and keeping material objects, smooth shading, Phong, textures, UVs, samplers, and
scene graphs out of scope.

## Scope

S039 accepts flat Lambert diffuse shading only for opaque DATA-space 3D triangle meshes in a resolved
`View3D`.

In scope:

- face normals;
- deterministic triangle face-normal generation;
- scalar ambient light on `View3D`;
- one optional scalar white DATA-space directional light on `View3D`;
- exact RGB Lambert formula;
- alpha passthrough.

Out of scope:

- public `MeshMaterial3D`;
- vertex normals or smooth Lambert;
- Phong/specular/shininess;
- textured Lambert, samplers, normal maps;
- multiple lights, colored lights, point/spot lights, attenuation, light IDs, scene graph;
- backend-native material, shader, draw-state, or artist objects.

## Public Schema

Canonical material/shading selectors:

| Field | Type | Default | Semantics |
|---|---|---|---|
| `MeshVisual.shading` | `"unlit_rgba" | "flat_lambert"` | `"unlit_rgba"` | `unlit_rgba` is S038. `flat_lambert` is S039. |
| `MeshVisual.normal_mode` | `"none" | "face"` | `"none"` | Face normals only for S039. |
| `MeshVisual.normals` | float array `(F,3)` or `None` | `None` | Explicit face normals when `normal_mode="face"`. |
| `MeshVisual.normal_generation` | `"none" | "face_flat"` | `"none"` | Deterministic generated triangle face normals. |
| `View3D.ambient_light_intensity` | float | `0.0` | Finite scalar in `[0.0, 1.0]`. |
| `View3D.directional_light` | `DirectionalLight3D | None` | `None` | Optional single DATA-space directional light. |
| `DirectionalLight3D.direction_to_light` | tuple `(x,y,z)` | required | Finite non-zero DATA-space vector from shaded point toward light. |
| `DirectionalLight3D.intensity` | float | `1.0` | Finite scalar in `[0.0, 1.0]`. |

Legacy `shading="flat"` may be accepted by adapters as a compatibility alias for `unlit_rgba`.
Legacy `shading="lambert"` is not canonical S039 protocol input and should be rejected or diagnosed.

## Normal Semantics

Strict `flat_lambert` requires:

- `MeshVisual.positions.shape == (N,3)`;
- `MeshVisual.coordinate_space == CoordinateSpace.DATA`;
- triangle faces with canonical rendered face count `F`;
- a resolved `View3D`;
- one valid face-normal source.

Valid normal sources:

| Source | Required fields |
|---|---|
| Explicit face normals | `normal_mode="face"`, `normals.shape == (F,3)`, `normal_generation="none"`. |
| Generated face normals | `normal_mode="face"`, `normals is None`, `normal_generation="face_flat"`. |

Invalid combinations include:

- `normal_mode="vertex"`;
- normals shaped `(N,3)` for Lambert;
- `normal_mode="face"` with neither explicit normals nor `face_flat` generation;
- explicit normals plus `normal_generation="face_flat"`;
- `flat_lambert` on `(N,2)` positions;
- `flat_lambert` on `CoordinateSpace.NDC` positions;
- `flat_lambert` without a resolved `View3D`.

Normals are in DATA coordinates. Existing 2D affine transforms do not apply to `(N,3)` mesh geometry
or normals. S039 has no model/local or view/camera normal space.

Input normals may be non-unit. Protocol shading uses:

```text
n = normal / length(normal)
```

Normals with non-finite components, non-finite length, or zero length are invalid.

Generated face normals use the face vertex order:

```text
raw = cross(p1 - p0, p2 - p0)
n = raw / length(raw)
```

The winding is right-handed with respect to the triangle face order. Reversing face order flips the
generated normal. The protocol does not auto-orient generated normals toward camera, light, or depth.

Degenerate triangles and non-finite positions fail validation for generated normals.

## Light Semantics

`View3D.ambient_light_intensity` is a scalar white ambient term in `[0.0, 1.0]`.

`DirectionalLight3D.direction_to_light` is a DATA-space vector from the shaded point toward the
light. It is not camera-space, view-space, a backend-native light direction, or a headlight.
View3D navigation changes projection, not the DATA-space light vector.

If `View3D.directional_light is None`, the directional term is zero.

## Color and Alpha Formula

Let `base` be the S038 resolved base RGBA from `MeshVisual.color`, `A` be
`ambient_light_intensity`, and `n` be the normalized face normal.

If no directional light is present:

```text
D = 0
```

Otherwise:

```text
l = normalize(direction_to_light)
D = directional_light.intensity * max(0, dot(n, l))
```

The scalar light factor and output color are:

```text
L = clamp(A + D, 0.0, 1.0)
output.rgb = clamp(base.rgb * L, 0.0, 1.0)
output.a = base.a
```

Alpha is not lit. For alpha `< 1.0`, S039 defines the pre-composition RGBA value but final 3D
compositing remains non-strict and uses `mesh3d_alpha_not_strict`.

S039 does not define linear RGB, sRGB conversion, gamma correction, tone mapping, or display
color-management semantics. The formula applies to normalized protocol channel values.

## Capabilities

Accepted S039 capabilities:

| Capability | Meaning | Strict requirements |
|---|---|---|
| `meshvisual.material.flat_lambert.v1` | Flat diffuse Lambert mesh shading. | DATA-space `(N,3)` positions, View3D, explicit or generated face normals, exact scalar formula, opaque conformance fixtures. |
| `meshvisual.normals.face3d.v1` | Explicit per-face 3D normals. | `normal_mode="face"`, `(F,3)` finite non-zero normals, one normal per canonical rendered face. |
| `meshvisual.normal_generation.face_flat.v1` | Deterministic generated triangle face normals. | Triangle faces, DATA positions, `cross(p1-p0, p2-p0)`, failure on degeneracy. |
| `view3d.light.ambient.v1` | Scalar ambient term on `View3D`. | Finite `[0,1]` scalar participating in `L = clamp(A + D, 0, 1)`. |
| `view3d.light.directional.v1` | One DATA-space directional light on `View3D`. | Finite non-zero `direction_to_light`, finite `[0,1]` intensity, exact dot-product semantics. |

Prerequisites:

- `view3d.static.orthographic.v1`;
- `meshvisual.positions3d.data.view3d.v1`;
- `meshvisual.positions3d.opaque_depth.v1` for strict opaque visual ordering;
- `meshvisual.material.unlit_rgba.v1` for base color semantics.

Deferred:

- `meshvisual.normals.vertex3d.v1`;
- `meshvisual.material.smooth_lambert.v1`;
- `meshvisual.material.flat_phong.v1`;
Accepted separately by S050:

- `texture2d.rgba8.v1`;
- `meshvisual.uv.vertex2d.v1`;
- `meshvisual.material.texture2d_unlit.v1`.

## Diagnostics

| Diagnostic | Trigger |
|---|---|
| `flat_lambert_requires_view3d` | `flat_lambert` without a resolved `View3D`. |
| `flat_lambert_requires_data3d_positions` | Positions are not `(N,3)` DATA coordinates. |
| `flat_lambert_requires_face_normals` | Neither explicit face normals nor `face_flat` generation are provided. |
| `vertex_normals_deferred` | Vertex normals or smooth Lambert are requested. |
| `normal_source_conflict` | Explicit normals and `face_flat` generation are both supplied. |
| `normal_mode_normals_conflict` | Normal fields are inconsistent with `normal_mode`. |
| `face_normals_shape_mismatch` | Explicit normals are not `(F,3)`. |
| `normal_nonfinite` | Explicit normal contains NaN or infinity. |
| `normal_zero_length` | Explicit normal has zero length. |
| `face_normal_generation_nontriangular_deferred` | `face_flat` generation is requested for non-triangle faces. |
| `face_normal_generation_degenerate` | Generated triangle normal is zero-length or non-finite. |
| `ambient_light_invalid` | Ambient intensity is non-finite or outside `[0,1]`. |
| `directional_light_direction_invalid` | Directional light vector is missing, non-finite, or zero-length. |
| `directional_light_intensity_invalid` | Directional light intensity is non-finite or outside `[0,1]`. |
| `legacy_lambert_shading_not_canonical` | Legacy `shading="lambert"` appears in public input. |
| `flat_lambert_unsupported` | Backend lacks S039 support. |
| `flat_lambert_adapted_not_strict` | Backend renders approximate/review Lambert only. |
| `mesh3d_alpha_not_strict` | Lambert mesh has alpha `< 1.0`. |

Unsupported normal, light, material, texture, UV, or backend-native material concepts must not be
silently ignored when a public payload requests them.

## Backend Conformance

Matplotlib is primarily an adapted review backend for visual 3D rendering. It may be strict for
material math if it computes exact S039 resolved face RGBA values from canonical protocol fields.
The combined 3D mesh raster path remains adapted unless projection, face sorting, color assignment,
and opaque depth are proven under accepted tolerances.

Datoviz may claim strict S039 support only when the adapter implements exact GSP semantics. CPU
resolution of Lambert face colors into an unlit retained mesh path is acceptable if one color per
canonical face is preserved. Native Datoviz Lambert paths are strict only if they match S039 normal,
light direction, color arithmetic, and alpha semantics exactly.

VisPy2 producer helpers should emit canonical fields and diagnostics. They must not introduce
engine-specific material objects or backend-native material names.

## Fixtures

Positive fixtures before advertising support:

- explicit face normal aligned with directional light;
- non-unit normal normalization equivalence;
- back-facing clamp to ambient only;
- generated normal for CCW DATA XY triangle;
- reversed winding flips generated normal;
- ambient-only and directional-only cases;
- `A + D > 1` clamp;
- two faces with distinct normals and no interpolation;
- camera/navigation invariance for DATA-space lights;
- alpha passthrough and `mesh3d_alpha_not_strict`;
- capability advertisement gate.

Negative fixtures:

- `(N,2)` positions;
- `(N,3)` NDC positions;
- missing `View3D`;
- vertex normals;
- wrong normal shape;
- non-finite or zero normals;
- explicit normals plus generation;
- degenerate generated normal;
- invalid ambient or directional light values;
- legacy `shading="lambert"`;
- Phong/specular/texture/UV/backend-native material fields attempting to affect Lambert color.

## Implementation Boundary

Implementation may add protocol dataclasses/enums/validation and backend adapters that compute the
accepted semantics. It must not expose Datoviz material structs, shader slots, Vulkan state names,
Matplotlib artists/axes/controllers, or legacy GSP material classes as public API.
