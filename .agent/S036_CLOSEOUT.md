# S036 Closeout - Static View3D, Orthographic Projection, and 3D Mesh Baseline

Status: completed.

## Completed Scope

S036 adds the bounded public 3D baseline accepted from P020:

- `Camera3D`, `OrthographicProjection3D`, and static `View3D`;
- deterministic View3D projection snapshots;
- DATA `(N, 3)` `MeshVisual` projection through `View3D`;
- NDC `(N, 3)` `MeshVisual` interpretation as panel NDC3;
- Matplotlib reference rendering for projected 3D meshes;
- adapted opaque face-depth ordering fixture for non-intersecting triangles;
- S036 query ray readback with `gsp.view3d-query@0.1`;
- explicit deferral diagnostics for 3D mesh picking, translucent strict-depth cases, and Datoviz
  retained View3D support.

## Backend Status

| Backend | S036 status | Notes |
|---|---|---|
| Matplotlib | reference/adapted | Strict validation, projection math, snapshot identity, and ray readback. 3D mesh rendering is projected into 2D with adapted face ordering, not strict fragment-depth support. |
| Datoviz v0.4 | unsupported for public `(N, 3)` MeshVisual | The retained adapter reports `mesh3d_coordinate_space_unsupported` until a public View3D camera binding exists. |
| VisPy2 producer API | deferred | May add ergonomic constructors later, but S036 does not expose public 3D navigation or engine objects. |

## Validation Summary

Focused validation completed across the S036 missions:

```bash
uv run pytest tests/test_view3d_protocol.py tests/test_mesh_visual_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_matplotlib_protocol_query.py tests/test_datoviz_v04_protocol_renderer.py::test_add_mesh_visual_accepts_default_data_domain_and_rejects_3d_with_diagnostic tests/test_import_surface.py -q
uv run ruff check src/gsp/protocol/view3d.py src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_renderer.py src/gsp_matplotlib/protocol_query.py src/gsp_datoviz/protocol_renderer.py tests/test_view3d_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_matplotlib_protocol_query.py tests/test_datoviz_v04_protocol_renderer.py
uv run mypy src/gsp/protocol/ src/gsp_matplotlib/protocol_renderer.py src/gsp_matplotlib/protocol_query.py src/gsp_datoviz/protocol_renderer.py --strict --show-error-codes
tools/compare-review-examples examples/review/07_view3d_cube.py examples/review/08_view3d_terrain.py examples/review/09_view3d_ndc_depth.py --offscreen
uv run python examples/review/s036_alpha_not_strict_negative.py
```

## Deferred Work

- Public View3D navigation and interaction.
- Perspective projection.
- Strict GPU/fragment-depth conformance for 3D meshes.
- 3D mesh face picking and barycentric/depth readback.
- Materials, lights, scene graphs, model loaders, and backend-native controller exposure.

## S037 Recommendation

Do not open public `View3DNavigationController` directly from S036. S037 should start with a
ChatGPT Pro consultation for the public 3D navigation contract and its relationship to static
`View3D` snapshots, query freshness, and backend-retained camera state. The first implementation
stage should remain adapter-only until that contract is accepted.
