# Notes for Nicolas

This is a first serious 2026 GSP white paper draft for review by Nicolas Rougier and Cyrille
Rossant.

## Intent

The draft presents GSP as a shared protocol layer for scientific visualization, not as a plotting
API and not as a replacement renderer. The target reader is a technically sophisticated scientific
visualization library developer.

## Current framing

- GSP is a semantic graphics server protocol below plotting APIs and above concrete renderers.
- Visuals are described as semantic visual families with conformance contracts, not backend draw
  calls.
- Capability discovery and explicit adaptation are central to the argument.
- Query/readback is treated as first-class scientific visualization behavior.
- Matplotlib is described as the reference/conformance/publication backend.
- Datoviz v0.4 is described as the flagship high-performance GPU backend.
- VisPy2 is described as the high-level Python producer API, not as the protocol itself.
- Conformance fixtures, visual review packs, diagnostics, and backend capability matrices are part
  of the credibility story.

## Feedback requested

1. Is the main thesis right: GSP as a semantic graphics server protocol below plotting APIs and
   above concrete renderers?
2. Does the paper understate or overstate the role of anti-aliased GPU primitive rendering?
3. Should the paper foreground Datoviz more strongly, or keep Datoviz as one flagship backend among
   several possible renderers?
4. Does the "semantic visual families" framing match your intent, or should it be closer to
   primitive decomposition?
5. Are the illustrative code/protocol snippets helpful, or should they be reduced to avoid looking
   like API reference?
6. Should the related-work section include a sharper comparison with ANARI, Vega/Vega-Lite,
   Matplotlib backends, VTK, WebGPU, or browser graphics systems?
7. Is the current authorship framing acceptable: Nicolas P. Rougier and Cyrille Rossant as
   coauthors?

## Known rough edges

- The citations are better than the first draft, but still not exhaustive.
- The protocol snippets are illustrative and should be checked for tone: concrete enough to be
  useful, but not presented as stable API.
- The current-status section should be checked carefully against release claims before external
  circulation.
- The governance/community section is intentionally tentative.
