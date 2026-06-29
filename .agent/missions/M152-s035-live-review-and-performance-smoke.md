# M152 - S035 live review and performance smoke

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Completed.

## Summary

Add a live pan/zoom review example and performance smoke after protocol and backend retained-update
paths are in place.

## Deliverables

- Live review example where drag/wheel native events adapt to S035 semantic navigation actions.
- Matplotlib and Datoviz review commands where supported.
- Performance smoke that records frame/update counts and verifies stable visual-buffer upload counts
  during navigation.
- Documentation for supported and unsupported live-input paths.

## Stop Condition

Stop before claiming interactive support if the Datoviz retained-update proof is absent.

## Result

Added a backend-neutral pointer input adapter that converts resolved target-panel pointer events into
S035 semantic `pan_by` and `zoom_about` actions. Added a Matplotlib live review example where native
drag/wheel events use that adapter, plus a scripted Datoviz retained-update smoke that verifies
navigation updates do not re-upload unchanged visual buffers. Datoviz v0.4 native pointer callbacks
remain explicitly deferred for the protocol renderer.

## Review Commands

- `uv run python examples/protocol_view2d_navigation.py --backend matplotlib`
- `uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke`
- `uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000`

## Validation

- `uv run ruff check src/gsp/protocol/navigation.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py tests/test_navigation_smoke.py`
- `uv run mypy src/gsp/protocol/ src/gsp_matplotlib/ src/gsp_datoviz/ --strict --show-error-codes`
- `uv run pytest tests/ -q`
- `GSP_TEST=True uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke`
- `uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000`
