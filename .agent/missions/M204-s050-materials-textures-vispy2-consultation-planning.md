# M204 - S050 materials textures and VisPy2 API consultation planning

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Prepare and integrate the next architecture/API-shape consultation for materials, textures, UVs, and
broader VisPy2 public 3D/plotting ergonomics.

## Stop Conditions

- Stop before implementing materials, textures, UVs, smooth lighting, Phong, or broad VisPy2 API
  helpers without a self-contained ChatGPT Pro consultation packet and user-provided result.

## Result

Created the self-contained ChatGPT Pro consultation packet:

`.agent/consultations/P031-materials-textures-vispy2-api.md`

Archived the user-provided response as:

`.agent/consultations/P031-response.md`

Accepted the response's recommended next stage, unlit Texture2D plus per-vertex UVs for
`MeshVisual`, and created the ADR/spec baseline:

- `adr/ADR-0029-mesh-texture2d-unlit.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `.agent/decisions/S050_texture2d_unlit_contracts.md`

Dependent implementation may proceed only for that accepted stage. Culling/alpha semantics and
expanded 3D query payloads remain blocked pending separate ChatGPT Pro consultations.
