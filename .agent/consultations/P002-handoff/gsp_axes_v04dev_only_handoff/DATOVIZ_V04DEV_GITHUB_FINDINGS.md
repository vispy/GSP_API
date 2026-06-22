# Datoviz v0.4-dev GitHub Findings For GSP Axes

Checked date: 2026-06-22.

Authoritative Datoviz source for this mission: `github.com/datoviz/datoviz`, branch `v0.4-dev`.

Explicitly not authoritative for this mission: `datoviz.org` pages and v0.3-era Python plotting examples.

## Findings from `README.md` on `v0.4-dev`

The branch README says the active `v0.4-dev` branch is preparing v0.4 release candidates around:

- retained scene API;
- DRP2 command streams;
- native Vulkan/vklite/canvas runtime.

It also says the v0.4 branch is **not** a compatibility layer for the v0.3 Python plotting API, and is instead the low-level engine surface that higher-level projects such as GSP/VisPy2 can target.

Release-facing v0.4 surfaces listed in the README include:

- C scene/app API under `include/datoviz/`;
- generated `datoviz.raw` Python `ctypes` bindings for the exported C ABI;
- top-level `import datoviz as dvz` array-aware direct-engine facade for policy-declared calls.

The README explicitly says v0.3 source/ABI compatibility and high-level Python plotting wrappers inside Datoviz are out of scope for v0.4.

The README also says the latest published PyPI package is still v0.3.x and v0.4 testing should build from source until release-candidate wheels and packages are published.

## Findings from `include/datoviz/scene.h` on `v0.4-dev`

The exported scene header includes these relevant panel/view/axis calls. The local implementation must verify exact signatures against its current checkout before coding.

### Panel data domain and View2D

Relevant symbols:

```c
dvz_panel_set_domain(DvzPanel* panel, DvzDim dim, double min, double max)
dvz_panel_view2d(void)
dvz_panel_set_view2d(DvzPanel* panel, const DvzPanelView2D* view)
dvz_panel_clear_view2d(DvzPanel* panel)
dvz_panel_view2d_extent(DvzPanel* panel, float out[4])
dvz_panel_visible_domain(DvzPanel* panel, DvzDim dim, double* out_min, double* out_max)
dvz_panel_data_to_visual_positions(DvzPanel* panel, const float* data_positions, float* visual_positions, uint32_t count)
```

The header comment for `dvz_panel_set_domain()` says the first WIP axis slice supports finite linear X/Y domains, with axis geometry derived from the domain and the panel panzoom extent during frame emission.

The header comment for `dvz_panel_set_view2d()` says the panel view owns the controller-visible 2D base extent and fitted data domains, and that equal aspect preserves equal X/Y screen scale under the current plot rectangle.

The header comment for `dvz_panel_visible_domain()` says the visible data domain combines the panel's domain with current panzoom extent.

The header comment for `dvz_panel_data_to_visual_positions()` says X and Y are mapped from data coordinates into panel visual coordinates in `[-1, +1]`.

### Panel-owned axes

Relevant symbols:

```c
dvz_panel_axis(DvzPanel* panel, DvzDim dim)
dvz_axis_tick_policy(void)
dvz_axis_style(void)
dvz_axis_set_visible(DvzAxis* axis, bool visible)
dvz_axis_set_grid(DvzAxis* axis, bool visible)
dvz_axis_set_label(DvzAxis* axis, const char* label)
dvz_axis_set_tick_policy(DvzAxis* axis, const DvzAxisTickPolicy* policy)
dvz_axis_set_style(DvzAxis* axis, const DvzAxisStyle* style)
dvz_axis_set_plot_margins(DvzAxis* axis, float left, float right, float bottom, float top)
dvz_axis_set_units(DvzAxis* axis, DvzUnits* units)
dvz_axis_set_datetime(DvzAxis* axis, DvzDateTimeFormat* format)
dvz_axis_set_datetime_range(DvzAxis* axis, double data0, double data1, DvzTimestamp t0, DvzTimestamp t1)
```

The header comment for `dvz_panel_axis()` says it returns a panel-owned axis and creates its WIP geometry visual on first use.

The header comment for `dvz_axis_set_label()` says the active 2D axis path renders the label through the scene text visual pipeline.

This is enough to classify Datoviz v0.4-dev as having a native axis provider candidate.

## Findings from `include/datoviz/scene/types.h` and `scene/enums.h`

Relevant concepts in the v0.4-dev headers include:

- `DvzPickRequest`, `DvzPickResult`, `DvzProbeRequest`, and `DvzProbeResult` for scene query/probe result paths;
- `DvzText`, `DvzTextStyle`, `DvzTextPlacement`, and retained text lowering to glyph visuals;
- visual attachment descriptor concepts such as draw order and controller mode;
- coordinate/controller enums including view/data/panel and controller-applied/fixed modes.

Because the branch is active and the raw header comments may not perfectly match struct fields at every commit, the adapter must inspect the local checkout before assuming field names such as coordinate-space slots.

## Architecture implications

1. The Datoviz backend should advertise an axis realization provider, probably named `datoviz.v04.panel_axis.wip` until the API stabilizes.
2. The first Datoviz proof should map GSP `View2D.x_range` and `View2D.y_range` to `dvz_panel_set_domain()` and `dvz_panel_set_view2d()`.
3. The first Datoviz proof should request x/y panel axes through `dvz_panel_axis()` and configure label, visibility, grid, style, and tick policy only when supported by the local bindings.
4. If explicit GSP tick lists cannot be passed to Datoviz native axes, then Datoviz-native auto ticks are an **adapted provider mode**, not strict GSP tick conformance.
5. Data coordinate handling should use Datoviz's data-domain/view machinery only when verified. Otherwise, CPU-side `dvz_panel_data_to_visual_positions()` or GSP normalization can be used as a temporary adapter path with diagnostics.
6. Query/readback for native axis guide contributions must be capability-gated. If Datoviz can pick/probe data visuals but not axis text/glyph contributions, report guide-query as unsupported instead of claiming a miss.

## Local verification checklist

```bash
# Must be run in the local Datoviz checkout.
git status --short
git branch --show-current

# Ensure the branch is the source of truth.
git checkout v0.4-dev

# Inspect axis/view symbols.
rg -n "dvz_panel_set_domain|dvz_panel_set_view2d|dvz_panel_view2d_extent|dvz_panel_visible_domain|dvz_panel_data_to_visual_positions|dvz_panel_axis|dvz_axis_set_visible|dvz_axis_set_grid|dvz_axis_set_label|dvz_axis_set_tick_policy|dvz_axis_set_style|dvz_axis_set_plot_margins|dvz_axis_set_units|dvz_axis_set_datetime|DvzAxisTickPolicy|DvzAxisStyle|DvzPanelView2D" include src spec examples tests datoviz

# Inspect bindings exposure.
rg -n "panel_set_domain|panel_set_view2d|panel_axis|axis_set_label|axis_set_tick_policy|DvzAxisTickPolicy|DvzAxisStyle|PanelView2D" datoviz include src tests examples

# Check whether explicit ticks are supported, or only auto policies.
rg -n "explicit.*tick|tick.*explicit|tick.*values|tick.*labels|AxisTick|TickPolicy" include src spec examples tests datoviz

# Check query/probe ability on generated axis/text contributions.
rg -n "PickResult|ProbeResult|query|probe|picking|glyph|text.*query|axis.*query" include src spec examples tests datoviz
```
