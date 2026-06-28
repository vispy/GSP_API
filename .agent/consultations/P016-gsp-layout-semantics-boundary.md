# ChatGPT Pro Consultation: GSP Layout Semantics Boundary

## Prompt to paste into ChatGPT Pro

```text
We are working on GSP / VisPy2, a backend-independent Graphics Server Protocol for scientific visualization.

Project context:
- Mission: define a semantic visualization protocol that can target Matplotlib as reference/publication backend, Datoviz v0.4 as flagship GPU backend, remote renderers, and future web/browser paths.
- Non-negotiable principles include:
  - GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
  - Capability discovery and explicit adaptation are mandatory.
  - Visual families are semantic contracts, not backend draw calls.
  - Matplotlib is the reference/conformance/publication backend.
  - Datoviz v0.4 is the flagship GPU backend.
- Current protocol accepts semantic visual families such as PointVisual, MarkerVisual, SegmentVisual, PathVisual, ImageVisual, TextVisual, MeshVisual, ColorScale/ColorbarGuide, View2D, AxisGuide, PanelTextGuide.
- Coordinate spaces are currently `NDC` and `DATA`.
- Units already specified:
  - point/marker sizes are rendered screen-pixel diameters;
  - segment/path widths are rendered screen-pixel stroke widths;
  - TextVisual `font_size_px` values are logical screen-pixel font sizes;
  - marker stroke width is rendered screen-pixel stroke width.
- Matplotlib converts screen pixels to points via figure DPI.
- Datoviz uses `*_px` attributes where exposed.

Relevant accepted/working spec facts:
- Matplotlib backend is the strict reference for S027 transform/view and S028 guide/View2D semantics.
- S028 guide/View2D reference target for Matplotlib says guide rendering/query must:
  - resolve x guide ticks from View2D.xlim and y guide ticks from View2D.ylim;
  - accept reversed finite limits;
  - preserve explicit ticks and labels;
  - use deterministic GSP auto ticks rather than Matplotlib locators as semantic authority;
  - use the same View2D snapshot for guide rendering/query/readout;
  - keep Matplotlib axis artists as backend realization details.
- Visual QA spec says Datoviz guide/View2D QA remains capability-gated and Datoviz guide rows may render as `adapted` review artifacts when native axes consume the same View2D domains and missing guide semantics are reported as diagnostics. Guide query, all-rendered guide contributions, and panel title layout remain explicit missing semantics until the backend proves them or the GSP contract excludes them.

Observed issue prompting this consultation:
- A review example creates the same GSP scene for Matplotlib and Datoviz:
  - data points in DATA;
  - View2D x_range=(-2.5, 2.5), y_range=(0.0, 2.2);
  - x/y AxisGuide with labels/grid;
  - PanelTextGuide role=TITLE, text="Basic scatter";
  - point sizes in pixels.
- Matplotlib renders a 900x650 PNG with the title above the axes/plot area because Matplotlib native axes layout reserves top margin and `tight_layout()` handles text.
- Datoviz renders a 900x650 PNG too, so the output image size is not smaller, but its plot area/grid nearly fills the panel and title placement initially overlapped or sat inside the plot. Axis/tick text looked thinner/smaller because Datoviz font/rasterization and axis defaults differ.
- We found several backend realization gaps:
  1. Datoviz native axes have style fields (`tick_size_px`, `label_size_px`, tick lengths, margins) but the GSP adapter was not fully specifying them.
  2. GSP PanelTextGuide title was being temporarily adapted into a TextVisual. Datoviz retained text supports SCREEN/DATA placement, not the same exact NDC attachment semantics as other visuals.
  3. Datoviz axis plot margins affect data mapping, but its grid implementation can still span through areas that Matplotlib would reserve for title/labels.
  4. Workarounds like adding a white overlay title band or hand-tuned constants improve review artifacts but feel like backend-specific patches rather than durable protocol semantics.

Decision needed:
Should GSP remain primarily semantic and deliberately leave pixel layout to backend capabilities, or should GSP define enough resolved layout/pixel geometry for guides, titles, axes, ticks, labels, legends, colorbars, and plot rectangles to make backend outputs visually comparable?

Please analyze the long-term design options below and recommend one:

Option A: Semantic-only guides
- GSP specifies only semantic intent: title text, axis labels, tick values/labels, grid intent, View2D domains.
- Backends choose native layout and font metrics.
- Pixel-perfect or near-pixel layout parity is not part of strict conformance.
- Visual QA compares semantic/readback properties, not precise placement.
- Matplotlib and Datoviz may legitimately differ visually.

Option B: Resolved layout as part of protocol/conformance
- GSP adds a backend-independent layout pass that resolves figure/panel/plot rectangles, title rectangles, axis-label rectangles, tick-label lanes, legend/colorbar rectangles, text sizes, grid clipping, and z/layer ordering.
- Backends render resolved geometry, so strict conformance is closer to visual parity.
- Producer can send semantic intent; server may resolve layout, but resulting resolved layout is inspectable and queryable.
- Requires substantial spec, implementation, conformance fixture, and capability work.

Option C: Hybrid tiers
- GSP has semantic guide objects as the primary protocol.
- It adds optional/resolved layout artifacts for strict/reference rendering and publication modes.
- Strict conformance tiers:
  - semantic strict: same data domains, ticks, labels, guide identities, query/readout semantics;
  - layout strict: resolved plot/title/axis rectangles and grid clipping match a GSP layout model;
  - raster tolerant: font rasterization/antialiasing can differ within tolerance unless backend opts into pixel-baseline parity.
- Matplotlib can be the initial layout-reference backend.
- Datoviz can advertise `adapted` for guides until it supports layout strictness or consumes resolved layout.

Constraints:
- GSP should remain backend independent and transport independent.
- Local fast path must not require JSON/base64.
- Capability discovery and adaptation diagnostics are required.
- Visual families are semantic contracts, not backend draw-call parameters.
- Matplotlib is reference/conformance/publication backend.
- Datoviz is high-performance GPU backend and may not naturally match Matplotlib's layout engine.
- GSP should support scientific visualization: publication-quality static output and fast interactive GPU rendering both matter.
- Query/readback is first-class. Guide query and all-rendered query semantics matter.

Questions to answer:
1. Which option should the project choose long term, and why?
2. What is the precise boundary between "GSP semantic spec" and "resolved pixel layout"?
3. Should title/axis/legend/colorbar layout be part of protocol records, a derived server-side layout result, or only conformance artifacts?
4. Should strict conformance require visually identical title/axis placement across Matplotlib and Datoviz?
5. How should DPI/device-scale/font metrics be specified? What can be strict, tolerant, or backend-defined?
6. How should guide query semantics relate to resolved layout?
7. What minimal spec changes should be made now to avoid accumulating backend-specific hacks?
8. What should the Datoviz adapter advertise until it supports the chosen level of layout strictness?
9. What tasks should be created next?

Please produce the expected output format below.
```

