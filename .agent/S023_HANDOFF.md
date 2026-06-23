# S023 Handoff - Visual Families v1 and Manual Visual QA Foundation

Generated: 2026-06-23

## Current State

S023 is in progress at 25%.

Completed:

- M064 - Datoviz v0.4 API audit and probe.
- M065 - Visual QA harness foundation.

Next:

- M066 - PointVisual v1 and Datoviz v0.4 retained point path.

Recent commits:

- `5d9ec8e` - Implement Datoviz v0.4 API probe.
- `1b92a8f` - Correct Datoviz v0.4 probe evidence.
- `ea70c79` - Implement visual QA harness foundation.

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
python -m gsp.qa.visual run --suite s023 --backends matplotlib,datoviz-v04 --out artifacts/visual_qa/s023/dev --contact-sheet
```

New harness files:

- `src/gsp/qa/visual/case_spec.py`
- `src/gsp/qa/visual/cases.py`
- `src/gsp/qa/visual/artifacts.py`
- `src/gsp/qa/visual/contact_sheet.py`
- `src/gsp/qa/visual/runner.py`
- `src/gsp/qa/visual/cli.py`
- `src/gsp/qa/visual/__main__.py`

Initial S023 cases:

- `point/basic_ndc`
- `point/diameter_ramp_ndc`
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
  backends/datoviz-v04/*.png or *.unsupported.json
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

## M066 Review Point

Before implementing M066, freeze this semantic decision:

- `PointVisual.sizes` should mean screen-pixel diameters.

Recommendation: accept this. It aligns with Datoviz v0.4 `"diameter"` and makes manual visual QA
straightforward.

Known follow-up work for M066:

- Write/adjust PointVisual v1 spec text.
- Fix Matplotlib point mapping: `scatter(..., s=...)` takes area in points squared, not diameter.
- Keep Datoviz mapping as direct `"diameter"` upload.
- Replace NULL visual attachment in the Datoviz point path with an explicit attach descriptor for coordinate-space semantics.
- Extend/harden point QA cases in the M065 harness.
- Keep v0.3 Datoviz symbols banned except in explicit banned-symbol checks.

Stop if coordinate-space mapping remains ambiguous without a documented fixture/result.
