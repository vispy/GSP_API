# S030 Datoviz Guide-Axis Runtime Proof

## Scope

Mission M120 probed Datoviz v0.4-dev native panel-axis behavior for the two
remaining unsupported guide rows:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

This mission did not promote either row in the GSP capability matrix.

## Artifacts

- Probe script: `tools/probe_datoviz_guide_axis.py`
- Runtime report: `artifacts/visual_qa/s030/datoviz-guide-axis-proof/report.json`
- Auto/grid screenshot: `artifacts/visual_qa/s030/datoviz-guide-axis-proof/guide_view2d_auto_grid.png`
- Reversed/explicit screenshot: `artifacts/visual_qa/s030/datoviz-guide-axis-proof/guide_view2d_reversed_explicit.png`

## Runtime Findings

| Behavior | Classification | Evidence |
| --- | --- | --- |
| Backend auto tick policy API | Proven | `configure_view2d_axes(..., backend_auto_ticks=True)` completed. |
| Grid API | Proven | `dvz_axis_set_grid` is present and accepted for both axes. |
| Axis label API | Proven | `dvz_axis_set_label` is present and accepted UTF-8 labels for both axes. |
| Reversed View2D domain API | Proven | `dvz_panel_set_domain` accepted `(1, -1)` ranges. |
| Explicit tick values/labels | Proven at facade level | `dvz_axis_set_ticks(axis, values, labels)` returned true for both axes. |
| Rendered tick/grid/label placement | Proven | `--capture` produced both guide screenshots with the MoltenVK runtime environment configured. |
| Explicit ticks through GSP renderer | Blocked | `DatovizV04ProtocolRenderer.configure_view2d_axes(..., backend_auto_ticks=False)` still rejects explicit GSP ticks by contract. |
| Panel title placement | Unsupported | The local facade exposes neither `dvz_panel_set_title` nor `dvz_panel_title`. |
| Guide/all-rendered query | Unsupported | No Datoviz guide picking/query API was proven. |
| Strict GSP auto tick identity | Adapted | Datoviz resolves native ticks; this is not the GSP `AUTO_LINEAR_NICE_V0` reference tick algorithm. |

## Recommendation

Defer row promotion. M121 should only wire a Datoviz guide review path if it can
surface the remaining gaps explicitly: native axes can render for review, but title
layout and guide query behavior must stay unsupported, and explicit ticks require a
renderer contract change before they can be considered for the reversed row.

Do not approximate the panel title with ad hoc text primitives in a strict guide row.
