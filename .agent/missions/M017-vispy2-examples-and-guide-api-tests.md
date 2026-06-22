# M017 - VisPy2 examples and guide API tests

## Goal

Add runnable examples and tests for the VisPy2 scatter/image/limits/labels/title/ticks/grid guide
API surface.

## State

Completed.

## Required reading

- `spec/vispy2/api.md`
- `src/vispy2/protocol.py`
- `tests/test_vispy2_protocol_mvp.py`
- `examples/vispy2_protocol_scatter.py`
- `examples/vispy2_protocol_imshow.py`
- `examples/vispy2_protocol_point_over_image.py`

## Expected tasks

- Add a focused VisPy2 protocol guide example.
- Register the example in `examples/README.md`.
- Add tests that run the VisPy2 protocol examples.
- Assert labels, title, limits, explicit ticks, grid intent, and data-visual stream invariants.

## Allowed paths

- `examples/**`
- `tests/**`
- `.agent/**`

## Forbidden paths

- Backend-provider implementation details in the public VisPy2 API.
- General Matplotlib compatibility beyond the bounded guide API names.
- Query-scope architecture.
- Adding guide-generated primitives to the user visual stream.

## Acceptance criteria

- Runnable examples cover scatter, image, limits, labels, title, ticks, and grid.
- Example tests pass under the Matplotlib reference path.
- `Figure.visuals()` remains data visuals only.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `examples/vispy2_protocol_guides.py`, documented it in the
examples README, and extended VisPy2 protocol tests to run the examples and assert semantic guide
state.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 105 passed, 1 skipped.

## Stop conditions

Stop if examples or tests require broad query-scope decisions, backend-provider details in the
public API, or generated guide primitives in `Figure.visuals()`.
