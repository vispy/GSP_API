# M221 - S050 Matplotlib Texture2D policy

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft.

## Summary

Implement the Matplotlib policy for S050 textured meshes: explicit unsupported diagnostics unless a
separate CPU textured-triangle rasterizer is approved.

## Required Context

- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/backends/matplotlib.md`
- `adr/ADR-0029-mesh-texture2d-unlit.md`

## Deliverables

- Ensure Matplotlib does not advertise `meshvisual.material.texture2d_unlit.v1`.
- Add renderer/planner diagnostics for `MeshVisual.shading="texture2d_unlit"`.
- Add tests proving textures are not silently dropped or approximated as face colors.

## Acceptance

- Textured meshes fail with `meshvisual_material_texture2d_unlit_unsupported` on Matplotlib.
- Existing untextured mesh tests remain unchanged.

## Stop Conditions

- Stop before implementing approximate texture rendering with face colors.
- Stop before adding a CPU texture rasterizer without a separate approved mission.
