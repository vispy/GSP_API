# M021 - Query planner and axis-provider composition

## Goal

Add the bounded S015 planner composition layer that intersects typed query capabilities with selected
axis-provider query capabilities.

## State

Completed.

## Required reading

- `.agent/consultations/P004-response.md`
- `adr/ADR-0006-unified-query-scopes.md`
- `spec/capabilities.md`
- `src/gsp/protocol/capabilities.py`
- `tests/test_protocol_spine.py`

## Expected tasks

- Add scene/provider query planning context.
- Map `AxisQueryScopeRequirement` to `QueryScope`.
- Add a scene-aware query adaptation helper.
- Require guide-query provider support for `guides`.
- Require guide-query provider support for `all-rendered` when guides are visible.
- Require text-query provider support when text hit testing is requested.
- Add focused tests.

## Allowed paths

- `src/gsp/protocol/**`
- `tests/**`
- `spec/capabilities.md`
- `.agent/**`

## Forbidden paths

- Matplotlib scoped query execution routing.
- Broad scene planner implementation.
- Datoviz runtime query support.
- Guessing guide misses for non-queryable providers.

## Acceptance criteria

- Data queries still plan with visible non-queryable guides.
- Guide queries reject non-queryable providers.
- All-rendered queries reject visible non-queryable guides.
- Text-guide query planning rejects providers without text-query support.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `QueryPlanningContext`,
`query_scope_for_axis_requirement()`, scene-aware `CapabilitySnapshot.adapt_query_request_for_scene()`,
spec notes, exports, and focused tests.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 119 passed, 1 skipped.

## Stop conditions

Stop before scoped backend query routing or Datoviz runtime query support.
