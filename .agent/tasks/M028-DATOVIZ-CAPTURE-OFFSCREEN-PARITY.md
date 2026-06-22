# M028-DATOVIZ-CAPTURE-OFFSCREEN-PARITY - Datoviz capture/offscreen parity

## Mission

M028

## Goal

Expose bounded Datoviz v0.4 offscreen PNG capture capability and implementation.

## Acceptance

- Capture readiness reports missing symbols.
- Capability snapshot promotes `png` output only when offscreen capture symbols are available.
- `DatovizV04ProtocolRenderer.capture_png_bytes()` returns PNG bytes via `dvz_view_capture_png`.
- Capture is documented as screenshot/export output, not scientific readback.

## Stop conditions

Stop before raw RGBA/scientific readback, video capture, visual conformance comparison, public
cross-backend capture API design, or Datoviz repository edits.
