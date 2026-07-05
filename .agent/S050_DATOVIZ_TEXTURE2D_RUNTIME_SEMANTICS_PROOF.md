# S050 Datoviz Texture2D runtime semantics proof

Date: 2026-07-05

Mission: M228 - S050 Datoviz Texture2D runtime semantics proof

## Decision

Do not unblock M222. The active Datoviz v0.4-dev public API still does not prove strict S050
`texture2d_unlit` semantics.

The public sampled-field mesh texture path can upload, bind, and render a textured mesh only with
`DVZ_COLOR_ROLE_SRGB_COLOR` and explicit normals. That is not enough for GSP to advertise
`texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, or
`meshvisual.material.texture2d_unlit.v1` for Datoviz.

## Evidence Source

GSP checkout:

- path: `/Users/cyrille/GIT/Viz/GSP_API`
- branch: `agentic-gsp-vispy2`

Datoviz checkout imported read-only:

- path: `/Users/cyrille/GIT/Viz/datoviz`
- runtime module: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`

No sibling Datoviz files were edited.

## Artifacts

- `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/probe_report.json`
- `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/probe_report_srgb.json`
- `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/probe_report_srgb_normals.json`
- `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/texture2d_sampled_field_quad_srgb.png`
- `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/texture2d_sampled_field_quad_srgb_normals.png`

## Findings

| M220 blocker | Runtime result | Strict S050 status |
|---|---|---|
| Public packed RGBA8 convenience upload | `dvz_visual_set_texture_rgba8` is absent in the active generated binding. | Blocked for that path. |
| Public sampled-field mesh texture binding | `dvz_sampled_field`, `dvz_sampled_field_set_data`, and `dvz_visual_set_field(mesh, "texture", field)` are present; upload and bind returned true with `SRGB_COLOR`. | Feasible but not strict by itself. |
| Unmanaged numeric RGBA | `DVZ_COLOR_ROLE_DATA` for a color sampled field logged `color sampled fields require srgb_color or linear_color role`, returned a null field, then native upload asserted if not guarded. | Failed. No public unmanaged numeric RGBA proof. |
| Required mesh metadata | Texture binding without explicit normals logged `typed textured mesh metadata missing normal/texcoords resource` and rendered fallback magenta. | Requires normals beyond S050 unlit texture fields, or upstream clarification. |
| Top-row/high-v origin | With texcoords mapping high `v` to the top mesh edge, sampled output showed top-left as blue and bottom-left as red for a texture whose row 0 left texel was red and row 1 left texel was blue. | Failed without adapter-side V flip. |
| Nearest/clamp/no-mipmap sampler | Quadrant samples were not exact texel colors; center sample was blended (`[58, 125, 119, 255]`). No public sampler control was found. | Failed/unproven. |
| Exact unlit base-color multiplication | The render with base color `[128, 255, 255, 255]` produced approximate screenshot samples such as `[123, 0, 0, 255]` and `[123, 245, 245, 255]`, not exact unmanaged byte-normalized values. | Failed/unproven. |

## Runtime Sample Summary

The successful SRGB+normal run rendered:

```text
top_left     [24, 24, 246, 255]
top_right    [123, 245, 245, 255]
bottom_left  [123, 0, 0, 255]
bottom_right [0, 245, 0, 255]
center       [58, 125, 119, 255]
```

The output proves a public textured mesh path exists, but also demonstrates that the current default
behavior is not the S050 fixed sampler plus unmanaged numeric RGBA contract.

## Required Upstream Work

Before M222 can become ready, Datoviz needs public retained-scene support or documentation for:

- mesh texture sampler selection or fixed nearest/clamp/no-mipmap semantics;
- unmanaged numeric RGBA texture sampling for mesh textures, or an accepted GSP color-role contract
  different from S050;
- documented texture origin semantics, or public API that lets GSP adapt origin deterministically;
- documented unlit texture color equation and whether explicit normals are required for textured
  meshes.

Private Vulkan state, private shader slots, native texture handles, and sibling Datoviz edits remain
outside the GSP implementation boundary.

## Validation

The proof used one-off child-process Python probes via `uv run python` and wrote durable artifacts
under `artifacts/visual_qa/s050/m228-dataviz-texture2d-runtime/`.

Two native termination hazards were observed:

- the DATA-role sampled-field attempt aborted with a Datoviz assertion after a null field;
- successful offscreen render runs still exited with a Vulkan validation abort during process
  teardown after writing the JSON report and PNG.

Those hazards are part of the evidence and reinforce keeping M222 blocked.
