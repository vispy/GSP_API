# M014 - Reference guide query support

## Goal

Add bounded reference guide query behavior for semantic axis-guide contributions, while preserving
the broader query-scope consultation gate for future `data`, `guides`, and `all-rendered` semantics.

## State

Completed.

## Required reading

- `.agent/consultations/P003-response.md`
- `src/gsp/protocol/query.py`
- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/ticks.py`
- `src/gsp_matplotlib/protocol_query.py`
- `src/gsp_matplotlib/guides.py`
- `tests/test_matplotlib_protocol_query.py`
- `tests/test_matplotlib_guides.py`

## Expected tasks

- Add a small guide-query payload model.
- Add a reference helper that queries semantic axis guide contributions using GSP-resolved ticks.
- Return `unsupported`, not `miss`, when a provider renders guides but does not support guide queries.
- Keep general query scope semantics out of this mission.
- Add deterministic tests for guide hits, guide misses, and unsupported guide query behavior.

## Allowed paths

- `src/gsp/protocol/**`
- `src/gsp_matplotlib/**`
- `tests/**`
- `spec/**`, only for brief notes
- `.agent/**`
- `STATUS.md`

## Forbidden paths

- General `data` / `guides` / `all-rendered` query scope hardening.
- Datoviz query lifecycle implementation.
- Pixel/glyph hit testing.
- Backend-native text/tick queries as protocol authority.

## Acceptance criteria

- Guide queries can hit deterministic tick/spine contributions using GSP semantics.
- Guide misses are distinct from unsupported guide-query capability.
- Unsupported guide query helpers return `QueryStatus.UNSUPPORTED`.
- Existing visual query tests still pass.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `GuideQueryPayload`, `GUIDE_QUERY_PAYLOAD_KIND`,
`src/gsp_matplotlib/guide_query.py`, and `tests/test_matplotlib_guide_query.py`.

This mission intentionally did not implement the broader `data` / `guides` / `all-rendered` query
scope model. That remains gated on the planned query-scope consultation.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 93 passed, 1 skipped.

## Stop conditions

Stop if implementing guide query requires broad query-scope precedence/payload decisions or exact
text/glyph hit testing. Those belong to the planned ChatGPT Pro query-scope consultation.
