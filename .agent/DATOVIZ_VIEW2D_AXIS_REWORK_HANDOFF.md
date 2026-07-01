# Datoviz / GSP View2D Axis Rework Handoff

Generated: 2026-06-27
Updated: 2026-06-27 after Datoviz `v0.4-dev` commits through `4e5f6aec6`
(`docs: document panel coordinate transforms`).
Updated: 2026-07-01 with the long-term native grid clipping plan after the Datoviz
`examples/review/01_scatter_basic.py` clipping review.

This handoff is intended for another agent to pick up. It covers both repositories:

- GSP_API: `/home/cyrille/GIT/Viz/GSP_API`
- Datoviz: `/home/cyrille/GIT/Viz/datoviz`

## 2026-07-01 Follow-up: Native Grid Clipping Architecture

### Observed Problem

`examples/review/01_scatter_basic.py` exposes a guide/data clipping mismatch in Datoviz:

- a large marker near the accepted `View2D` top boundary is clipped at the data/plot boundary;
- the vertical grid line below it continues into the title/reserve area.

The marker clipping is the desired behavior. The grid line is using a broader panel/source extent
than the data visual clip region, so guide and data geometry do not share the same plot-rect
boundary.

This is not a `View2D` navigation bug. It is a Datoviz native axis/grid clipping issue that GSP
should continue to classify as adapted or partial until Datoviz exposes native evidence that grid
geometry is clipped to the resolved plot rectangle.

### Long-Term Architectural Fix

The durable fix belongs primarily in Datoviz, with GSP_API consuming and testing the capability.

#### Datoviz-1: Make plot-rect clipping native axis semantics

Datoviz should define this invariant for panel-owned 2D axes:

- data visuals, grid lines, ticks, tick labels, and axis labels derive from the same resolved
  `DvzPanelFrameSnapshot`;
- grid lines are clipped to the resolved plot rectangle, not to the full panel/source extent;
- `dvz_panel_plot_rect_px()` is the authoritative pixel-space plot rectangle for data/guide
  clipping and layout snapshots.

#### Datoviz-2: Fix axis grid generation

The short-term implementation target is `src/scene/annotation/axis_visual.c`.

Current grid generation already skips ticks whose fixed visual coordinate is outside the plot range,
but grid line endpoints are derived from the full inverse panzoom/source extent:

- X-axis grid lines use `source_y0` to `source_y1`;
- Y-axis grid lines use `source_x0` to `source_x1`.

That lets grid geometry bleed into reserved title/label space. Datoviz should instead clamp or derive
grid endpoints from the plot rectangle (`x0`, `x1`, `y0`, `y1`) transformed through the same
panzoom/source mapping used by axis geometry. In other words, the grid segment endpoints should
represent the visible data plot area, not the full panel.

#### Datoviz-3: Add a visual clip safety net

If the visual attachment pipeline supports it, add or expose a plot-rect clip mode for generated
guide visuals, for example:

```c
DVZ_VISUAL_CLIP_PLOT
```

The preferred design is both:

- generated grid geometry endpoints respect the plot rectangle; and
- the retained grid visual is clipped to the plot rectangle as a defensive invariant.

This avoids relying on every future guide generator to remember manual endpoint trimming.

#### Datoviz-4: Native tests

Add Datoviz tests that inspect generated grid geometry or captured output against
`dvz_panel_plot_rect_px()`.

Required cases:

- large marker near plot boundary with a title/reserve area;
- backend auto ticks with grid enabled;
- explicit ticks with grid enabled;
- reversed X/Y domains;
- panzoom and resize;
- high-DPI/content-scale path if plot rect is measured in logical pixels.

Acceptance:

- no grid vertex extends outside the resolved plot rectangle except for expected stroke-width
  tolerance;
- data visual clipping and grid clipping agree;
- title/label reserve areas remain free of grid geometry.

#### GSP-1: Keep Datoviz grid clipping classified as adapted/partial

