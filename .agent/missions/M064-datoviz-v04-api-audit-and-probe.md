# M064 - Datoviz v0.4 API audit and probe

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Ready.

## Summary

Replace v0.3-drift assumptions with a generated actual-v0.4 capability matrix before any new
visual-family implementation. This mission is the required first step for S023.

## Required Context

- Read `.agent/consultations/P008-response.md`.
- Inspect the installed `datoviz` package in the active environment.
- Inspect the sibling `../datoviz/` checkout as the local v0.4-dev source of truth.

## Planned Deliverables

- `gsp/qa/visual/datoviz_probe.py` or equivalent focused probe module.
- A probe report schema and generated report path documented for later harness use.
- Facade/raw symbol matrix covering installed package and local source.
- Banned v0.3 symbol check, especially `dvz_*_alloc` visual-family assumptions.
- Evidence notes for retained-scene pattern:
  - `dvz_scene`
  - `dvz_figure`
  - `dvz_panel_full`
  - `dvz_<family>(scene, flags)`
  - `dvz_visual_set_data*`
  - `dvz_panel_add_visual` with explicit attach descriptor.

## Acceptance

- Probe records installed package path, import status, source path/revision, facade/raw availability,
  capture availability, required v0.4 symbols, missing symbols, and banned v0.3 names.
- Probe attempts both `import datoviz as dvz` and `import datoviz.raw as raw`.
- Probe records whether `_array_facade.py` and `_ctypes.py` are present.
- Probe records enum/style helper availability needed for early Point/Marker/Segment/Path/Image
  work.
- A minimal Point scene construction is attempted if symbols are present; capture/run may be
  capability-gated.
- No new mission/task/spec text expects `dvz_*_alloc` visual functions.

## Stop Condition

Stop and report if implementation starts using v0.3-style visual APIs such as `dvz_path_alloc`,
`dvz_point_alloc`, `dvz_point_position`, `dvz_marker_color`, or `dvz_segment_linewidth`.

Do not stop Matplotlib/reference work only because Datoviz facade bindings are incomplete; report
that as structured unsupported capability data.
