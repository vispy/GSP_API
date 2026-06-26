# S029 Continuation Handoff

Updated: 2026-06-26

## Current State

S029 is open at 55% after the Datoviz text promotion audit.

Completed S029 missions:

- M112: capability matrix and review-pack foundation
- M113: Datoviz rendered-family promotion audit
- M114: Datoviz color/colorbar promotion audit
- M115: Datoviz text promotion audit

Current pushed GSP branch:

- `agentic-gsp-vispy2`
- Latest completed commit before M115: `5e09c58 Complete S029 Datoviz color audit`
- M115 changes are recorded by the commit containing this handoff update.

Current pushed Datoviz branch:

- `v0.4-dev`
- Latest relevant commit: `fb6a94718 Fix explicit colorbar tick handling`

Datoviz has one pre-existing local worktree marker:

- `m data`

Do not commit or revert that submodule marker unless the user explicitly asks.

## Current Review Pack

Current pack:

- `artifacts/visual_qa/s029/current-review-pack`

Current matrix status after M115:

- `strict`: 46
- `adapted`: 10
- `unsupported`: 2
- `crashed`: 0
- `disabled`: 0
- `experimental`: 0
- `not_run`: 0

Strict Datoviz rendered rows now include:

- point, marker, segment, path, image, overlay rows from M113
- `color/scalar_image_viridis_colorbar`
- `color/point_scalar_gray_range`
- `color/marker_scalar_fill_alpha`
- `text/rotation_alpha_ndc`

All promoted Datoviz rows remain rendering-only:

- `query_supported: false`

## Next Mission Batch

The next batch is recorded as ready missions M116-M119:

1. M116 - S029 Datoviz mesh promotion audit
2. M117 - S029 Datoviz transform promotion audit
3. M118 - S029 Datoviz guide/View2D unsupported closure
4. M119 - S029 review-pack closeout

Execute in order unless one mission exposes an upstream Datoviz blocker.

## Recommended Resume Command

From the GSP repo:

```bash
tools/agentctl next
tools/agentctl mission show M116
```

Then execute M116 locally or approve a bounded worker launch.

## Validation Baseline

Latest completed validation before this handoff:

- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 23 passed
- S029 capability matrix/index regenerated from existing `report.json`
- Full Datoviz runtime regeneration blocked locally: missing
  `/Users/cyrille/GIT/Viz/datoviz/libs/vulkan/macos_arm64/MoltenVK_icd.json`
- `git diff --check`: clean