Until Datoviz has native proof, GSP_API should keep diagnostics such as:

- `grid_clip_not_enforced`;
- `grid_clip_native_api_unverified`.

Do not hide the issue by drawing an opaque title band or by unclipping data markers. Those would make
the review artifact prettier while preserving inconsistent guide/data clipping semantics.

#### GSP-2: Add a targeted visual QA regression

Add a GSP visual QA case that intentionally reproduces the screenshot-class failure:

- large marker close to the top plot boundary;
- title or panel text reserve above the plot;
- grid enabled;
- Datoviz backend axis guides enabled.

Expected strict behavior after Datoviz promotion:

- marker and grid both stop at the same plot boundary;
- grid does not enter title/label reserve space;
- Matplotlib reference and Datoviz output agree on guide/data clipping boundaries.

Before Datoviz promotion, this case should remain adapted or flagged with the explicit grid clipping
blocker.

#### GSP-3: Capability-gate promotion

After Datoviz lands native tests and a stable API/behavior contract, update GSP_API:

- enhance `datoviz_v04_axis_provider_capability()` or related diagnostics to detect/probe the grid
  clipping capability;
- remove or narrow the grid clipping blockers only for Datoviz builds that expose the proven
  behavior;
- add a runtime probe or fixture assertion that ties Datoviz grid geometry to
  `dvz_panel_plot_rect_px()`.

#### Cross-repo acceptance

The combined promotion is complete only when both repositories prove the same contract:

- Datoviz native tests prove grid geometry is plot-rect clipped;
- GSP_API visual QA proves guide/data clipping coherency in a real review scene;
- GSP_API capability metadata no longer overstates Datoviz guide strictness on older builds.

## Current Verdict

The current S028 guide/View2D mismatch is still primarily a GSP Datoviz adapter bug. The
Datoviz-side API/documentation gap described in the original handoff has largely been addressed in
the local Datoviz `v0.4-dev` branch.

GSP currently sets panel domains and then enables a default Datoviz `DvzPanelView2D` whose embedded `data_x/data_y` are `[-1, +1]`. Once `view2d_enabled` is true, Datoviz resolves from `panel->view2d.data_x/data_y`, so the intended GSP ranges are effectively replaced with the Datoviz defaults.

This explains the visible failures:

- `guide/view2d_auto_grid`: GSP intends `x=(-2, 2)`, `y=(-1, 1)`, but Datoviz behaves like `x=(-1, 1)`, clipping the outer points.
- `guide/view2d_reversed_explicit`: GSP intends reversed ordered endpoints, but Datoviz behaves like default non-reversed ranges.

Datoviz now documents and tests the relevant behavior:

- `DvzPanelView2D.data_x/data_y` are accepted as ordered endpoints, including reversed endpoints.
- `dvz_panel_visible_domain()` preserves active domain orientation.
- `dvz_panel_data_to_visual_positions()` maps DATA to VIEW and is documented as only appropriate
  for visuals attached with `DVZ_COORD_VIEW`.
- `dvz_panel_transform_point()`, `dvz_panel_position_to_data()`, and
  `dvz_panel_data_to_position()` are available as explicit coordinate conversion APIs.
- `dvz_axis_set_ticks()` is now present in the local Datoviz public header and Python import path.

Therefore the next GSP task should be the carrier fix and validation, not another Datoviz API
consultation.

## Target Architecture

GSP must own semantic view state. Datoviz must be treated as one backend realization of that state.

Required model:

- `DataView2D`: protocol-level semantic data-space view, replacing or superseding ambiguous public/internal use of `View2D`.
- `DataView2DSnapshot`: immutable resolved ordered x/y endpoint snapshot consumed by both DATA visuals and guides during one render/query pass.
- `AxisGuideSpec`: provider-independent axis/grid/tick/label intent.
- `AxisGuideRealization`: backend/provider-specific status and diagnostics.
- `DatovizPanelView2D` or local adapter helper: backend carrier mapping `DataView2DSnapshot` into `DvzPanelView2D.data_x/data_y`.
- Datoviz coordinate conversion helpers for runtime/readback checks:
  `dvz_panel_transform_point()`, `dvz_panel_visible_domain()`,
  `dvz_panel_data_to_visual_positions()`.

