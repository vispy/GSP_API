# M020 - Typed query capability schema

## Goal

Add the typed query capability schema for S015 `data`, `guides`, and `all-rendered` query planning.

## State

Completed.

## Required reading

- `.agent/consultations/P004-response.md`
- `adr/ADR-0006-unified-query-scopes.md`
- `spec/capabilities.md`
- `src/gsp/protocol/capabilities.py`
- `tests/test_protocol_spine.py`

## Expected tasks

- Add `QueryOrderingGuarantee`.
- Add `QueryTargetKind`.
- Add `QueryTargetCapability`.
- Add `QueryScopeCapability`.
- Add `CapabilitySnapshot.query_capabilities`.
- Add helpers for typed query-scope support and request adaptation.
- Keep `query_modes` compatibility behavior intact.
- Add focused tests.

## Allowed paths

- `src/gsp/protocol/**`
- `tests/**`
- `spec/capabilities.md`
- `.agent/**`

## Forbidden paths

- Matplotlib scoped query execution routing.
- Axis-provider scene/provider composition planner.
- Datoviz runtime query implementation.
- Removing `query_modes`.

## Acceptance criteria

- Typed capabilities express scope, targets, payloads, extension payloads, hit policies, and ordering.
- `all-rendered` must be explicitly advertised.
- `all-rendered` rejects without global ordering.
- Unsupported payloads and extension payloads reject planning.
- Full test suite passes.

## Result

Completed by local-main-codex. Added typed query capability dataclasses, request adaptation helpers,
exports, spec notes, and focused protocol tests.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 113 passed, 1 skipped.

## Stop conditions

Stop before scoped backend query routing, query planner composition, or Datoviz runtime query
support.
