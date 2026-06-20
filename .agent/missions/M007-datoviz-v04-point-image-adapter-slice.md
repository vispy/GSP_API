# M007 - Datoviz v0.4 point/image protocol adapter slice

## Goal

Implement or prototype a bounded Datoviz v0.4 protocol renderer slice for the current GSP point/image vertical slice.

This mission must use the local/sibling Datoviz v0.4 checkout as authority, not old online Datoviz v0.3 Python docs. The target is the C-shaped `dvz_*` API, not old `datoviz.App` / `datoviz.visuals`.

Query support is explicitly out of scope until Python can decode `DvzQueryResult`.

## State

Draft.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- LEGACY_MAP.md
- spec/backends/datoviz.md
- spec/visuals/point.md
- spec/visuals/image.md
- spec/capabilities.md
- .agent/reviews or reports from M004
- Current files under src/gsp_datoviz/
- Relevant headers/source from `../datoviz/` current branch only.

## Expected tasks

- Create a new v0.4-oriented Datoviz protocol-renderer path, or a documented spike if implementation is blocked.
- Map GSP `PointVisual` to the Datoviz v0.4 C-shaped point visual API.
- Map GSP `ImageVisual` to the Datoviz v0.4 sampled-field/image path if confirmed.
- Add a static capability snapshot for the Datoviz adapter where runtime probing is not yet available.
- Add tests that skip cleanly if Datoviz v0.4 bindings are unavailable.
- Do not depend on Datoviz query decoding.
- Produce exact Datoviz API gap tasks if blocked.

## Allowed paths

- src/gsp_datoviz/
- tests/
- spec/backends/datoviz.md
- .agent/tasks/
- .agent/status.json
- STATUS.md
- docs/ or .agent/reviews/ for gap reports

## Forbidden paths

- src/vispy2/
- src/gsp_matplotlib/ except test interoperability references
- Online Datoviz API docs unless verified against `../datoviz/`
- Any Datoviz repo modifications from this branch
- Query result decoding implementation unless `DvzQueryResult` Python decode already exists

## Acceptance criteria

- Point/image Datoviz adapter path exists or a precise blocker report exists.
- Tests pass or skip cleanly when Datoviz v0.4 runtime/bindings are unavailable.
- No old v0.3 `datoviz.App` / `datoviz.visuals` assumptions are introduced.
- Any Datoviz-side gaps are written as explicit task files.
- Local in-process path remains primary.

## Stop conditions

Stop if:
- the Datoviz v0.4 C API cannot be safely identified;
- image sampled-field semantics are unclear;
- runtime capability query is required but absent;
- implementation would require modifying the Datoviz repo;
- query support becomes necessary.

## Notes

This mission should prove Datoviz point/image feasibility in code, not solve all Datoviz integration.