Strict rule:

DATA visuals and axis guides must consume the same `DataView2DSnapshot`. Backend-native axes may be used only when diagnostics clearly state whether the result is strict, adapted, or unsupported.

## GSP_API Work Plan

### GSP-1: Immediate Datoviz View2D Carrier Fix

Files likely involved:

- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `tests/test_visual_qa_harness.py`
- `src/gsp/qa/visual/runner.py`

Steps:

1. Add at least one internal helper so the View2D carrier can be tested independently of native
   axis realization:

   ```python
   apply_datoviz_data_view2d(view_or_snapshot)
   ```

2. Populate the Datoviz panel view descriptor from the GSP ordered endpoints before calling `dvz_panel_set_view2d()`:

   ```python
   panel_view = self.dvz.dvz_panel_view2d()
   panel_view.data_x.min = float(snapshot.x_range[0])
   panel_view.data_x.max = float(snapshot.x_range[1])
   panel_view.data_y.min = float(snapshot.y_range[0])
   panel_view.data_y.max = float(snapshot.y_range[1])
   panel_view.padding = 0.0
   self.dvz.dvz_panel_set_view2d(self.panel, panel_view)
   ```

3. Preserve ordered endpoints exactly. Do not sort reversed ranges.

4. Stop using `dvz_panel_set_domain()` as the primary GSP `DataView2D` carrier. If legacy panel
   domain sync is retained temporarily, isolate it in a compatibility helper and call it before
   `dvz_panel_set_view2d()` because `dvz_panel_set_domain()` disables `view2d_enabled`.

5. Record diagnostics similar to:

   ```text
   datoviz_view2d_carrier = DvzPanelView2D.data_x/data_y
   ordered_ranges_preserved = true
   reversed_x = ...
   reversed_y = ...
   legacy_panel_domain_sync = true|false
   datoviz_visible_domain_readback = available|missing
   ```

Acceptance:

- S028 auto-grid Datoviz render shows all four points, including `x=-1.5` and `x=1.5`.
- S028 reversed guide Datoviz point orientation matches Matplotlib geometry.
- No hidden fallback to Datoviz default `[-1, +1]`.

### GSP-2: Split View Mapping From Axis Realization

Files likely involved:

- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp/qa/visual/capability_matrix.py`
- `src/gsp/qa/visual/runner.py`
- `spec/transforms.md`
- `spec/visual_qa_harness.md`
- `spec/vispy2/api.md`

Steps:

1. Replace adapter API shape:

   Current:

   ```python
   configure_view2d_axes(...)
   ```

   Target:

   ```python
   apply_data_view2d(...)
   realize_axis_guides(...)
   ```

2. Keep `apply_data_view2d()` limited to DATA-to-panel mapping.

3. Move native axis/grid/label/tick work into `realize_axis_guides()`.

4. Return or store a structured `AxisGuideRealization`-like diagnostic for each axis provider.

5. Keep Datoviz native axes classified as adapted even when explicit tick functions are present,
   until title/query/all-rendered guide semantics are strict.

Acceptance:

- Tests prove view mapping can be configured without creating axes.
- Tests prove axes consume the same snapshot as DATA visuals.
- Capability matrix does not imply strict guide support just because `dvz_axis_set_ticks` is
  present.

### GSP-3: Break/Rename Ambiguous View Types

This can be a separate mission because it is wider API churn.

Steps:

1. Introduce `DataView2D` as the semantic protocol object.

2. Introduce `DataView2DSnapshot` as the immutable render/query snapshot.

3. Either:

   - keep `View2D` as a short-lived compatibility alias with deprecation diagnostics, or
   - aggressively replace it everywhere now if the release is still pre-public.

4. Update documentation to distinguish:

   - `DataView2D`: semantic data-space mapping;
   - panel layout/viewport: physical panel bounds;
   - backend panel view descriptors: non-authoritative backend carriers.

5. Update VisPy2 APIs and docs so `Axes.set_xlim()`, `Axes.set_ylim()`, and `set_view2d()` update semantic `DataView2D`.

Acceptance:

- Specs no longer use “View2D” ambiguously when referring to Datoviz-native view descriptors.
- Public semantics say first endpoint maps to negative panel edge, second endpoint maps to positive panel edge, including reversed ranges.

### GSP-4: Capability Declarations And Realization Diagnostics

Add feature-level Datoviz capabilities rather than broad backend labels.

Recommended capability names:

- `data_view2d_ordered_limits`
- `data_view2d_reversed_x`
- `data_view2d_reversed_y`
- `data_visual_native_data_mapping`
- `axis_native_auto_ticks`
- `axis_explicit_ticks`
- `axis_explicit_tick_labels`
- `axis_realized_tick_query`
- `srgb_pipeline_control`

Current expected Datoviz classification after the latest Datoviz commits:

- `data_view2d_ordered_limits`: strict after the GSP carrier fix and tests.
- `data_view2d_reversed_x/y`: Datoviz-native proof now exists; GSP can promote after adapter tests
  confirm it populates `DvzPanelView2D.data_x/data_y` and readback agrees.
- `axis_native_auto_ticks`: adapted.
- `axis_explicit_ticks`: adapted when `dvz_axis_set_ticks` is exposed; unsupported when absent.
- `axis_explicit_tick_labels`: adapted until the Python binding wrapper shape is proven stable
  against the C `DvzAxisTicks*` API.
- `axis_realized_tick_query`: unsupported.
- `srgb_pipeline_control`: adapted/no-op when `dvz_figure_set_color_pipeline` is absent.

Acceptance:

- Review pack matrix explains strict/adapted/unsupported per feature.
- No visual row is promoted to strict just because a PNG rendered.

### GSP-5: Tests To Add

Add or update tests in `tests/test_datoviz_v04_protocol_renderer.py` and `tests/test_visual_qa_harness.py`.

Required tests:

1. Adapter descriptor test:
   - Input `x=(-2, 2)`, `y=(-1, 1)`.
   - Assert `panel_view.data_x.min/max == -2, 2`.
   - Assert `panel_view.data_y.min/max == -1, 1`.
   - Assert `dvz_panel_set_view2d()` receives the populated descriptor.

2. Reversed descriptor test:
   - Input `x=(1, -1)`, `y=(1, -1)`.
   - Assert exact ordered endpoint preservation.
   - Assert no sorting.

3. Call-order test:
   - `dvz_panel_set_domain()` is not used in the strict carrier path, or if temporary legacy sync is enabled it is called before `dvz_panel_set_view2d()`.

4. Native transform integration test when available:
   - Prefer `dvz_panel_transform_point()` for point conversions.
   - Use `dvz_panel_visible_domain()` for resolved ordered-domain readback.
   - Keep `dvz_panel_data_to_visual_positions()` only for DATA-to-VIEW checks.
   - Normal range:
     - `(-2, -1) -> (-1, -1)`
     - `(0, 0) -> (0, 0)`
     - `(2, 1) -> (1, 1)`
   - Reversed range:
     - `(1, 1) -> (-1, -1)`
     - `(0, 0) -> (0, 0)`
     - `(-1, -1) -> (1, 1)`

5. Visual QA acceptance:
   - `guide/view2d_auto_grid`: all four Datoviz points visible.
   - `guide/view2d_reversed_explicit`: Datoviz geometry matches Matplotlib normalized panel orientation.

6. Diagnostics:
   - Explicit tick case with missing `dvz_axis_set_ticks` must be adapted or unsupported, not strict.
   - Explicit tick case with present `dvz_axis_set_ticks` remains adapted until guide title/query
     semantics are strict.
   - Add a binding-shape check for the Python `dvz_axis_set_ticks` wrapper. The C API takes
     `const DvzAxisTicks*`; the current GSP adapter assumes a convenience wrapper accepting
     values/labels.

### GSP-6: Regenerate Artifacts

After fixes:

1. Run focused tests:

   ```bash
   PYTHONPATH=. uv run pytest tests/test_datoviz_v04_protocol_renderer.py tests/test_visual_qa_harness.py -q
   ```

2. Run type checking:

   ```bash
   PYTHONPATH=. uv run mypy src/ --strict --show-error-codes
   ```

3. Regenerate S031/S028 review pack with legacy sRGB:

   ```bash
   DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
     --suite s028 \
     --out artifacts/visual_qa/s031/full-review-pack-legacy \
     --run-id s031-full-review-pack-legacy \
     --resolution 800x600
   ```

4. Optionally regenerate linear pack if still retained:

   ```bash
   DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
     --suite s028 \
     --out artifacts/visual_qa/s031/full-review-pack-linear \
     --run-id s031-full-review-pack-linear \
     --resolution 800x600 \
     --datoviz-color-pipeline linear_srgb
   ```

5. Run full tests:

   ```bash
   PYTHONPATH=. uv run pytest -q
   ```

Acceptance:

- Datoviz guide rows remain rendered.
- Geometry mismatch in the attached guide screenshot is resolved.
- Unsupported count remains `0` for the review pack unless a feature is intentionally reclassified.
- Adapted count remains honest for native axes lacking explicit tick/query semantics.

## Datoviz Repo Work Plan

Do not mix these changes with unrelated Datoviz work such as animation timer refactors. Coordinate branch ownership before editing `/home/cyrille/GIT/Viz/datoviz`.

Current Datoviz status after commits `58b0b464b`, `3469a58f8`, and `4e5f6aec6`:

| Area | Status | GSP impact |
|---|---|---|
| Domain/View2D authority docs | Mostly landed | GSP should consume the documented `DvzPanelView2D.data_x/data_y` carrier. |
| Reversed `DvzPanelView2D` domains | Landed in native tests | GSP still needs adapter and visual QA proof. |
| Visible-domain readback | Present | Prefer `dvz_panel_visible_domain()` for ordered endpoint assertions. |
| Coordinate conversion | Present | Prefer `dvz_panel_transform_point()` for DATA/VIEW/pixel conversion checks. |
| `dvz_axis_set_ticks()` | Present in local header/import path | Keep guide rows adapted until title/query semantics are strict. |
| Safer one-shot View2D constructor/setter | Not present | Optional ergonomic follow-up, not blocking GSP carrier fix. |

### DVZ-1: Document Domain Authority - mostly landed

Files likely involved:

- `include/datoviz/scene.h`
- `include/datoviz/scene/types.h`
- relevant docs/spec files if present.

Clarify the relationship among:

- `dvz_panel_set_domain()`
- `DvzPanelView2D.data_x/data_y`
- `dvz_panel_set_view2d()`
- `panel->view2d_enabled`
- `dvz_panel_visible_domain()`
- `dvz_panel_data_to_visual_positions()`
- native DATA attachments
- native axes

Status:

- The public header now documents ordered domains, active visible-domain orientation, and coordinate
  conversion helpers.
- The GSP-relevant remaining check is whether Python docs/bindings expose the same wording clearly.

Original required explicit statement:

When `view2d_enabled` is true, `DvzPanelView2D.data_x/data_y` are the active data domains for data-to-visual mapping and visible-domain resolution.

Also document that `dvz_panel_set_domain()` disables active View2D.

### DVZ-2: Add Safer View2D Construction API - optional follow-up

Add one of these APIs:

```c
DvzPanelView2D dvz_panel_view2d_data(double x0, double x1, double y0, double y1);
```

or:

```c
int dvz_panel_set_view2d_domain(
    DvzPanel* panel,
    DvzDataDomain data_x,
    DvzDataDomain data_y,
    DvzPanelView2DMode mode,
    DvzPanelView2DAspect aspect,
    double padding);
