# M171 - S039 Lambert normals ADR

## Stage

S039 - Lambert Normals Pre-Design

## Status

Blocked pending ChatGPT Pro consultation P024.

## Summary

Convert the P024 response into durable S039 ADR/spec authority, or explicitly defer Lambert if the
response recommends against accepting it now.

## Candidate Deliverables

- ADR/spec for the accepted normal, Lambert material, light, alpha, color-space, diagnostic, and
  fixture boundary.
- Updated capability names and strict/adapted backend wording.
- Explicit deferral for Phong/specular/shininess and textures/UVs/samplers.
- Revised mission stack for implementation only after the ADR/spec baseline exists.

## Stop Condition

Stop if material/light/normal implementation is requested before an accepted S039 spec exists.

## Consultation

Created `.agent/consultations/P024-lambert-normals-s039.md`.

Dependent ADR/spec implementation should wait until the P024 answer is available because S039 is an
architecture/spec decision about public normals, Lambert lighting, material/light fields, color
combination, diagnostics, capabilities, and conformance fixtures.
