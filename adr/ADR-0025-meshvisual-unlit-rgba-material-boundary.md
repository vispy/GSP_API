# ADR-0025 - MeshVisual Unlit RGBA Material Boundary

## Status

Accepted

ADR-0026 later accepts flat Lambert face-normal shading. ADR-0029 later accepts unlit Texture2D
sampling with per-vertex UVs. Those later ADRs do not change the S038 `unlit_rgba` boundary.

## Context

S036 and S037 accepted a bounded orthographic `View3D` baseline, public `View3D` navigation
actions, Datoviz static `View3D` mesh binding, and canonical View3D ray-context readback. They
explicitly deferred public material, light, texture, UV, sampler, culling, perspective, strict 3D
picking, and scene graph semantics.

S025 accepted `MeshVisual` as an inline indexed triangle mesh and described strict rendering as flat
filled triangles. It also left normals, generated face normals, and Lambert shading as
capability-gated future surface area. P023 reviewed that older optional wording after S037 and
recommended a smaller S038 boundary before any public lighting or texture model is accepted.

## Decision

S038 accepts only implicit `unlit_rgba` material semantics for existing `MeshVisual` RGBA colors.

- `meshvisual.material.unlit_rgba.v1` is the only accepted S038 material capability.
- `unlit_rgba` is a protocol concept, not a public `MeshMaterial3D` object.
- A color-bearing `MeshVisual` without a future explicit material is interpreted as unlit RGBA.
- Existing `MeshVisual.color` remains the base color source. S038 does not add new color
  cardinalities.
- Strict opaque unlit rendering uses `output.rgb = base.rgb` and `output.a = base.a`.
- No normal, light, camera position, view direction, depth value, texture sample, or backend-native
  material state may alter the material color.
- Alpha remains part of RGBA, but strict 3D mesh material conformance is only claimed for opaque
  alpha. Non-opaque 3D mesh composition remains non-strict and uses `mesh3d_alpha_not_strict`.
- S038 makes no linear-RGB, sRGB conversion, tone-mapping, gamma-correction, or display
  color-management claim.

Deferred from S038:

- public `MeshMaterial3D` objects or material resources;
- `MeshVisual.normals`, `normal_mode`, `normal_generation`, or generated backend normals as accepted
  material semantics;
- Lambert, Phong, specular, shininess, public ambient lights, public directional lights, and
  `View3D.lights`;
- `Texture2D`, UVs, samplers, texture/color combination rules, and textured mesh materials;
- transparency sorting, culling expansion, shadows, PBR, model loading, instancing, or scene graph
  semantics.

The older S025 optional normals/Lambert wording is superseded for accepted public material support:
those names remain experimental or reserved until a later ADR/spec accepts normal, light-space,
color-space, alpha, and fixture semantics.

## Capability Boundary

Accepted in S038:

```text
meshvisual.material.unlit_rgba.v1
```

Reserved or deferred, not advertised as S038 support:

```text
meshvisual.material.flat_lambert.v1
meshvisual.material.flat_phong.v1
view3d.light.ambient.v1
view3d.light.directional.v1
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
```

ADR-0026 later accepts `meshvisual.material.flat_lambert.v1`, `view3d.light.ambient.v1`, and
`view3d.light.directional.v1`. ADR-0029 later accepts `texture2d.rgba8.v1`,
`meshvisual.uv.vertex2d.v1`, and `meshvisual.material.texture2d_unlit.v1`. Phong and broader
material/sampler behavior remain deferred.

Future normal capability names such as `meshvisual.normals.vertex3d.v1` and
`meshvisual.normals.face3d.v1` are not introduced by S038.

## Backend Expectations

Matplotlib may claim `meshvisual.material.unlit_rgba.v1` for accepted opaque `MeshVisual` RGBA color
modes it preserves without lighting, generated normals, texture sampling, Phong calculation, or
backend material tinting. Its `(N, 3)` mesh raster path remains adapted because it CPU-projects
vertices to 2D collections and approximates opaque depth by face sorting.

Datoviz may claim `meshvisual.material.unlit_rgba.v1` when the adapter preserves retained mesh RGBA
colors with implicit lighting disabled and without exposing Datoviz-native material structs, shader
slots, Vulkan state, or camera/controller objects. Datoviz native depth testing remains governed by
the existing 3D mesh depth capabilities, not by this material capability.

VisPy2 producer helpers may emit canonical `MeshVisual` objects with RGBA colors, but must not define
`MeshMaterial3D`, Lambert, Phong, `Texture2D`, UV, sampler, or light semantics ahead of accepted
protocol specs.

## Consequences

S038 gives the existing flat RGBA mesh behavior a clear material name without starting a graphics
engine material system. Review-only legacy Matplotlib lighting/texture code and Datoviz-native
material/light APIs remain implementation evidence or private experiments, not public protocol
support.

The next material expansion must be a separate evidence-backed ADR. A Lambert ADR must first accept
normal source/cardinality/space, light direction space, color combination, alpha, and fixture
semantics. A texture ADR must first accept texture resource ownership, pixel format, UV cardinality,
sampler, color-space, and texture/color combination semantics.

## Source

`.agent/consultations/P023-response.md` converted into this ADR and
`spec/visuals/mesh_materials_s038.md`.
