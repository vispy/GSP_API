# M287 - S065 shared viewport backend consumption

## Status

Owner-approved implementation direction; blocked until M286 is integrated and independently
accepted. Execute with the pinned `codex-ucl-gpt-5.6-sol-medium` provider.

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

