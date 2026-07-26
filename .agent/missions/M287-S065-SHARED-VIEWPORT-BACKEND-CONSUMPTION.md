# M287 - S065 shared viewport backend consumption

## Status

Approved for execution after M286 was integrated and independently accepted on 2026-07-26.
Execute with the pinned `codex-ucl-gpt-5.6-sol-medium` provider.

## Goal

Make Matplotlib and Datoviz render, query, and navigate against the same resolved plot viewport
without altering canonical camera state or screen-space visual sizes.

## Required scope

In `gsp`:

- Add an optional resolved-layout input to the backend session render/display path without making
  Matplotlib a public protocol dependency.
- Retain Matplotlib as the first layout producer permitted by ADR-0020. A produced snapshot must be
  reusable as an input and reproduce the same axes/guide geometry within tolerance.
- Make Matplotlib honor the scene panel allocation and place its axes at the consumed
  `plot_rect_px`; do not let `add_subplot()` defaults silently replace a supplied layout.
- Keep titles as guide artists positioned from resolved guide geometry. If the producer snapshot
  uses a title lane, consuming the snapshot must preserve that lane.
- Make every Matplotlib 2D/3D projection, aspect calculation, clipping boundary, data query,
  View3D ray, mesh pick, and navigation conversion use the consumed plot rectangle.
- Add partial resolved-layout consumption to the Datoviz adapter. Use only qualified public binding
  APIs to place the visual viewport at the supplied plot rectangle.
- Datoviz must preserve the supplied outer panel/plot distinction in the GSP result and query path
  even if its native panel object represents only the plot viewport.
- Keep Datoviz `PanelTextGuide` unsupported unless a truthful public rendering path exists. Missing
  title rendering must not change the consumed plot rectangle.
- Advertise resolved-layout consumption only at the level actually proven.
- Preserve logical-pixel marker, pixel, text, line, and vector sizing independently of viewport
  dimensions.

The first implementation may be single-panel only. It must reject unsupported multi-panel
consumption explicitly rather than silently selecting a panel.

Datoviz is read-only evidence in this mission. If its current public binding cannot place or clip a
View3D visual viewport at the resolved rectangle, stop with the exact missing native API and propose
a separate Datoviz mission.

## Required tests

- Matplotlib produced-layout round trip: produce, consume, rerender, and compare plot/title boxes.
- Matplotlib default native subplot margins cannot override a consumed plot rectangle.
- Datoviz fake-binding tests prove the exact panel/viewport descriptor values.
- Full and inset panel/plot rectangles.
- Title present and absent.
- Orthographic and perspective View3D.
- Effective aspect stored in the projection snapshot.
- NDC corners and center map to the expected logical pixels.
- A logical coordinate in the title/margin region is outside the data viewport.
- Matplotlib and Datoviz View3D ray contexts agree for the same layout and logical coordinate.
- Mesh-pick/query snapshot staleness changes when layout changes.
- Screen-space visual diameters and stroke widths do not scale with the plot rectangle.
- View2D guide behavior and prior navigation behavior do not regress.

## Acceptance

- Both backends can consume one snapshot and map the same NDC coordinates to the same logical
  viewport.
- Rendering and data-query geometry use the same plot rectangle.
- No canonical camera values are changed to compensate for layout.
- Full GSP tests, strict mypy, Ruff, backend import checks, and diff checks pass.
- An independent supervisor accepts the implementation and capability wording.
- Changes are committed in `gsp`; Mission Control records the evidence.

## Stop conditions

- Stop on any code/spec conflict with M286 or existing accepted layout/View3D authority.
- Stop rather than adding per-backend scale factors, camera-fit compensation, or hard-coded
  800×600 constants.
- Stop before any Datoviz repository edit.
- Stop on a native crash, hang, or missing public viewport API and report exact evidence.
- Do not edit VisPy2, push, merge, tag, release, publish, or change package versions.

## Correction pass after R20260726-132016-M287

The first medium-worker run ended because its Codex response stream disconnected after exhausting
transport retries. Its useful implementation draft is preserved in GSP commit `add9a76` as an
explicit WIP checkpoint. The next worker starts from that commit and must finish the implementation
directly in its provided worktrees. It is already the launched worker: do not call `agentctl launch`
recursively.

