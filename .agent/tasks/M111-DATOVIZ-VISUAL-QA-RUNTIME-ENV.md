# M111 - Datoviz Visual QA Runtime Env and Image Sampling Gate

Status: completed

## Goal

Make post-S028 Datoviz visual QA runnable and reviewable on the local macOS v0.4-dev runtime without
requiring developers to remember transient environment variables.

## Closeout

- Added `tools/run_datoviz_visual_qa.sh`, which opts into in-process offscreen QA, points Python at
  the sibling Datoviz checkout, and configures the bundled MoltenVK ICD on macOS.
- Changed the visual QA Datoviz color-pipeline default to `linear_srgb`, matching the v0.4-dev
  facade available today. `legacy_srgb_blend` remains explicit opt-in and still requires
  `dvz_figure_set_color_pipeline`.
- Updated the Datoviz backend and visual QA harness specs with the new runtime command and color
  pipeline policy.
- Captured a full S028 Datoviz runtime-fixed visual QA artifact set for review.
- Left text, mesh, colorbar, guide, and true 3D promotion deferred pending P013 and Datoviz-side
  contract decisions.

## Evidence

- Review note: `artifacts/visual_qa/s028/datoviz-runtime-fixed-review.md`
- Contact sheet: `artifacts/visual_qa/s028/datoviz-runtime-fixed-full/contact_sheets/s028_all_cases.png`
- Structured report: `artifacts/visual_qa/s028/datoviz-runtime-fixed-full/report.json`
