# M286 - S065 resolved plot-viewport contract

## Status

Approved by the owner on 2026-07-25 as the first mission in the M286-M288 correction sequence.
Execute with the pinned `codex-ucl-gpt-5.6-sol-medium` provider. M284 remains open for human review.

## Context and confirmed defect

The M285 review pack uses equal 800×600 framebuffers, but guide-free Matplotlib View3D geometry is
about 1.29 times smaller than Datoviz geometry. Matplotlib maps panel NDC through its default
approximately 620×462 subplot plot rectangle, while Datoviz maps through its full 800×600 panel.
This is not a camera-state or camera-fit difference.

The deeper implementation mismatch is:

- `Panel.viewport_rect` is not consumed by the main Matplotlib or Datoviz render paths;
- Matplotlib rendering uses its native axes/plot rectangle, while its View3D query path converts
  panel coordinates through the full `panel_rect_px`;
- Datoviz rendering and query use the full native panel;
- `PerspectiveProjection3D(aspect_ratio=None)` is projected using a backend-local rectangle, while
  `View3DProjectionSnapshot.aspect_ratio` remains `None` instead of recording the resolved value;
- `LayoutResolveRequest` and resolved-layout consume capabilities exist but are not connected to
  backend session rendering.

Authority already requires one resolved layout snapshot to govern render, query, and readback:
`spec/current/views-layout.md`, `spec/layout.md`, `spec/view3d.md`, ADR-0020, and the accepted S043
Datoviz panel-frame decision. Do not create a competing layout model.

## Goal

Make the distinction between outer panel geometry and the data/3D plot viewport executable in the
GSP protocol, and provide backend-neutral conversion/projection fixtures that M287 can consume.

## Required protocol decisions

Record these decisions in the authoritative specification and one durable S065 decision record:

1. `Panel.viewport_rect` allocates the outer panel inside the resolved render target.
2. `ResolvedLayoutSnapshot.panel_rect_px` is the complete panel presentation and guide-query region.
3. `ResolvedLayoutSnapshot.plot_rect_px` is the visual viewport after guide/layout allocation.
4. DATA and panel-NDC visual positions map through `plot_rect_px`, not through the whole canvas or
   the outer panel rectangle.
5. Perspective aspect resolution for `aspect_ratio=None` uses
   `plot_rect_px.width / plot_rect_px.height`.
6. An explicitly authored positive perspective aspect remains an explicit projection input; the
   snapshot must distinguish it from a layout-resolved aspect.
7. Data queries, View3D rays, mesh picking, and layout-dependent navigation use `plot_rect_px`.
   Coordinates inside `panel_rect_px` but outside `plot_rect_px` cannot hit data visuals; guide
   queries may still use guide boxes in the outer panel.
8. The resolved projection snapshot records the effective perspective aspect ratio and changes
   identity when the effective plot viewport changes.
9. `PanelTextGuide` remains a guide. A backend that cannot render it may still consume the same
   resolved plot rectangle and must report the missing guide rather than changing visual scale.
10. Layout-strict or cross-backend comparison uses one produced `ResolvedLayoutSnapshot` consumed
    by every backend. Semantic-only rendering may remain backend-resolved with diagnostics.

## Required implementation

In `gsp`:

- Strengthen `ResolvedLayoutSnapshot` validation so the panel and plot rectangles are finite,
  nonnegative, inside the render target, and the plot rectangle is contained by the panel.
- Add small typed protocol helpers for:
  - plot logical pixel ↔ panel-NDC conversion;
  - resolved plot aspect ratio;
  - testing whether a logical coordinate is inside the data viewport.
- Extend View3D projection snapshot resolution so a strict layout context supplies the effective
  plot aspect and the snapshot stores it. Preserve an explicitly authored aspect and keep a
  clearly diagnosed compatibility path for old callers that provide only an ID.
- Ensure snapshot identity hashes all effective projection inputs, including the resolved aspect.
- Add conformance fixtures for full and inset plot rectangles, title-lane space, non-full panels,
  perspective projection/unprojection, stale layout identity, and outside-plot data coordinates.
- Do not implement backend layout consumption in this mission.

In Mission Control:

- Update `spec/current/views-layout.md`, `spec/layout.md`, and `spec/view3d.md`.
- Add `.agent/decisions/S065_resolved_plot_viewport.md` with the accepted boundary, staged
  producer/consumer plan, and deferred multi-panel/font-layout work.

## Acceptance

- The protocol has one unambiguous rectangle for visual projection and data queries.
- Effective perspective aspect is inspectable and snapshot-identified.
- Pure protocol project/unproject and logical-pixel/NDC round trips pass for full, inset, and
  non-square plot rectangles.
- Outside-plot coordinates are distinguishable from outside-panel coordinates.
- Existing compatible call sites and tests remain green or receive a precise migration.
- Full `gsp-core` tests, strict mypy, Ruff, and diff checks pass.
- Changes are committed separately in every writable repository.

## Stop conditions

- Stop on conflict with PROJECT_CHARTER, ARCHITECTURE, accepted ADR-0020, or accepted View3D
  projection semantics.
- Stop rather than introducing backend names or Matplotlib native axes concepts into public GSP.
- Stop rather than choosing backend-specific scale constants, camera margins, or gallery-only
  aspect overrides.
- Stop if the change requires a new public multi-panel layout authoring API; record that as deferred
  work instead.
- Do not edit Datoviz or VisPy2, push, merge, tag, release, publish, or change package versions.

