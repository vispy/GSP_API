# M184 - S043 Datoviz first-class guide objects

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Completed and landed on Datoviz `v0.4-dev`.

## Result

Implemented in Datoviz on branch `agent/M184-first-class-guides`, rebased onto `v0.4-dev`, and
pushed to `v0.4-dev` as commits `7b3bd2f7f` and `7c6e48f64`. Added public frame-snapshot guide
layout, hit, and rendered-contribution records/APIs; populated axes, guide lines/spans, colorbars,
and legends from retained layout state; regenerated Python ctypes; and validated native scene tests
plus ctypes ABI checks.

## Summary

Make Datoviz axes, titles, tick labels, axis labels, grids, legends, and colorbars semantic guide
objects with layout, query, and contribution identity.

## Deliverables

- `DvzGuide` descriptors for axes, titles, legends, colorbars, text guides, and grid/tick roles.
- Guide layout boxes and anchors in `DvzPanelFrameSnapshot`.
- Guide hit query returning snapshot id, guide id, role, hit part, box, tick index/data value, and
  label where applicable.
- All-rendered contribution enumeration for guide outputs.
- Python guide API exposure.
- Native tests for guide boxes, hit testing, contribution enumeration, dense ticks, reversed domains,
  multi-panel layout, colorbar/legend boxes, and snapshot id equality.

## Acceptance

- Guide render/query/readback/contribution paths can share one snapshot id.
- Title, tick label, axis label, legend, and colorbar boxes are inspectable.
- Grid clipping remains true plot clipping/scissor/equivalent clipping.

## Stop Conditions

- Stop if guides remain generated geometry with no durable guide identity.
- Stop if query/readback cannot return the same snapshot id used by render.
- Stop if all-rendered output omits guide contributions.

## Implementation Packet

This mission targets the sibling Datoviz repository, not GSP_API source. If another agent is active
in `/Users/cyrille/GIT/Viz/datoviz`, use a separate Datoviz worktree and do not touch the dirty main
checkout or its `data` submodule marker.

### Current Datoviz Building Blocks

- Axes: `include/datoviz/scene.h`, `src/scene/annotation/axis.c`,
  `src/scene/annotation/axis_visual.c`, `src/scene/annotation/axis_text.c`,
  `src/scene/annotation/axis_ticks.c`, `src/scene/annotation/axis_layout.c`.
- User guide lines/spans: `src/scene/annotation/guide.c`.
- Colorbars: `src/scene/annotation/colorbar.c`.
- Legends: `src/scene/annotation/legend.c`.
- Generated visual role policy: `src/scene/core/generated_visual_policy.h`.
- Snapshot core: `src/scene/core/panel_frame_snapshot.c`.
- Tests with relevant coverage: `src/scene/tests/axis.c`, `src/scene/tests/fields.c`,
  `src/scene/tests/scene_interaction_graph.c`.

### Minimal First Slice

Implement a neutral guide identity/layout/readback layer over existing retained adornments rather
than rewriting rendering first.

1. Add public guide layout/readback records in `include/datoviz/scene/types.h`:
   `DvzGuideKind`, `DvzGuideRole`, `DvzGuidePart`, `DvzGuideLayout`,
   `DvzGuideHit`, and `DvzRenderedContribution` or equivalent.
2. Add snapshot enumeration APIs in `include/datoviz/scene.h`:
   guide count/layout by index, guide hit query for one logical-pixel point, and rendered
   contribution count/item by index.
3. Extend `DvzPanelFrameSnapshot` to own immutable copies of guide layout boxes and contribution
   records for the resolved snapshot id.
4. Populate guide records from existing objects:
   panel X/Y axes, title/axis labels/tick labels/grid roles, line/span guides, colorbars, and
   legends.
5. Keep existing generated visuals as the rendering backend, but every generated guide/adornment
   visual must map back to a durable guide id/role/part in snapshot contribution enumeration.
6. Add focused native tests before broadening:
   axis label/title/tick/grid boxes, reversed-domain tick values, dense ticks, colorbar/legend
   boxes, guide hit query, all-rendered guide contribution enumeration, and same snapshot id across
   frame info/layout/hit/contribution APIs.

### Deferred Within M184 Unless Needed

- Pixel-perfect text extents beyond deterministic approximate logical boxes.
- Full high-level Python object wrappers. Raw ctypes exposure and ABI freshness are required first.
- GSP strict promotion. That belongs to M186 after M185 adapts snapshots into GSP.

### Validation

Run from the Datoviz worktree:

```sh
cmake --build build --target dvztest_scene
./build/testing/dvztest_scene scene/axis
./build/testing/dvztest_scene scene/fields
./build/testing/dvztest_scene scene/scene-graph
just ctypes-check
git diff --check
```

If a fresh isolated worktree lacks optional submodules, initialize only the submodules needed for
the chosen build and do not stage or commit `data` gitlink changes.
