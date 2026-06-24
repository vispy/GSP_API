# M092-S026 - S026 color mapping protocol dataclasses and validation

## Mission

M092

## Goal

Implement accepted S026 protocol dataclasses, enums, and validation after M091.

## Status

Completed.

## Deliverables

- Protocol objects/enums for the accepted color mapping/scalar/colorbar model.
- Validation tests for shapes, dtypes, ranges, defaults, and rejected/deferred semantics.

## Acceptance

- M091 is completed first.
- Focused tests cover accepted validation and key negative cases.
- Mission Control status is updated before closeout.

## Stop Conditions

- Stop if implementation needs semantics not accepted by M091.

## Completion Notes

- Added `gsp.protocol.color` with S026 dataclasses/enums for `ColorScale`, `ColorMapRef`,
  `LinearNormalize`, `ScalarColorEncoding`, and `ColorbarGuide`.
- Exported S026 protocol objects from `gsp.protocol`.
- Added optional scalar color encoding fields to `ImageVisual`, `PointVisual`, `MarkerVisual`, and
  capability-gated `MeshVisual.face_color_encoding` while preserving existing RGBA behavior.
- Added focused validation tests for accepted and rejected S026 cases.
- Validation: `uv run pytest tests/test_color_mapping_protocol.py tests/test_mesh_visual_protocol.py
  tests/test_vispy2_protocol_mvp.py tests/test_matplotlib_protocol_slice.py
  tests/test_matplotlib_protocol_query.py tests/test_protocol_spine.py`; `uv run ruff check
  src/gsp/protocol/color.py src/gsp/protocol/visuals.py src/gsp/protocol/__init__.py
  tests/test_color_mapping_protocol.py`; `uv run ruff format --check src/gsp/protocol/color.py
  src/gsp/protocol/visuals.py src/gsp/protocol/__init__.py tests/test_color_mapping_protocol.py`;
  `git diff --check`.
