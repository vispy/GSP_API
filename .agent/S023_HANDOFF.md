# S023 Handoff - Visual Families v1 and Manual Visual QA Foundation

Generated: 2026-06-24

## Current State

S023 is in progress at 60%.

Completed:

- M064 - Datoviz v0.4 API audit and probe.
- M065 - Visual QA harness foundation.
- M066 - PointVisual v1 and Datoviz v0.4 retained point path.
- M067 - MarkerVisual v1.
- M068 - SegmentVisual v1.

Milestone reached:

- The current S023 contact sheet has good-enough Matplotlib/Datoviz parity for point, marker,
  nearest-image, and point-over-image cases.
- The systematic Datoviz paleness was fixed by the Datoviz legacy sRGB blend pipeline and UNORM
  offscreen legacy target.
- Datoviz `v0.4-dev` now contains the no-ff merge commit:
  `f0d90d2bb` - Merge legacy sRGB blend pipeline.
- GSP commit `d2938c2` wires Datoviz color-pipeline selection and defaults visual QA comparison
  runs to `legacy_srgb_blend`.

Next:

- M069 - PathVisual v1.

Recent commits:

- `d2938c2` - Wire Datoviz color pipeline option.
- `216698d` - Normalize Matplotlib diamond marker bbox.
- `3d9fec2` - Fix Matplotlib rotated marker scale semantics.
- `f705219` - Remove Datoviz marker angle workaround.
- `d667ee5` - Fix Datoviz marker orientation and alpha blending.

## Datoviz Environment

The active GSP venv must use the sibling Datoviz v0.4 checkout, not PyPI `datoviz 0.3.x`.

Current expected setup:

```bash
uv pip show datoviz
```

Expected result:

- `Version: 0.4.0.dev0`
- `Editable project location: /home/cyrille/GIT/Viz/datoviz`

If the environment falls back to PyPI `datoviz 0.3.5`, rerun:

```bash
uv pip install -e ../datoviz
```

The sibling checkout should be on Datoviz `v0.4-dev` at or after `f0d90d2bb`.

## M064 Output

Reusable probe module:

- `src/gsp/qa/visual/datoviz_probe.py`

Generated probe evidence:

- `artifacts/visual_qa/s023/datoviz_v04_probe/probe_report.json`
- `artifacts/visual_qa/s023/datoviz_v04_probe/capability_matrix.json`
- `artifacts/visual_qa/s023/datoviz_v04_probe/facade_symbols.json`
- `artifacts/visual_qa/s023/datoviz_v04_probe/raw_symbols.json`
- `artifacts/visual_qa/s023/datoviz_v04_probe/banned_symbol_check.json`

Current probe expectation:

- `datoviz` import works.
- `datoviz.raw` import works.
- Minimal retained point scene construction works.
- Capture symbols are available.
- Banned v0.3 symbol scan has zero unexpected hits.

Important detail: generated v0.4 ctypes exposes coordinate constants as
`DvzVisualCoordSpace.DVZ_COORD_DATA` style enum members, not necessarily as flat raw module constants.

## M065 Output

Visual QA entry points:

```bash
python -m gsp.qa.visual list --suite s023
python -m gsp.qa.visual run --suite s023 --backends matplotlib,datoviz --out artifacts/visual_qa/s023/dev --contact-sheet
```

New harness files:

- `src/gsp/qa/visual/case_spec.py`
- `src/gsp/qa/visual/cases.py`
- `src/gsp/qa/visual/artifacts.py`
- `src/gsp/qa/visual/contact_sheet.py`
- `src/gsp/qa/visual/runner.py`
- `src/gsp/qa/visual/cli.py`
- `src/gsp/qa/visual/__main__.py`

Current S023 cases:

- `point/basic_ndc`
- `point/diameter_ramp_ndc`
- `point/alpha_overlap_ndc`
- `marker/shapes_ndc`
- `marker/angle_size_stroke_ndc`
- `segment/width_cap_ndc`
- `segment/alpha_order_ndc`
- `image/checker_nearest_ndc`
- `overlay/point_over_image_ndc`

Generated run layout:

```text
artifacts/visual_qa/s023/<run_id>/
  run_manifest.json
  environment.json
  report.json
  summary.md
  manual_notes.yaml
  scenes/*.scene.json
  scenes/*.arrays.npz
  backends/matplotlib/*.png
  backends/datoviz/*.png or *.unsupported.json
  contact_sheets/*.png
  notes/*.md
```

M065 intentionally does not commit generated sample runs.

## Datoviz Capture Fix

M065 exposed a real v0.4 binding issue in the GSP adapter: `dvz_view_capture_png()` expects a
bytes path, not a Python `str`.

Fixed in:

- `src/gsp_datoviz/protocol_renderer.py`

Regression test:

- `tests/test_datoviz_v04_protocol_renderer.py::test_capture_png_bytes_uses_offscreen_view_and_returns_png_bytes`

## Validation State

Last validation before this handoff:

```bash
uv run ruff check
uv run pytest -q
uv run mypy src/ --strict --show-error-codes
python -m json.tool .agent/status.json >/dev/null
git diff --check
GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"
GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"
```

