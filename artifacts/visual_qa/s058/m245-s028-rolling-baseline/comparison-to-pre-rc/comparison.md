# Visual QA capability matrix comparison

- Baseline: `/Users/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/capability_matrix.json`
- Candidate: `/Users/cyrille/GIT/Viz/GSP_API/artifacts/visual_qa/s058/m245-s028-rolling-baseline/capability_matrix.json`
- Baseline run: `pre-rc-compat-s028-timeout`
- Candidate run: `s058-m245-v04dev-71c444cee`

## Summary

| Outcome | Count |
|---|---:|
| improved | 14 |
| regressed | 0 |
| changed | 0 |
| added | 0 |
| removed | 0 |
| unchanged | 46 |

## Improvements

| Backend | Case | Baseline | Candidate |
|---|---|---|---|
| datoviz | `color/marker_scalar_fill_alpha` | crashed | strict |
| datoviz | `color/point_scalar_gray_range` | crashed | strict |
| datoviz | `color/scalar_image_viridis_colorbar` | crashed | strict |
| datoviz | `guide/view2d_auto_grid` | crashed | adapted |
| datoviz | `guide/view2d_grid_clip_title_boundary` | crashed | adapted |
| datoviz | `guide/view2d_reversed_explicit` | crashed | adapted |
| datoviz | `image/scalar_gray_clim_ndc` | crashed | strict |
| datoviz | `marker/angle_size_stroke_ndc` | crashed | strict |
| datoviz | `marker/shapes_ndc` | crashed | strict |
| datoviz | `mesh/indexed_square_per_face_ndc_2d` | crashed | strict |
| datoviz | `mesh/indexed_square_uniform_ndc_2d` | crashed | strict |
| datoviz | `mesh/single_triangle_uniform_ndc_2d` | crashed | strict |
| datoviz | `point/diameter_ramp_ndc` | crashed | strict |
| datoviz | `transform/view2d_data_ndc_overlay` | crashed | strict |
