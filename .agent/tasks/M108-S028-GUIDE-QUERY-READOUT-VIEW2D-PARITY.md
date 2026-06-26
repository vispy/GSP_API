# M108-S028 - Guide query/readout View2D parity

## Mission

M108

## Goal

Make guide query and readout behavior consume the same deterministic `View2D` state as rendering.

## Status

Completed.

## Deliverables

- Reversed-axis guide query tests.
- Same-snapshot guide/data scoped-query coverage.
- Clear unsupported diagnostics for unavailable guide query behavior.

## Acceptance

- Focused guide-query and scoped-query tests pass.
- Results do not silently adapt unsupported guide behavior.

## Result

- Reversed-axis guide query tests added for auto and explicit ticks.
- Same-snapshot scoped query coverage added for reversed `View2D`.
- Unsupported behavior remains explicit through existing `View2D`-required diagnostics.
- `uv run pytest tests/test_matplotlib_guide_query.py tests/test_matplotlib_scoped_query.py -q`: 19 passed.
- `uv run pytest tests/test_protocol_spine.py tests/test_conformance_matrix.py tests/test_conformance_debug_report.py tests/test_matplotlib_protocol_slice.py -q`: 55 passed, 1 skipped.
