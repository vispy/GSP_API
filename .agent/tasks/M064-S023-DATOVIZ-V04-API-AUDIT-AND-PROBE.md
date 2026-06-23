# M064-S023-DATOVIZ-V04-API-AUDIT-AND-PROBE - Datoviz v0.4 API audit and probe

## Mission

M064

## Goal

Create an executable audit/probe that captures the actual Datoviz v0.4 API surface available to
GSP before implementing any new visual family. This is primarily evidence gathering plus a reusable
capability report for M065+.

## Required Reads

- `.agent/consultations/P008-response.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/capabilities.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- Sibling source: `../datoviz/README.md`, `../datoviz/datoviz/__init__.py`,
  `../datoviz/datoviz/raw.py`, and relevant `../datoviz/examples/c/visuals/*.c`.

## Implementation Guidance

Prefer a small new module under `src/gsp/qa/visual/` if that package is introduced now, or a
minimal internal module under `src/gsp_datoviz/` if that fits the current codebase better. The
probe must be usable by the later visual QA harness and by tests.

The probe must attempt:

```python
import datoviz as dvz
import datoviz.raw as raw
```

Record:

- import status and exception traceback;
- package path;
- whether generated `_array_facade.py` is present;
- whether generated `_ctypes.py` is present;
- `../datoviz` path and git revision when available;
- exact callable names found/missing;
- enum names needed for caps, joins, symbols, coordinate space, alpha, and attach descriptors;
- whether top-level `datoviz.capture` exists;
- whether a minimal retained Point scene can be constructed without requiring a GUI run;
- whether capture/offscreen is available;
- all banned v0.3-style names found in new GSP Datoviz adapter code.

Required capability names to check at minimum:

```text
datoviz.facade.import
datoviz.raw.import
scene.create.dvz_scene
scene.figure.dvz_figure
scene.panel.dvz_panel_full
panel.add_visual.dvz_panel_add_visual
visual.data.dvz_visual_set_data
visual.data_many.dvz_visual_set_data_many
visual.data_range.dvz_visual_set_data_range
visual.point.constructor.dvz_point
visual.marker.constructor.dvz_marker
visual.segment.constructor.dvz_segment
visual.path.constructor.dvz_path
visual.image.constructor.dvz_image
visual.path.style.dvz_path_set_subpaths
visual.path.style.dvz_path_set_caps
visual.path.style.dvz_path_set_join
visual.image.field.dvz_sampled_field
visual.image.field.dvz_sampled_field_set_data
visual.image.field.dvz_visual_set_field
capture.top_level.datoviz_capture
attach.desc.DvzVisualAttachDesc
attach.coord_space.DVZ_COORD_VIEW
attach.coord_space.DVZ_COORD_DATA
attach.coord_space.DVZ_COORD_PANEL
```

Banned-symbol check:

```text
dvz_path_alloc
dvz_point_alloc
dvz_marker_alloc
dvz_segment_alloc
dvz_image_alloc
dvz_point_position
dvz_marker_color
dvz_segment_linewidth
```

The banned-symbol check should scan only new S023 Datoviz adapter/probe code and mission/spec text
where practical. It may mention banned names in tests and documentation only as forbidden examples.

## Acceptance

- Tests cover successful probe with a fake module/facade and missing-symbol behavior.
- Tests cover banned v0.3 symbol detection.
- Probe output is JSON-safe and deterministic enough for fixtures/reports.
- Running the probe in the current environment does not require live rendering or a display.
- Existing test suite remains green.

## Stop Conditions

- Stop if the work starts implementing visual rendering beyond minimal probe construction.
- Stop if code depends on legacy `gsp_datoviz.renderer`.
- Stop if the worker cannot locate either installed `datoviz` or `../datoviz`; report a structured
  unavailable result instead of inventing APIs.
