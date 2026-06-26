# M107-S028 - Reversed View2D tick and guide reference behavior

## Mission

M107

## Goal

Implement reference tick/grid rendering behavior for reversed `View2D` limits after M106 defines
the exact semantics.

## Status

Completed.

## Deliverables

- Tick resolver support for reversed finite domains.
- Matplotlib guide rendering tests for reversed x/y limits.
- Grid visibility/placement checks under reversed limits.

## Acceptance

- Focused tests pass.
- No Matplotlib native locator authority leaks into GSP semantics.

## Result

- Reversed finite domains are accepted by the deterministic tick resolver.
- Auto ticks resolve over sorted numeric bounds; rendering preserves original `View2D` orientation.
- Explicit ticks and labels are preserved exactly.
- Matplotlib guide rendering now applies `View2D` x/y limits.
- `uv run pytest tests/test_tick_resolver.py tests/test_matplotlib_guides.py -q`: 17 passed.
- `uv run pytest tests/test_vispy2_protocol_mvp.py tests/test_matplotlib_protocol_slice.py tests/test_matplotlib_scoped_query.py tests/test_matplotlib_guide_query.py -q`: 76 passed.
