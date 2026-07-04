# M224 - S050 Texture2D docs and capability audit

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft.

## Summary

Audit S050 textured mesh documentation, capability claims, diagnostics, and examples after
implementation missions.

## Required Context

- `SPEC_INDEX.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/backend_capabilities_visuals.md`
- `spec/backends/matplotlib.md`
- `spec/backends/datoviz.md`
- `spec/vispy2/api.md`

## Deliverables

- Verify every advertised backend and producer capability is fixture-backed.
- Update docs/examples with exact limitations, deferred concepts, alpha non-strict behavior, and UV
  seam duplication requirements.
- Confirm docs do not imply Phong, smooth normals, model files, alpha sorting, repeated textures, or
  backend-native material control.

## Acceptance

- Capability matrix, backend specs, VisPy2 docs, and examples agree with ADR-0029.
- Test/docs validation passes for changed surfaces.

## Stop Conditions

- Stop before release-facing claims if Datoviz or Matplotlib capability evidence is incomplete.
