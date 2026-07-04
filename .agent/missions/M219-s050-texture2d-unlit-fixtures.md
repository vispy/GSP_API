# M219 - S050 Texture2D unlit conformance fixtures

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft.

## Summary

Create deterministic conformance and manual review fixtures for S050 textured meshes.

## Required Context

- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/conformance-fixtures.md`
- `spec/visual_qa_harness.md`

## Deliverables

- Add positive fixtures for UV orientation, checker quads, clamp-to-edge, color multiplication,
  duplicate-position seams, opaque View3D textured quads, and alpha diagnostics.
- Add negative fixtures for invalid texture resources, missing/unknown texture ids, invalid UVs,
  unsupported samplers/color-space requests, and unsupported textured-material renderer claims.
- Generate review artifacts using interior probe points rather than full-image exact matches at
  triangle or texel edges.

## Acceptance

- Fixture metadata records expected sample/probe values and diagnostics.
- Fixtures do not depend on backend antialiasing at triangle edges.

## Stop Conditions

- Stop before requiring Datoviz or Matplotlib renderer promotion.
- Stop if fixture semantics require perspective-correct texturing, alpha sorting, or culling.
