# ADR-0020 - GSP Guide Layout Semantics Boundary

## Status

Accepted

## Context

GSP must support both Matplotlib publication rendering and Datoviz high-performance GPU rendering.
Those backends differ in native title, axis, tick-label, grid, legend, colorbar, DPI, and font
behavior. Pure semantic guide intent is not enough for reproducible publication layout or guide
query/readback, but mandatory pixel-identical layout across all backends would be too costly and
would risk turning GSP into a Matplotlib-layout clone.

The P016 ChatGPT Pro consultation recommended a hybrid model: keep semantic guide records as the
primary scene contract, and add resolved layout snapshots as a first-class optional protocol artifact
for strict layout, query, readback, and review workflows.

## Decision

GSP adopts a hybrid guide/layout model with tiered conformance:

- `semantic_strict`: scene semantics, `View2D` domains, deterministic guide intent, guide identities,
  roles, labels, ticks, grid intent, and supported query semantics match. Pixel placement is not
  required to match across backends.
- `layout_strict`: a backend renders and queries against the same GSP resolved layout snapshot,
  including panel rectangle, plot rectangle, guide boxes, grid clipping, data-to-screen transform,
  and layout snapshot identity.
- `raster_tolerant`: output size, nominal logical sizes, and layout geometry match, while glyph
  rasterization, antialiasing, hinting, and minor subpixel differences remain tolerant.
- Optional `pixel_parity` may be advertised separately by backends or QA jobs that intentionally
  require raster-level parity.

GSP semantics define what exists and what it means. A resolved layout snapshot defines where that
meaning lands for one render target, device scale, font/layout context, and layout policy.

`PanelTextGuide`, `AxisGuide`, `ColorbarGuide`, and legend guides remain guide objects even when a
backend realizes them through native axes, text primitives, images, or other visual primitives. A
backend may adapt a guide into backend-native or screen-space rendering only when it reports that
adaptation explicitly and does not claim layout-strict conformance for the missing semantics.

Render, query, readback, and all-rendered contributions must reference the same `layout_snapshot_id`
whenever a backend advertises layout-strict guide behavior. Layout-strict grid lines are clipped to
the resolved plot rectangle unless a future spec explicitly defines another policy.

## Consequences

Matplotlib remains the initial reference/publication backend for layout-strict behavior, but
Matplotlib native `tight_layout()` is not itself the GSP contract. The backend must expose the
resolved GSP layout used for rendering and guide query/readback.

Datoviz remains the flagship GPU backend, but it should advertise guide/layout support as partial or
adapted until it can produce or consume resolved layout snapshots and provide guide query semantics.
Datoviz review artifacts may render adapted titles or native axes, but those rows must not be counted
as layout-strict passes until the resolved layout and query contract is implemented.

The next specification step is S029: define `RenderTarget`, logical pixels, device scale, DPI,
`ResolvedLayoutSnapshot`, guide boxes, grid clipping, layout snapshot IDs, and layout/query protocol
operations.

## Rejected

Option A, semantic-only GSP with backend-defined layout, was rejected because it leaves plot
rectangles, title placement, grid clipping, and guide query geometry underspecified.

Option B, mandatory resolved pixel layout for every backend as baseline, was rejected because it
imposes excessive implementation burden and risks overfitting the protocol to one backend.

## Source

`.agent/consultations/P016-response.md`.
