# S038 Mesh Material Boundary Decisions

Status: accepted by M169 from P023 response.

## Accepted

- Existing `MeshVisual` RGBA color is explicitly interpreted as implicit `unlit_rgba` material color.
- `meshvisual.material.unlit_rgba.v1` is accepted as a capability name.
- `unlit_rgba` is a protocol concept only; S038 adds no public material object.
- Strict opaque material output is `output.rgb = base.rgb` and `output.a = base.a`.
- Camera/projection/depth affect geometry and ordering only, not material color.
- Non-opaque 3D mesh alpha remains non-strict and uses `mesh3d_alpha_not_strict`.
- No strict color-space conversion, tone-mapping, or display color-management claim is made.

## Deferred

- `MeshMaterial3D`, public material resources, and public backend-native material objects.
- Public normals, generated normals, Lambert, Phong, specular, shininess, ambient lights,
  directional lights, and `View3D.lights`.
- `Texture2D`, UVs, samplers, texture/color combination rules, and textured mesh materials.
- Transparency sorting, culling expansion, shadows, PBR, model loading, instancing, and scene graph
  semantics.

## Superseded Optional Wording

S025 optional normals, generated face normals, and Lambert wording remains historical implementation
material. It is not accepted S038 public material support and must not be advertised until a later
ADR/spec accepts normal, light-space, color-space, alpha, and fixture semantics.

## Source

`.agent/consultations/P023-response.md` converted into ADR-0025 and
`spec/visuals/mesh_materials_s038.md`.
