# M171 - S039 Lambert normals ADR

## Stage

S039 - Lambert Normals Pre-Design

## Status

Completed by local-main-codex.

## Summary

Convert the P024 response into durable S039 ADR/spec authority, or explicitly defer Lambert if the
response recommends against accepting it now.

## Deliverables

- ADR/spec for the accepted normal, Lambert material, light, alpha, color-space, diagnostic, and
  fixture boundary.
- Updated capability names and strict/adapted backend wording.
- Explicit deferral for Phong/specular/shininess and textures/UVs/samplers.
- Revised mission stack for implementation only after the ADR/spec baseline exists.

## Stop Condition

Stop if material/light/normal implementation is requested before an accepted S039 spec exists.

## Result

Completed. Archived the pasted answer as `.agent/consultations/P024-response.md`, accepted S039 as a
narrow flat Lambert face-normal extension, and added ADR-0026,
`spec/visuals/mesh_flat_lambert_s039.md`, `.agent/decisions/S039_flat_lambert_normals.md`,
capability wording, and M172 as the next ready implementation mission.