## Expected output format

```markdown
# Consultation Result: GSP Layout Semantics Boundary

## Recommendation

Choose Option A/B/C, with any refinements.

## Rationale

Explain tradeoffs for protocol purity, publication rendering, interactive GPU rendering, conformance, capability negotiation, and implementation cost.

## Contract Boundary

State what GSP must specify semantically, what resolved layout artifacts must exist, and what remains backend-defined/tolerant.

## DPI, Fonts, And Pixels

State recommended semantics for logical pixels, device scale, DPI, font size, font family, font metrics, antialiasing, and acceptable tolerance.

## Guide And Query Semantics

State how title/axis/tick/grid/legend/colorbar guide rendering relates to query/readback and all-rendered queries.

## Spec Changes

- file: spec/protocol.md or new spec/layout.md
  change: ...
- file: spec/backends/matplotlib.md
  change: ...
- file: spec/backends/datoviz.md
  change: ...
- file: spec/visual_qa_harness.md
  change: ...
- file: SPEC_INDEX.md
  change: ...

## Capability Model Changes

List any new capability fields, tiers, diagnostic statuses, or review-pack classifications.

## Task Changes

- create/update task: ...

## Risks

List technical and project risks.

## Decision Record Draft

ADR-style bullet list or draft text suitable for an accepted decision.
```

