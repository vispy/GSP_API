# S050 Datoviz latest pre-RC replay

Date: 2026-07-05

Mission: M232 - S050 Datoviz latest pre-RC compatibility impact replay

## Outcome

Replayed the GSP Datoviz compatibility pack against the current sibling Datoviz
`api/pre-rc-cleanup` checkout after the post-M231 controller/result-contract and teardown updates.

| Field | Value |
|---|---|
| Datoviz path | `/home/cyrille/GIT/Viz/datoviz` |
| Branch | `api/pre-rc-cleanup` |
| Replay commit | `1ef626a56` |
| Worktree | clean |
| GSP planning checkpoint | `64ab6ec` |

The latest Datoviz tail after M231 includes:

- controller/camera/panzoom/arcball/turntable/fly mutators returning `DvzResult`;
- generated raw `ctypes` refreshes;
- GUI/canvas teardown timing waits;
- pre-RC API exception classification and future composition-layer planning docs.

## Validation

Passed:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run python tools/datoviz_v04_smoke.py
```

Result: Datoviz v0.4 facade import OK, sampled fields ready, capture ready, query binding ready,
live point hit OK, live image hit OK.

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run python -m pytest -q \
  tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_call_succeeded_accepts_bool_and_result_conventions \
  tests/test_datoviz_v04_protocol_renderer.py::test_add_image_visual_uploads_packed_rgba8_sampled_field \
  tests/test_datoviz_v04_protocol_renderer.py::test_add_image_visual_uses_sampled_field_path_with_sampling_api \
  tests/test_datoviz_v04_protocol_renderer.py::test_retained_view2d_navigation_update_does_not_reupload_visual_buffers \
  tests/test_datoviz_v04_protocol_renderer.py::test_retained_view3d_navigation_updates_camera_without_reuploading_mesh_buffers \
  tests/test_datoviz_v04_protocol_renderer.py::test_retained_view3d_navigation_updates_perspective_camera_without_reupload
```

Result: `6 passed`.

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run mypy \
  src/gsp_datoviz/protocol_renderer.py --strict --show-error-codes
```

Result: clean.

Replay command:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
OUT_DIR=/home/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/latest_pre_rc_compat_s028 \
GUIDE_OUT=/home/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/latest_pre_rc_datoviz_guide_axis \
COMPARE_OUT=/home/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/latest_pre_rc_compat_s028/comparison_to_pre_rc_baseline \
RUN_ID=latest-pre-rc-compat-s028 \
tools/run_datoviz_pre_rc_replay.sh
```

Additional comparison:

```bash
uv run python -m gsp.qa.visual compare-matrix \
  --baseline artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028 \
  --candidate artifacts/visual_qa/s050/latest_pre_rc_compat_s028 \
  --out artifacts/visual_qa/s050/latest_pre_rc_compat_s028/comparison_to_m231
```

## Replay Evidence

Artifacts:

- `artifacts/visual_qa/s050/latest_pre_rc_datoviz_guide_axis/`
- `artifacts/visual_qa/s050/latest_pre_rc_compat_s028/`
- `artifacts/visual_qa/s050/latest_pre_rc_compat_s028/comparison_to_pre_rc_baseline/`
- `artifacts/visual_qa/s050/latest_pre_rc_compat_s028/comparison_to_m231/`

Latest matrix:

| Status | Count |
|---|---:|
| strict | 52 |
| adapted | 4 |
| crashed | 4 |
| unsupported | 0 |
| disabled | 0 |
| not_run | 0 |

Comparison to the committed pre-RC timeout baseline:

| Outcome | Count |
|---|---:|
| improved | 10 |
| regressed | 0 |
| changed | 0 |
| unchanged | 50 |

Comparison to M231:

| Outcome | Count |
|---|---:|
| improved | 0 |
| regressed | 0 |
| changed | 0 |
| unchanged | 60 |

Remaining Datoviz crashed rows:

- `color/scalar_image_viridis_colorbar`;
- `guide/view2d_auto_grid`;
- `guide/view2d_reversed_explicit`;
- `guide/view2d_grid_clip_title_boundary`.

## Decision

No GSP adapter code change is needed for the latest Datoviz pre-RC tail. The existing generic
Datoviz call-success handling covers the new `DvzResult` mutator contracts used by the adapter
paths tested here.

No capability rows are promoted from M232. Crash reductions did not improve beyond M231, and the
remaining colorbar/guide rows still terminate the isolated Datoviz offscreen child with signal 11.

M222 remains blocked. The latest Datoviz changes do not provide Texture2D-specific evidence for
sampler behavior, origin behavior, unmanaged RGBA sampling, or exact unlit multiplication.
