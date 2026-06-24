# S024 next stage scoping - Text/Glyph or Mesh

## Status

Active S024 direction selected by M073: Text/Glyph first, with implementation gated on P009 ChatGPT Pro consultation.

## Context

S023 closed point, marker, segment, path, and image visual-family v1 contracts. Legacy source still
contains text and mesh functionality, but those are not accepted protocol semantics.

## Selected direction: Text/Glyph stage

Potential deliverables:

- `TextVisual` / `GlyphVisual` protocol contract;
- font, glyph atlas, anchor/alignment, rotation, color, and size decisions;
- Matplotlib reference text rendering;
- Datoviz v0.4 text/glyph API evidence and capability gates;
- visual QA cases for labels, anchors, rotation, alpha, and DPI/size.

ChatGPT Pro consultation is required before committing public text/glyph semantics. Packet: `.agent/consultations/P009-text-glyph-protocol-semantics.md`.

## Candidate B: Mesh stage

Potential deliverables:

- `MeshVisual` protocol contract;
- indexed geometry/resource ownership decisions;
- face/vertex color and normal/material baseline;
- Matplotlib reference slice where feasible;
- Datoviz v0.4 mesh API evidence and capability gates;
- visual QA cases for solid color, indexed triangles, depth ordering, and simple lighting/material
  scope if accepted.

Use ChatGPT Pro consultation before committing transform/resource/material semantics.

## Recommendation

Proceed with Text/Glyph first because the requested goal is plot annotation, labels, titles, axes polish, and publication-style output. Mesh remains deferred for a later 3D/scientific geometry stage. Do not implement Text/Glyph by copying legacy behavior without the P009 response, accepted protocol contract, and QA plan.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M073 | completed | Create S024 Text/Glyph scoping and P009 ChatGPT Pro consultation packet. |
| M074 | blocked | Convert P009 response into ADR/spec baseline before implementation. |
