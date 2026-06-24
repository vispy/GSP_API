# Visual QA Harness - Accepted S023 Baseline

Status: accepted for S023; S024 text QA plan accepted.

The S023 visual QA harness lives under `gsp.qa.visual` and provides deterministic scene generation,
backend rendering, contact-sheet generation, reports, and manual review templates.

Run with both S023 backends when Datoviz v0.4 is active:

```bash
PYTHONPATH=../datoviz:. \
DYLD_LIBRARY_PATH=../datoviz/build/src \
DVZ_SHADERC_RUNTIME_LIBRARY=../datoviz/build/src/libshaderc_shared.dylib \
uv run python -m gsp.qa.visual run \
  --backends matplotlib,datoviz \
  --out artifacts/visual_qa/s023/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

Important outputs:

- `report.json`: machine-readable run result;
- `summary.md`: compact backend status table;
- `manual_notes.yaml`: human review checklist;
- `contact_sheets/s023_all_cases.png`: full side-by-side review sheet;
- `notes/*.md`: per-case manual notes.

Accepted S023 case families:

- point: basic, diameter ramp, alpha overlap;
- marker: shapes, angle/size/stroke;
- segment: width/cap, alpha/draw order;
- path: multiple subpaths, width, caps, joins;
- image: checker/origin, lower origin, scalar gray/clim, RGBA alpha;
- overlay: point over image layering.

The harness may report structured unsupported diagnostics when a backend binding is unavailable, but
S023 closeout was validated with all 13 Matplotlib and Datoviz cases rendered in the local v0.4
binding environment.

## S024 TextVisual QA plan

Add deterministic text cases with Matplotlib reference output, optional Datoviz output where
capability-gated support exists, contact sheets, and manual review notes:

- `text_basic_ndc`: centered ASCII label;
- `text_anchor_grid`: `LEFT/CENTER/RIGHT` by `TOP/CENTER/BOTTOM/BASELINE` with anchor markers;
- `text_rotation_anchor`: radians and anchor-pivot behavior;
- `text_alpha_overlap`: RGBA alpha and draw order;
- `text_size_dpi`: 8/13/24/40 px at multiple output DPIs;
- `text_data_vs_ndc`: data-attached labels plus panel-relative labels;
- `text_z_order`: layering relative to existing visuals;
- `text_multiline_smoke`: explicit newline behavior;
- `text_unicode_smoke`: capability-gated non-ASCII glyphs;
- `text_missing_glyph_diag`: strict diagnostic behavior;
- `text_guide_integration`: guides remain guides beside explicit TextVisuals;
- `text_query_smoke`: item-level payload when `query.text` is advertised.

Manual review focuses on semantic placement, size class, anchors, alpha, rotation, and diagnostics,
not pixel-perfect glyph raster identity across backends.
