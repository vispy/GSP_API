# M019-QUERY-SCOPE-PROTOCOL-MODEL - Query scope protocol dataclass update

## Mission

M019

## Goal

Implement the first S015 protocol model slice from P004: query scopes, hit lists, extension payload
requirements, and compatibility mirrors.

## Acceptance

- `QueryRequest.scope` defaults to `data`.
- `QueryRequest.requested_extension_payload_kinds` exists and rejects empty kinds.
- `QueryResult.hits` exists and old top-level single-hit fields remain usable.
- Old top-level hit fields synthesize `hits`.
- `hits[0]` mirrors into old top-level fields when constructing new-style results.
- Non-hit results reject all hit payload fields, including `hits`.
- Existing query tests remain compatible.

## Stop conditions

Stop before adding typed query capability records, planner composition, Matplotlib scoped routing,
or Datoviz runtime query support.
