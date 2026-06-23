# S023 Handoff - Visual Families v1 and Manual Visual QA Foundation

Generated: 2026-06-23

## Current State

S023 is in progress at 38%.

Completed:

- M064 - Datoviz v0.4 API audit and probe.
- M065 - Visual QA harness foundation.
- M066 - PointVisual v1 and Datoviz v0.4 retained point path.

Next:

- M067 - MarkerVisual v1.

Recent commits:

- `5d9ec8e` - Implement Datoviz v0.4 API probe.
- `1b92a8f` - Correct Datoviz v0.4 probe evidence.
- `ea70c79` - Implement visual QA harness foundation.
- local working tree - Complete M066 PointVisual v1.

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

The sibling checkout was on `v0.4-dev` during M064/M065 work.

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

Observed result:

- Ruff passed.
- Pytest: `241 passed, 1 skipped`.
- Strict mypy passed.
- Status JSON and diff whitespace checks passed.
- Both backend import checks passed.

CLI smoke also rendered all four S023 cases with both Matplotlib and Datoviz in a temporary output directory.

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

## M067 Review Point

Before implementing M067, keep MarkerVisual distinct from PointVisual. MarkerVisual may add marker
shape, angle, stroke, and edge styling, but PointVisual must remain the simple high-volume point
family with position/color/diameter only.