The checkpoint is not accepted. The independent supervisor found the following mandatory
corrections:

1. Datoviz consumed-layout creation must fail closed. Preflight and use the qualified public
   `dvz_panel_desc()` plus `dvz_panel()` API. If either API or a usable descriptor is absent, raise an
   exact unsupported diagnostic. Never fall back to `dvz_panel_full()` while retaining or reporting
   a supplied layout snapshot.
2. Validate consumed snapshot coherence before either backend creates resources: active view ID,
   panel ID, single-panel target, render-target logical size, device scale, pixel origin, and scene
   canvas policy. Conflicting scene canvas and snapshot target must reject explicitly or resolve to
   the identical target; Datoviz must not normalize against one target and construct its figure from
   another.
3. All placement and coordinate conversion must branch on `PixelOrigin`. Datoviz's native panel
   descriptor is top-left normalized, so a bottom-left GSP rectangle requires the correct y
   conversion. Matplotlib axes/title placement must also convert origin explicitly. Do not silently
   assume top-left or bottom-left.
4. Datoviz panel queries are plot-local logical pixels. Classify the original outer-panel logical
   coordinate against the consumed snapshot, reject guide/title lanes as DATA misses, translate
   accepted plot coordinates to native plot-local logical pixels, and preserve the original
   coordinate in the result. Do not apply framebuffer scaling to this public logical-pixel API.
5. Reject stale `layout_snapshot_id` before Datoviz DATA query, View3D ray, mesh pick, or navigation.
   Never relabel stale decoded evidence with the current consumed snapshot ID.
6. Replace the Matplotlib and Datoviz duplicated originless View3D
   `_panel_coordinate_to_ndc()`/bounds-only paths with the accepted M286 snapshot-aware conversion.
   TOP_LEFT plot top maps to NDC `+1`; BOTTOM_LEFT plot top maps according to its declared origin.
   Mesh-pick and ray paths must share that conversion. Cross-backend agreement alone is insufficient
   because two duplicated wrong formulas can agree.
7. Datoviz strict View2D navigation must construct `View2DNavigationInputAdapter` with
   `layout_snapshot=renderer.consumed_layout_snapshot`, must not call `set_panel_rect()` in strict
   mode, and must keep snapshot origin/geometry/ID atomic. View3D pan/orbit/zoom must likewise use
   the consumed plot rectangle and ID. Resize must not mutate geometry beneath an unchanged strict
   snapshot ID; either reject/disable strict resize or atomically accept a new snapshot.
8. Preserve the legacy navigation path for renderers without a consumed snapshot. Current checkpoint
   breaks three legacy navigation test doubles by directly requiring
   `renderer.consumed_layout_snapshot`; use a compatible optional access boundary and keep existing
   behavior green.
9. Matplotlib producer mode must honor `Panel.viewport_rect` outer allocation. A renderer that is
   only handed visuals/view cannot satisfy this; pass the relevant scene panel into the producer
   layout path and test full plus inset allocations.
10. Native axes, colorbars, titles, or margins must not shrink or reclaim an already-consumed plot
    rectangle. Reject or explicitly adapt unsupported guide combinations unless exact readback proves
    the native plot remains equal to the supplied plot. A supplied title guide without a matching
    resolved title box must not silently fall back to native placement.
11. Capability claims must match evidence. Matplotlib currently consumes only plot geometry and a
    bounded title slice, so advertise `partial`, not `full`, until all guide/tick/axis/colorbar/legend
    geometry is consumed and proven. Datoviz remains partial with `layout_strict=False` and
    `PanelTextGuide` unsupported.
12. Add the mission's missing tests: panel viewport producer allocation; top-left and bottom-left
    corners/center; title present/absent and guide-lane DATA miss; exact public Datoviz descriptor
    preflight/failure; render-target mismatch; stale query/ray/pick/navigation; orthographic and
    perspective aspect/ray behavior; cross-backend expected NDC/ray values; consumed native
    axes/title-lane non-shrink; opposite-y navigation; and logical-pixel size invariance for marker,
    pixel, text, line, and vector visuals.

Before final acceptance, run the full GSP suite, strict mypy over the complete source set, Ruff,
backend import checks, and `git diff --check`. The supervisor must review the final diff and issue an
unconditional ACCEPT.
