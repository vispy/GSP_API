# M169 - S038 materials and lights ADR

## Stage

S038 - Materials, Lights, and Textures Pre-Design

## Status

Blocked pending ChatGPT Pro consultation P023.

## Summary

Decide the minimal public material/light model after S037. This is not part of S037 implementation.

## Candidate Deliverables

- ADR/spec for `MeshMaterial3D`, unlit color clarification, flat Lambert directional lighting, and
  diagnostics.
- Reserved capability names and strict/adapted wording.
- Explicit deferral or separate plan for Phong and texture/UV semantics.

## Stop Condition

Stop if material/light implementation is requested before an accepted S038 spec exists.

## Consultation

Created `.agent/consultations/P023-materials-lights-s038.md`.

Dependent ADR/spec implementation should wait until the P023 answer is available because S038 is an
architecture/spec decision about public material, light, normal, texture, and capability semantics.
