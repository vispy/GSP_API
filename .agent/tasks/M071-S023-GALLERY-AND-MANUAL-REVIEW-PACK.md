# M071-S023-GALLERY-AND-MANUAL-REVIEW-PACK - S023 gallery and manual review pack

## Mission

M071

## Goal

Package the S023 visual-family work into examples and review artifacts the user can inspect
manually.

## Deliverables

- `examples/vispy2_protocol_marker.py`
- `examples/vispy2_protocol_segment.py`
- `examples/vispy2_protocol_path.py`
- updated point/image examples if needed for pixel-size semantics;
- a combined S023 gallery example or QA command;
- documentation in `examples/README.md` or a visual QA spec page;
- final contact sheets and `manual_notes.yaml` from the harness.

## Acceptance

- Examples are runnable.
- Examples produce formal GSP protocol scenes through VisPy2/GSP producers.
- The QA harness can render all examples/cases with Matplotlib and Datoviz-v0.4 or structured
  unsupported diagnostics.
- Manual review notes exist and are referenced in the final summary.

## Stop Conditions

- Stop if examples import backend renderers directly except through the visual QA harness.
- Stop if examples use legacy GSP/Datoviz paths as implementation dependencies.

## Completion Notes

- Added examples:
  - `examples/vispy2_protocol_marker.py`
  - `examples/vispy2_protocol_segment.py`
  - `examples/vispy2_protocol_path.py`
  - `examples/vispy2_protocol_image_scalar.py`
- Updated documentation:
  - `examples/README.md`
  - `mkdocs_source/s023_visual_qa.md`
  - `mkdocs.yml`
- Final QA artifacts regenerated under `artifacts/visual_qa/s023/latest-local/`:
  - `contact_sheets/s023_all_cases.png`
  - `manual_notes.yaml`
  - `report.json`
  - `summary.md`
- Validation passed:
  - all protocol examples run and write PNGs
  - S023 QA: 13 cases, Matplotlib rendered, Datoviz rendered
  - `uv run pytest tests -q`
  - `uv run mypy src/ --strict --show-error-codes`
  - `uv run mkdocs build --strict`
