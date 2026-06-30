# M169 - S038 materials and lights ADR

## Stage

S038 - Materials, Lights, and Textures Pre-Design

## Status

Completed by local-main-codex.

## Summary

Decide the minimal public material/light model after S037. This is not part of S037 implementation.

## Deliverables

- Archived P023 response.
- ADR/spec for implicit `unlit_rgba` material semantics.
- Reserved capability names and strict/adapted wording.
- Explicit deferral for public `MeshMaterial3D`, normals, Lambert, Phong, lights, textures, UVs, and
  samplers.

## Stop Condition

Stop if material/light implementation is requested before an accepted S038 spec exists.

## Result

Completed. Archived the pasted answer as `.agent/consultations/P023-response.md`, accepted
`meshvisual.material.unlit_rgba.v1` as the only S038 material capability, and added ADR-0025,
`spec/visuals/mesh_materials_s038.md`, `.agent/decisions/S038_mesh_material_boundary.md`, capability
wording, and S038 closeout documentation.
