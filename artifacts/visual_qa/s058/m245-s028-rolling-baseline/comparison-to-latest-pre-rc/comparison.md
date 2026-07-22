# Visual QA capability matrix comparison

- Baseline: `artifacts/visual_qa/s050/latest_pre_rc_compat_s028/capability_matrix.json`
- Candidate: `artifacts/visual_qa/s058/m245-s028-rolling-baseline/capability_matrix.json`
- Baseline run: `latest-pre-rc-compat-s028`
- Candidate run: `s058-m245-v04dev-71c444cee`

## Summary

| Outcome | Count |
|---|---:|
| improved | 4 |
| regressed | 0 |
| changed | 0 |
| added | 0 |
| removed | 0 |
| unchanged | 56 |

## Improvements

| Backend | Case | Baseline | Candidate |
|---|---|---|---|
| datoviz | `color/scalar_image_viridis_colorbar` | crashed | strict |
| datoviz | `guide/view2d_auto_grid` | crashed | adapted |
| datoviz | `guide/view2d_grid_clip_title_boundary` | crashed | adapted |
| datoviz | `guide/view2d_reversed_explicit` | crashed | adapted |
