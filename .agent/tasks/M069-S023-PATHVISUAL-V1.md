# M069-S023-PATHVISUAL-V1 - PathVisual v1

## Mission

M069

## Goal

Implement continuous open polyline and multi-subpath rendering with a stable protocol contract.

## Contract Starting Point

Suggested v1 fields:

```text
id
positions
path_lengths
colors
widths
cap
join
miter_limit
coordinate_space
```

Important v1 decision from P008: closed paths are deferred. A producer may duplicate the first
vertex to create an explicitly closed-looking polyline, but there is no `closed` protocol field in
S023.

## Backend Mapping

- Matplotlib: LineCollection or Path/Patch collection depending on what gives clean open-subpath
  semantics; keep implementation simple and typed.
- Datoviz v0.4: `dvz_path(scene, flags)`, upload `"position"`, `"color"`, and always
  `"stroke_width"`; call `dvz_path_set_subpaths`, `dvz_path_set_caps`, and `dvz_path_set_join`
  when present.
- Datoviz expects per-point color/width arrays; expand GSP per-path values using `path_lengths`.

## Acceptance

- Path validation rejects inconsistent `path_lengths`.
- Matplotlib QA outputs show multiple subpaths, caps, joins, and width ramp.
- Datoviz outputs or structured unsupported diagnostics identify exact missing helpers.
- No fill/Bezier/dash/closed path scope enters v1.

## Stop Conditions

- Stop if path semantics require filled polygons or text/glyph decisions.
- Stop if per-vertex public styling is added without a separate decision.
