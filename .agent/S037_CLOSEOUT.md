# S037 Closeout - View3D Navigation and Datoviz Binding Evidence

Status: completed.

## Completed Scope

S037 accepted P021 and completed the implementation work that is evidence-backed today:

- archived the P021 ChatGPT Pro answer as `.agent/consultations/P021-response.md`;
- accepted ADR-0024 and `.agent/decisions/S037_view3d_navigation_datoviz_contracts.md`;
- added `spec/view3d_navigation.md`;
- added protocol-only `View3DNavigationAction` payloads, `View3DNavigationResult`, diagnostics,
  reducers, and snapshot/revision freshness checks;
- added Matplotlib live review navigation for `View3D` examples using canonical S037 actions;
- probed Datoviz v0.4 camera/View3D binding evidence.

## Backend Status

| Backend | S037 status | Notes |
|---|---|---|
| Matplotlib | supported reference/adapted | Protocol reducers are backend-neutral. Live review supports left-drag orbit, right/middle-drag pan, wheel zoom, and `r` reset. Rendering remains adapted 2D projection/far-to-near face sorting. |
| Datoviz v0.4 | unsupported for public `(N, 3)` View3D meshes | Camera/depth symbols exist, but Python-visible `DvzCameraView` and `DvzCameraDesc` fields/factories are not bindable and S036 x/y orthographic bounds parity is unproven. |
| VisPy2 producer API | deferred | May add ergonomic wrappers later, but S037 did not add VisPy2 navigation helpers. |

## Validation Summary

Validation completed across S037 missions:

```bash
uv run pytest tests/test_view3d_protocol.py tests/test_import_surface.py tests/test_navigation_protocol.py -q
uv run pytest tests/test_review_runner_interactive.py -q
uv run pytest tests/test_view3d_protocol.py tests/test_review_runner_interactive.py tests/test_import_surface.py -q
uv run ruff check src/gsp/protocol/view3d.py src/gsp/protocol/__init__.py tests/test_view3d_protocol.py
uv run ruff check examples/review/_review_runner.py tests/test_review_runner_interactive.py
uv run mypy src/gsp/protocol/view3d.py src/gsp/protocol/__init__.py --strict --show-error-codes
tools/compare-review-examples examples/review/07_view3d_cube.py --offscreen
tools/probe_datoviz_view3d.py
```

`tools/probe_datoviz_view3d.py` reports `status: not-ready` and exits nonzero until the Datoviz
binding evidence is sufficient; that is the expected S037 outcome.

## Deferred Work

- Datoviz static `View3D` mesh binding.
- Datoviz `query.view3d.ray_readback.v1` parity.
- Public material, light, texture, UV, sampler, culling, perspective, 3D picking, and strict
  fragment-depth/clipping semantics.
- VisPy2 ergonomic View3D navigation helpers.

## Recommendation

Do not claim Datoviz public 3D support in release notes yet. The next actionable work is either:

- an upstream Datoviz fix exposing safe camera ctypes fields/factories plus a public camera-level
  explicit orthographic-bounds API, as detailed in `.agent/consultations/P022-response.md`; or
- S038 material/light pre-design if 3D visual appearance should be expanded independent of Datoviz
  binding.
