# Consultation Result: GSP Layout Semantics Boundary

## Recommendation

Choose **Option C: Hybrid tiers**, with one refinement:

**Semantic guide records remain the primary GSP contract, but resolved layout must become a first-class optional protocol artifact for publication, strict review, and query/readback.**

Do **not** make every backend reproduce Matplotlib’s native layout engine. Also do **not** leave guide geometry completely undefined. GSP should define a tiered contract:

1. **Semantic strict**

   * Same scene semantics.
   * Same `View2D` domains.
   * Same deterministic ticks and labels.
   * Same guide identities, roles, labels, grid intent, and query/readback semantics where supported.
   * No requirement that title, axis labels, tick labels, or colorbars land at the same pixels.

2. **Layout strict**

   * A GSP layout model resolves panel, plot, guide, title, label, tick, legend, and colorbar rectangles in logical pixels.
   * Rendering and query use the same resolved layout snapshot.
   * Grid and data transforms are clipped/mapped using the resolved plot rectangle.
   * Backends must either consume the resolved layout or explicitly report adaptation.

3. **Raster tolerant**

   * Stroke widths, marker sizes, font sizes, and geometry are checked in logical pixel units.
   * Exact glyph rasterization, antialiasing, subpixel hinting, and font rendering may differ within tolerance.
   * Pixel-baseline parity is a separate opt-in capability, not general conformance.

This preserves GSP as a semantic visualization protocol while acknowledging that scientific visualization also needs reproducible publication layout.

## Rationale

**Option A is too weak long term.**
A purely semantic guide contract allows Matplotlib and Datoviz to differ legitimately, but it leaves no durable answer for questions such as:

* Is the title inside or outside the plot area?
* Does the grid stop at the plot rectangle or continue through reserved label/title space?
* What rectangle defines the `DATA` to screen transform?
* What guide object should a screen-coordinate query return?
* Is an overlay title band a legitimate layout implementation or just a visual patch?

Without a resolved layout concept, backend-specific hacks accumulate because every adapter invents its own answer.

**Option B is too heavy as the default.**
Making full resolved pixel layout mandatory for all strict conformance would turn GSP into a cross-backend page-layout engine. That would raise the cost for GPU and remote backends, overfit the protocol to Matplotlib-like layout behavior, and make Datoviz-style native fast rendering look permanently non-conforming even when it satisfies the important interactive semantics.

**Option C matches the project’s dual mission.**
GSP needs both publication-quality reference rendering and high-performance interactive rendering. These are not the same tier. Matplotlib can initially be the reference implementation for publication/layout behavior, while Datoviz can remain the flagship GPU backend with explicit capability-gated adaptation until it can consume or produce resolved layout.

The key principle should be:

> GSP semantics define what the visualization means. Resolved layout defines where that meaning lands for a particular render target, viewport, DPI/device scale, font context, and layout policy.

That resolved result should be inspectable and queryable, not hidden inside backend heuristics.

## Contract Boundary

### GSP semantic spec must define

GSP should strictly define the semantic guide objects and their relationship to views:

* `View2D.xlim`, `View2D.ylim`, including reversed finite limits.
* Deterministic GSP tick generation.
* Explicit tick value and label preservation.
* Axis identity, orientation, label text, tick text, grid intent, and associated `View2D`.
* `PanelTextGuide` identity, role, text, and attachment semantics.
* Legend and colorbar semantic association with visuals/scales.
* Logical pixel units for sizes, widths, font sizes, paddings, and margins when specified.
* Query/readback identity: guides are queryable semantic objects, not anonymous backend decoration.
* The rule that guide rendering, guide query, data readout, and all-rendered query must use the same view/layout snapshot.

For the observed example, the semantic spec should say:

* The data points are in `DATA`.
* The `View2D` domain is `x=(-2.5, 2.5)`, `y=(0.0, 2.2)`.
* The title is a `PanelTextGuide(role=TITLE)`.
* Axis guides are guides associated with the `View2D`.
* The grid belongs to the plot/data rectangle, not to arbitrary panel background.
* Point sizes are logical screen-pixel diameters.

