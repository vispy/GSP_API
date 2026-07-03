# S050 Datoviz retained View3D depth proof

## Mission

M210 - S050 Datoviz retained View3D depth runtime proof.

## Fixture

M210 implemented the M209 fixture as visual QA suite `s050`, case
`mesh3d/opaque_depth_intersecting_triangles_view3d`.

The fixture uses two opaque DATA-space triangles with the same projected XY footprint and opposite
depth gradients under an orthographic `View3D`. Strict per-fragment depth should produce red at the
left sample and blue at the right sample. Average-face painter sorting draws blue last across the
whole overlap.

## Code changes

- Added `S050_SUITE` and the strict-depth candidate case to `src/gsp/qa/visual/cases.py`.
- Added a `view3d` slot to `VisualQAScene`.
- Threaded `view3d` through the visual QA Matplotlib and Datoviz render paths.
- Wrote `view3d` metadata into scene artifacts.
- Added focused visual QA tests for the S050 case and artifact metadata.

## Validation

Focused tests passed:

```text
uv run pytest tests/test_visual_qa_harness.py -q -k 's050 or s025_mesh_visual_qa_run or s034_layout_snapshot_reports_device_scale'
4 passed, 31 deselected
```

Matplotlib review-pack run completed:

```text
uv run python -m gsp.qa.visual review-pack --suite s050 --mode matplotlib-only \
  --out artifacts/visual_qa/s050/m210-depth-proof-matplotlib \
  --case mesh3d/opaque_depth_intersecting_triangles_view3d \
  --resolution 640x480 --run-id s050-m210-depth-matplotlib
```

Diagnostic Datoviz review-pack run completed with Datoviz offscreen disabled by policy:

```text
uv run python -m gsp.qa.visual review-pack --suite s050 --mode datoviz-diagnostic \
  --out artifacts/visual_qa/s050/m210-depth-proof-diagnostic \
  --case mesh3d/opaque_depth_intersecting_triangles_view3d \
  --resolution 640x480 --run-id s050-m210-depth-diagnostic
```

The diagnostic probe reported Datoviz source revision
`dc8b168ed86e0f674be204d00c29e5869ee5e6c4`, minimal point support, and capture symbols available.

Previous Datoviz opt-in offscreen run failed:

```text
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
  --suite s050 --out artifacts/visual_qa/s050/m210-depth-proof-dataviz \
  --case mesh3d/opaque_depth_intersecting_triangles_view3d \
  --resolution 640x480 --run-id s050-m210-depth-dataviz
```

Result: exit code `139`.

The failed run wrote PNG/log artifacts before the process exited, but no completed `report.json`,
`capability_matrix.json`, or review-pack index was produced. Those partial PNG artifacts are not
accepted as strict-depth evidence because the native process crashed.

M214 latest-binding validation completed the Datoviz run:

```text
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
  --suite s050 \
  --case mesh3d/opaque_depth_intersecting_triangles_view3d \
  --out artifacts/visual_qa/s050/m214-latest-depth \
  --run-id s050-m214-latest-depth
```

Result: `artifacts/visual_qa/s050/m214-latest-depth/index.md`.

The Datoviz backend rendered, with capability matrix status `adapted`, review classification
`review.adapted`, and reason code `datoviz_rendered_pending_promotion_audit`.

## Decision

Do not advertise `meshvisual.positions3d.opaque_depth.v1` for Datoviz.

The crash and stale generated-binding blockers are resolved, but M210 remains blocked on manual
review and a family-specific strict-depth promotion audit. The strict-depth fixture and local
harness support are ready; promotion requires accepting the M214 Datoviz artifact as strict
per-fragment depth evidence.
