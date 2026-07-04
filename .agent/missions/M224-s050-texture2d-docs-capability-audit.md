# M224 - S050 Texture2D docs and capability audit

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

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

## Result

Completed the S050 Texture2D docs and capability audit.

Updated:

- `spec/backend_capabilities_visuals.md` with a current S050 support table distinguishing protocol
  validation, Matplotlib unsupported posture, Datoviz blocked posture, and VisPy2 producer support;
- `spec/vispy2/api.md` to document the implemented `texture`/`uvs` extension, emitted
  `Figure.texture_resources()`, and rejection of non-default shading for textured meshes;
- `spec/backends/datoviz.md` with the M220 public-symbol evidence and remaining sampler/origin/color
  blockers;
- `spec/backends/matplotlib.md` to state that direct `render_mesh_visual()` rejects textured meshes
  before building a `PolyCollection`;
- `examples/README.md` to label legacy Phong/textured mesh examples as outside the accepted GSP v1
  material and S050 renderer capability contracts.

Audited capability strings in `src/`, `tests/`, `spec/`, `examples/`, and `.agent/`; renderer
Texture2D capability advertisement remains absent. Datoviz and Matplotlib renderer claims remain
incomplete and unpromoted.