### Resolved pixel layout must define

A resolved layout snapshot should exist for layout-strict rendering. It should be a derived protocol artifact, not merely a backend side effect.

A minimal `ResolvedLayoutSnapshot` should include:

* Render target logical size, for example `900 x 650`.
* Device scale, for example `1.0`, `2.0`, etc.
* DPI metadata/conversion context.
* Panel rectangle in logical pixels.
* Plot/data rectangle in logical pixels.
* Data-to-logical-pixel transform for each `View2D`.
* Axis guide lanes:

  * tick mark geometry,
  * tick label rectangles,
  * axis label rectangles,
  * spine/baseline geometry where applicable.
* Title rectangles and anchors.
* Grid clipping rectangle.
* Legend rectangles.
* Colorbar rectangles, including ramp, ticks, tick labels, and label.
* Z/layer ordering for guides relative to data visuals.
* Stable IDs linking resolved layout elements back to semantic guide IDs.
* A layout snapshot ID used by render, query, and readback.

This does not mean every backend must implement the full layout solver immediately. It means the protocol has a place to put the answer.

### Backend-defined or tolerant behavior

The following should remain backend-defined unless a stricter capability is advertised:

* Default font family when none is specified.
* Font fallback and glyph substitution.
* Exact glyph rasterization.
* Antialiasing.
* Text hinting.
* Subpixel rounding.
* Native axis aesthetics not specified by GSP.
* Interactive label collision avoidance, elision, or simplification outside layout-strict mode.
* GPU-specific text rasterization differences.

The important distinction is that backend-defined behavior must be **reported**, not silently treated as strict equivalence.

## DPI, Fonts, And Pixels

GSP should explicitly separate **logical pixels**, **device pixels**, and **DPI metadata**.

### Logical pixels

All existing `*_px` units should mean **logical screen pixels**:

* point diameter,
* marker diameter,
* marker stroke width,
* segment/path stroke width,
* text `font_size_px`,
* tick size,
* tick length,
* tick label padding,
* guide margins,
* layout rectangles.

A `900 x 650` render target is therefore `900 x 650` logical pixels.

### Device scale

Add a render target field such as:

```text
device_scale: float
```

Physical framebuffer size is:

```text
physical_width_px  = logical_width_px  * device_scale
physical_height_px = logical_height_px * device_scale
```

For ordinary PNG review output, `device_scale = 1.0` is enough. Retina/high-DPI interactive windows may use `device_scale = 2.0` or similar.

Queries should default to logical pixel coordinates. If physical-pixel queries are allowed, the query request must declare the coordinate space.

### DPI

DPI should be part of the render target context, but it should not redefine GSP logical pixels.

For Matplotlib:

```text
points = logical_px * 72 / dpi
```

So a `font_size_px=14` at `dpi=100` becomes approximately `10.08 pt`.

For Datoviz:

```text
backend_px = logical_px * device_scale
```

unless Datoviz itself already interprets the value as logical window pixels, in which case the adapter must document that conversion.

DPI should be strict for:

* Matplotlib pixel-to-point conversion,
* raster output size,
* image metadata where applicable,
* publication export reproducibility.

DPI should not be used to excuse different semantic sizes.

### Fonts

GSP should support three font levels:

1. **Unspecified font**

   * Backend chooses.
   * Font metrics are backend-defined.
   * Raster comparison is tolerant.
   * Backend must expose the chosen font/fallback in readback if possible.

2. **Requested font family/style**

   * GSP records a preferred family, weight, style, and size.
   * Backend may substitute if unavailable.
   * Substitution must be reported.

3. **Layout-strict font metrics profile**

   * The resolved layout snapshot includes measured text bounding boxes.
   * Layout comparison uses those boxes and anchors.
   * Backends need not rasterize glyphs identically, but they must respect the resolved boxes/anchors closely enough to avoid layout drift.

