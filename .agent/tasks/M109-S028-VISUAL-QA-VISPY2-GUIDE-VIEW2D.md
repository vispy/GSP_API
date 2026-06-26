# M109-S028 - Visual QA and VisPy2 guide View2D coverage

## Mission

M109

## Goal

Cover accepted S028 guide/View2D behavior in visual QA and VisPy2 producer tests.

## Status

Completed.

## Deliverables

- Visual QA cases for guide/View2D behavior.
- VisPy2 guide/view tests for normal and reversed limits.
- Minimal docs/examples updates if implementation changes public behavior.

## Acceptance

- Focused QA and VisPy2 tests pass.
- Guide artifacts remain semantic guide state, not user data visuals.

## Result

- Visual QA cases added: `guide/view2d_auto_grid` and `guide/view2d_reversed_explicit`.
- Scene artifacts now serialize `axis_guides` and `panel_text_guides`.
- Matplotlib QA rendering realizes semantic guides while keeping them out of the visual stream.
- VisPy2 reversed guide rendering coverage added.
- `uv run pytest tests/test_visual_qa_harness.py tests/test_vispy2_protocol_mvp.py -q`: 51 passed.
- `uv run pytest tests/test_matplotlib_guides.py tests/test_matplotlib_guide_query.py tests/test_matplotlib_scoped_query.py -q`: 27 passed.
- `uv run mypy src/ --strict --show-error-codes`: clean.
