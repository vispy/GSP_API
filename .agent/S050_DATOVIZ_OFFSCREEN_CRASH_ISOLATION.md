# S050 Datoviz offscreen crash isolation

## Mission

M213 - S050 Datoviz offscreen crash isolation.

## Decision

Crash isolation belongs in the Python review-pack runner, not only in
`tools/run_datoviz_visual_review_pack.sh`.

The wrapper still configures the Datoviz checkout and offscreen opt-in environment, but
`run_visual_review_pack(mode="datoviz-offscreen-opt-in")` now runs Matplotlib in the parent process
and Datoviz in a child `python -m gsp.qa.visual run --backends datoviz` process. The parent merges a
clean Datoviz child report into the review pack, or records a structured Datoviz error row if the
child exits nonzero. Child staging artifacts are discarded unless the child exits cleanly.

## Validation

Focused tests passed:

```text
uv run pytest tests/test_visual_qa_harness.py -q -k 'datoviz_offscreen_review_pack or visual_review_pack_writes_matrix_and_index or s050'
5 passed, 32 deselected
```

M210 strict-depth isolated review-pack run completed with parent exit code `0`:

```text
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
  --suite s050 --out artifacts/visual_qa/s050/m213-depth-proof-isolated \
  --case mesh3d/opaque_depth_intersecting_triangles_view3d \
  --resolution 640x480 --run-id s050-m213-depth-isolated
```

Result: the parent review pack completed and removed `_datoviz_offscreen_child`. Datoviz reported a
structured unsupported row:

```text
AttributeError: type object 'DvzVisualCoordSpace' has no attribute 'DVZ_COORD_DATA'
```

M206 colorbar isolated review-pack run completed with parent exit code `0`:

```text
DATOVIZ_REPO=/home/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh \
  --suite s028 --out artifacts/visual_qa/s050/m213-colorbar-isolated \
  --case color/scalar_image_viridis_colorbar \
  --resolution 640x480 --run-id s050-m213-colorbar-isolated
```

Result: the parent review pack completed and removed `_datoviz_offscreen_child`. Datoviz reported a
structured unsupported row:

```text
AttributeError: type object 'DvzVisualCoordSpace' has no attribute 'DVZ_COORD_VIEW'
```

## Outcome

M213 is complete. The parent review-pack process no longer dies on Datoviz offscreen failures. In
the current local Datoviz checkout, the next blocker is coordinate-space enum compatibility in the
Datoviz Python facade or GSP adapter, not parent-process crash isolation.

No sibling Datoviz files were edited.
