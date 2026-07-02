# Notes for Nicolas

This is a first serious 2026 rewrite of the preliminary 2023 GSP white paper.

## Intent

The draft keeps the original motivation: scientific visualization libraries repeatedly rebuild the
same renderer-level machinery, especially for GPU rendering, interaction, export, large data, and
backend portability. GSP is presented as a shared protocol layer, not as a plotting API and not as a
replacement renderer.

## What changed since the 2023 draft

- The paper now frames GSP as a session protocol, inspired by systems such as LSP, rather than as a
  static collection of Canvas/Viewport/Buffer/Visual objects.
- Visuals are described as semantic visual families with conformance contracts, not backend draw
  calls.
- Capability discovery and explicit adaptation are now central to the argument.
- Query/readback is treated as first-class scientific visualization behavior.
- Matplotlib is described as the reference/conformance/publication backend.
- Datoviz v0.4 is described as the flagship high-performance GPU backend.
- VisPy2 is described as the high-level Python producer API, not as the protocol itself.
- Conformance fixtures, visual review packs, diagnostics, and backend capability matrices are now
  part of the credibility story.

## Reused 2023 material

The draft reuses the original decomposition and architecture figures as historical/design material:

- `figures/legacy-plot-decomposition.pdf`
- `figures/legacy-gsp-architecture.pdf`
- `figures/legacy-visualization-pipeline.pdf`

The prose is mostly rewritten. The old requirements section still influenced the new sections on
primitive families, high-quality rendering, transforms, large data, and remote rendering.

## Feedback requested

1. Is the main thesis right: GSP as a semantic graphics server protocol below plotting APIs and
   above concrete renderers?
2. Does the paper understate or overstate the role of anti-aliased GPU primitive rendering?
3. Should the paper foreground Datoviz more strongly, or keep Datoviz as one flagship backend among
   several possible renderers?
4. Does the "semantic visual families" framing match your intent, or should it be closer to
   primitive decomposition?
5. Should the paper include a sharper comparison with ANARI, Vega/Vega-Lite, Matplotlib backends,
   VTK, or browser graphics systems?
6. Is the current authorship framing acceptable: Nicolas P. Rougier and Cyrille Rossant, with this
   draft explicitly derived from the 2023 draft and current GSP implementation/spec work?

## Known rough edges

- Citations are intentionally light in this draft.
- The protocol section is narrative and omits many fields from the current specs.
- The current-status section is compact and should be checked carefully against release claims
  before external circulation.
- The governance/community section is intentionally tentative.
