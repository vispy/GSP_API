# M029 - Datoviz runtime point/image query execution proof

## Goal

Add a bounded Datoviz v0.4 queue/poll query execution wrapper for point/image data queries.

## State

Completed.

## Required reading

- `.agent/tasks/DATOVIZ-V04-QUERY-BINDING.md`
- `.agent/tasks/DATOVIZ-V04-QUERY-PARITY.md`
- `spec/query.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/query.py`
- `src/gsp_datoviz/capabilities.py`
- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/include/datoviz/scene/interaction.h`
- `../datoviz/include/datoviz/scene/types.h`
- `../datoviz/include/datoviz/scene/enums.h`

## Expected tasks

- Add a renderer method that queues a Datoviz panel query and polls one result.
- Decode `DvzQueryResult` through the existing GSP decoder.
- Promote point/image query modes only when the v0.4 query binding is present.
- Add typed data-scope capability for frontmost panel-coordinate requests.
- Add fake-facade tests and skip-clean imported binding smoke.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Guide-scope or all-rendered Datoviz query claims.
- `hit_policy=all` Datoviz query claims.
- Extension query payload claims.
- Live GPU/headless runtime requirements in the local 0.3.5 environment.
- Datoviz repository edits.

## Acceptance criteria

- Fake-facade runtime test proves query request creation, enqueue, poll, decode, and GSP request-id remap.
- Bounded no-result poll returns `dropped` with a diagnostic.
- Unsupported scopes/policies return `unsupported` with diagnostics.
- Capability snapshot promotes `panel-query`, `point-item`, and `image-texel` only when the query binding is ready.
- Full test suite passes.

## Result

Completed by local-main-codex. Added the bounded `query_panel()` runtime wrapper, typed Datoviz
data-scope query capability, point/image query-mode promotion, fake-facade runtime coverage, and
spec notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 145 passed, 6 skipped.

## Stop conditions

Stop before guide/all-rendered query semantics, `hit_policy=all`, extension payload support, live
GPU/headless runtime enforcement, v0.4 binding activation, or Datoviz repository edits.
