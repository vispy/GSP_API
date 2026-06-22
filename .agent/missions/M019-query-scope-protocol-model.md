# M019 - Query scope protocol model

## Goal

Implement the first S015 protocol dataclass update for unified query scopes and hit-list payloads.

## State

Completed.

## Required reading

- `.agent/consultations/P004-unified-query-scopes-capability-semantics.md`
- `.agent/consultations/P004-response.md`
- `spec/query.md`
- `src/gsp/protocol/query.py`
- `tests/test_matplotlib_protocol_query.py`

## Expected tasks

- Add `QueryScope`.
- Add `QueryContributionKind`.
- Add `QueryHit`.
- Add `QueryRequest.scope`.
- Add `QueryRequest.requested_extension_payload_kinds`.
- Add `QueryResult.hits`.
- Preserve top-level single-hit compatibility fields.
- Add focused protocol/query tests.

## Allowed paths

- `src/gsp/protocol/**`
- `tests/**`
- `spec/query.md`
- `adr/**`
- `.agent/**`

## Forbidden paths

- Typed query capability schema.
- Query planner composition.
- Matplotlib `data`/`guides`/`all-rendered` routing.
- Datoviz runtime query implementation.

## Acceptance criteria

- Existing data-query behavior defaults to `scope=data`.
- Existing top-level result payload fields still work.
- New-style hit-list results mirror `hits[0]` to compatibility fields.
- Non-hit results cannot include hit payload fields.
- Full test suite passes.

## Result

Completed by local-main-codex. Added scoped query protocol dataclasses, compatibility mirroring,
ADR/spec updates, and focused tests.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 109 passed, 1 skipped.

## Stop conditions

Stop before typed capability schema, scoped backend routing, or Datoviz runtime query support.
