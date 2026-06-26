# Visual QA Harness - Accepted S023 Baseline

Status: accepted for S023; S024 text QA accepted; S025 mesh QA plan accepted; S026 scalar color QA
plan accepted.

The S023 visual QA harness lives under `gsp.qa.visual` and provides deterministic scene generation,
backend rendering, contact-sheet generation, reports, and manual review templates.

Run with both S023 backends when Datoviz v0.4 is active. On macOS, prefer the wrapper so the sibling
Datoviz checkout and bundled MoltenVK ICD are configured consistently:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
tools/run_datoviz_visual_qa.sh \
  --suite s028 \
  --backends matplotlib,datoviz \
  --out artifacts/visual_qa/s028/latest-local \
  --run-id latest-local \
  --contact-sheet \
  --resolution 800x600
```

The wrapper sets `GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1`, prepends `PYTHONPATH` with `DATOVIZ_REPO`,
points `DYLD_LIBRARY_PATH` and `VK_ICD_FILENAMES` at the Datoviz `libs/vulkan/macos_arm64`
directory, and keeps the QA default Datoviz color pipeline at `legacy_srgb_blend`.

Visual QA uses `legacy_srgb_blend` by default because Matplotlib/Agg blends alpha directly in
display/sRGB values. That is the legacy, non-linear behavior required for pixel-level parity with
the Matplotlib reference. Datoviz also exposes the mathematically correct `linear_srgb` path, but
that mode is for Datoviz-correct comparisons and must be requested explicitly with
`--datoviz-color-pipeline linear_srgb`.

`legacy_srgb_blend` requires `dvz_figure_set_color_pipeline` in the Datoviz binding.

The equivalent manual command shape is:

```bash
PYTHONPATH=../datoviz:. \
DYLD_LIBRARY_PATH=../datoviz/libs/vulkan/macos_arm64 \
VK_ICD_FILENAMES=../datoviz/libs/vulkan/macos_arm64/MoltenVK_icd.json \
GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1 \
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

## S029 capability matrix and review pack

S029 adds a review-pack layer over the S023-S028 visual QA suites. The review pack does not promote
Datoviz behavior by rendering alone; it classifies each backend/case row as `strict`, `adapted`,
`experimental`, `unsupported`, `disabled`, `crashed`, or `not_run`.

Generate the current Matplotlib-left / Datoviz-right review pack on macOS with:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
tools/run_datoviz_visual_review_pack.sh \
  --suite s028 \
  --out artifacts/visual_qa/s029/latest-review-pack \
  --run-id s029-latest-review-pack \
  --resolution 800x600
```

Review-pack outputs:

- `index.md`: human entry point;
- `capability_matrix.json`: machine-readable taxonomy and evidence rows;
- `capability_matrix.md`: compact matrix table;
- `summary.json`: compact counts and contact-sheet pointers;
- `contact_sheets/`: case sheets and full-suite sheet.

Matplotlib rendered rows are the strict reference for S023-S028 2D semantics. Datoviz rendered rows
start as `adapted` until a family-specific promotion audit proves strict protocol conformance.
Datoviz guide query, all-rendered guide contributions, and public 3D camera/projection semantics
remain deferred. If Datoviz exposes a native visual family but the GSP adapter has not implemented
and verified the accepted GSP contract, the row must say so as a GSP adapter/verification gap rather
than as a missing Datoviz feature.

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


## S025 MeshVisual QA plan

Strict mesh QA covers deterministic 2D filled-triangle cases with Matplotlib reference output and
Datoviz output where capability gates pass:

- `mesh_single_triangle_uniform_ndc_2d`;
- `mesh_indexed_square_uniform_ndc_2d`;
- `mesh_indexed_square_per_face_ndc_2d`;
- `mesh_data_coordinates_2d`;
- `mesh_order_overlap_2d`;
- `mesh_validation_invalid_index`;
- `mesh_validation_bad_color_shape`;
- `mesh_query_face_2d`.

Optional/capability-gated cases include per-vertex color interpolation, 3D cube depth/culling, alpha
overlap, normals/flat shading, optional Lambert demonstration, 3D face query, and wireframe only if
later accepted. Manual review checks geometry placement, face colors, draw order, diagnostics, and
face-query payloads rather than pixel-perfect antialiasing.

## S026 scalar color QA plan

Strict scalar color QA covers deterministic color mapping and colorbar cases with Matplotlib
reference output:

- `scalar_image_gray_clim`;
- `scalar_image_viridis_lut`;
- `point_scalar_colors`;
- `marker_fill_scalar_colors`;
- `shared_color_scale_with_colorbar`;
- `colorbar_explicit_ticks`;
- `scalar_color_validation_failures`;
- `scalar_color_query_payloads`.

Optional/capability-gated cases include Datoviz canonical LUT upload, Datoviz GPU normalization,
CPU pre-map diagnostics, native Datoviz colorbar rendering with explicit tick-label parity still
unverified, strict 2D `MeshVisual` per-face scalar colors, and mesh face scalar query. Manual review
checks canonical color placement, endpoint clipping, explicit colorbar ticks/labels, diagnostics,
and scalar query payloads.

## S028 guide/View2D QA plan

Strict guide/View2D QA should cover deterministic semantic guide behavior against the Matplotlib
reference backend:

- normal and reversed x/y `View2D` limits;
- explicit x/y ticks and labels under normal and reversed axes;
- auto-linear-nice ticks under normal and reversed axes;
- grid lines tied to resolved tick values;
- guide labels and panel titles remaining semantic guides, not data visuals;
- guide-scoped and all-rendered query payloads using the same `View2D` snapshot as rendering;
- VisPy2 `set_xlim`, `set_ylim`, `set_view2d`, tick, label, and grid producer APIs.

Datoviz guide/View2D QA remains capability-gated. Unsupported Datoviz guide, grid, reversed-axis, or
guide-query behavior should appear as structured diagnostics rather than adapted visual success.