Observed result after M067:

- Ruff passed.
- Pytest: `251 passed, 2 skipped`.
- Strict mypy passed.
- Status JSON and diff whitespace checks passed.
- Both backend import checks passed.

CLI smoke rendered all S023 cases to `artifacts/visual_qa/s023/latest-local`. Point, marker,
segment, image nearest, and point-over-image cases render in both Matplotlib and Datoviz.

The latest regenerated contact sheet is:

- `artifacts/visual_qa/s023/latest-local/contact_sheets/s023_all_cases.png`

Use this command shape for local regeneration:

```bash
DVZ_SHADERC_RUNTIME_LIBRARY=/home/cyrille/GIT/Viz/datoviz/build/wheel-stage/datoviz/libshaderc_shared.so \
  uv run python -m gsp.qa.visual run \
    --out artifacts/visual_qa/s023/latest-local \
    --run-id latest-local \
    --contact-sheet \
    --resolution 800x600
```

The generated run records `datoviz_color_pipeline: legacy_srgb_blend`.

## M066 Completion

M066 froze this semantic decision:

- `PointVisual.sizes` should mean screen-pixel diameters.

This is recorded in `adr/ADR-0010-pointvisual-size-units.md`.

Completed M066 work:

- Point spec now defines `sizes` as rendered screen-pixel diameters.
- Matplotlib converts protocol diameters to `scatter(..., s=...)` area units using figure DPI.
- Datoviz maps protocol diameters directly to the retained point visual `"diameter_px"` upload.
- Datoviz point/image visual attachment now uses an explicit `DvzVisualAttachDesc`.
- `point/alpha_overlap_ndc` was added to the S023 visual QA suite.
- Local M066 QA rendered all point cases in both Matplotlib and Datoviz.

## Backend Naming

Plain `datoviz` now refers to the Datoviz v0.4 retained/protocol backend. The old renderer path is
explicitly named `datoviz-v03` in legacy example helpers. The former `datoviz-v04` visual-QA backend
id is accepted as a compatibility alias but should not be used in new commands.

## M067 Completion

M067 added markers as a distinct visual family:

- `MarkerVisual` and `MarkerShape` live in `gsp.protocol`.
- The v1 shape vocabulary is conservative: `disc`, `square`, `triangle`, `diamond`, and `cross`.
- `Axes.markers(...)` and `vispy2.markers(...)` emit protocol marker visuals.
- Matplotlib renders marker paths and converts protocol pixel diameters to Matplotlib area units.
- Datoviz v0.4 renders retained markers with `dvz_marker()`, `dvz_marker_style()`,
  `dvz_marker_set_style()`, and dense uploads for `position`, `color`, `diameter_px`, `angle`,
  and `shape`.
- `marker/shapes_ndc` and `marker/angle_size_stroke_ndc` were added to visual QA and render in both
  backends in the latest local run.

## Datoviz Parity Fixes Landed

The visual QA work exposed several Datoviz-side semantic gaps that are now fixed on Datoviz
`v0.4-dev`:

- nearest image sampling support;
- marker triangle bbox/rotation semantics;
- marker angle handling with positive angles using the math convention;
- legacy sRGB/display-space blending as an opt-in figure color pipeline;
- UNORM offscreen targets for legacy color-pipeline capture.

Those fixes make the S023 visual QA cases useful for checking GSP regressions rather than mainly
tracking Datoviz limitations.

## M068 Review Point

M068 added SegmentVisual as a distinct visual family:

- `SegmentVisual` and `StrokeCap` live in `gsp.protocol`.
- The v1 cap vocabulary is conservative: `butt`, `round`, and `square`.
- `Axes.segments(...)` and `vispy2.segments(...)` emit protocol segment visuals.
- Matplotlib renders segments with `LineCollection`; protocol widths are screen pixels and are
  converted to Matplotlib point linewidths using figure DPI.
- Datoviz v0.4 renders retained segments with `dvz_segment`, `dvz_segment_set_caps`, and dense
  uploads for `position_start`, `position_end`, `color`, and `stroke_width_px`.
- `segment/width_cap_ndc` and `segment/alpha_order_ndc` were added to visual QA and render in both
  backends in the latest local run.

## M069 Review Point

Before implementing M069, keep PathVisual distinct from SegmentVisual. Path should cover continuous
polyline/subpath semantics with joins and ordered vertices; it should not regress the independent
segment contract added in M068.

## M069 PathVisual v1 update

- Added `PathVisual` and `StrokeJoin` for open polyline/subpath semantics.
- `path_lengths` partitions ordered vertices into open subpaths; closed paths, fills, holes,
  Beziers, dashes, and polygons remain deferred.
- Matplotlib renders each subpath as an open `PathPatch` with cap/join styles and pixel-width
  conversion.
- Datoviz v0.4 uses `dvz_path`, `dvz_path_set_subpaths`, `dvz_path_set_caps`, and
  `dvz_path_set_join` when exposed, expanding per-subpath colors/widths to per-vertex arrays.
- Visual QA case `path/subpaths_width_join_ndc` was added and Matplotlib smoke-generated under
  `artifacts/visual_qa/s023/m069_path_smoke`.
