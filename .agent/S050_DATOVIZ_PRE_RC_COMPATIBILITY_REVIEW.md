# S050 Datoviz pre-RC compatibility review

Date: 2026-07-05

Mission: M229 - S050 Datoviz pre-RC compatibility review and handoff

## Outcome

Completed a GSP-side compatibility pass against the sibling Datoviz `api/pre-rc-cleanup` branch
without editing Datoviz.

GSP now anticipates the Datoviz pre-RC API cleanup:

- `dvz_visual_set_texture_rgba8()` is no longer a required GSP Datoviz facade symbol.
- Packed RGBA image visuals use the sampled-field path (`dvz_sampled_field` plus
  `dvz_visual_set_field`) like scalar/RGB images.
- View2D setup accepts the pre-RC `dvz_panel_view2d_desc()` factory and keeps
  `dvz_panel_view2d()` only as a historical fallback.
- Isolated Datoviz review-pack children have a bounded runtime through
  `GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS`, so a hung native child becomes a structured crash row.

This does not unblock M222. Datoviz Texture2D strict promotion remains blocked by the M228 sampler,
origin, unmanaged RGBA, multiplication, DATA-role crash, and teardown-abort findings.

## Datoviz checkout

Read-only sibling checkout:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `api/pre-rc-cleanup`
- commit during review: `ed846dd094679f7f75f2ad9eef43ed1fe7c09e1b`
- worktree note: dirty from the parallel Datoviz agent; GSP did not modify it

## GSP commits

| Commit | Purpose |
|---|---|
| `c25d7da` | Align GSP Datoviz adapter with pre-RC API |
| `d1d3285` | Bound isolated Datoviz review child runtime |
| `178fd08` | Record Datoviz pre-RC compatibility review pack |

## Evidence

Primary evidence pack:

- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/`
- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/index.md`
- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/report.json`
- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/capability_matrix.json`

Command:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1 \
GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS=45 \
uv run python -m gsp.qa.visual review-pack \
  --suite s028 \
  --mode datoviz-offscreen-opt-in \
  --out artifacts/visual_qa/s050/pre_rc_compat_s028_timeout \
  --resolution 800x600 \
  --run-id pre-rc-compat-s028-timeout
```

Datoviz row summary:

| Status | Count |
|---|---:|
| strict | 12 |
| adapted | 4 |
| crashed | 14 |

Full matrix summary:

| Status | Count |
|---|---:|
| strict | 42 |
| adapted | 4 |
| crashed | 14 |
| unsupported | 0 |
| disabled | 0 |
| experimental | 0 |
| not_run | 0 |

Focused validation passed:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
  .venv/bin/pytest -q tests/test_visual_qa_harness.py
```

Result: `43 passed`.

```bash
.venv/bin/mypy src/gsp/qa/visual/review_pack.py --strict --show-error-codes
```

Result: clean.

## Crash rows for Datoviz upstream

All crash rows are per-case isolated Datoviz children. Each exited with signal 11 and empty
stdout/stderr. No Python exception was captured.

| Case | Family | Required features |
|---|---|---|
| `point/diameter_ramp_ndc` | point | point, ndc, rgba8, diameter-ramp |
| `marker/shapes_ndc` | marker | marker, ndc, rgba8, shape, stroke |
| `marker/angle_size_stroke_ndc` | marker | marker, ndc, rgba8, angle, pixel-size, stroke |
| `image/scalar_gray_clim_ndc` | image | image, ndc, scalar, gray, clim |
| `mesh/single_triangle_uniform_ndc_2d` | mesh | mesh, ndc, rgba8, uniform, 2d |
| `mesh/indexed_square_uniform_ndc_2d` | mesh | mesh, ndc, rgba8, indexed, 2d |
| `mesh/indexed_square_per_face_ndc_2d` | mesh | mesh, ndc, rgba8, per-face, 2d |
| `color/scalar_image_viridis_colorbar` | color | image, scalar, colormap, colorbar, viridis |
| `color/point_scalar_gray_range` | color | point, scalar, colormap, range-clipping |
| `color/marker_scalar_fill_alpha` | color | marker, scalar, fill, alpha |
| `transform/view2d_data_ndc_overlay` | transform | view2d, data, ndc, reversed-limits |
| `guide/view2d_auto_grid` | guide | guide, view2d, auto-ticks, grid, labels |
| `guide/view2d_reversed_explicit` | guide | guide, view2d, reversed-limits, explicit-ticks, grid, labels |
| `guide/view2d_grid_clip_title_boundary` | guide | guide, view2d, explicit-ticks, grid, plot-clip, title |

Crash artifacts live under:

```text
artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/backends/datoviz/*.native_crash.json
```

## Rendered/adapted rows

The pre-RC branch still renders a useful subset:

- strict rows include basic point, alpha point, segment, path, RGBA image, overlay, and selected
  transform rows.
- adapted rows are the known text rows: `text/basic_ndc`, `text/anchor_grid_ndc`,
  `text/data_vs_ndc`, and `text/multiline_unicode_smoke`.

This means the pre-RC API alignment is viable at the Python/facade level. The remaining failures are
native runtime stability rows, not missing GSP symbol compatibility.

## Datoviz upstream handoff

Suggested upstream Datoviz debugging order:

1. Start with the smallest failing rows:
   - `point/diameter_ramp_ndc`
   - `marker/shapes_ndc`
   - `image/scalar_gray_clim_ndc`
2. Then inspect family-wide failures:
   - all three 2D mesh rows crash;
   - all three guide/View2D rows crash;
   - all scalar/color rows crash.
3. Compare against rendered neighbors:
   - `point/basic_ndc` and `point/alpha_overlap_ndc` render;
   - `image/checker_nearest_ndc`, `image/origin_lower_ndc`, and `image/rgba_alpha_ndc` render;
   - `transform/family_affine_view2d` renders while `transform/view2d_data_ndc_overlay` crashes.
4. Preserve the GSP command shape above so Datoviz can reproduce the same one-case child process
   behavior.

Do not ask GSP to add compatibility aliases for removed Datoviz pre-RC symbols. The current GSP
adapter already accepts the expected pre-RC surface.

## Post-Dataviz-merge checklist

After the Datoviz `api/pre-rc-cleanup` branch lands or materially changes:

1. Verify import/API shape:

   ```bash
   PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
     .venv/bin/python tools/datoviz_v04_smoke.py
   ```

2. Verify guide-axis symbol/probe state:

   ```bash
   PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
     .venv/bin/python tools/probe_datoviz_guide_axis.py \
     --out artifacts/visual_qa/s050/post_merge_datoviz_guide_axis
   ```

3. Rerun the broad review pack:

   ```bash
   DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
   PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. \
   GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1 \
   GSP_DATOVIZ_QA_CHILD_TIMEOUT_SECONDS=45 \
   uv run python -m gsp.qa.visual review-pack \
     --suite s028 \
     --mode datoviz-offscreen-opt-in \
     --out artifacts/visual_qa/s050/post_merge_pre_rc_compat_s028 \
     --resolution 800x600 \
     --run-id post-merge-pre-rc-compat-s028
   ```

4. Compare Datoviz row counts against this baseline:
   - current baseline: 12 strict, 4 adapted, 14 crashed;
   - any crash reduction should be inspected before promotion;
   - any strict-row regression should block Datoviz promotion.

5. Keep M222 blocked unless the Texture2D-specific M228 blockers are resolved by fresh runtime
   evidence.

## Decision

Record this as GSP compatibility evidence and Datoviz upstream handoff. Do not change GSP capability
advertisement or release posture from this run.