```

Preferred property: callers cannot accidentally enable default `[-1, +1]` domains after setting non-default domains.

This is no longer blocking GSP. The immediate GSP adapter fix can populate the existing
`DvzPanelView2D.data_x/data_y` descriptor directly.

Acceptance:

- API accepts ordered endpoints, including reversed ranges, or clearly rejects them with a documented alternative.
- Tests prove `x0=1, x1=-1` and `y0=1, y1=-1` preserve reversed mapping if that is intended support.

### DVZ-3: Add Resolved Domain Getter - superseded by visible-domain/transform APIs for GSP

The originally requested exact API has not landed, but GSP now has enough public surface for the
carrier fix:

- `dvz_panel_visible_domain()` returns resolved visible ordered endpoints.
- `dvz_panel_transform_point()` converts between DATA, VIEW, and pixel spaces.
- `dvz_panel_data_to_visual_positions()` remains available for DATA-to-VIEW checks.

An exact whole-view getter remains optional:

```c
bool dvz_panel_get_resolved_data_domain(
    DvzPanel* panel,
    DvzDataDomain* out_x,
    DvzDataDomain* out_y);
```

or equivalent.

Acceptance:

- Returns the domains actually used by `dvz_panel_data_to_visual_positions()` after current panel/view state is resolved.
- Preserves ordered endpoints.

### DVZ-4: Clarify Or Rename Ordered Ranges - mostly landed

Current field names are `min` and `max`, but GSP requires ordered endpoints for reversed axes.
Datoviz native tests now prove reversed `DvzPanelView2D.data_x/data_y` behavior. A future rename or
ordered range type remains ergonomic, not a GSP blocker.

Options:

1. Document that `min/max` are ordered endpoints in `DvzPanelView2D` even when `min > max`.
2. Add a new ordered range type:

   ```c
   DvzOrderedRange { double first; double second; }
   ```

3. Add explicit reverse flags if Datoviz wants sorted min/max internally.

Acceptance:

- Datoviz docs and tests make reversed axis behavior unambiguous.

### DVZ-5: Stabilize Python Bindings Needed By GSP Strict Support - partially landed

Required Python-visible APIs:

Panel/View2D:

- `dvz_panel_view2d`
- `dvz_panel_set_view2d`
- writable `DvzPanelView2D.data_x.min/max`
- writable `DvzPanelView2D.data_y.min/max`
- writable `DvzPanelView2D.mode`
- writable `DvzPanelView2D.aspect`
- writable `DvzPanelView2D.padding`
- `dvz_panel_data_to_visual_positions`
- `dvz_panel_visible_domain`
- `dvz_panel_transform_point`

Axes/guides:

- `dvz_panel_axis`
- `dvz_axis_set_ticks` or replacement
- explicit tick labels API if separate
- `dvz_axis_set_tick_policy`
- `dvz_axis_set_grid`
- `dvz_axis_set_label`
- `dvz_axis_set_visible`
- realized tick query if strict query support is desired

Visual attribute stability:

- Decide and document whether `diameter` or `diameter_px` is canonical.
- Decide and document whether `stroke_width` or `stroke_width_px` is canonical.

Color pipeline:

- Restore `dvz_figure_set_color_pipeline` or document its replacement/removal.

Acceptance:

- GSP no longer needs broad alias fallbacks for functions that are meant to be stable.
- GSP capability probe can distinguish absent experimental APIs from stable unsupported features.

Additional GSP-side verification now required:

- Confirm the Python `dvz_axis_set_ticks` wrapper shape. The public C API takes
  `const DvzAxisTicks*`, while the current GSP adapter assumes a convenience wrapper accepting
  values/labels.
- Confirm `DvzPanelView2D.data_x/data_y` fields are writable in the Python facade used by the
  review pack.

### DVZ-6: Add Native Tests - partially landed

Add Datoviz C/Python tests for:

1. `DvzPanelView2D.data_x/data_y` with normal ordered ranges.
2. `DvzPanelView2D.data_x/data_y` with reversed ordered ranges.
3. `dvz_panel_data_to_visual_positions()` matches those ranges.
4. Native DATA visual attachments consume the same resolved data view.
5. Native axes/grid visible domain matches DATA visual mapping.
6. `dvz_panel_set_domain()` plus `dvz_panel_set_view2d()` behavior is documented and tested.

Acceptance:

- The exact GSP S028 normal and reversed guide geometry can be reproduced in Datoviz-native tests without relying on GSP.

Status:

- Native reversed `DvzPanelView2D` visible-domain and DATA-to-VIEW tests exist.
- Remaining Datoviz-native proof, if desired, is full native axis/grid geometry parity with the
  exact GSP S028 guide cases.

## Cross-Repo Sequencing

1. GSP first: implement `DvzPanelView2D.data_x/data_y` carrier patch and tests.
2. GSP first: verify Python binding shape for writable `DvzPanelView2D.data_x/data_y`,
   `dvz_panel_visible_domain()`, `dvz_panel_transform_point()`, and `dvz_axis_set_ticks()`.
3. GSP first: keep native Datoviz guide rows adapted even when explicit ticks render, until
   title/query/all-rendered guide semantics are strict.
4. Datoviz optional follow-up: add a safer one-shot View2D constructor/setter if the existing
   descriptor API remains too easy to misuse.
5. GSP after adapter validation: remove temporary compatibility aliases and promote strict
   data-view rows feature-by-feature.

## Stop Conditions

Stop and classify Datoviz rows as adapted or unsupported if any of these occur:

- The active Python binding cannot preserve ordered/reversed `DvzPanelView2D.data_x/data_y` ranges.
- Native DATA attachments ignore `DvzPanelView2D.data_x/data_y`.
- Native axes consume a different domain than DATA visuals.
- Explicit ticks cannot be set but a strict explicit-tick row is requested.
- `dvz_axis_set_ticks()` is present only as the C `DvzAxisTicks*` ABI and the Python wrapper needed
  by GSP is not stable.
- Binding instability prevents stable tests.
- `dvz_panel_visible_domain()` / `dvz_panel_transform_point()` are unavailable in the tested
  binding and image-only evidence remains ambiguous.

## Deliverables For The Next Agent

Minimum GSP deliverables:

- Patch `src/gsp_datoviz/protocol_renderer.py` so the active Datoviz View2D descriptor carries GSP ranges.
- Add normal and reversed descriptor/call-order tests.
- Add binding-shape/readback checks for writable `DvzPanelView2D`, `dvz_panel_visible_domain()`,
  `dvz_panel_transform_point()`, and `dvz_axis_set_ticks()`.
- Add or update visual QA assertions for the S028 guide rows.
- Regenerate the legacy review pack.
- Commit and push.

Optional Datoviz follow-up deliverables:

- Add or propose safe View2D domain constructor/setter if direct descriptor mutation remains too
  error-prone.
- Add exact native axis/grid geometry tests for the GSP S028 guide cases if GSP visual QA remains
  ambiguous.
- Stabilize Python binding surface needed for strict GSP support, especially `dvz_axis_set_ticks()`
  wrapper semantics.

Do not promote Datoviz native guide/tick rows to strict until explicit tick/label APIs, title
layout, guide query, and all-rendered guide semantics are stable and tested.
