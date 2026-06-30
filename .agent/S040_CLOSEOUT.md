# S040 Closeout

## Result

S040 completed Datoviz strict promotion for the accepted S039 flat Lambert slice.

Accepted backend route:

- Datoviz resolves `flat_lambert` through protocol CPU face colors.
- Native Datoviz lighting/material controls are not used as strict S039 evidence.
- Triangle-expanded upload preserves one constant RGBA per canonical face.
- Datoviz advertises S039 Lambert, face-normal, generated-normal, ambient-light, and
  directional-light capabilities when the View3D path is available.
- Non-opaque Datoviz 3D mesh alpha remains non-strict through `mesh3d_alpha_not_strict`.

## Implemented

- Datoviz adapter validates S039 Lambert before upload.
- CPU Lambert resolver mirrors accepted S039 arithmetic.
- Existing per-face Datoviz mesh payload path is reused for constant face colors.
- Capability snapshot includes S040 capability metadata.
- Focused Datoviz tests cover CPU-resolved colors, triangle expansion, alpha rejection, and
  capability gates.

## Validation

Latest validation during M178:

- `uv run python -m pytest tests/test_datoviz_v04_protocol_renderer.py -q`
- `uv run python -m pytest tests/test_datoviz_v04_protocol_renderer.py tests/test_mesh_visual_protocol.py tests/test_view3d_protocol.py tests/test_matplotlib_protocol_slice.py -q`
- `uv run python -m pytest tests/ -q`
- `uv run ruff check src tests`
- `uv run mypy src/ --strict --show-error-codes`
- backend import smokes for Matplotlib and Datoviz.

## Deferred

- Native Datoviz lighting/material strict proof.
- Vertex normals and smooth Lambert.
- Phong/specular/shininess.
- Textures, UVs, samplers, normal maps, and material resources.
