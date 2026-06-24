# M069 - PathVisual v1

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Add continuous open polyline/subpath contract with caps and joins.

## Planned Deliverables

- `PathVisual` and `StrokeJoin` enum.
- Producer API, likely `Axes.plot(...)`, `Axes.path(...)`, or `Axes.paths(...)`.
- Matplotlib mapping for open subpaths.
- Datoviz v0.4 `dvz_path` adapter with per-path-to-per-point expansion, subpath lengths, caps,
  joins, and stroke width upload.
- QA cases for multiple subpaths, width, cap, and join.

## Completed

- Added `PathVisual` and `StrokeJoin` to the formal protocol.
- Added `Axes.path(...)`, `Axes.plot(...)`, and top-level `vispy2.path(...)`.
- Added Matplotlib open-subpath rendering with `PathPatch`, pixel-to-point stroke width conversion, caps, and joins.
- Added Datoviz v0.4 retained path rendering gated on `dvz_path`, `dvz_path_set_subpaths`, `dvz_path_set_caps`, and `dvz_path_set_join`, with per-subpath color/width expansion.
- Added S023 visual QA case `path/subpaths_width_join_ndc`.
- Added path visual spec notes and backend/API spec updates.

## Acceptance

Multiple-subpath, cap, join, and width cases render in Matplotlib. Datoviz renders or reports
missing subpath/join/cap helpers.

## Stop Condition

Closed paths, fills, holes, Beziers, dashes, and polygons are deferred.
