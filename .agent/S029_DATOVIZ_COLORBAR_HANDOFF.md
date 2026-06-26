# S029 Datoviz Colorbar Handoff

Updated: 2026-06-26

## Current Branch And Commits

- Branch: `agentic-gsp-vispy2`
- Pushed latest commit: `28b1f71 Archive P014 Datoviz colorbar consultation`
- Prior related GSP commits:
  - `d5a9046 Open S029 visual review pack`
  - `ccb7a9a Update S029 Datoviz visual review pack`
  - `cb838ea Improve S029 colorbar review rendering`

## Consultation Archive

P014 is archived in:

- `.agent/consultations/P014-datoviz-colorbar-explicit-ticks-api.md`
- `.agent/consultations/P014-response.md`

The accepted recommendation is to add a Datoviz colorbar-specific explicit tick descriptor and
dynamic mutators, not to extend `DvzColorbarDesc` and not to reuse `DvzAxisTicks` publicly.

## Datoviz State

The sibling Datoviz repo `/Users/cyrille/GIT/Viz/datoviz` has a pushed WIP commit:

- Branch: `v0.4-dev`
- Commit: `0be4b0da8 WIP add explicit colorbar ticks API`
- Handoff: `agents/now/HANDOFF_COLORBAR_EXPLICIT_TICKS_API.md`

That WIP adds:

- `DvzColorbarTicks`
- `dvz_colorbar_ticks()`
- `dvz_colorbar_set_ticks()`
- `dvz_colorbar_clear_ticks()`
- Python array facade generator support for `dvz_colorbar_set_ticks(colorbar, values, labels=None)`

## Important Blocker

Do not wire GSP to the new Datoviz colorbar API until the Datoviz WIP is fixed and validated.

Current Datoviz validation status:

- `cmake --build build --target dvztest_scene -j4` succeeds.
- Focused `dvztest_scene` colorbar execution currently segfaults with exit code 139.
- The crash was not debugged because the user requested immediate WIP commits and pushes.

## Next GSP Work

After Datoviz is green:

1. Update `src/gsp_datoviz/protocol_renderer.py` so `ColorbarGuide.ticks` / labels call
   `dvz_colorbar_set_ticks()`.
2. Update fake Datoviz facade tests to include the new colorbar tick functions.
3. Regenerate S029 Datoviz review outputs, especially the scalar image viridis colorbar case.
4. Refresh capability documentation/matrix if explicit colorbar tick labels become strict instead
   of adapted/unsupported.
5. Run:
   - `uv run pytest tests/ -q`
   - `uv run mypy src/ --strict --show-error-codes`
   - Datoviz import smoke
   - `git diff --check`

## Visual QA Context

The user confirmed the latest regenerated colorbar image looked good after margin/title changes, but
explicit Datoviz colorbar ticks/labels still require the upstream Datoviz API to land cleanly.

Also preserve the documented color behavior: Datoviz must use sRGB legacy mode for parity with
Matplotlib's default non-mathematically-correct sRGB alpha blending behavior where required by S029.
