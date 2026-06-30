# S038 Closeout

## Result

S038 completed as an ADR/spec boundary stage. P023 recommended the smallest public material surface:
accept implicit `unlit_rgba` semantics for existing `MeshVisual` RGBA colors and defer public
material objects, normals, lights, UVs, textures, samplers, and shaded material models.

## Durable Authority

- `adr/ADR-0025-meshvisual-unlit-rgba-material-boundary.md`
- `spec/visuals/mesh_materials_s038.md`
- `.agent/decisions/S038_mesh_material_boundary.md`
- `.agent/consultations/P023-response.md`

## Capability Outcome

Accepted:

```text
meshvisual.material.unlit_rgba.v1
```

Deferred/reserved, not advertised:

```text
meshvisual.material.flat_lambert.v1
meshvisual.material.flat_phong.v1
view3d.light.ambient.v1
view3d.light.directional.v1
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
```

## Recommended Next Stage

Open a separate evidence-backed stage for exactly one next expansion:

- Lambert-with-normals, requiring normal source/cardinality/space, light-space, color-combination,
  alpha, color-space, and fixture semantics; or
- unlit texture-with-UVs, requiring texture resource ownership, pixel format, UV cardinality,
  sampler, color-space, alpha, and texture/color combination semantics.

Do not combine Lambert and textures in the same next stage.
