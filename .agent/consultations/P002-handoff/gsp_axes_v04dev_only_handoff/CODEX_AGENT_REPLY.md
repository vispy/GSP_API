# Reply To The Local Codex Agent

You generated the P002 prompt asking how axes, frames, ticks, labels, titles, coordinate display, Matplotlib, Datoviz, and query semantics should work in GSP / VisPy2.

Use this zip as the handoff bundle. It supersedes earlier handoffs because the Datoviz assumption changed.

## Updated answer

Implement axes as **semantic GSP intent plus pluggable axis realization providers**.

GSP protocol truth should be semantic:

- `Panel` / plot rectangle / reserved adornment areas;
- `View2D` / x-y data ranges / scale / aspect / controller attachment;
- `AxisGuide` for x/y axis guide intent;
- `PanelTextGuide` for title and other panel-level text;
- `TickSpec` with explicit ticks and a small GSP reference automatic policy;
- query/readback identity for guide contributions.

Backend realization should be provider-selected:

- `gsp.reference.generated_primitives.v0` — strict fallback/reference path using resolved line/text guide contributions;
- `matplotlib.native.axes.v0` — publication output through native Matplotlib artists, but with GSP-resolved limits/ticks in conformance mode;
- `datoviz.v04.panel_axis.wip` — native Datoviz v0.4-dev panel-axis path when the requested semantics are supported;
- `generated-primitives` or future custom providers for gaps.

## Datoviz v0.4-dev correction

Do not treat Datoviz as lacking native axis support. The v0.4-dev branch has native panel/axis hooks in `include/datoviz/scene.h`.

However, also do not use Datoviz v0.3 Python plotting docs. For this mission, Datoviz source of truth is the local checkout of:

```bash
git checkout v0.4-dev
```

Then inspect:

```bash
rg -n "dvz_panel_set_domain|dvz_panel_set_view2d|dvz_panel_view2d_extent|dvz_panel_visible_domain|dvz_panel_data_to_visual_positions|dvz_panel_axis|dvz_axis_set_visible|dvz_axis_set_grid|dvz_axis_set_label|dvz_axis_set_tick_policy|dvz_axis_set_style|dvz_axis_set_plot_margins|dvz_axis_set_units|dvz_axis_set_datetime|DvzAxisTickPolicy|DvzAxisStyle|DvzPanelView2D" include src spec examples tests datoviz
```

Use exported headers first. Specs and docs are design intent only unless confirmed by headers and examples.

## First implementation sequence

1. Capture the ADR.
2. Add semantic `Panel` and `View2D` protocol objects.
3. Add VisPy2 `set_xlim` / `set_ylim` by emitting `View2D`, while keeping `Figure.visuals()` data-only.
4. Update Matplotlib rendering to honor `View2D` limits.
5. Add provider/capability schema for axis realization.
6. Add semantic `AxisGuide` / tick spec / title-label model.
7. Add strict Matplotlib native-artist conformance using GSP-resolved ticks.
8. Add Datoviz v0.4-dev provider proof using `dvz_panel_set_domain`, `dvz_panel_set_view2d`, and `dvz_panel_axis` if supported by the local headers/bindings.
9. Add generated primitive fallback only as a backend realization artifact, not as `Figure.visuals()` content.
10. Add query/readback scopes for `data`, `guides`, and `all-rendered`.

## Stop conditions

- Do not implement broad Matplotlib compatibility.
- Do not implement log/date/category/polar/3D/twin axes in the first mission.
- Do not block on perfect Datoviz guide text query if v0.4-dev cannot expose it yet; report a capability/diagnostic instead.
- Do not use datoviz.org v0.3-era examples as callable API evidence.
