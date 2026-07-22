# M222 - S050 Datoviz Texture2D capability advertisement

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed on 2026-07-22 against post-RC2 Datoviz `v0.4-dev`.

## Summary

Advertise Datoviz S050 textured mesh capabilities only if public API evidence and fixtures prove
strict semantics.

## Required Context

- M220 evidence note
- sibling Datoviz `spec/scene/integration/GSP_TEXTURE2D_MESH_PLAN.md`
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

## Resolution

Datoviz commit `be7f2a80354c25e85bab88c85f5ea7340975b569` supplies the public field-slot
sampling descriptor and setter. GSP commit `e2008b1` implements capability-gated RGBA8 upload,
per-vertex UV binding, top-row/high-v origin adaptation, nearest min/mag selection, clamp/no-mipmap
defaults, linear-color role, vertex-color multiplication, and the unlit material model.

The focused S050 review rendered all five Texture2D cases, including retained DATA-space View3D and
alpha diagnostics, without a Datoviz unsupported or crashed row. `tools/run_datoviz_texture2d_checkpoint.sh`
now preserves exact provenance and repeats that evidence. Builds without the field-slot API fail
current-binding preflight or omit the capability through the conservative snapshot translator.

Linear filtering remains outside this completed nearest-only mission and is tracked separately by
P036.