Recommended strictness:

* Layout rectangle origins/sizes: within about `0.5` logical px.
* Tick/grid/data transform positions: within about `0.5` logical px.
* Stroke widths and marker sizes: within existing visual QA tolerance.
* Text bounding boxes: layout-strict comparison should use resolved boxes, with a small tolerance, but actual glyph pixels remain raster-tolerant.
* Pixel-perfect text parity: separate capability, not required.

## Guide And Query Semantics

Guide rendering and query/readback should be tied to the same snapshot.

For every rendered frame or static output, the backend should be able to report:

```text
rendered_scene_id
view_snapshot_id
layout_snapshot_id, if any
capability_tier_used
adaptation_diagnostics
```

### Axis guides

Axis guide query should be defined over resolved guide geometry when layout is available.

A screen-coordinate query should be able to return:

* plot/data region hit,
* x-axis tick hit,
* y-axis tick hit,
* tick label hit,
* axis label hit,
* gridline hit if applicable,
* spine/baseline hit if represented,
* guide ID,
* associated `View2D`,
* associated tick value where applicable.

If no resolved layout exists, the backend may provide native guide query only if it can prove equivalent semantics. Otherwise it must report guide query as missing or adapted.

### Grid clipping

In layout-strict mode, grid lines should be clipped to the resolved plot rectangle unless the spec adds an explicit alternate policy.

A Datoviz grid that spans through title or label space is therefore not layout-strict. A white overlay band that merely hides the grid is also not a semantic substitute unless the rendered/query model says the grid does not exist under that band.

### Titles

`PanelTextGuide(role=TITLE)` should not be silently lowered to a generic `TextVisual`.

It may be implemented using backend text primitives, but semantically it remains a guide with:

* guide ID,
* panel association,
* role,
* layout participation,
* resolved rectangle/anchor in layout-strict mode,
* query/readback contribution.

If Datoviz temporarily renders it as screen text, that is acceptable only as an explicit adaptation.

### Legends and colorbars

Legends and colorbars should follow the same model:

* semantic guide record as input,
* resolved boxes/lanes/ramp/ticks as layout result,
* queryable guide contributions,
* capability-gated rendering.

A colorbar is not just an image plus labels. It is a guide associated with a color scale, and its ticks, labels, ramp rectangle, title/label, and query behavior should be inspectable.

## Spec Changes

* file: `spec/protocol.md` or new `spec/layout.md`
  change: Add a formal distinction between `semantic strict`, `layout strict`, and `raster tolerant` conformance. Define `ResolvedLayoutSnapshot` as a first-class derived protocol artifact.

* file: `spec/protocol.md` or new `spec/layout.md`
  change: Add `RenderTarget` fields:

  ```text
  logical_width_px
  logical_height_px
  device_scale
  dpi
  pixel_origin
  query_coordinate_space
  ```

* file: `spec/protocol.md` or new `spec/layout.md`
  change: Define logical pixel semantics for all `*_px` values, including guide font sizes, tick lengths, tick widths, paddings, margins, and layout rectangles.

* file: `spec/protocol.md` or new `spec/layout.md`
  change: Add protocol operations or records equivalent to:

  ```text
  layout/resolve
  layout/get
  render/layout_snapshot_id
  query/layout_snapshot_id
  ```

  Exact names can vary, but render and query must identify the same layout snapshot.

* file: `spec/protocol.md` or new `spec/layout.md`
  change: Define minimal `ResolvedLayoutSnapshot` schema:

  ```text
  snapshot_id
  render_target
  panel_rect_px
  plot_rect_px
  view_id
  data_to_screen_transform
  guide_boxes
  guide_anchors
  tick_label_boxes
  axis_label_boxes
  title_boxes
  legend_boxes
  colorbar_boxes
  grid_clip_rect_px
  z_layers
  diagnostics
  ```

* file: `spec/protocol.md`
  change: Clarify that `PanelTextGuide` is a guide, not a `TextVisual`, even if an adapter realizes it using backend text primitives.

