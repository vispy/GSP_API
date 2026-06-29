# M150 - S035 Matplotlib programmatic navigation reference

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Completed by local-main-codex.

## Summary

Implement a strict reference path for programmatic `View2D` navigation against Matplotlib render and
query behavior.

## Deliverables

- Programmatic navigation action application to Matplotlib protocol scenes.
- Render/query results carrying matching view and layout snapshot identifiers.
- Focused tests for navigation/render/query coherence.
- Explicit unsupported posture for live GUI input if not implemented in this mission.

## Stop Condition

Stop before adding broad GUI event semantics.

## Result

Completed. Added a Matplotlib reference helper for applying S035 programmatic navigation actions to
`View2D`, added `view_snapshot_id` propagation on query requests/results and Matplotlib render
results, and marked Matplotlib as supporting programmatic `interaction.view2d.navigation.v1`.

Validation performed:

- `uv run python -m py_compile src/gsp/protocol/query.py src/gsp_matplotlib/navigation.py src/gsp_matplotlib/protocol_query.py src/gsp_matplotlib/protocol_renderer.py src/gsp_matplotlib/capabilities.py tests/test_matplotlib_protocol_slice.py tests/test_layout_protocol.py`
- `uv run ruff check src/gsp/protocol/query.py src/gsp_matplotlib/navigation.py src/gsp_matplotlib/protocol_query.py src/gsp_matplotlib/protocol_renderer.py src/gsp_matplotlib/capabilities.py tests/test_matplotlib_protocol_slice.py tests/test_layout_protocol.py`
- `uv run pytest tests/test_matplotlib_protocol_slice.py tests/test_matplotlib_protocol_query.py tests/test_layout_protocol.py tests/test_navigation_protocol.py -q`
- `uv run mypy src/gsp/protocol/ src/gsp_matplotlib/ --strict --show-error-codes`
- `uv run pytest tests/ -q` (`455 passed, 3 skipped`)
