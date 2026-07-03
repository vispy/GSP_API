# S050 Datoviz TextVisual Strictness Proof

Date: 2026-07-03

Mission: M208 - S050 Datoviz TextVisual strictness proof

## Outcome

Completed with no new Datoviz TextVisual strict promotion.

The current latest-only Datoviz v0.4-dev generated binding can render the focused TextVisual cases
when run one case per Datoviz offscreen child process, but only the already-promoted
`text/rotation_alpha_ndc` row satisfies the current strict rendered scope. The other four rows remain
adapted for the same semantic blockers recorded in S029 and S050 scoping.

No public `TextVisual` anchor, DATA coordinate, multiline, Unicode, or query/readback semantics were
changed. No sibling Datoviz files were edited.

## Latest Binding Fix

M208 found one real latest-binding issue before the text proof could be interpreted: packed RGBA8
image uploads were passing a NumPy array to `dvz_visual_set_texture_rgba8()`, while the generated
ctypes binding declares:

```text
DvzVisual*, POINTER(c_ubyte), c_uint, c_uint, c_ulong
```

The GSP adapter now passes a contiguous `POINTER(c_ubyte)` for packed RGBA8 texture uploads. This is
not a compatibility shim; it matches the current generated C API binding.

## Runtime Evidence

Combined five-case TextVisual review pack:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s024 \
  --case text/basic_ndc \
  --case text/anchor_grid_ndc \
  --case text/rotation_alpha_ndc \
  --case text/data_vs_ndc \
  --case text/multiline_unicode_smoke \
  --out artifacts/visual_qa/s050/m208-textvisual-strictness \
  --run-id s050-m208-textvisual-strictness
```

Result: parent review pack completed, but the Datoviz child process crashed with signal 11, so the
combined Datoviz rows are classified as `crashed`. This remains useful runtime evidence: the
multi-case Datoviz text path is not stable enough to support any broader promotion.

Isolated one-case review packs:

```bash
for case_id in text/basic_ndc text/anchor_grid_ndc text/rotation_alpha_ndc \
  text/data_vs_ndc text/multiline_unicode_smoke; do
  safe=${case_id//\//_}
  DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
    tools/run_datoviz_visual_review_pack.sh \
    --suite s024 \
    --case "$case_id" \
    --out "artifacts/visual_qa/s050/m208-textvisual-strictness-isolated/$safe" \
    --run-id "s050-m208-textvisual-$safe"
done
```

Result:

| Row | Isolated Datoviz status | Decision |
|---|---|---|
| `text/basic_ndc` | `adapted` / `review.adapted` | Keep adapted: default `BASELINE` anchor semantics are not strictly verified. |
| `text/anchor_grid_ndc` | `adapted` / `review.adapted` | Keep adapted: baseline/top/center/bottom text-box anchors need a focused fixture. |
| `text/rotation_alpha_ndc` | `strict` / `pass.semantic_strict` | Keep strict for the existing bounded scope: center-anchored NDC ASCII text, rotation, alpha, logical font size, and image overlay order. |
| `text/data_vs_ndc` | `adapted` / `review.adapted` | Keep adapted: DATA and NDC placement are only proven under identity `[-1,+1]` view. |
| `text/multiline_unicode_smoke` | `adapted` / `review.adapted` | Keep adapted: Unicode fallback and multiline `BASELINE` anchoring remain unverified. |

Local Datoviz checkout used read-only:

- path: `/Users/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `f5b81a397e3be69ecfffbffa88754c1c227e6820`
- imported module: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`

The sibling checkout had pre-existing dirty files and was not modified.

## Validation

Passed:

```bash
PYTHONPATH=src python -m pytest \
  tests/test_datoviz_v04_protocol_renderer.py \
  -k 'image_visual or text_visual'
```

Result: `9 passed, 133 deselected`.

## Decision

Accept M208 as completed.

Do not promote any additional Datoviz TextVisual rows. Keep text query/readback unsupported. Treat
the combined TextVisual crash as a runtime stability blocker for broader claims, and use the
isolated artifacts only to preserve the existing bounded strict row and confirm the remaining rows
stay adapted.
