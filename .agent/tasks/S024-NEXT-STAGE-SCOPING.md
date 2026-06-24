# S024 next stage scoping - Text/Glyph or Mesh

## Status

Draft follow-up created by M072.

## Context

S023 closed point, marker, segment, path, and image visual-family v1 contracts. Legacy source still
contains text and mesh functionality, but those are not accepted protocol semantics.

## Candidate A: Text/Glyph stage

Potential deliverables:

- `TextVisual` / `GlyphVisual` protocol contract;
- font, glyph atlas, anchor/alignment, rotation, color, and size decisions;
- Matplotlib reference text rendering;
- Datoviz v0.4 text/glyph API evidence and capability gates;
- visual QA cases for labels, anchors, rotation, alpha, and DPI/size.

Use ChatGPT Pro consultation before committing public text/glyph semantics if font/glyph atlas
architecture is uncertain.

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

Prefer Text/Glyph first if the next goal is plot annotation and axes polish. Prefer Mesh first if the
next goal is 3D/scientific geometry parity. Do not implement either by copying legacy behavior without
an accepted protocol contract and QA plan.
