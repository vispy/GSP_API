# M009 - Query hardening and Datoviz query handoff

## Goal

Harden the GSP query/readback model after the M005 reference proof and create exact handoff tasks for Datoviz v0.4 query integration.

This mission must not implement Datoviz Python query decoding unless the required `DvzQueryResult` decode path already exists.

## State

Draft.

## Required reading

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- spec/query.md
- spec/capabilities.md
- spec/backends/datoviz.md
- M005 query implementation and tests
- M004 Datoviz assessment output
- Datoviz query-related notes from `../datoviz/` current branch only if needed

## Expected tasks

- Review and harden `QueryRequest`, `QueryResult`, and `QueryStatus`.
- Ensure statuses distinguish:
  - hit;
  - miss;
  - outside panel;
  - unsupported;
  - stale/dropped where applicable;
  - backend/readback failure where applicable.
- Add capability fields or adapter hooks needed to express query support.
- Add conformance tests for query status behavior.
- Add a Datoviz handoff task for Python `DvzQueryResult` decoding.
- Add a Datoviz handoff task for image/point query parity if needed.
- Do not depend on Datoviz query execution in GSP tests yet.

## Allowed paths

- src/gsp/
- src/gsp_matplotlib/
- tests/
- spec/query.md
- spec/capabilities.md
- spec/backends/datoviz.md
- .agent/tasks/
- .agent/status.json
- STATUS.md

## Forbidden paths

- src/gsp_datoviz/ query implementation unless explicitly limited to stubs/capability reporting
- ../datoviz/
- Large extension/data-source work
- VisPy2 API changes unless tests need a small fixture

## Acceptance criteria

- Query schema/status behavior is documented and tested.
- Matplotlib reference query remains deterministic.
- Datoviz query blockers are represented as explicit handoff task files.
- No false claim of Datoviz query support is introduced.
- All tests pass.

## Stop conditions

Stop if:

- query result fields require broad redesign;
- Datoviz query semantics conflict with current GSP result model;
- capability model changes become architectural rather than incremental.

## Notes

This mission prepares future Datoviz query integration without blocking on it.
