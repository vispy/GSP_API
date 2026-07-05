# M228 - S050 Datoviz Texture2D runtime semantics proof

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Attempt a narrow public-API Datoviz runtime proof for the S050 `texture2d_unlit` blockers left by
M220, without advertising renderer capabilities.

## Required Context

- `.agent/S050_DATOVIZ_TEXTURE2D_PUBLIC_API_FEASIBILITY.md`
- `.agent/decisions/S050_texture2d_unlit_contracts.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/renderer/datoviz_renderer_mesh.py`

## Deliverables

- Build the smallest public Datoviz retained-scene textured-mesh smoke or probe that uses only
  `dvz_mesh`, public mesh `texcoords`, public indexed mesh upload, and public RGBA8 sampled-field or
  texture binding APIs.
- Record durable evidence for nearest/clamp/no-mipmap sampler behavior, top-row/high-v texture
  origin, unmanaged numeric RGBA behavior, and exact unlit base-color multiplication.
- If evidence passes, update Mission Control with whether M222 can move from blocked to ready; do
  not implement capability advertisement in this mission.
- If evidence fails or cannot be collected with public APIs, record the exact blocker and keep M222
  blocked.

## Acceptance

- A `.agent/` evidence note states pass/fail/blocked for each M220 blocker.
- Any generated runtime artifacts live under `artifacts/visual_qa/s050/`.
- No private Datoviz APIs, sibling Datoviz checkout edits, or GSP capability advertisements are
  introduced.

## Stop Conditions

- Stop before using private Vulkan state, private shader slots, native texture handles, or sibling
  Datoviz source edits.
- Stop before promoting `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, or
  `meshvisual.material.texture2d_unlit.v1`.
- Stop if Datoviz crashes before producing inspectable evidence; record the crash instead.

## Result

Completed locally.

Added `.agent/S050_DATOVIZ_TEXTURE2D_RUNTIME_SEMANTICS_PROOF.md` and artifacts under
`artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/`.

The active Datoviz v0.4-dev binding no longer exposes `dvz_visual_set_texture_rgba8`, but the public
sampled-field mesh texture path can upload, bind, and render with `DVZ_COLOR_ROLE_SRGB_COLOR` when
explicit normals are supplied. Strict S050 promotion remains blocked: `DVZ_COLOR_ROLE_DATA` crashes
the public path, high-v/top-row origin is inverted relative to S050 without adaptation, center/edge
samples show non-nearest or blended behavior, output values are not exact unmanaged byte-normalized
multiplication, and successful probes still hit a Vulkan validation abort during process teardown
after artifacts are written.

No private Datoviz APIs, sibling Datoviz edits, or GSP capability advertisements were introduced.
