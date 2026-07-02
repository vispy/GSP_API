# S043 Scoping - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Stage Goal

Implement the accepted P027 architecture direction across Datoviz and GSP_API:

- Datoviz gets an immutable resolved panel frame snapshot core.
- Datoviz views become revisioned state objects.
- Datoviz guides become first-class semantic/layout/query participants.
- GSP consumes Datoviz snapshots conservatively.
- Datoviz guide rows promote from adapted to strict only with full snapshot/query/contribution
  evidence.
- Datoviz `View3D` live navigation becomes available only through retained DATA-space visuals and
  camera/projection updates.

## Current State

| Area | State | Notes |
|---|---|---|
| Datoviz grid clipping | Native verified for current local source | Datoviz commit `9ba820489` uses plot viewport plus plot clipping; this is not full guide strictness. |
| Datoviz guide rows | Strict-gated | Rows promote only when native guide identity, layout boxes, guide query/readback, all-rendered guide contributions, and snapshot id equality are all verified; otherwise they remain adapted. |
| Datoviz View2D navigation | Implemented in GSP review paths | Uses retained S035 navigation when local input bindings are available. |
| Datoviz static View3D | Partially supported/gated | Static mesh rendering and canonical ray readback exist for the accepted slices. |
| Datoviz View3D live navigation | Unsupported | Current GSP Datoviz renderer uploads CPU-projected panel-NDC mesh buffers; retained navigation would require DATA-space visual attachments. |

## Authority And Boundary

Follow:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/layout.md`
5. `spec/navigation.md`
6. `spec/view3d_navigation.md`
7. `.agent/decisions/S043_datoviz_panel_frame_architecture.md`
8. existing source code

GSP public semantics must remain backend-independent. Datoviz-native controller, material, shader,
draw-state, and pipeline names remain private implementation details.

## Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M181 | completed | Archive P027 response, accept S043 architecture, and open this mission stack. |
| M182 | completed | Datoviz panel frame snapshot core. |
| M183 | completed | Datoviz unified revisioned view descriptors. |
| M184 | completed | Datoviz first-class guide objects. |
| M185 | completed | GSP partial Datoviz snapshot adapter. |
| M186 | completed | GSP Datoviz guide strict promotion. |
| M187 | draft | Datoviz retained DATA-space View3D visuals. |
| M188 | draft | GSP Datoviz View3D live navigation. |

## Implementation Order

1. Implement `DvzPanelFrameSnapshot` in Datoviz with immutable ids/revisions, panel/plot/grid rects,
   view transforms, diagnostics, C API, Python wrapper, and native tests.
2. Replace public mutable view structs with revisioned `DvzView2D`/`DvzView3D` descriptors and
   readback APIs. Keep `dvz_panel_set_domain()` only as a temporary compatibility wrapper.
3. Add first-class Datoviz guides with semantic identity, layout boxes, hit query, all-rendered
   contributions, and snapshot ids.
4. Add a GSP partial snapshot adapter. Preserve adapted diagnostics for fields Datoviz cannot report.
5. Promote only guide rows backed by render/query/readback/all-rendered snapshot equality.
6. Add Datoviz retained DATA-space View3D mesh attachments and retained update stats.
7. Enable GSP Datoviz View3D live navigation behind capability gates and retained-update proofs.

## Stop Conditions

- Stop if GSP would have to expose Datoviz-private controller/material/pipeline names publicly.
- Stop guide strict promotion if Datoviz cannot report guide boxes, identities, hit/readback payloads,
  contribution enumeration, or snapshot ids.
- Stop retained `View3D` navigation if ordinary orbit/pan/zoom requires CPU vertex reprojection or
  unchanged visual buffer reupload.
- Stop if logical pixels, framebuffer pixels, panel pixels, plot pixels, NDC, and DATA coordinates
  are ambiguous in Datoviz API outputs.
- Stop before treating native-verified grid clipping as full guide strictness.

## Acceptance

- `tools/agentctl next` shows S043 and M187 as the next ready mission.
- Datoviz API break direction is recorded in both the GSP decision record and Datoviz architecture
  note.
- M130 remains superseded/deferred; strict guide promotion now belongs to S043.
- S042/M180 remains completed; Datoviz View3D live navigation now depends on retained DATA-space
  Datoviz work, not more review-runner polish.
