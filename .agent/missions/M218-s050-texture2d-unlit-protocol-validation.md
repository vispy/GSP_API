# M218 - S050 Texture2D unlit protocol validation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Implement the accepted S050 protocol surface for unlit Texture2D mesh materials.

## Required Context

- `adr/ADR-0029-mesh-texture2d-unlit.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/visuals/mesh.md`
- `spec/resources.md`
- `.agent/decisions/S050_texture2d_unlit_contracts.md`

## Deliverables

- Add protocol dataclasses/enums/resources for `Texture2D`, `MeshVisual.texture2d_id`,
  `uv_mode`, `uvs`, and `shading="texture2d_unlit"`.
- Add strict validation for RGBA8 texture resources, per-vertex UV cardinality, unsupported sampler
  and color-space requests, missing/unknown texture ids, and lighting/material conflicts.
- Add focused protocol validation tests for the accepted positive and negative structural cases.

## Acceptance

- Existing mesh behavior remains unchanged when `texture`/`uvs` are absent.
- Invalid texture and UV payloads fail with S050 diagnostics.
- No renderer advertises `meshvisual.material.texture2d_unlit.v1` as part of this mission.

## Stop Conditions

- Stop before accepting public sampler objects, external image paths, material objects, textured
  lighting, alpha/culling semantics, model loading, or backend-native texture handles.
- Stop if implementation would require changing S038/S039 material semantics.

## Result

Implemented the accepted S050 protocol surface:

- `Texture2D` and `Texture2DFormat` resource models with strict RGBA8 validation;
- duplicate texture-id validation through `validate_texture2d_resources()`;
- `MeshShading.TEXTURE2D_UNLIT`;
- `MeshUVMode`;
- `MeshVisual.texture2d_id`, `uv_mode`, and `uvs`;
- `validate_mesh_visual_texture2d_unlit()` for cross-resource texture id resolution;
- focused tests for positive protocol construction, invalid textures, missing/unknown texture ids,
  UV shape/non-finite failures, and material-field conflicts.

Renderer capability promotion was not changed. Public sampler objects, external image paths,
material objects, textured lighting, alpha/culling semantics, model loading, and backend-native
texture handles remain out of scope.
