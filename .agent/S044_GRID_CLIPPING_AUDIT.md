# S044 Grid Clipping Audit

Status: completed for M190.

## Scope

Audit the Datoviz native grid clipping proof after S043 and verify that GSP credits the proof
without promoting full guide strictness from clipping evidence alone.

## Findings

| Area | Finding |
|---|---|
| Datoviz source proof | The sibling checkout `/home/cyrille/GIT/Viz/datoviz` is at `7c6e48f64` and contains `9ba820489` as an ancestor. |
| Source sentinels | `src/scene/annotation/axis_visual.c` contains full inverse `[-1,+1]` source-extent grid geometry. `src/scene/tests/axis.c` contains `test_axis_grid_style_margins_do_not_double_clip`. |
| GSP capability gate | `datoviz_v04_grid_clip_to_plot_rect_ready_for_source()` detects the commit or equivalent source/test sentinels. |
| Verified diagnostics | Verified builds report `grid_clip_to_plot_rect: native-verified`, `grid_clip_native_verified`, and visual-QA `grid_clip_evidence: datoviz-native-axis-grid-plot-viewport-clip`. |
| Unverified diagnostics | Unverified builds keep `grid_clip_not_enforced` and `grid_clip_native_api_unverified`. |
| Guide strictness | Review rows remain adapted unless guide identity, guide boxes, guide query/readback, all-rendered guide query, contribution enumeration, and snapshot equality are also verified. |

## Conclusion

No Datoviz repository edits are needed for this mission. The GSP-side grid clipping gate and
review-matrix behavior are correct. The live spec wording has been updated so it no longer describes
the old S034 unsupported-only posture as current for verified Datoviz builds.
