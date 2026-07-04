# M223 - S050 VisPy2 Texture2D producer

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Add the thin VisPy2 producer extension for S050 textured meshes.

## Required Context

- `spec/vispy2/api.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `adr/ADR-0029-mesh-texture2d-unlit.md`

## Deliverables

- Extend `Axes.mesh(..., texture=None, uvs=None)`.
- Emit canonical `Texture2D`, `MeshVisual.texture2d_id`, `uv_mode="vertex"`, `uvs`, and
  `shading="texture2d_unlit"` only when both `texture` and `uvs` are supplied.
- Add producer validation tests and renderer-capability failure tests.

## Acceptance

- Existing mesh calls are unchanged.
- Supplying exactly one of `texture` or `uvs` fails.
- No public sampler/material/backend-specific keywords are added.

## Stop Conditions

- Stop before accepting filenames, URIs, PIL objects, RGB expansion, float scaling, public sampler
  controls, material classes, or backend handles.

## Result

Implemented the thin VisPy2 S050 producer extension:

- `Axes.mesh(..., texture=None, uvs=None)` now emits `Texture2D` resources and
  `MeshVisual.shading="texture2d_unlit"` only when both `texture` and `uvs` are supplied;
- `Figure.texture_resources()` exposes emitted `Texture2D` resources;
- supplying exactly one of `texture` or `uvs` fails without appending visuals or resources;
- texture input is strict `uint8 (H,W,4)` through the protocol `Texture2D` model;
- UVs are finite `(N,2)` per-vertex values;
- texture plus non-default mesh shading is rejected;
- Matplotlib rendering still reports `meshvisual_material_texture2d_unlit_unsupported`.

No filenames, URIs, PIL objects, RGB expansion, float scaling, sampler controls, material classes,
or backend handles were accepted.
