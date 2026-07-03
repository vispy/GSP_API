# M208 - S050 Datoviz TextVisual strictness proof

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Use focused fixtures and review artifacts to decide which adapted Datoviz TextVisual rows can move
toward strict rendering without changing the public TextVisual contract.

## Stop Conditions

- Stop before changing TextVisual anchor, multiline, Unicode, or DATA coordinate public semantics
  without a consultation packet.
- Stop before claiming text query/readback support.
- Stop if Datoviz cannot report enough font/layout behavior to distinguish baseline/top/bottom and
  multiline anchor semantics.

## Result

Completed with no new TextVisual strict promotion. See
`.agent/S050_DATOVIZ_TEXTVISUAL_STRICTNESS_PROOF.md`.

M208 also fixed the latest generated-binding call shape for packed RGBA8 texture uploads:
`dvz_visual_set_texture_rgba8()` now receives a contiguous `POINTER(c_ubyte)`, matching the current
ctypes binding rather than any legacy wrapper behavior.

Fresh real Datoviz evidence:

- `artifacts/visual_qa/s050/m208-textvisual-strictness/`: combined five-case TextVisual review pack
  still crashes the Datoviz offscreen child with signal 11.
- `artifacts/visual_qa/s050/m208-textvisual-strictness-isolated/`: one-case runs render; only the
  existing `text/rotation_alpha_ndc` row is strict, and `text/basic_ndc`,
  `text/anchor_grid_ndc`, `text/data_vs_ndc`, and `text/multiline_unicode_smoke` remain adapted.

No public `TextVisual` semantics changed, and text query/readback remains unsupported.
