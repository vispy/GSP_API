# M022 - Matplotlib scoped query routing

## Goal

Implement the bounded Matplotlib/reference scoped query router for `data`, `guides`, and
`all-rendered`.

## State

Completed.

## Required reading

- `.agent/consultations/P004-response.md`
- `adr/ADR-0006-unified-query-scopes.md`
- `spec/query.md`
- `src/gsp_matplotlib/protocol_query.py`
- `src/gsp_matplotlib/guide_query.py`
- `tests/test_matplotlib_protocol_query.py`
- `tests/test_matplotlib_guide_query.py`

## Expected tasks

- Add scoped query router.
- Extend data visual query helper to support `hit_policy=all`.
- Extend guide query helper to support `hit_policy=all`.
- Merge data and guide hits by bounded reference `z_order`.
- Add tests for data-only, guides-only, all-rendered frontmost, all-rendered all-hits, and
  unsupported prerequisites.

## Allowed paths

- `src/gsp_matplotlib/**`
- `tests/**`
- `spec/query.md`
- `.agent/**`

## Forbidden paths

- Datoviz runtime query support.
- Broad scene planner implementation.
- Full native text/layout hit testing.
- Pixel-perfect rendered picking.

## Acceptance criteria

- Scoped Matplotlib query tests pass.
- Existing data and guide query tests remain compatible.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `gsp_matplotlib.scoped_query`, `hit_policy=all` support in
data and guide query helpers, spec notes, and scoped query tests.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 124 passed, 1 skipped.

## Stop conditions

Stop before Datoviz query implementation or broader native text/layout hit testing.
