# M020-QUERY-CAPABILITY-SCHEMA - Typed query capability schema

## Mission

M020

## Goal

Add typed query capability records for S015 query scopes while keeping `query_modes` as a v0.1
compatibility projection.

## Acceptance

- `CapabilitySnapshot.query_capabilities` exists.
- Typed capability records can express scope, target, payloads, extension payloads, hit policies,
  and ordering guarantees.
- `all-rendered` is not inferred from separate `data` and `guides`.
- `all-rendered` requires a global render-order guarantee.
- Unsupported payloads and extension payloads reject planning.
- Existing string `query_modes` behavior remains compatible.

## Stop conditions

Stop before scoped Matplotlib query routing, query planner scene/provider composition, or Datoviz
runtime query implementation.
