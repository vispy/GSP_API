# S050 Datoviz Colorbar Explicit Tick Proof

Date: 2026-07-03

Mission: M206 - S050 Datoviz colorbar explicit tick proof

## Outcome

Completed after M214 latest-binding alignment.

The current local Datoviz facade exposes the colorbar explicit tick/label API, focused GSP adapter
tests pass, and the real Datoviz offscreen visual review path now renders
`color/scalar_image_viridis_colorbar` after M214 replaced stale generated-binding symbol usage.

No public `ColorbarGuide` semantics changed. Colorbar query remains unsupported. No Datoviz files
were edited.

## Local Datoviz Evidence

Read-only sibling checkout:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `dc8b168ed86e0f674be204d00c29e5869ee5e6c4`
- pre-existing dirty file: `NOTES`

Python facade symbol check:

| Symbol | Present |
|---|---|
| `dvz_colorbar_desc` | yes |
| `dvz_colorbar` | yes |
| `dvz_colorbar_set_title` | yes |
| `dvz_colorbar_set_ticks` | yes |
| `dvz_colorbar_set_format` | yes |

Source evidence:

- `src/scene/annotation/colorbar.c::dvz_colorbar_set_ticks()`
- `include/datoviz/scene/scale.h::dvz_colorbar_set_ticks()`
- `src/scene/tests/fields.c::test_scene_colorbar_explicit_ticks_and_labels`

## Validation

Passed:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz \
  uv run pytest tests/test_datoviz_v04_protocol_renderer.py -q -k 'colorbar'
```

Result: `4 passed, 138 deselected`.

Passed:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz \
  uv run pytest tests/test_visual_qa_harness.py -q -k 'colorbar or color_visual_qa'
```

Result: `1 passed, 32 deselected`.

Previously blocked:

```bash
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s028 \
  --out artifacts/visual_qa/s050/m206-colorbar-proof \
  --case color/scalar_image_viridis_colorbar \
  --resolution 640x480 \
  --run-id s050-m206-colorbar
```

Result: exit code `139`.

Partial artifacts were written under `artifacts/visual_qa/s050/m206-colorbar-proof`; the Datoviz
backend did not complete. A non-offscreen Datoviz diagnostic run completed and reported the expected
unsupported status because in-process Datoviz offscreen QA is disabled by default:

```bash
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz \
  uv run python -m gsp.qa.visual run \
  --suite s028 \
  --backends datoviz \
  --out artifacts/visual_qa/s050/m206-colorbar-smoke \
  --case color/scalar_image_viridis_colorbar \
  --no-contact-sheet \
  --resolution 320x240 \
  --run-id s050-m206-colorbar-smoke
```

Result: `artifacts/visual_qa/s050/m206-colorbar-smoke/report.json`, with Datoviz marked
`unsupported` due to offscreen QA opt-in safety.

M214 latest-binding validation passed:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s028 \
  --case color/scalar_image_viridis_colorbar \
  --out artifacts/visual_qa/s050/m214-latest-colorbar \
  --run-id s050-m214-latest-colorbar
```

Result: `artifacts/visual_qa/s050/m214-latest-colorbar/index.md`.

Datoviz rendered the case and the capability matrix reports:

- status: `strict`;
- review classification: `pass.semantic_strict`;
- reason code: `datoviz_rendered_strict_s029_family_audit`.

## Decision

Accept M206 as completed. The S050 colorbar proof has fresh Datoviz runtime evidence and no longer
depends only on the historical S029 audit. Colorbar query remains out of scope until native colorbar
guide-hit evidence exists.

Next safe work is M207 guide query strictness audit, which must still avoid promoting full guide
strictness if panel title evidence remains absent.
