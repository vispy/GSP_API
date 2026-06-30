# M174 - S039 Datoviz Lambert capability gates

## Stage

S039 - Lambert Normals Pre-Design

## Status

Ready.

## Summary

Define Datoviz behavior for S039 flat Lambert support: strict only if exact S039 semantics are
implemented, otherwise adapted/unsupported with structured diagnostics.

## Deliverables

- Datoviz capability-gate updates for S039 Lambert, face normals, generated normals, and View3D
  lights.
- Unsupported/adapted behavior that does not expose backend-native material, shader, or Vulkan state.
- Focused tests proving unsupported/adapted reporting for unavailable strict Lambert paths.

## Acceptance

- Datoviz does not silently accept `flat_lambert` unless exact S039 semantics are implemented.
- Capability names match ADR-0026 and `spec/visuals/mesh_flat_lambert_s039.md`.
- Existing unlit 3D mesh behavior remains unchanged.

## Stop Condition

Stop if strict Datoviz Lambert would require native semantics that differ from S039 or public exposure
of Datoviz-native material/shader state.
