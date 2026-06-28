# S029 Resolved Layout Contract Decisions

Status: accepted direction from P016 response; full S029 specification pending.

## Accepted

- GSP uses a hybrid guide/layout model: semantic guide records are the primary scene contract, and
  resolved layout snapshots are first-class derived protocol artifacts for layout-strict rendering,
  query, readback, and conformance.
- Conformance is tiered into `semantic_strict`, `layout_strict`, `raster_tolerant`, and optional
  `pixel_parity`.
- Semantic strictness does not require visually identical guide placement across Matplotlib, Datoviz,
  or future backends.
- Layout strictness requires rendering and querying against the same resolved layout snapshot.
- A future `ResolvedLayoutSnapshot` must include at least render target metadata, panel and plot
  rectangles, data-to-screen transform, guide boxes/anchors, tick/label/title boxes, legend and
  colorbar boxes, grid clipping rectangle, z/layer information, diagnostics, and a stable snapshot id.
- Logical pixels are distinct from physical framebuffer pixels. A render target must distinguish
  logical dimensions, `device_scale`, DPI metadata, pixel origin, and query coordinate space.
- Guide records remain guides even when a backend realizes them with native axes, screen text, image
  ramps, or other implementation primitives.
- Backend-specific guide adaptations must be reported explicitly and must not count as layout-strict
  passes.

## Capability-Gated

- Matplotlib is the initial reference/publication backend for layout-strict behavior, but its native
  layout engine is an implementation mechanism, not the abstract GSP contract.
- Datoviz guide/layout support is partial or adapted until it can produce or consume resolved layout
  snapshots and provide guide query semantics from the same snapshot.
- Datoviz titles rendered as screen text are acceptable review artifacts only when reported as
  adapted panel-text-guide realization.
- Datoviz grid clipping, guide query, all-rendered guide contributions, font metrics parity, and
  raster pixel parity remain capability-gated.

## Deferred

The full S029 spec should define `RenderTarget`, logical-pixel semantics, device-scale/DPI
conversion, layout resolve/get operations, `layout_snapshot_id` propagation through render/query, the
minimal `ResolvedLayoutSnapshot` schema, guide style fields, grid clipping rules, tiered visual QA
checks, and backend capability records.

## Source

`.agent/consultations/P016-response.md` converted into ADR-0020 and this decision note.
