# P015 - Datoviz View2D / Axis Provider Contract

This needs ChatGPT Pro consultation.

Paste the full prompt below into ChatGPT Pro. The expected output is a concrete decision memo and migration plan. Do not rely on attached files or external paths; all relevant facts are embedded here.

## Prompt

We need an architecture decision for GSP_API, a semantic visualization protocol where VisPy2 produces GSP, Matplotlib is the strict/reference backend, and Datoviz v0.4-dev is the flagship GPU backend.

Current problem:

The S028 visual QA guide/View2D cases show a mismatch between Matplotlib and Datoviz:

- Case `guide/view2d_auto_grid`:
  - GSP `View2D`: `x_range=(-2.0, 2.0)`, `y_range=(-1.0, 1.0)`.
  - DATA point positions: `(-1.5,-0.5)`, `(-0.5,0.45)`, `(0.5,-0.15)`, `(1.5,0.65)`.
  - Matplotlib renders all four points with x axis `[-2,2]`.
  - Datoviz renders only the two middle points and visually behaves as if x domain is `[-1,1]`.

- Case `guide/view2d_reversed_explicit`:
  - GSP `View2D`: `x_range=(1.0,-1.0)`, `y_range=(1.0,-1.0)`.
  - Matplotlib reverses both axes.
  - Datoviz renders the points in effectively non-reversed default orientation, suggesting it is not consuming the GSP View2D ranges.

Relevant GSP adapter code currently does this in `DatovizV04ProtocolRenderer.configure_view2d_axes()`:

```python
dim_x = getattr(self.dvz, "DVZ_DIM_X", 0)
dim_y = getattr(self.dvz, "DVZ_DIM_Y", 1)
self.dvz.dvz_panel_set_domain(self.panel, dim_x, view.x_range[0], view.x_range[1])
self.dvz.dvz_panel_set_domain(self.panel, dim_y, view.y_range[0], view.y_range[1])

panel_view = self.dvz.dvz_panel_view2d()
self.dvz.dvz_panel_set_view2d(self.panel, panel_view)

x_axis = self.dvz.dvz_panel_axis(self.panel, dim_x)
y_axis = self.dvz.dvz_panel_axis(self.panel, dim_y)
```

Relevant Datoviz v0.4-dev source/header facts:

1. `dvz_panel_set_domain(panel, dim, min, max)` sets a panel data domain for one dimension. Its implementation calls `_panel_set_domain(..., clear_fit=true)`, and when `clear_fit` is true it sets `panel->view2d_enabled = false`.

2. `dvz_panel_view2d()` returns a descriptor with defaults:

```c
return (DvzPanelView2D){
    DVZ_STRUCT_INIT_FIELDS(DvzPanelView2D),
    .mode = DVZ_PANEL_VIEW2D_CONTAIN,
    .aspect = DVZ_PANEL_VIEW2D_ASPECT_FREE,
    .data_x = {.min = -1.0, .max = +1.0},
    .data_y = {.min = -1.0, .max = +1.0},
    .padding = 0.0,
};
```

3. `dvz_panel_set_view2d(panel, &view)` stores the descriptor and enables `panel->view2d_enabled`.

4. Datoviz view resolution uses `panel->view2d.data_x/data_y` when `panel->view2d_enabled` is true:

```c
if (panel->view2d_enabled) {
    *out_x = panel->view2d.data_x;
    *out_y = panel->view2d.data_y;
}
```

5. Therefore GSP currently sets the correct axis domains, then enables a default Datoviz View2D descriptor whose own `data_x/data_y` are `[-1,+1]`, likely overriding the intended GSP domain for DATA visual mapping and axis visible domains.

6. Datoviz has separate concepts:
   - panel axis domains via `dvz_panel_set_domain`;
   - panel View2D descriptor via `DvzPanelView2D.data_x/data_y`;
   - data-to-visual mapping via `dvz_panel_data_to_visual_positions` or native DATA attachments.

7. GSP protocol authority:
   - `View2D` is accepted as panel-level deterministic linear mapping from DATA coordinates to panel NDC.
   - Reversed limits are valid and reverse axis direction.
   - Semantic guides consume the same `View2D` snapshot as DATA visuals.
   - Matplotlib is strict reference.
   - Backend native guide/axis providers are allowed, but must be capability-gated and must not define protocol semantics.

8. Current Datoviz Python binding instability:
   - Some C functions are present but missing from the Python facade.
   - `dvz_axis_set_ticks` is missing, so explicit tick values/labels are currently adapted to backend-native tick policy.
   - `dvz_figure_set_color_pipeline` is missing in the current local library, so GSP recently made legacy sRGB mode a compatibility no-op when missing.
   - `diameter_px` and `stroke_width_px` were renamed in the current binding to `diameter` and `stroke_width`, and GSP added adapter aliases.

Question:

Decide the correct long-term architecture and near-term migration plan. We can aggressively break API compatibility at this stage if that creates a cleaner contract. Address whether the current discrepancy is a Datoviz bug, a GSP connector/adapter bug, or both.

Required output format:

1. Verdict:
   - Is this a Datoviz bug, GSP adapter bug, both, or ambiguous?
   - Which component should change first?

2. Architecture decision:
   - Define the authoritative GSP model for `View2D`, panel domains, axis guides, and DATA visual mapping.
   - Decide whether GSP should use Datoviz `DvzPanelView2D.data_x/data_y` as the primary View2D carrier, `dvz_panel_set_domain`, both, or a new wrapper/contract.
   - Decide whether native Datoviz axis providers should be strict, adapted, or unsupported under missing explicit tick/query support.

3. Breaking API recommendations:
   - What public/internal GSP APIs should be renamed or broken now?
   - Should `View2D` be split into semantic `DataView2D` vs backend `PanelView2D`?
   - Should guide/axis configuration be represented as provider-independent semantic records plus provider-specific realization diagnostics?

4. Datoviz handoff:
   - What exact Datoviz API clarifications or changes should be requested?
   - Should Datoviz change `dvz_panel_set_domain`, `dvz_panel_set_view2d`, default `dvz_panel_view2d`, or documentation?
   - What Python binding functions must be stable for GSP strict support?

5. Implementation plan:
   - Immediate patch steps in GSP.
   - Tests to add or change.
   - Visual QA acceptance criteria.
   - Migration stages/missions.

6. Risk and stop conditions:
   - When to stop and classify Datoviz rows as adapted/unsupported rather than keep patching.

7. Final recommendation:
   - A concise ordered checklist that a coding agent can implement.

