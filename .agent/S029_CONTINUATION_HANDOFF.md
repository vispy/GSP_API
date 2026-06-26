# S029 Continuation Handoff

Updated: 2026-06-26

## Current State

S029 is open at 90% after the Datoviz guide/View2D unsupported closure.

Completed S029 missions:

- M112: capability matrix and review-pack foundation
- M113: Datoviz rendered-family promotion audit
- M114: Datoviz color/colorbar promotion audit
- M115: Datoviz text promotion audit
- M116: Datoviz mesh promotion audit
- M117: Datoviz transform promotion audit
- M118: Datoviz guide/View2D unsupported closure

Current pushed GSP branch:

- `agentic-gsp-vispy2`
- Latest completed commits include M115 text audit, macOS review-pack regeneration, MoltenVK
  launcher discovery, Datoviz binding regeneration note, and M116 mesh audit.

Current pushed Datoviz branch:

- `v0.4-dev`
- Latest relevant commit: `fb6a94718 Fix explicit colorbar tick handling`

Datoviz has one pre-existing local worktree marker:

- `m data`

Do not commit or revert that submodule marker unless the user explicitly asks.

## Current Review Pack

Current pack:

- `artifacts/visual_qa/s029/current-review-pack`

Current matrix status after M118:

- `strict`: 52
- `adapted`: 4
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
- `mesh/single_triangle_uniform_ndc_2d`
- `mesh/indexed_square_uniform_ndc_2d`
- `mesh/indexed_square_per_face_ndc_2d`
- `transform/inline_named_equivalence`
- `transform/view2d_data_ndc_overlay`
- `transform/family_affine_view2d`

All promoted Datoviz rows remain rendering-only:

- `query_supported: false`

Datoviz guide/View2D rows remain explicitly unsupported:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

Both are blocked on rendered/runtime proof for Datoviz axis tick/grid/title placement and guide or
all-rendered query semantics. The reversed-explicit row also requires exact explicit tick label and
reversed-domain proof.

## Next Mission Batch

The next batch is recorded as ready mission M119:

1. M119 - S029 review-pack closeout

Execute in order unless one mission exposes an upstream Datoviz blocker.

## Recommended Resume Command

From the GSP repo:

```bash
tools/agentctl next
tools/agentctl mission show M119
```

Then execute M119 locally or approve a bounded worker launch.

## Validation Baseline

Latest completed validation before this handoff:

- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 23 passed
- `PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_visual_qa_harness.py -q`:
  23 passed
- `PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`:
  93 passed
- `DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh --suite s028 --out artifacts/visual_qa/s029/current-review-pack --run-id current-review-pack --resolution 800x600`:
  passed after the local Datoviz dev environment was refreshed and the colorbar tick facade was
  verified.
- S029 full review pack regenerated successfully on macOS after regenerating Datoviz ctypes wrappers.
- `tools/run_datoviz_visual_review_pack.sh` smoke passed after teaching the launcher to discover
  `VK_ICD_FILENAMES`, VULKAN_SDK, and Homebrew MoltenVK locations.
- Datoviz validation: `just ctypes-check` and `tools/bindings/array_facade_smoke.py` passed with
  the Datoviz `.venv` on `PATH`.
- `git diff --check`: clean

M117 focused validation:

- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 23 passed
- `PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`:
  93 passed

M118 focused validation:

- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 24 passed
- `PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`:
  94 passed
- `DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh --suite s028 --out /tmp/gsp-s029-dataviz-binding-refresh.* --run-id binding-refresh-smoke --resolution 800x600`:
  passed; `color/scalar_image_viridis_colorbar` rendered and the matrix was `strict=52`,
  `adapted=4`, `unsupported=2`.

## Datoviz Binding Regeneration Note

If Datoviz C headers/API change, or if GSP reports missing Datoviz facade symbols that are present
in the C library, regenerate the Datoviz Python bindings before changing GSP adapter code.

From `/Users/cyrille/GIT/Viz/datoviz`:

```bash
uv pip install -r requirements-dev.txt
PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH just ctypes
PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH just ctypes-check
PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=. python tools/bindings/array_facade_smoke.py
```

Then verify expected direct facade symbols from GSP, for example:

```bash
PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run python - <<'PY'
import datoviz as dvz
print(hasattr(dvz, "dvz_text_placement"))
print(hasattr(dvz, "DvzColorbarTicks"))
print(hasattr(dvz, "dvz_colorbar_set_ticks"))
PY
```

Do not add GSP-side fallbacks for skipped/generated Datoviz ctypes helpers unless a spec/ADR
explicitly accepts that adaptation. The intended S029 path is direct Datoviz facade support.