* file: `spec/protocol.md`
  change: Add guide style fields where currently implicit:

  ```text
  title_font_size_px
  axis_label_font_size_px
  tick_label_font_size_px
  tick_length_px
  tick_width_px
  tick_label_padding_px
  axis_label_padding_px
  grid_width_px
  guide_margin_px
  ```

  Unspecified values may use backend defaults in semantic mode but must be resolved/read back in layout mode.

* file: `spec/protocol.md`
  change: Define default grid clipping as `plot_rect_px` in layout-strict mode.

* file: `spec/backends/matplotlib.md`
  change: State that Matplotlib is the initial reference/publication backend for layout-strict behavior, but Matplotlib native `tight_layout()` is not itself the abstract protocol contract. The backend must expose the resolved GSP layout snapshot used for rendering.

* file: `spec/backends/matplotlib.md`
  change: Require Matplotlib to use the same `View2D` and `ResolvedLayoutSnapshot` for rendering, guide query, and readback. Axis artists remain realization details.

* file: `spec/backends/matplotlib.md`
  change: Specify pixel-to-point conversion:

  ```text
  points = logical_px * 72 / dpi
  ```

* file: `spec/backends/datoviz.md`
  change: Require the Datoviz adapter to advertise guide/layout support precisely:

  ```text
  guide_semantics: partial/adapted
  resolved_layout_produce: false initially
  resolved_layout_consume: false or partial initially
  guide_query: false initially
  all_rendered_guides_query: false initially
  panel_text_layout: adapted
  grid_clip_to_plot_rect: unsupported or partial
  font_metrics_parity: false
  ```

* file: `spec/backends/datoviz.md`
  change: Require the adapter to set exposed native axis style fields when GSP supplies corresponding guide style values:

  ```text
  tick_size_px
  label_size_px
  tick_length_px
  tick_width_px
  margins
  ```

  Missing mappings must be diagnostics, not silent visual differences.

* file: `spec/backends/datoviz.md`
  change: Forbid silent lowering of `PanelTextGuide(role=TITLE)` to a plain `TextVisual` in conformance mode. Allow it only as:

  ```text
  adapted: panel_text_guide_as_screen_text
  ```

* file: `spec/visual_qa_harness.md`
  change: Split guide QA into:

  ```text
  semantic guide QA
  resolved layout QA
  raster tolerant QA
  adapted review artifacts
  ```

* file: `spec/visual_qa_harness.md`
  change: Add checks for:

  ```text
  plot_rect_px
  title_rect_px
  axis_label_rect_px
  tick_label_rect_px
  grid_clip_rect_px
  data_to_screen_transform
  guide query contribution
  all-rendered guide contribution
  layout_snapshot_id consistency
  ```

* file: `spec/visual_qa_harness.md`
  change: Classify white overlay title bands or hand-tuned backend constants as review-only unless they are generated from a resolved layout snapshot and participate in query/readback.

* file: `SPEC_INDEX.md`
  change: Add a layout semantics entry, for example:

  ```text
  S029 Resolved Layout, Logical Pixels, And Guide Geometry
  ```

  and list dependencies from S027 transforms/View2D and S028 guide/View2D semantics.

## Capability Model Changes

Add capability fields similar to:

```text
layout:
  semantic_guides: true | false
  resolved_layout_produce: none | partial | full
  resolved_layout_consume: none | partial | full
  layout_strict: true | false
  raster_pixel_parity: true | false
```

```text
guides:
  axis:
    native: true | false
    explicit_ticks: true | false
    deterministic_gsp_ticks: true | false
    labels: true | false
    grid: true | false
    grid_clip_to_plot_rect: true | false
    query: true | false
  panel_text:
    title: native | resolved | adapted | unsupported
    participates_in_layout: true | false
    query: true | false
  colorbar:
    native | resolved | adapted | unsupported
    query: true | false
  legend:
    native | resolved | adapted | unsupported
    query: true | false
```

