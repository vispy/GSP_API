# Datoviz / GSP View2D Axis Rework Handoff

Generated: 2026-06-27

This handoff incorporates the ChatGPT Pro answer saved locally as `./ANSWER` and is intended for another agent to pick up. It covers both repositories:

- GSP_API: `/home/cyrille/GIT/Viz/GSP_API`
- Datoviz: `/home/cyrille/GIT/Viz/datoviz`

## Verdict

The current S028 guide/View2D mismatch is primarily a GSP Datoviz adapter bug, exposed by a Datoviz API footgun.

GSP currently sets panel domains and then enables a default Datoviz `DvzPanelView2D` whose embedded `data_x/data_y` are `[-1, +1]`. Once `view2d_enabled` is true, Datoviz resolves from `panel->view2d.data_x/data_y`, so the intended GSP ranges are effectively replaced with the Datoviz defaults.

This explains the visible failures:

- `guide/view2d_auto_grid`: GSP intends `x=(-2, 2)`, `y=(-1, 1)`, but Datoviz behaves like `x=(-1, 1)`, clipping the outer points.
- `guide/view2d_reversed_explicit`: GSP intends reversed ordered endpoints, but Datoviz behaves like default non-reversed ranges.

Datoviz is not necessarily wrong at the renderer-behavior level, but the relationship between `dvz_panel_set_domain()`, `DvzPanelView2D.data_x/data_y`, and `dvz_panel_set_view2d()` needs stronger API/documentation support.

## Target Architecture

GSP must own semantic view state. Datoviz must be treated as one backend realization of that state.

Required model:

- `DataView2D`: protocol-level semantic data-space view, replacing or superseding ambiguous public/internal use of `View2D`.
- `DataView2DSnapshot`: immutable resolved ordered x/y endpoint snapshot consumed by both DATA visuals and guides during one render/query pass.
- `AxisGuideSpec`: provider-independent axis/grid/tick/label intent.
- `AxisGuideRealization`: backend/provider-specific status and diagnostics.
- `DatovizPanelView2D` or local adapter helper: backend carrier mapping `DataView2DSnapshot` into `DvzPanelView2D.data_x/data_y`.

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

1. Replace the current `configure_view2d_axes()` mixed responsibility with at least one internal helper:

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

4. Stop using `dvz_panel_set_domain()` as the primary GSP `DataView2D` carrier. If native axes still need it temporarily, isolate it in a compatibility helper and call it before `dvz_panel_set_view2d()` because `dvz_panel_set_domain()` disables `view2d_enabled`.

5. Record diagnostics similar to:

   ```text
   datoviz_view2d_carrier = DvzPanelView2D.data_x/data_y
   ordered_ranges_preserved = true
   reversed_x = ...
   reversed_y = ...
   legacy_panel_domain_sync = true|false
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

5. Keep Datoviz native axes classified as adapted when explicit tick functions are missing.

Acceptance:

- Tests prove view mapping can be configured without creating axes.
- Tests prove axes consume the same snapshot as DATA visuals.
- Capability matrix does not imply strict explicit tick support when `dvz_axis_set_ticks` is absent.

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

Current expected Datoviz classification:

- `data_view2d_ordered_limits`: strict after carrier fix and tests.
- `data_view2d_reversed_x/y`: strict only after tests prove Datoviz honors ordered endpoints.
- `axis_native_auto_ticks`: adapted.
- `axis_explicit_ticks`: unsupported while `dvz_axis_set_ticks` is absent.
- `axis_explicit_tick_labels`: unsupported/adapted until stable binding.
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
   - Use `dvz_panel_data_to_visual_positions`.
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

### DVZ-1: Document Domain Authority

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

Required explicit statement:

When `view2d_enabled` is true, `DvzPanelView2D.data_x/data_y` are the active data domains for data-to-visual mapping and visible-domain resolution.

Also document that `dvz_panel_set_domain()` disables active View2D.

### DVZ-2: Add Safer View2D Construction API

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

Acceptance:

- API accepts ordered endpoints, including reversed ranges, or clearly rejects them with a documented alternative.
- Tests prove `x0=1, x1=-1` and `y0=1, y1=-1` preserve reversed mapping if that is intended support.

### DVZ-3: Add Resolved Domain Getter

Add a stable API for GSP tests/debugging:

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

### DVZ-4: Clarify Or Rename Ordered Ranges

Current field names are `min` and `max`, but GSP requires ordered endpoints for reversed axes.

Options:

1. Document that `min/max` are ordered endpoints in `DvzPanelView2D` even when `min > max`.
2. Add a new ordered range type:

   ```c
   DvzOrderedRange { double first; double second; }
   ```

3. Add explicit reverse flags if Datoviz wants sorted min/max internally.

Acceptance:

- Datoviz docs and tests make reversed axis behavior unambiguous.

### DVZ-5: Stabilize Python Bindings Needed By GSP Strict Support

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
- resolved-domain getter once added

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

### DVZ-6: Add Native Tests

Add Datoviz C/Python tests for:

1. `DvzPanelView2D.data_x/data_y` with normal ordered ranges.
2. `DvzPanelView2D.data_x/data_y` with reversed ordered ranges.
3. `dvz_panel_data_to_visual_positions()` matches those ranges.
4. Native DATA visual attachments consume the same resolved data view.
5. Native axes/grid visible domain matches DATA visual mapping.
6. `dvz_panel_set_domain()` plus `dvz_panel_set_view2d()` behavior is documented and tested.

Acceptance:

- The exact GSP S028 normal and reversed guide geometry can be reproduced in Datoviz-native tests without relying on GSP.

## Cross-Repo Sequencing

1. GSP first: implement `DvzPanelView2D.data_x/data_y` carrier patch and tests.
2. GSP first: keep native Datoviz axes adapted for missing explicit ticks.
3. Datoviz next: document and add safer APIs/getters.
4. GSP after Datoviz API stabilization: remove temporary compatibility aliases and promote strict rows feature-by-feature.

## Stop Conditions

Stop and classify Datoviz rows as adapted or unsupported if any of these occur:

- Datoviz cannot preserve ordered/reversed ranges.
- Native DATA attachments ignore `DvzPanelView2D.data_x/data_y`.
- Native axes consume a different domain than DATA visuals.
- Explicit ticks cannot be set but a strict explicit-tick row is requested.
- Binding instability prevents stable tests.
- No resolved-state query exists for core semantic features and image-only evidence remains ambiguous.

## Deliverables For The Next Agent

Minimum GSP deliverables:

- Patch `src/gsp_datoviz/protocol_renderer.py` so the active Datoviz View2D descriptor carries GSP ranges.
- Add normal and reversed descriptor/call-order tests.
- Add or update visual QA assertions for the S028 guide rows.
- Regenerate the legacy review pack.
- Commit and push.

Minimum Datoviz deliverables:

- Clarify View2D/domain authority in headers/docs.
- Add or propose safe View2D domain constructor/setter.
- Add or propose resolved-domain getter.
- Stabilize Python binding surface needed for strict GSP support.

Do not promote Datoviz native explicit guide/tick rows to strict until explicit tick/label APIs and query semantics are stable.

