# M088-S025 - S025 VisPy2 mesh producer API and examples

## Mission

M088

## Goal

Expose a minimal VisPy2 producer for accepted mesh scenes without backend-specific calls.

## Status

Completed.

## Deliverables

- Add high-level mesh creation API according to M083.
- Add examples that emit formal GSP protocol scenes.
- Keep advanced materials/shading deferred unless accepted.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop if the API starts exposing Datoviz draw calls or private renderer knobs.

## Completion Notes

- Added `Axes.mesh()` and top-level `vispy2.mesh()` producer APIs for accepted `MeshVisual`
  semantics: inline indexed triangles, RGBA color, optional explicit color mode, coordinate space,
  and visual order.
- Routed VisPy2 Matplotlib rendering through the existing protocol `render_mesh_visual()` reference
  path.
- Added `examples/vispy2_protocol_mesh.py` and focused VisPy2 producer tests.
- Updated `spec/vispy2/api.md` with the bounded mesh producer surface and deferred material/backend
  features.
- Validation: `uv run pytest tests/test_vispy2_protocol_mvp.py tests/test_mesh_visual_protocol.py
  tests/test_matplotlib_protocol_slice.py`; `uv run ruff check src/vispy2/protocol.py
  src/vispy2/__init__.py tests/test_vispy2_protocol_mvp.py examples/vispy2_protocol_mesh.py`;
  `uv run ruff format --check src/vispy2/protocol.py src/vispy2/__init__.py
  tests/test_vispy2_protocol_mvp.py examples/vispy2_protocol_mesh.py`; `git diff --check`.
