# M069 - PathVisual v1

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Draft.

## Summary

Add continuous open polyline/subpath contract with caps and joins.

## Planned Deliverables

- `PathVisual` and `StrokeJoin` enum.
- Producer API, likely `Axes.plot(...)`, `Axes.path(...)`, or `Axes.paths(...)`.
- Matplotlib mapping for open subpaths.
- Datoviz v0.4 `dvz_path` adapter with per-path-to-per-point expansion, subpath lengths, caps,
  joins, and stroke width upload.
- QA cases for multiple subpaths, width, cap, and join.

## Acceptance

Multiple-subpath, cap, join, and width cases render in Matplotlib. Datoviz renders or reports
missing subpath/join/cap helpers.

## Stop Condition

Closed paths, fills, holes, Beziers, dashes, and polygons are deferred.
