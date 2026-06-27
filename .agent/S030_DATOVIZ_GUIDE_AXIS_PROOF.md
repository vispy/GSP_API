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
- M121 review pack: `artifacts/visual_qa/s030/m121-guide-review-path/index.md`
- M121 Datoviz auto/grid review artifact:
  `artifacts/visual_qa/s030/m121-guide-review-path/backends/datoviz/guide_view2d_auto_grid.png`
- M121 Datoviz reversed/explicit review artifact:
  `artifacts/visual_qa/s030/m121-guide-review-path/backends/datoviz/guide_view2d_reversed_explicit.png`
- M122 final review pack: `artifacts/visual_qa/s030/final-review-pack/index.md`

## Runtime Findings

| Behavior | Classification | Evidence |
| --- | --- | --- |
| Backend auto tick policy API | Proven | `configure_view2d_axes(..., backend_auto_ticks=True)` completed. |
| Grid API | Proven | `dvz_axis_set_grid` is present and accepted for both axes. |
| Axis label API | Proven | `dvz_axis_set_label` is present and accepted UTF-8 labels for both axes. |
| Reversed View2D domain API | Proven | `dvz_panel_set_domain` accepted `(1, -1)` ranges. |
| Explicit tick values/labels | Proven at facade level | `dvz_axis_set_ticks(axis, values, labels)` returned true for both axes. |
| Rendered tick/grid/label placement | Proven | `--capture` produced both guide screenshots with the MoltenVK runtime environment configured. |
| Explicit ticks through GSP renderer | Proven/adapted review | M121 wires explicit tick values/labels through `dvz_axis_set_ticks` and renders `guide/view2d_reversed_explicit` as an adapted review artifact. |
| Panel title placement | Unsupported | The local facade exposes neither `dvz_panel_set_title` nor `dvz_panel_title`. |
| Guide/all-rendered query | Unsupported | No Datoviz guide picking/query API was proven. |
| Strict GSP auto tick identity | Adapted | Datoviz resolves native ticks; this is not the GSP `AUTO_LINEAR_NICE_V0` reference tick algorithm. |

## Closeout

S030 is closed. Datoviz guide rows render for review and are classified as `adapted`, not `strict`,
in the final S030 review pack. Native axes can render for review, including explicit ticks, but title
layout and guide query behavior remain unsupported.

Do not approximate the panel title with ad hoc text primitives in a strict guide row.