```text
fonts:
  logical_font_size_px: true | false
  font_family_request: true | false
  font_fallback_report: true | false
  text_measurement: none | backend | reference
  font_metrics_profile: none | backend_defined | gsp_reference
  rasterization_parity: true | false
```

```text
render_target:
  logical_pixels: true | false
  device_scale: true | false
  dpi_metadata: true | false
  physical_framebuffer_scale: true | false
```

```text
query:
  screen_logical_px: true | false
  data_readout_uses_view_snapshot: true | false
  guide_query: true | false
  all_rendered_guides: true | false
  reports_layout_snapshot_id: true | false
```

Recommended diagnostic statuses:

```text
native
resolved
adapted
degraded
unsupported
missing
backend_default_used
font_substituted
layout_snapshot_not_used
query_semantics_missing
grid_clip_not_enforced
```

Recommended review-pack classifications:

```text
pass.semantic_strict
pass.layout_strict
pass.raster_tolerant
review.adapted
review.native_backend
fail.semantic
fail.layout
fail.query
unsupported.capability
```

## Task Changes

* create task: **ADR: Choose hybrid semantic/resolved layout model**

  * Record Option C as accepted.
  * Define semantic strict, layout strict, and raster tolerant tiers.
  * State that global pixel-identical parity is not required.

* create task: **Spec S029: Resolved Layout Snapshot**

  * Define `RenderTarget`.
  * Define logical pixels, device scale, and DPI.
  * Define `ResolvedLayoutSnapshot`.
  * Define guide boxes, plot rectangles, grid clipping, and layout snapshot IDs.

* create task: **Spec: Guide style fields**

  * Add title, axis label, tick label, tick length, tick width, padding, margin, and grid width fields.
  * Define unspecified style behavior and readback requirements.

* create task: **Protocol: layout resolve/query operations**

  * Add `layout/resolve` and `layout/get` or equivalent.
  * Require render/query/readback to report the layout snapshot used.

* create task: **Matplotlib backend: layout reference implementation**

  * Produce resolved layout snapshots.
  * Use deterministic GSP ticks.
  * Convert px to points by DPI.
  * Ensure guide query/readback references the same snapshot used for rendering.

* create task: **Matplotlib backend: stop treating native axes layout as hidden authority**

  * `tight_layout()` may remain an implementation mechanism temporarily.
  * The conformance artifact must expose the resolved GSP layout.

* create task: **Datoviz backend: guide capability audit**

  * Enumerate native axis fields currently available.
  * Map GSP style fields to Datoviz `*_px` and margin fields where possible.
  * Report all missing fields as diagnostics.

* create task: **Datoviz backend: adapted title handling**

  * Keep `PanelTextGuide(role=TITLE)` as a guide identity.
  * If rendered through screen text, mark as adapted.
  * Do not claim layout participation or guide query until implemented.

* create task: **Datoviz backend: grid clipping investigation**

  * Determine whether native Datoviz grid can be clipped to resolved plot rectangle.
  * If not, report `grid_clip_not_enforced`.
  * Avoid white overlay bands in strict artifacts.

* create task: **Visual QA: tiered guide fixtures**

  * Add fixtures for:

    * one-panel scatter with title,
    * reversed axes,
    * explicit ticks and labels,
    * auto GSP ticks,
    * grid clipping,
    * axis labels,
    * colorbar,
    * legend,
    * resized viewport,
    * non-1.0 device scale.

* create task: **Visual QA: query fixtures**

  * Query inside plot rectangle.
  * Query on title.
  * Query on tick label.
  * Query on axis label.
  * Query on colorbar ramp and colorbar tick.
  * Query all-rendered contributions.

* create task: **Review report classification update**

  * Separate semantic failures from layout failures.
  * Allow Datoviz guide rows as `review.adapted` when diagnostics are complete.
  * Prevent adapted artifacts from being counted as layout-strict passes.

## Answers To The Specific Questions

