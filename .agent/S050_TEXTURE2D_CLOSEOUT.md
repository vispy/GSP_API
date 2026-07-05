# S050 Texture2D closeout

Date: 2026-07-04

Mission: M225 - S050 Texture2D closeout

## Summary

The S050 Texture2D material thread is complete for protocol validation, fixture metadata,
Matplotlib unsupported policy, VisPy2 producer support, and documentation/capability posture.

No renderer advertises `meshvisual.material.texture2d_unlit.v1`.

## Implemented

Protocol:

- `Texture2D` and `Texture2DFormat` resource models;
- `validate_texture2d_resources()`;
- `MeshShading.TEXTURE2D_UNLIT`;
- `MeshUVMode`;
- `MeshVisual.texture2d_id`, `uv_mode`, and `uvs`;
- `validate_mesh_visual_texture2d_unlit()`;
- exported capability constants:
  - `texture2d.rgba8.v1`;
  - `meshvisual.uv.vertex2d.v1`;
  - `meshvisual.material.texture2d_unlit.v1`;
  - `vispy2.producer.mesh.texture2d_unlit.v1`.

Fixtures and QA metadata:

- S050 Texture2D visual-QA cases for UV orientation, checker/clamp, color multiplication plus seam,
  opaque DATA-space View3D metadata, and alpha diagnostics;
- scene artifact serialization for `Texture2D` resources and mesh UV fields;
- negative fixture metadata for invalid resources, missing/unknown texture ids, invalid UVs,
  unsupported sampler/color-space requests, and unsupported renderer claims;
- visual-QA Matplotlib and Datoviz texture rows report structured unsupported diagnostics.

Matplotlib:

- direct `render_mesh_visual()` rejects `texture2d_unlit` with
  `meshvisual_material_texture2d_unlit_unsupported`;
- no `PolyCollection` fallback silently drops texture fields;
- no CPU textured-triangle rasterizer was added.

Datoviz:

- M220 found public v0.4-dev candidate symbols for future implementation:
  `dvz_mesh`, mesh `"texcoords"` upload, indexed mesh upload, RGBA8 sampled fields,
  `dvz_visual_set_field(..., "texture", field)`, and `dvz_visual_set_texture_rgba8()`;
- M222 remains blocked because public evidence does not yet prove mesh nearest/clamp/no-mipmap
  sampling, texture origin, unmanaged numeric RGBA, or exact multiplicative unlit output.

VisPy2:

- `Axes.mesh(..., texture=None, uvs=None)` emits canonical S050 protocol payloads only when both
  `texture` and `uvs` are supplied;
- `Figure.texture_resources()` exposes emitted `Texture2D` resources;
- exactly one of `texture` or `uvs` fails without appending visuals or resources;
- `texture` is strict `uint8 (H,W,4)`;
- `uvs` are finite `(N,2)`;
- non-default `shading` with `texture` is rejected;
- renderers still diagnose unsupported textured meshes separately.

Docs:

- `spec/backend_capabilities_visuals.md` now distinguishes protocol validation, Matplotlib
  unsupported posture, Datoviz blocked posture, and VisPy2 producer support;
- `spec/vispy2/api.md`, `spec/backends/datoviz.md`, `spec/backends/matplotlib.md`, and
  `examples/README.md` were aligned with S050 limits.

## Evidence

Relevant commits:

```text
70fbcce Accept Texture2D unlit mesh protocol direction
62cd935 Add Texture2D unlit mesh protocol validation
f358513 Add S050 Texture2D fixture metadata
15fe8d5 Audit Datoviz Texture2D public API feasibility
dbce68b Reject Texture2D meshes in Matplotlib renderer
3863d83 Add VisPy2 Texture2D mesh producer
23734c6 Document S050 Texture2D capability posture
```

Focused validation passed:

```bash
uv run python -m pytest tests/test_vispy2_protocol_mvp.py \
  tests/test_matplotlib_protocol_slice.py::test_render_mesh_visual_rejects_texture2d_unlit_without_dropping_texture_fields \
  tests/test_mesh_visual_protocol.py \
  tests/test_visual_qa_harness.py::test_s050_texture2d_cases_record_probe_metadata_and_unsupported_backend

uv run ruff check src/vispy2/protocol.py tests/test_vispy2_protocol_mvp.py \
  src/gsp_matplotlib/protocol_renderer.py tests/test_matplotlib_protocol_slice.py

uv run mypy src/vispy2/protocol.py src/gsp_matplotlib/protocol_renderer.py

uv run python -m pytest tests/test_import_surface.py tests/test_vispy2_protocol_mvp.py \
  tests/test_matplotlib_protocol_slice.py::test_render_mesh_visual_rejects_texture2d_unlit_without_dropping_texture_fields \
  tests/test_visual_qa_harness.py::test_s050_texture2d_cases_record_probe_metadata_and_unsupported_backend
```

Results:

- 64 focused tests passed for the implementation surface;
- 46 focused import/VisPy2/docs-adjacent tests passed with 1 skipped;
- Ruff passed;
- mypy passed for touched producer/renderer modules;
- `.agent/status.json` is valid JSON;
- `git diff --check` passed.

## Remaining Blockers

Blocked S050 missions:

| Mission | Blocker |
|---|---|
| M211 - culling and alpha semantics consultation | Completed after P032; projected-NDC face culling is accepted, strict non-opaque alpha remains deferred. |
| M212 - 3D query payload expansion consultation | Requires ChatGPT Pro consultation output before expanded UV/texel/material/3D query payloads are accepted. |
| M222 - Datoviz Texture2D capability advertisement | Requires M220 sampler, origin, unmanaged RGBA, and exact unlit multiplication proof before implementation or promotion. |
| M226 - projected-NDC face culling protocol fixtures | Ready follow-up for the accepted P032 boundary; renderer capability promotion remains gated on fixtures. |

## Recommendation

Do not launch renderer promotion work next.

After P032, the next implementation branch is M226 for projected-NDC face-culling protocol fixtures
and diagnostics. M212 remains the next ChatGPT Pro consultation track for expanded 3D query
payloads. M222 should stay blocked until Datoviz public API/runtime evidence proves the M220 fixture
requirements.
