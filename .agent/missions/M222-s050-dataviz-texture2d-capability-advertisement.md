# M222 - S050 Datoviz Texture2D capability advertisement

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Blocked by M220.

## Summary

Advertise Datoviz S050 textured mesh capabilities only if public API evidence and fixtures prove
strict semantics.

## Required Context

- M220 evidence note
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/backends/datoviz.md`

## Deliverables

- Implement Datoviz lowering for canonical RGBA8 textures and per-vertex UVs if M220 proves public
  API viability.
- Gate `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and
  `meshvisual.material.texture2d_unlit.v1` on fixture-backed support.
- Preserve strict opaque-depth combination only for retained DATA-space View3D and conservatively
  opaque final alpha.

## Acceptance

- S050 positive fixtures pass where capabilities are advertised.
- Unsupported Datoviz builds return structured diagnostics.

## Stop Conditions

- Stop if the implementation needs private Datoviz APIs, unsupported sampler behavior, alpha/culling
  expansion, or mesh-picking payload expansion.

## Blocker

M220 found public Datoviz upload and mesh texture binding symbols, but strict capability
advertisement remains blocked pending fixture evidence for mesh nearest/clamp/no-mipmap sampler
behavior, texture-origin behavior, unmanaged numeric RGBA behavior, and exact unlit
multiplication. Do not implement or advertise Datoviz Texture2D renderer capabilities until those
blockers are resolved.