### 1. Which option should the project choose long term, and why?

Choose **Option C**.

It preserves GSP’s semantic-protocol identity while adding enough resolved geometry for publication, reproducible review, and query/readback. It avoids Option A’s ambiguity and Option B’s excessive cost.

### 2. What is the precise boundary between “GSP semantic spec” and “resolved pixel layout”?

The semantic spec defines **what exists and what it means**:

```text
views
domains
visuals
guides
roles
ticks
labels
scales
query identities
logical pixel units
```

Resolved layout defines **where those things land for one render target**:

```text
panel rect
plot rect
title rect
axis lanes
tick label boxes
legend/colorbar boxes
grid clip rect
data-to-screen transform
z/layer order
```

Semantic records are stable scene intent. Resolved layout is a snapshot derived from scene intent plus render target plus font/layout context.

### 3. Should title/axis/legend/colorbar layout be part of protocol records, a derived server-side layout result, or only conformance artifacts?

Use all three, but with different roles:

* Input protocol records should contain **semantic guide intent**.
* The server should derive a **resolved layout result**.
* Conformance should compare that resolved result and its query behavior.

Resolved layout should **not** be only a conformance artifact. It must be queryable/readable protocol state. Otherwise render and query can silently diverge.

A producer may optionally supply an explicit resolved layout snapshot for reproducibility, but the normal model should be semantic input followed by server-side layout resolution.

### 4. Should strict conformance require visually identical title/axis placement across Matplotlib and Datoviz?

Not for baseline strict conformance.

Strictness should be tiered:

* **Semantic strict:** no visually identical placement requirement.
* **Layout strict:** title, axis, legend, colorbar, plot rectangle, and grid clipping must match the GSP resolved layout within geometric tolerance.
* **Raster strict/pixel parity:** not required unless a backend explicitly advertises it.

So Datoviz may be semantically useful and reviewable without matching Matplotlib layout. But it should not claim layout-strict conformance if its title sits inside the plot while the resolved layout places it above the plot.

### 5. How should DPI/device-scale/font metrics be specified?

Use:

```text
logical_px
device_scale
dpi
font request
font metrics profile
```

Strict:

* logical pixel interpretation,
* DPI conversion formulas,
* device-scale conversion,
* resolved layout rectangles,
* data-to-screen transform,
* stroke/marker/text nominal sizes.

Tolerant:

* antialiasing,
* glyph hinting,
* text rasterization,
* minor subpixel differences.

Backend-defined:

* default font family,
* fallback fonts,
* native text rendering,
* unspecified guide style defaults.

Backend-defined choices must be read back or diagnosed.

### 6. How should guide query semantics relate to resolved layout?

Guide query must use the same layout snapshot as rendering.

A query should be able to identify whether a point lies in:

* plot/data rectangle,
* title rectangle,
* x/y axis lane,
* tick label box,
* axis label box,
* gridline region,
* legend item,
* colorbar ramp,
* colorbar tick/label.

If a backend renders native guide decorations but cannot query them, it must report missing guide query semantics.

### 7. What minimal spec changes should be made now to avoid accumulating backend-specific hacks?

Do these now:

1. Add conformance tiers.
2. Add `RenderTarget`.
3. Define logical pixels/device scale/DPI.
4. Add `ResolvedLayoutSnapshot`.
5. Define grid clipping to plot rect in layout-strict mode.
6. Define `PanelTextGuide` as a guide, not a temporary text visual.
7. Add guide style fields for title/axis/tick/grid sizes.
8. Require adapters to report native/adapted/missing guide layout and query capabilities.
9. Update QA to distinguish semantic pass, layout pass, raster-tolerant pass, and adapted review artifact.

### 8. What should the Datoviz adapter advertise until it supports the chosen level of layout strictness?

Datoviz should advertise something like:

