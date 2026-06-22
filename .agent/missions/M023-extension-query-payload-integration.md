# M023 - Extension query payload integration

## Goal

Integrate typed extension query payloads with scoped Matplotlib/reference query routing.

## State

Completed.

## Required reading

- `.agent/consultations/P004-response.md`
- `adr/ADR-0006-unified-query-scopes.md`
- `spec/query.md`
- `src/gsp_matplotlib/scoped_query.py`
- `src/gsp_matplotlib/tiled_image.py`
- `tests/test_extension_data_sources.py`
- `tests/test_matplotlib_scoped_query.py`

## Expected tasks

- Add a scoped query extension entry surface.
- Route built-in tiled-image query payloads through `data` scoped queries.
- Include extension hits in `all-rendered` bounded render-order merges.
- Reject unsupported requested extension payload kinds.
- Add focused scoped query tests and spec notes.

## Allowed paths

- `src/gsp/protocol/**`
- `src/gsp_matplotlib/**`
- `tests/**`
- `spec/query.md`
- `.agent/**`

## Forbidden paths

- Datoviz runtime query implementation.
- Remote data fetching, credentials, cache eviction, prefetch, or retry semantics.
- Dynamic extension loading.
- Broad scene planner implementation.

## Acceptance criteria

- Scoped Matplotlib tiled-image query tests pass.
- Existing direct tiled-image query tests remain compatible.
- Existing protocol capability tests remain compatible.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `QueryExtensionEntry`, a protocol constant for the built-in
tiled-image query payload kind, scoped tiled-image payload tests, and spec notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 128 passed, 1 skipped.

## Stop conditions

Stop before Datoviz runtime query implementation, dynamic extension loading, or broader virtual
data-source hardening.
