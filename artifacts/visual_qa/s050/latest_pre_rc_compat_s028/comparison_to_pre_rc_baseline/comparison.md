# Visual QA capability matrix comparison

- Baseline: `/home/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/capability_matrix.json`
- Candidate: `/home/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/latest_pre_rc_compat_s028/capability_matrix.json`
- Baseline run: `pre-rc-compat-s028-timeout`
- Candidate run: `latest-pre-rc-compat-s028`

## Summary

| Outcome | Count |
|---|---:|
| improved | 10 |
| regressed | 0 |
| changed | 0 |
| added | 0 |
| removed | 0 |
| unchanged | 50 |

## Improvements

| Backend | Case | Baseline | Candidate |
|---|---|---|---|
| datoviz | `color/marker_scalar_fill_alpha` | crashed | strict |
| datoviz | `color/point_scalar_gray_range` | crashed | strict |
| datoviz | `image/scalar_gray_clim_ndc` | crashed | strict |
| datoviz | `marker/angle_size_stroke_ndc` | crashed | strict |
| datoviz | `marker/shapes_ndc` | crashed | strict |
| datoviz | `mesh/indexed_square_per_face_ndc_2d` | crashed | strict |
| datoviz | `mesh/indexed_square_uniform_ndc_2d` | crashed | strict |
| datoviz | `mesh/single_triangle_uniform_ndc_2d` | crashed | strict |
| datoviz | `point/diameter_ramp_ndc` | crashed | strict |
| datoviz | `transform/view2d_data_ndc_overlay` | crashed | strict |