```text
semantic_data_visuals: supported
view2d_domains: supported
native_axes: partial
axis_style_mapping: partial
panel_text_guide: adapted
resolved_layout_produce: unsupported
resolved_layout_consume: unsupported or partial
layout_strict: false
guide_query: false
all_rendered_guides_query: false
grid_clip_to_plot_rect: unsupported or partial
font_metrics_parity: false
raster_pixel_parity: false
```

Datoviz review rows can remain valid as `adapted` artifacts when:

* they use the same `View2D` domains,
* they render native axes from the same semantic intent where possible,
* they report missing layout/query semantics explicitly,
* they do not claim layout-strict conformance.

### 9. What tasks should be created next?

Create the ADR first, then the layout spec, then the Matplotlib reference implementation, then the Datoviz capability audit, then the QA split.

The most urgent practical task is to stop silent guide adaptation. A Datoviz title rendered as screen text is acceptable as a review artifact only if the artifact says:

```text
PanelTextGuide TITLE rendered as adapted screen text.
Does not participate in GSP layout strictness.
Guide query missing.
All-rendered guide contribution missing.
```

## Risks

* **Scope creep:** resolved layout can grow into a full page-layout system.
* **Matplotlib leakage:** the project may accidentally standardize Matplotlib quirks instead of a GSP layout model.
* **Font instability:** font availability and metrics vary across machines.
* **GPU cost:** Datoviz may need extra overlay/layout machinery that is not natural for its native axes.
* **Tier confusion:** users may misunderstand semantic strict as visual parity.
* **Review ambiguity:** adapted artifacts may look good but lack query/readback semantics.
* **Query divergence:** render and query can disagree if layout snapshot IDs are not enforced.
* **Version drift:** backend native layout behavior can change.
* **Over-tolerance:** too much raster tolerance can hide real geometry errors.
* **Under-tolerance:** too little raster tolerance can make harmless font differences fail.

## Decision Record Draft

* **Title:** GSP Guide Layout Semantics Boundary
* **Status:** Proposed for acceptance
* **Decision:** Adopt a hybrid guide/layout model.
* **Chosen option:** Option C, refined so that resolved layout is a first-class optional protocol artifact.
* **Context:** GSP must support both Matplotlib publication rendering and Datoviz high-performance GPU rendering. Native backend layout behavior differs, especially for titles, axes, tick labels, grid clipping, and font metrics.
* **Problem:** Pure semantic guide intent is insufficient for reproducible publication layout and guide query semantics. Mandatory pixel-identical layout across all backends is too costly and would overfit the protocol to one backend.
* **Decision:** GSP will define semantic guide records as the primary scene contract and add resolved layout snapshots for layout-strict rendering, query, and conformance.
* **Conformance tiers:**

  * `semantic_strict`
  * `layout_strict`
  * `raster_tolerant`
  * optional `pixel_parity`
* **Rule:** Strict semantic conformance does not imply visually identical guide placement.
* **Rule:** Layout-strict conformance requires matching the GSP resolved layout, not merely producing a similar-looking image.
* **Rule:** Render, query, readback, and all-rendered contributions must reference the same `layout_snapshot_id`.
* **Rule:** `PanelTextGuide`, `AxisGuide`, `ColorbarGuide`, and legend guides remain guide objects even if a backend realizes them using native text, axes, or visual primitives.
* **Rule:** Backend-specific workarounds are acceptable only as explicitly diagnosed adaptations.
* **Matplotlib consequence:** Matplotlib remains the initial reference/publication backend and should expose the resolved GSP layout it used.
* **Datoviz consequence:** Datoviz remains the flagship GPU backend but should advertise guide/layout support as partial or adapted until it can consume or produce resolved layout and guide query semantics.
* **Rejected:** Option A, because it leaves plot rectangles, title placement, grid clipping, and guide query geometry underspecified.
* **Rejected:** Option B as mandatory baseline, because it imposes excessive implementation burden and risks turning GSP into a Matplotlib-layout clone.
* **Expected result:** Publication workflows can demand layout strictness. Interactive GPU workflows can use semantic/native/adapted guide rendering with honest capability diagnostics.
