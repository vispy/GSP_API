# M184-S043 - Datoviz first-class guide snapshot handoff

## Mission

M184

## Status

Completed locally and pushed for review. Datoviz changes are on a sibling repository branch, not in
this GSP repository.

## Datoviz Branch

- Repository: `/Users/cyrille/GIT/Viz/datoviz-agent-worktrees/M184-first-class-guides`
- Branch: `agent/M184-first-class-guides`
- Base commit: `3ad83213b`
- Handoff file: `agents/now/HANDOFF_FIRST_CLASS_GUIDE_SNAPSHOT.md`

The main Datoviz checkout was not edited because another agent was active there during the work.

## What Datoviz Now Exposes

Public snapshot records:

- `DvzGuideLayout`
- `DvzGuideHit`
- `DvzRenderedContribution`

Public API:

- `dvz_panel_frame_guide_count()`
- `dvz_panel_frame_guide_layout()`
- `dvz_panel_frame_guide_hit()`
- `dvz_panel_frame_contribution_count()`
- `dvz_panel_frame_contribution()`

The implementation populates snapshot records for axes, axis grids, tick labels, axis labels, guide
lines/spans, colorbars, and legends. Geometry is in figure logical pixels and shares the
`snapshot_id` from `DvzPanelFrameInfo`.

Text boxes are coarse retained-layout boxes, not exact glyph extents. This is deliberately surfaced
by the Datoviz snapshot diagnostic `guide_layout_snapshot_first_slice`.

## Validation

Datoviz validation completed from the isolated worktree:

```sh
cmake --build build --target dvztest_scene
cmake --build build --target datoviz
./build/testing/dvztest_scene scene/scene-graph/panel_frame_snapshot_guide_layouts
./build/testing/dvztest_scene scene/scene-graph/panel_frame_snapshot_core
./build/testing/dvztest_scene scene/scene-graph/panel_view3d_state_readback
./build/testing/dvztest_scene scene/axis/panel_view2d
./build/testing/dvztest_scene scene/fields
./build/testing/dvztest_scene scene/scene-graph
just ctypes
just ctypes-check
git diff --check
```

Results:

- `scene/scene-graph`: 203/203 passed.
- `scene/fields`: 55/55 passed.
- `just ctypes-check`: ctypes policy, array facade coverage, and ABI validation passed.
- `git diff --check`: passed.

## Next Agent Guidance

M185 should remain a partial Datoviz snapshot adapter unless the pushed Datoviz branch has been
merged into the local Datoviz runtime that GSP imports.

For M185:

- Detect the new Datoviz ctypes APIs before using them.
- Map `DvzPanelFrameInfo` plus available `DvzGuideLayout` and `DvzRenderedContribution` records into
  GSP layout snapshot structures.
- Preserve explicit diagnostics when the runtime lacks the new APIs.
- Do not synthesize guide boxes or contribution ids in GSP.
- Keep native grid clipping as an independent capability.

For M186:

- Promote Datoviz guide rows only when the local Datoviz runtime provides guide identity, layout
  boxes, hit/readback payloads, rendered contributions, and matching `snapshot_id` evidence.
- Leave rows adapted with row-specific blockers when any piece is missing.

## Stop Conditions

- Stop if the local Datoviz import still resolves to a checkout without the M184 APIs.
- Stop if GSP must invent fields that Datoviz does not report.
- Stop if exact text glyph boxes are required for strict promotion; Datoviz M184 intentionally
  exposes coarse retained text boxes only.
