# S050 Datoviz post-refactor replay

Date: 2026-07-05

Mission: M231 - S050 Datoviz post-refactor replay and result-code compatibility

## Outcome

Replayed the GSP Datoviz compatibility pack against the finished Datoviz `api/pre-rc-cleanup`
branch and patched GSP for the Datoviz pre-RC mutator return-code convention.

Datoviz checkout:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `api/pre-rc-cleanup`
- replay commit: `af168b5a9`
- worktree at initial inspection: clean

GSP did not modify the sibling Datoviz checkout. A later final status check during this turn showed
new sibling Datoviz work after the replay baseline: local commit `bb867b2ba` plus uncommitted
controller-file edits. Treat the artifacts in this note as evidence for `af168b5a9`, not for that
newer dirty sibling state.

## GSP compatibility fix

The Datoviz refactor changed many stable mutators from boolean return values to `DvzResult`, where
`0` is success. GSP was still treating successful `0` returns as false for some adapter paths.

GSP now centralizes Datoviz call success handling:

- `True` is success for old boolean-returning mutators;
- `False` is failure for old boolean-returning mutators;
- integer or ctypes integer `0` is success for `DvzResult`;
- nonzero integer results are failures;
- `None` remains success for void-style historical calls.

This unblocked sampled-field image upload against the finished Datoviz branch.

## Replay evidence

Command:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_pre_rc_replay.sh
```

Artifacts:

- `artifacts/visual_qa/s050/post_merge_datoviz_guide_axis/`
- `artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028/`
- `artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028/comparison_to_pre_rc_baseline/`

Baseline:

- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/`

## Matrix comparison

| Metric | Baseline | Candidate |
|---|---:|---:|
| strict | 42 | 52 |
| adapted | 4 | 4 |
| crashed | 14 | 4 |
| unsupported | 0 | 0 |
| disabled | 0 | 0 |
| not_run | 0 | 0 |

Comparison outcome:

| Outcome | Count |
|---|---:|
| improved | 10 |
| regressed | 0 |
| changed | 0 |
| unchanged | 50 |

Improved Datoviz rows:

- `point/diameter_ramp_ndc`
- `marker/shapes_ndc`
- `marker/angle_size_stroke_ndc`
- `image/scalar_gray_clim_ndc`
- `mesh/single_triangle_uniform_ndc_2d`
- `mesh/indexed_square_uniform_ndc_2d`
- `mesh/indexed_square_per_face_ndc_2d`
- `color/point_scalar_gray_range`
- `color/marker_scalar_fill_alpha`
- `transform/view2d_data_ndc_overlay`

Remaining Datoviz native SIGSEGV rows:

- `color/scalar_image_viridis_colorbar`
- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`
- `guide/view2d_grid_clip_title_boundary`

## M222 status

M222 remains blocked.

This replay proves that the Datoviz API cleanup improved broad S028 runtime stability, but it does
not resolve the Texture2D-specific M228 blockers:

- sampler control or fixed nearest/clamp/no-mipmap semantics;
- texture origin semantics;
- unmanaged numeric RGBA sampling or accepted alternate color-role contract;
- exact unlit texture color equation;
- Texture2D teardown/runtime stability.

Do not advertise Datoviz `texture2d.rgba8.v1`,
`meshvisual.uv.vertex2d.v1`, or `meshvisual.material.texture2d_unlit.v1` from this replay.

## Validation

Passed:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
  .venv/bin/python tools/datoviz_v04_smoke.py
```

```bash
.venv/bin/pytest -q \
  tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_call_succeeded_accepts_bool_and_result_conventions \
  tests/test_datoviz_v04_protocol_renderer.py::test_add_image_visual_uploads_packed_rgba8_sampled_field \
  tests/test_datoviz_v04_protocol_renderer.py::test_add_image_visual_uses_sampled_field_path_with_sampling_api \
  tests/test_visual_qa_harness.py::test_capability_matrix_comparison_reports_improvements_and_regressions
```

Result: `4 passed`.

```bash
.venv/bin/mypy src/gsp_datoviz/protocol_renderer.py --strict --show-error-codes
```

Result: clean.
