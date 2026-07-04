# M220 - S050 Datoviz Texture2D public API feasibility

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Draft.

## Summary

Determine whether the active Datoviz v0.4 public API can support strict S050 textured mesh
semantics.

## Required Context

- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/backends/datoviz.md`
- `spec/datoviz_v04_api_boundary.md`
- `.agent/decisions/S050_texture2d_unlit_contracts.md`

## Deliverables

- Audit generated bindings and runtime symbols for RGBA8 texture upload, per-vertex UV binding,
  nearest/clamp/no-mipmap sampling, image-origin behavior, and unmanaged numeric color behavior.
- Produce a durable `.agent/` evidence note with exact public symbols and blockers.
- Do not promote GSP Datoviz texture capabilities in this mission.

## Acceptance

- The report says clearly whether strict S050 implementation is viable with public Datoviz APIs,
  requires upstream Datoviz API work, or is blocked by a GSP semantic question.

## Stop Conditions

- Stop before using private Vulkan state, private shader slots, private mesh ids, or sibling
  Datoviz source edits.
- Stop before advertising `meshvisual.material.texture2d_unlit.v1`.
