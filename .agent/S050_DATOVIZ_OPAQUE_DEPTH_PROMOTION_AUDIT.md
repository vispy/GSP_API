# S050 Datoviz opaque depth promotion audit

Date: 2026-07-04

Mission: M210 - S050 Datoviz retained View3D depth runtime proof

## Decision

Datoviz may advertise `meshvisual.positions3d.opaque_depth.v1` for the retained DATA-space View3D
path when all of these are true:

- the Datoviz binding exposes the retained `DvzPanelView3DDesc` / `DvzPanelView3DState` path;
- `MeshVisual.positions` are `(N, 3)` DATA coordinates attached to the retained View3D panel;
- mesh colors are fully opaque;
- depth test and depth write are enabled by the public GSP depth mode.

This does not promote transparent mesh depth, culling semantics, clipping strictness, or mesh
triangle picking.

## Evidence

Review pack:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
  --suite s050 \
  --out artifacts/visual_qa/s050/m218-depth-face-order \
  --resolution 640x480 \
  --run-id s050-m218-depth-face-order
```

Result: `artifacts/visual_qa/s050/m218-depth-face-order/index.md`

Datoviz checkout:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `a9492af6526fbb722e2c0783811758f1b15be10e`

The run rendered both S050 strict-depth cases through the real Datoviz offscreen path:

- `mesh3d/opaque_depth_intersecting_triangles_view3d`
- `mesh3d/opaque_depth_intersecting_triangles_reversed_view3d`

The Datoviz child processes recorded post-render teardown-crash artifacts, but the review-pack
parent completed with exit code 0 and produced PNG, report, summary, and capability-matrix
artifacts for both cases. This matches the accepted S050 offscreen isolation behavior: complete
post-report teardown crashes preserve rendered evidence but remain recorded.

## Pixel Audit

Expected samples:

- left NDC sample `(-0.55, -0.45)` -> red `[230, 57, 70]`
- right NDC sample `(0.20, -0.45)` -> blue `[69, 123, 157]`

Measured raw PNG samples:

| Backend | Case | Left RGB | Right RGB |
|---|---|---:|---:|
| Datoviz | original order | `[230, 57, 70]` | `[69, 123, 157]` |
| Datoviz | reversed order | `[230, 57, 70]` | `[69, 123, 157]` |
| Matplotlib | original order | `[69, 123, 157]` | `[69, 123, 157]` |
| Matplotlib | reversed order | `[69, 123, 157]` | `[69, 123, 157]` |

The reversed Datoviz case proves the observed red/blue split is invariant to face submission order.
The Matplotlib adapted-reference result remains blue at both samples, so the fixture still
distinguishes strict fragment-depth behavior from average-face painter ordering.

## Scope Guardrails

- Datoviz `query.view3d.mesh_triangle_pick.v1` remains unadvertised until public canonical mesh
  face/triangle identity exists.
- Non-opaque mesh alpha remains rejected for this capability.
- Culling and transparent-depth semantics remain blocked pending ChatGPT Pro consultation.
- Builds without retained DATA-space View3D bindings must continue using adapted CPU projection and
  must not advertise strict opaque depth.

## Validation

Focused tests:

```bash
uv run pytest tests/test_visual_qa_harness.py -q -k 's050 or s025_mesh_visual_qa_run or s034_layout_snapshot_reports_device_scale'
```

Result: `4 passed, 35 deselected`

