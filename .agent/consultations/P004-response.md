# P004 Response - Unified query scopes and capability semantics

Status: received from ChatGPT Pro and accepted for S015 planning.

## Key decisions

- Add explicit `QueryScope` with exactly `data`, `guides`, and `all-rendered`.
- Keep scope as a single enum and default `QueryRequest.scope` to `data`.
- Treat `all-rendered` as a strict global rendered-order query, not shorthand for data plus guides.
- Do not allow partial direct query results for unsupported requested scope, payload, extension
  payload, or hit policy.
- Add `QueryHit`/multi-hit result shape while preserving top-level single-hit compatibility fields.
- Add typed query capability records in a follow-up mission; keep string `query_modes` only as a
  v0.1 compatibility projection.
- Compose global query capabilities with selected axis-provider query capabilities by intersection.
- Matplotlib should become the strict reference for scoped query conformance.
- Datoviz must remain capability-gated until an active v0.4 Python facade/raw binding exists.

## Recommended first implementation mission

Implement the protocol dataclass update:

- `QueryScope`
- `QueryContributionKind`
- `QueryHit`
- `QueryRequest.scope`
- `QueryRequest.requested_extension_payload_kinds`
- `QueryResult.hits`
- compatibility mirroring between `hits[0]` and legacy top-level hit fields
- stricter non-hit payload invariants

Typed query capabilities, planner composition, Matplotlib scoped routing, Datoviz gating, and
extension query payload integration remain follow-up missions.
