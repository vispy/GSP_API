# M286 - S065 resolved plot-viewport contract

## Status

Approved by the owner on 2026-07-25 as the first mission in the M286-M288 correction sequence.
Execute with the pinned `codex-ucl-gpt-5.6-sol-medium` provider. M284 remains open for human review.

First-pass commits were integrated after run `R20260725-173541-M286`:

- GSP: `f7dc8aa`;
- Mission Control: `7723def`.

The first independent supervision audit found the acceptance gaps below. A second pinned-provider
pass was integrated as GSP commit `1ad5d68` and Mission Control commit `f9966be`. Its complete
automated gates passed (722 tests, strict mypy across 51 source files, Ruff, and diff checks), but
independent semantic review rejected completion on the four third-pass blockers recorded below.
M286 remains approved and incomplete.

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

## Supervisor acceptance addendum

The second pass must close all of the following before M286 can complete:

1. Reconcile all affected authority, not only the three first-pass files:
   - `spec/navigation.md` must use `plot_rect_px` for layout-dependent pan/zoom scaling and
     anchors instead of the outer panel rectangle;
   - `spec/current/scene.md` must include `Panel.viewport_rect` as normalized render-target
     allocation intent, distinct from resolved backend geometry;
   - update `spec/current/queries.md` wherever needed to make the panel/guide-lane/plot routing
     result explicit.
2. State that public logical pointer/query coordinates are absolute render-target logical
   coordinates. Panel NDC `[-1,+1]` maps through `plot_rect_px`. For top-left origin, plot
   top-left maps to `(-1,+1)` and bottom-right to `(+1,-1)`; bottom-left origin reverses y.
3. Preserve closed geometric containment for exact NDC edge round trips. Raster sample ownership
   remains backend-private and may be half-open. A degenerate plot contains no data; conversion
   and aspect helpers reject it. The outer panel must be positive-area.
4. Add a typed classifier/helper that distinguishes:
   - outside the outer panel;
   - inside the panel guide lane but outside the plot;
   - inside the data plot.
   Supported data queries in a guide lane return MISS, while GUIDE/ALL_RENDERED may still hit
   guide boxes. No ray or mesh-pick may extrapolate from a guide-lane coordinate.
5. Extend `apply_view3d_navigation_action` with the same optional
   `ResolvedLayoutSnapshot` context and ID-matching compatibility shape as
   `resolve_view3d_projection_snapshot`. Both current and updated projection freshness IDs must
   resolve from that context. Preserve every existing ID-only call.
6. State and test that navigation deltas use plot width/height. Pointer/zoom anchors outside the
   plot are rejected or ignored, never clamped into the plot.
7. Add fixtures for exact corners and center, both pixel origins, closed edges, all three
   coordinate classifications, positive outer-panel validation, guide-lane ray/pick rejection,
   repeated-snapshot stability, changed layout/plot identity, legacy aspect diagnostics, and stale
   layout-resolved navigation rejection.
8. Keep the core snapshot single-panel and explicitly defer aggregate/multi-panel layout.
9. Run the complete GSP suite, strict mypy across all packages, Ruff, and diff checks.

## Third-pass correction addendum

The next pinned `codex-ucl-gpt-5.6-sol-medium` run must close all four blockers below. These are
acceptance requirements, not optional cleanup.

1. Make `Panel.viewport_rect` executable normalized allocation intent:
   - validate every component as finite;
   - require nonnegative `x` and `y`, positive width and height, and closed containment in
     `[0, 1]` (`x + width <= 1`, `y + height <= 1`);
   - add a deterministic Panel-intent-to-logical-outer-panel resolution helper or equivalent
     executable fixture;
   - test a valid inset, exact right/bottom edges, NaN/inf in every slot, negative/zero extents,
     and right/bottom overflow;
   - publicly export any new protocol helper.
2. Make View2D navigation pixel-origin aware while preserving rect-only compatibility:
   - provide a resolved-layout/pixel-origin-aware path for `pan_view2d`, `zoom_view2d_about`, and
     `View2DNavigationInputAdapter`;
   - use `plot_rect_px`, conditional y-anchor mapping, and origin-dependent vertical pan sign;
   - test identical view/plot inputs under TOP_LEFT and BOTTOM_LEFT: a top-edge zoom preserves
     `y_max` versus `y_min` respectively, and equal positive `dy_px` produces opposite signed
     data pan;
   - replace the contradictory unconditional y formula in `spec/navigation.md` with both origin
     cases.
3. Preserve explicit perspective aspect in low-level projection math:
   - `_resolve_perspective_aspect_ratio` must use an authored non-None
     `PerspectiveProjection3D.aspect_ratio` before any caller/layout fallback;
   - test authored `2.0` plus conflicting supplied `1.0` for both project and unproject;
   - test authored None uses a supplied layout aspect and both absent retain the diagnosed
     compatibility value `1.0`.
4. Validate `RenderTarget.pixel_origin` at runtime:
   - explicitly require/coerce `PixelOrigin`;
   - never let an invalid string or type silently behave as BOTTOM_LEFT;
   - add invalid string/type tests.

The second-pass classifier, closed containment, guide-lane conversion rejection, snapshot-aware
View3D navigation freshness, and public exports were independently accepted. Do not regress them.
M287 remains blocked until this third pass and a fresh independent review pass.

## Final freshness correction

The third pass was integrated as GSP commit `da235f2` and Mission Control commit `b3f353e`.
All four third-pass blockers are fixed and its complete gates passed (755 tests, strict mypy across
51 source files, Ruff, and diff checks). Independent review found one final state-transition defect:

- A `View2DNavigationInputAdapter` constructed or updated from a full `ResolvedLayoutSnapshot` can
  later receive `set_panel_rect()`. The current method clears `pixel_origin` but retains the prior
  `_layout_snapshot_id`, so emitted actions falsely claim strict snapshot provenance while using
  different rect-only geometry.

The final pinned `codex-ucl-gpt-5.6-sol-medium` correction must:

1. track whether adapter geometry is snapshot-backed versus the legacy
   `panel_rect + layout_snapshot_id` compatibility shape;
2. preserve the legacy opaque ID when a legacy adapter receives `set_panel_rect()`;
3. for snapshot-backed adapters, preferably reject `set_panel_rect()` and require
   `set_layout_snapshot()` for an atomic rect/origin/identity update (clearing all provenance is an
   acceptable alternative only if documented);
4. add regression tests proving that no action can retain a stale strict snapshot ID after geometry
   changes, and that `set_layout_snapshot()` restores a coherent strict tuple;
5. replace “top edge” wording/tests for BOTTOM_LEFT minimum-y coordinates with
   “origin-side/minimum-y edge,” or test the actual physical top at `y + height`;
6. rerun the complete GSP suite, strict source mypy, Ruff, and diff checks.

M287 remains blocked until independent review accepts this correction.

Run `R20260725-181001-M286` ended before any file changes because its Codex transport exhausted
WebSocket and HTTPS retries during a DNS/network interruption. This is an infrastructure failure,
not an implementation result; relaunch from the unchanged `7c54d8f` / `da235f2` baselines.

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
