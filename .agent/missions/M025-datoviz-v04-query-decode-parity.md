# M025 - Datoviz v0.4 query decode parity

## Goal

Add a pure Datoviz v0.4 `DvzQueryResult` decoder that maps Python-visible result fields into GSP
`QueryResult` without advertising runtime query support yet.

## State

Completed.

## Required reading

- `.agent/tasks/DATOVIZ-V04-QUERY-BINDING.md`
- `.agent/tasks/DATOVIZ-V04-QUERY-PARITY.md`
- `spec/query.md`
- `spec/backends/datoviz.md`
- `../datoviz/include/datoviz/scene/enums.h`
- `../datoviz/include/datoviz/scene/types.h`
- `../datoviz/src/scene/query/result.c`
- `../datoviz/src/scene/visuals/image/query.c`

## Expected tasks

- Add a pure decoder for `DvzQueryResult`-shaped objects.
- Map Datoviz terminal statuses to GSP query statuses.
- Map point item hits to `VisualFamily.POINT`.
- Map image texel/RGBA hits to `VisualFamily.IMAGE`.
- Add synthetic tests and a skip-clean runtime binding smoke.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Advertising Datoviz query modes.
- Runtime `dvz_panel_query()` execution path.
- Datoviz repository edits.
- GSP query protocol redesign.

## Acceptance criteria

- Synthetic decoder tests cover status, point hit, and image hit mappings.
- Runtime binding smoke skips cleanly if `DvzQueryResult` is unavailable or undecodable.
- Datoviz adapter still advertises no query modes.
- Full test suite passes.

## Result

Completed by local-main-codex. Added `gsp_datoviz.query.decode_dvz_query_result`, synthetic
decoder coverage, and skip-clean binding smoke.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 134 passed, 3 skipped.

## Stop conditions

Stop before runtime query execution, query capability promotion, or Datoviz repository edits.
