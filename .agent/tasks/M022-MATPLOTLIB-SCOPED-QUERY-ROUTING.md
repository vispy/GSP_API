# M022-MATPLOTLIB-SCOPED-QUERY-ROUTING - Matplotlib scoped query routing

## Mission

M022

## Goal

Implement bounded Matplotlib/reference routing for `data`, `guides`, and `all-rendered` query
scopes.

## Acceptance

- `data` scope routes to point/image query logic and ignores guides.
- `guides` scope routes to semantic guide query logic and ignores data visuals.
- `all-rendered` merges queryable data and guide hits by bounded reference render order.
- `hit_policy=frontmost` returns one frontmost hit.
- `hit_policy=all` returns all eligible hits front-to-back.
- Unsupported scope prerequisites return `unsupported`, not partial hits.

## Stop conditions

Stop before Datoviz query implementation, broad scene planner implementation, or native text/layout
hit testing beyond existing bounded guide roles.
