# M015 - Guide conformance fixtures

## Goal

Add deterministic conformance fixtures for the completed S012 guide/tick/render/query reference
slice.

## State

Completed.

## Required reading

- `.agent/consultations/P003-response.md`
- `fixtures/conformance/baseline.py`
- `fixtures/conformance/README.md`
- `src/gsp/protocol/guides.py`
- `src/gsp/protocol/ticks.py`
- `src/gsp_matplotlib/guides.py`
- `src/gsp_matplotlib/guide_query.py`
- `tests/test_conformance_baseline.py`

## Expected tasks

- Add guide/tick/title conformance fixtures.
- Cover explicit ticks, auto ticks, guide labels, grid visibility, titles, guide-query hits, guide
  misses, and unsupported guide-query results.
- Keep fixtures Python/in-process like the existing v0.1 baseline.
- Do not add broad `data` / `guides` / `all-rendered` query-scope semantics.

## Allowed paths

- `fixtures/conformance/**`
- `tests/**`
- `.agent/**`
- `STATUS.md`

## Forbidden paths

- General query scope architecture.
- Datoviz query implementation.
- JSON/base64 replay fixtures.
- Backend-native text/glyph picking.

## Acceptance criteria

- Fixture exports include a canonical guide scene.
- Conformance tests lock semantic guide intent and Matplotlib reference guide rendering.
- Guide query conformance distinguishes hit, miss, and unsupported statuses.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `GuideConformanceScene`, `guide_scene()`, exported the guide
fixture, extended the reference capability fixture with `guide-query`, and added conformance tests
for semantic guide intent, Matplotlib guide rendering, guide-query payloads, misses, and unsupported
providers.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 97 passed, 1 skipped.

## Stop conditions

Stop if the fixture requires broad query-scope precedence decisions, rendered pixel goldens, or
backend-native text/glyph hit testing.
