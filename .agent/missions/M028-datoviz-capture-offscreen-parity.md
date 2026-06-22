# M028 - Datoviz capture/offscreen parity

## Goal

Add bounded Datoviz v0.4 offscreen PNG capture support without claiming scientific readback.

## State

Completed.

## Required reading

- `spec/backends/datoviz.md`
- `docs/datoviz_v04_gap_analysis.md`
- `src/gsp_datoviz/capabilities.py`
- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/include/datoviz/app.h`
- `../datoviz/include/datoviz/canvas.h`

## Expected tasks

- Add capture readiness diagnostics for v0.4 offscreen PNG symbols.
- Promote `output_formats=("png",)` only when capture bindings are available.
- Add a renderer helper that captures PNG bytes through an offscreen view.
- Add fake-facade tests and skip-clean runtime binding smoke.
- Preserve the distinction between screenshot/export PNG and scientific readback.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Raw RGBA/scientific readback.
- Video capture.
- Visual conformance screenshot comparison.
- Datoviz repository edits.
- Public cross-backend capture API design.

## Acceptance criteria

- Capability snapshot advertises PNG output only when capture bindings are complete.
- Missing capture bindings produce diagnostics in metadata.
- Renderer capture path creates offscreen app/view, renders one frame, captures PNG bytes, and cleans temporary files.
- Full test suite passes.

## Result

Completed by local-main-codex. Added capture readiness diagnostics, conditional PNG output-format
promotion, lazy offscreen PNG byte capture, fake-facade coverage, skip-clean runtime binding smoke,
and spec notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 142 passed, 6 skipped.

## Stop conditions

Stop before raw RGBA readback, scientific readback semantics, visual conformance comparisons, video
capture, public cross-backend capture API design, or Datoviz repository edits.
