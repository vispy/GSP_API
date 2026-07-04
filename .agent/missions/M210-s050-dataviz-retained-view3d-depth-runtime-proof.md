# M210 - S050 Datoviz retained View3D depth runtime proof

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Run a bounded Datoviz runtime proof for retained DATA-space View3D opaque mesh depth after M209
defines the strict fixture and acceptance criteria.

## Required Context

- `.agent/S050_STRICT_3D_DEPTH_MESH_SCOPING.md`
- `.agent/S050_STRICT_OPAQUE_DEPTH_FIXTURE_PLAN.md`
- `.agent/S050_DATOVIZ_COLORBAR_EXPLICIT_TICK_PROOF.md`
- `.agent/missions/M209-s050-strict-opaque-depth-fixture-plan.md`
- `spec/view3d.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `tools/run_datoviz_visual_review_pack.sh`

## Deliverables

- Run the M209 fixture through the Datoviz retained View3D DATA-space path.
- Capture visual/review evidence that strict nearer opaque fragments win.
- Decide whether Datoviz can advertise `meshvisual.positions3d.opaque_depth.v1`.
- Update capability docs/tests only if the runtime proof passes.

## Stop Conditions

- Stop on Datoviz offscreen runtime crashes or manual build-system intervention.
- Stop before editing `/home/cyrille/GIT/Viz/datoviz`.
- Stop before coupling strict depth promotion to mesh triangle query promotion.

## Result

Blocked locally. See `.agent/S050_DATOVIZ_RETAINED_VIEW3D_DEPTH_PROOF.md`.

Outcome: added the S050 strict-depth candidate fixture and threaded `view3d` through the visual QA
harness. Focused tests and Matplotlib/diagnostic review-pack runs pass. The initial Datoviz opt-in
offscreen run exited with code `139` after writing partial PNG/log artifacts, so no strict-depth
promotion was made in M210.

M214 aligned GSP with the latest Datoviz v0.4-dev generated binding. The same S050 strict-depth case
now renders through real Datoviz offscreen review-pack evidence at
`artifacts/visual_qa/s050/m214-latest-depth/`.

Result: Datoviz rendered `mesh3d/opaque_depth_intersecting_triangles_view3d`, but the capability
matrix still classified it as `adapted` with reason code
`datoviz_rendered_pending_promotion_audit`. M210 remained blocked until manual review and a
family-specific strict-depth promotion audit.

M210 resumed on 2026-07-04. The S050 suite gained a reversed face-order companion case, and a fresh
Datoviz offscreen run completed at `artifacts/visual_qa/s050/m218-depth-face-order/index.md`.
Pixel sampling confirmed that both Datoviz original and reversed cases render red at the left
sample and blue at the right sample, while Matplotlib remains adapted/painter-sorted with blue at
both samples.

Decision: Datoviz may advertise `meshvisual.positions3d.opaque_depth.v1` only for the retained
DATA-space View3D path with fully opaque meshes and native depth test/write enabled. Transparent
mesh alpha, culling, clipping strictness, and mesh triangle picking remain unpromoted.

Audit: `.agent/S050_DATOVIZ_OPAQUE_DEPTH_PROMOTION_AUDIT.md`.
