# ADR-0026 - Minimal Flat Lambert Mesh Shading with Face Normals

## Status

Accepted

ADR-0029 later accepts unlit Texture2D sampling with per-vertex UVs. That later texture material
does not change S039 flat Lambert semantics.

## Context

S038 accepted only implicit `unlit_rgba` material semantics for existing `MeshVisual` RGBA colors.
It deliberately deferred public material objects, normals, generated normals, Lambert/Phong shading,
lights, textures, UVs, samplers, and scene graph semantics.

P024 reviewed the next material step and recommended accepting a narrow Lambert model only when it
stays deterministic, DATA-space, face-normal-only, and capability-gated. This ADR converts that
recommendation into public protocol authority before implementation.

## Decision

S039 accepts a minimal flat Lambert diffuse mode for opaque DATA-space 3D triangle meshes using face
normals.

Accepted public concepts:

- canonical `MeshVisual.shading="flat_lambert"` for S039 Lambert;
- `MeshVisual.shading="unlit_rgba"` as the canonical S038 material selector;
- legacy `shading="flat"` may be a compatibility alias for `unlit_rgba`;
- legacy `shading="lambert"` is not canonical public S039 input;
- `MeshVisual.normal_mode="face"`;
- `MeshVisual.normals` with shape `(F, 3)` for explicit face normals;
- `MeshVisual.normal_generation="face_flat"` for deterministic generated triangle face normals;
- `View3D.ambient_light_intensity`, a finite scalar in `[0.0, 1.0]`;
- `View3D.directional_light`, either absent or a single DATA-space `DirectionalLight3D`;
- `DirectionalLight3D.direction_to_light`, a finite non-zero DATA-space vector from shaded point
  toward the light;
- `DirectionalLight3D.intensity`, a finite scalar in `[0.0, 1.0]`.

S039 does not add a public `MeshMaterial3D` object. `MeshVisual.color` remains the base color source.
Lights are scalar white-light terms only.

For each Lambert face:

```text
l = normalize(direction_to_light)
n = normalize(face_normal)
D = directional_light.intensity * max(0, dot(n, l))
L = clamp(ambient_light_intensity + D, 0.0, 1.0)
output.rgb = clamp(base.rgb * L, 0.0, 1.0)
output.a = base.a
```

If no directional light is present, `D = 0`. Alpha is not lit. Non-opaque 3D mesh alpha remains
non-strict and uses `mesh3d_alpha_not_strict`.

S039 defines arithmetic over normalized protocol color channel values only. It does not claim linear
RGB, sRGB conversion, gamma correction, tone mapping, or display color-management semantics.

## Normal Semantics

Strict `flat_lambert` requires `(N, 3)` `CoordinateSpace.DATA` positions and a resolved `View3D`.
`CoordinateSpace.NDC` Lambert is deferred.

Exactly one normal source is valid:

- explicit face normals: `normal_mode="face"`, `normals.shape == (F, 3)`,
  `normal_generation="none"`;
- generated face normals: `normal_mode="face"`, `normals is None`,
  `normal_generation="face_flat"`.

`F` is the canonical rendered face count. S039 does not define per-vertex normal cardinality or
normal interpolation.

Explicit normals are in DATA coordinates, finite, and non-zero. Input normals need not be unit
length; protocol normalization is part of the semantics.

Generated face normals are triangle-only. For face vertices `p0`, `p1`, and `p2`:

```text
raw = cross(p1 - p0, p2 - p0)
n = raw / length(raw)
```

Winding is right-handed with respect to the face vertex order. Reversing the face flips the normal.
The protocol must not auto-orient normals toward the camera, light, or positive depth.

Degenerate or non-finite generated normals fail validation. Backends must not silently invent
fallback normals.

## Deferred

Deferred from S039:

- public material objects or reusable material resources;
- vertex normals, smooth Lambert, and normal interpolation;
- Phong, Blinn-Phong, specular color, shininess, view-vector, or camera-position lighting;
- multiple lights, colored lights, point/spot lights, attenuation, light IDs, and scene light graphs;
- texture resources, UVs, samplers, normal maps, and texture/color combination rules;
- Lambert on NDC meshes;
- backend-native Datoviz material structs, shader slots, Vulkan/draw-state names, Matplotlib
  artists/axes/controllers, and legacy GSP material classes as public API.

## Capability Boundary

Accepted in S039:

```text
meshvisual.material.flat_lambert.v1
meshvisual.normals.face3d.v1
meshvisual.normal_generation.face_flat.v1
view3d.light.ambient.v1
view3d.light.directional.v1
```

Existing prerequisite capabilities remain unchanged:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
meshvisual.material.unlit_rgba.v1
```

Accepted separately by ADR-0029:

```text
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
```

Still reserved or deferred after ADR-0029:

```text
meshvisual.normals.vertex3d.v1
meshvisual.material.smooth_lambert.v1
meshvisual.material.flat_phong.v1
```

## Backend Expectations

Matplotlib may compute S039 face normals and Lambert colors on the CPU from canonical protocol
fields, then pass resolved per-face colors to its existing collection path. This can be strict for
material math if fixtures compare resolved face RGBA values. The combined Matplotlib 3D mesh raster
path remains adapted unless fixtures prove projection, face sorting, color assignment, and opaque
depth behavior under accepted tolerances.

Datoviz may claim strict S039 support only if it implements the exact GSP semantics. CPU-resolving
flat Lambert face colors and submitting them through an unlit retained mesh path is acceptable when
topology preserves one color per face. Native Datoviz Lambert paths are strict only if normal
interpolation, light direction convention, color arithmetic, and alpha behavior match S039 exactly;
otherwise they are adapted review support.

VisPy2 producer helpers must emit canonical protocol fields and must not invent engine-specific
material semantics.

## Consequences

S039 opens one narrow material feature without creating a material-resource system or scene graph.
The next implementation mission may add public protocol dataclasses/enums/validation for the accepted
fields, but texture/UV and Phong work remain separate future stages.

## Source

`.agent/consultations/P024-response.md` converted into this ADR and
`spec/visuals/mesh_flat_lambert_s039.md`.
