# M026 - Datoviz v0.4 runtime query smoke and capability promotion

## Goal

Add a conservative runtime query binding gate for Datoviz v0.4 and promote only coarse
`panel-query` capability when the active Python facade exposes the required query symbols.

## State

Completed.

## Required reading

- `.agent/tasks/DATOVIZ-V04-QUERY-BINDING.md`
- `.agent/tasks/DATOVIZ-V04-QUERY-PARITY.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/capabilities.py`
- `src/gsp_datoviz/query.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/include/datoviz/scene/interaction.h`

## Expected tasks

- Add Datoviz v0.4 query binding readiness diagnostics.
- Promote `panel-query` only when query request, queue, poll, and decodable result bindings exist.
- Keep `point-item` and `image-texel` unadvertised.
- Add fake-facade tests and skip-clean runtime promotion smoke.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Runtime `dvz_panel_query()` execution proof with real GPU/offscreen runtime.
- Promoting point/image query modes.
- Datoviz repository edits.
- GSP query protocol redesign.

## Acceptance criteria

- Query binding readiness can report missing Datoviz symbols.
- Capability snapshot advertises `panel-query` only for a ready v0.4 query binding.
- Runtime smoke skips cleanly when the active binding is unavailable or incomplete.
- Full test suite passes.

## Result

Completed by local-main-codex. Added query binding readiness diagnostics, conditional `panel-query`
promotion, fake-facade coverage, skip-clean runtime promotion smoke, and spec notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 136 passed, 4 skipped.

## Stop conditions

Stop before real runtime query execution, point/image query mode promotion, or Datoviz repository
edits.
