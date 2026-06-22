# ADR-0006 - Unified query scopes and query hit payloads

## Status

Accepted

## Context

GSP already has a first-slice panel-query model for data visuals and a bounded reference guide-query
proof for semantic axis guides. The existing `QueryRequest` did not distinguish data visuals from
semantic guide contributions or from a final rendered-scene query.

String capability names such as `panel-query`, `point-item`, and `image-texel` are useful as a
v0.1 compatibility projection but are too coarse to drive planning for guide queries,
`all-rendered` ordering, requested payloads, extension payloads, or axis-provider constraints.

## Decision

GSP defines three core query scopes:

- `data`: user data visuals and data-scoped extension visuals;
- `guides`: semantic GSP guide contributions such as axes, ticks, spines, grids, labels, titles,
  and panel text guides;
- `all-rendered`: queryable data and guide contributions merged in final rendered order.

`QueryRequest.scope` is a single enum and defaults to `data` to preserve current behavior.
`all-rendered` is a distinct semantic request. It must not be inferred from separate support for
`data` and `guides`.

GSP also introduces `QueryHit` as the canonical hit payload item. `QueryResult.hits` holds the
frontmost hit or all hits depending on the request policy. Existing top-level single-hit fields stay
as compatibility mirrors of `hits[0]`.

Direct query execution must not silently return partial results. Unsupported requested scope, hit
policy, payload, extension payload, or provider behavior returns `unsupported` with a diagnostic.

## In Scope

- `QueryScope.DATA`, `QueryScope.GUIDES`, and `QueryScope.ALL_RENDERED`.
- `QueryContributionKind.DATA` and `QueryContributionKind.GUIDE`.
- `QueryHit` and `QueryResult.hits`.
- Default data-scope compatibility.
- Hit-only extension payloads.
- Non-hit payload invariants.

## Out of Scope

- UI/controller affordance hit testing.
- Arbitrary core scopes such as `ui`, `tools`, `legend`, or `overlay`.
- Partial-result query responses.
- Streaming or multi-stage query results.
- Typed query capability records; those are the next S015 mission.
- Datoviz runtime query implementation before an active v0.4 Python facade/raw binding exists.

## Consequences

Existing data-query callers continue to work because `scope` defaults to `data` and top-level
`QueryResult` hit fields are preserved.

Backends that render guides but cannot query them must report guide-scoped queries as
`unsupported`, not `miss`.

`all-rendered` becomes a strict guarantee: it requires a proven global rendered-order merge across
eligible data and guide contributions. Backends without that guarantee must reject the request.
