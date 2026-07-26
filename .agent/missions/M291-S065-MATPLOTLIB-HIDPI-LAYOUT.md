# M291 - S065 Matplotlib HiDPI logical layout normalization

## Status

Approved for direct execution with `codex-ucl-gpt-5.6-sol-medium`.

## Baseline

- GSP `61144d1` contains the accepted shared-layout contract and the M290 title-diagnostic regression.
- VisPy2 `81557b8` contains the independently accepted fail-closed gallery validator.
- `spec/backends/matplotlib.md` requires Matplotlib layout snapshots to expose plot and guide geometry in GSP logical/canvas pixels.
- `spec/current/views-layout.md` requires the plot rectangle to be contained by the outer panel and requires rendering, queries, navigation, and picking to share the same logical snapshot.
- Core containment validation is correct and must remain strict.
- Datoviz is not implicated and is read-only.

## Reproduction and root cause

On the macOS Retina backend, a default Matplotlib figure has `_original_dpi=100`, `figure.dpi=200`,
`figure.bbox=1280x960`, and a logical resolved canvas of `640x480`. The full panel is therefore
logical `(0,0,640,480)`, while current extraction incorrectly reports the physical axes box as
`(160,115.2,992,739.2)` and the render target as `1280x960` with `device_scale=1`. Core correctly
rejects the physical plot as outside the logical panel.

The defect is a coordinate-space mix in `gsp-matplotlib`: native Matplotlib display bboxes and
`axes.transData` are framebuffer/display coordinates, while the GSP snapshot is logical.

## Required implementation

1. Normalize Matplotlib layout production at the adapter boundary. Do not clamp rectangles or relax
   core containment.
2. When `_gsp_resolved_canvas` is present:
   - use its `canvas_width_px` and `canvas_height_px` as the render target logical size;
   - use its `output_dpi` as snapshot DPI;
   - use its resolved isotropic device scale for `RenderTarget.device_scale`, rather than a stale
     caller default;
   - compute actual display-to-logical x/y factors from `figure.bbox` divided by the resolved
     logical dimensions. This actual GUI factor is an implementation conversion and may differ from
     the requested output framebuffer scale.
3. Convert every extracted native display-space value through those factors:
   - `plot_rect_px` and `grid_clip_rect_px`;
   - axis-label, tick-label, title, and all combined guide boxes;
   - the affine `data_to_screen_transform`.
4. For direct resolver calls without `_gsp_resolved_canvas`, derive logical dimensions and DPI from
   `figure.get_size_inches()` and `_original_dpi` when the GUI backend has scaled `figure.dpi`;
   preserve unchanged behavior on ordinary Agg/non-HiDPI figures.
5. Handle x/y display conversion independently and reject only invalid, nonfinite, or nonpositive
   metrics. If a `ResolvedCanvas` itself declares unequal protocol device-scale x/y values that
   cannot fit scalar `RenderTarget.device_scale`, fail explicitly rather than average silently.
6. Preserve inset outer-panel allocation and all existing consumed-layout semantics.
7. Do not modify protocol/core semantics, Datoviz, public VisPy2 API, capability claims, camera math,
   or visual-size conversion constants.

## Required tests

- A deterministic simulated Retina producer case with logical `640x480` and physical/display
  `1280x960` proving:
  - render target and panel remain logical `640x480`;
  - physical plot `(160,115.2,992,739.2)` becomes logical
    `(80,57.6,496,369.6)`;
  - every guide box is logical;
  - the data-to-screen affine maps into the same logical plot rectangle.
- Direct resolver behavior without `_gsp_resolved_canvas` under simulated `_original_dpi`.
- Ordinary Agg/non-HiDPI behavior remains unchanged.
- Inset panel containment under scaled display coordinates.
- Explicit `CanvasSize`/output-DPI/device-scale behavior, including resolved device scale in the
  snapshot.
- Invalid or unequal resolved scale metadata fails explicitly.
- The canonical VisPy2 `minimal_query.py` and `text_billboards_3d.py` Matplotlib paths no longer
  raise layout containment errors on the current host.

## Required validation

- Focused Matplotlib layout, guide, query, and protocol-renderer tests.
- Full GSP pytest suite.
- Full VisPy2 pytest suite against the candidate GSP source.
- Complete strict GSP source mypy, Ruff, provider probes, and `git diff --check`.
- Seven Matplotlib gallery captures at exactly `800x600`.
- Do not invoke native Datoviz presentation in the worker sandbox.
- Commit one coherent GSP correction.

## Acceptance

- Independent source/static review issues unconditional ACCEPT.
- All emitted snapshot geometry and transforms are logical on Retina and ordinary backends.
- Core containment remains unchanged and strict.
- The two canonical VisPy2 failures and all full suites are green.
- No backend-specific scale compensation is introduced outside Matplotlib layout extraction.

## Stop conditions

- Stop rather than weakening containment or substituting broad clipping.
- Stop on a protocol/spec conflict, new public semantics, or any need for a Datoviz edit.
- Do not edit VisPy2, Datoviz, Mission Control decisions, credentials, package versions, or release
  metadata.
- The VisPy2 tests-only path lock exists solely so the isolated launcher can mount that repository
  for validation; it does not authorize edits.
- Do not push, merge, tag, release, publish, create a PR, or run native Datoviz presentation.
