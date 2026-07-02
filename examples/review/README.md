# API review examples

These examples are intentionally small and readable. Use them to review the GSP protocol/API shape and compare Matplotlib with the Datoviz v0.4 renderer.

## Quick commands

Open one example live with Matplotlib or Datoviz:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib
uv run python examples/review/01_scatter_basic.py --backend datoviz
```

Open both live windows sequentially:

```bash
uv run python examples/review/01_scatter_basic.py --backend both
```

Open Matplotlib and Datoviz live windows at the same time:

```bash
tools/compare-review-examples --live-side-by-side examples/review/01_scatter_basic.py
```

Live review enables GSP navigation by default for supported `View2D` and `View3D` scenes:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib
uv run python examples/review/01_scatter_basic.py --backend datoviz
uv run python examples/review/07_view3d_cube.py --backend matplotlib
uv run python examples/review/11_view3d_lit_mesh_arcball.py --backend matplotlib
```

Use `--no-interactive-navigation` when you want a static live window:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --no-interactive-navigation
```

Open all numbered review examples with live interactivity where a `View2D` or `View3D` is present,
one example after another. Offscreen review remains static and deterministic.

```bash
tools/compare-review-examples
```

Open Matplotlib and Datoviz interactive windows side by side for one example:

```bash
tools/compare-review-examples --live-side-by-side examples/review/01_scatter_basic.py
```

If the local Datoviz v0.4 build does not expose the live pointer-input binding, the Datoviz window
still opens as a normal live review window and prints a message that GSP navigation is unavailable.
Datoviz `View3D` examples enable S037 navigation only when the local v0.4 build exposes both live
input and the retained DATA-space `View3D` descriptor/state APIs. Older builds keep the static live
window and print structured diagnostics.

For 3D material review, compare the Matplotlib and Datoviz windows side by side:

```bash
tools/compare-review-examples --live-side-by-side examples/review/10_view3d_flat_lambert.py
tools/compare-review-examples --live-side-by-side examples/review/11_view3d_lit_mesh_arcball.py
```

Matplotlib enables canonical GSP orbit/pan/zoom controls for arcball-style manual inspection.
Datoviz renders the public static `View3D` state through the adapted GSP panel-NDC mesh path and S040
CPU-resolved Lambert colors; native Datoviz `panel.arcball()` demos are legacy/evidence-only until a
public GSP bridge is designed and proven without reuploading fixed projected mesh buffers.

Capture and compare offscreen outputs:

```bash
uv run python examples/review/01_scatter_basic.py --backend both --offscreen
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Offscreen artifacts are written under `artifacts/example_review/<example>/`.

Live review uses `CanvasSize.reference_px(<resolution>, reference_dpi=96)` so Matplotlib and
Datoviz target comparable apparent physical size. Offscreen review uses
`CanvasSize.pixel_exact(<resolution>)` so captured PNG dimensions remain deterministic. Change
`reference_dpi` in code when you need a setup-specific physical-size tweak; use visual style scale
only for marker/text/stroke styling, not window sizing.

For live review on a setup where the native Datoviz window comes out too small, set a semantic
monitor-DPI override in your shell or `.envrc`:

```bash
export GSP_REVIEW_MONITOR_DPI=139.2  # equivalent to 96 * 1.45
```

This lets Datoviz resolve `reference_px(1280, 720, reference_dpi=96)` using 139.2 physical pixels per
inch. Matplotlib live review keeps using the reference DPI for its figure size; use
`GSP_REVIEW_REFERENCE_DPI` only if you want to redefine the reference-pixel size itself.

## Examples

| File | Reviews |
|---|---|
| `01_scatter_basic.py` | Data-space scatter, per-point color/size, View2D, labels, grid |
| `02_image_basic.py` | Scalar image, extent, origin, interpolation, grayscale clim |
| `03_points_over_image.py` | RGBA image plus point overlay and composition order |
| `04_guides_axes_ticks.py` | Explicit ticks, tick labels, axis labels, grid, title |
| `05_color_mapping_colorbar.py` | ColorScale, ScalarColorEncoding, named colormap, colorbar |
| `06_text_labels.py` | TextVisual labels, anchors, z-order over points |
| `07_view3d_cube.py` | Static `(N,3)` DATA cube projected through `View3D` |
| `08_view3d_terrain.py` | Static terrain-like `(N,3)` DATA mesh with per-face colors |
| `09_view3d_ndc_depth.py` | `(N,3)` NDC mesh with adapted opaque face-depth ordering |
| `10_view3d_flat_lambert.py` | S039/S040 flat Lambert face-normal mesh shading |
| `11_view3d_lit_mesh_arcball.py` | Lit faceted View3D mesh and Matplotlib arcball-style orbit review |

In live mode, Matplotlib `View3D` examples support S037 review navigation by default: left-drag
orbit, right/middle-drag pan, wheel zoom, and `r` reset. Datoviz `View3D` examples use the same
canonical action semantics when retained DATA-space visuals and live input are available: left-drag
orbit, right-drag pan, wheel zoom, and double-click reset.

The non-default `s036_alpha_not_strict_negative.py` script checks that translucent 3D mesh colors
raise `mesh3d_alpha_not_strict` in the opaque-depth path.

## Query And Capability Boundaries

The review examples exercise rendering and live navigation paths. Query/readback capabilities are
validated by focused protocol tests and backend capability gates:

| Capability | Current review boundary |
|---|---|
| `query.view3d.ray_readback.v1` | Returns canonical public ray-context payloads for `View3D`; it is not a visual-hit query. |
| `query.view3d.mesh_triangle_pick.v1` | Backend-neutral S044 payload with a Matplotlib CPU reference oracle for strict opaque DATA-space mesh picking. Datoviz v0.4 returns structured unsupported and must not advertise this capability until public visual/triangle mapping and pick-scene freshness are proven. |
| `meshvisual.positions3d.opaque_depth.v1` | Still not strict for Datoviz or the Matplotlib adapted reference path; visible review examples must not be used as strict GPU depth evidence. |
| Datoviz grid clipping | Native-verified separately from full guide strictness; it does not imply guide query or all-rendered contribution support. |

## Manual Review Checklist

Use this checklist before approving release preparation.

1. Read each `examples/review/[0-9]*.py` file and decide whether the public API shape is acceptable for the release candidate.
2. Generate offscreen artifacts:

   ```bash
   tools/compare-review-examples --offscreen
   ```

3. Inspect `artifacts/example_review/<example>/` for each example:

   | File | Meaning |
   |---|---|
   | `matplotlib.png` | Matplotlib reference output. |
   | `datoviz.png` | Datoviz output when local capture succeeds. |
   | `summary.json` | Backend status report. |
   | `datoviz.unsupported.json` | Local Datoviz offscreen capture was unavailable. |

4. If Datoviz offscreen capture is unavailable, run the live review path:

   ```bash
   tools/compare-review-examples --live-side-by-side
   ```

5. Compare each Matplotlib result with Datoviz where available:

   | Example | Accept if |
   |---|---|
   | `01_scatter_basic.py` | Point positions, colors, sizes, axes, labels, and grid are coherent. |
   | `02_image_basic.py` | Image orientation, extent, grayscale mapping, and interpolation look correct. |
   | `03_points_over_image.py` | Points overlay the image in the expected positions and order. |
   | `04_guides_axes_ticks.py` | Explicit ticks, tick labels, axis labels, grid, and title are readable. |
   | `05_color_mapping_colorbar.py` | Colors match scalar values and colorbar semantics are clear. |
   | `06_text_labels.py` | Labels are placed correctly, anchored reasonably, and drawn above points. |
   | `07_view3d_cube.py` | Matplotlib shows a projected cube; interactive navigation changes the canonical `View3D`. Datoviz uses retained DATA-space navigation when the local v0.4 build exposes the gated APIs, otherwise it renders the same static projection. |
   | `08_view3d_terrain.py` | Matplotlib terrain projection and per-face colors are coherent; Datoviz uses retained DATA-space navigation when available, otherwise it renders the same static projection. |
   | `09_view3d_ndc_depth.py` | Opaque NDC3 depth ordering is visible in both backends. |
   | `10_view3d_flat_lambert.py` | Flat Lambert face colors are visibly lit in both backends when Datoviz S040 support is available. |
   | `11_view3d_lit_mesh_arcball.py` | Matplotlib arcball-style orbit changes the lit mesh projection; Datoviz static view matches the same public projection and CPU-resolved Lambert colors. |

6. Record the review result in this form:

   ```text
   01 scatter: OK
   02 image: OK
   03 overlay: issue - <short description>
   04 guides: OK
   05 colorbar: OK
   06 text: acceptable - <short note>

   API shape: approve / needs changes
   Release: approve / defer
   Notes:
   - ...
   ```

Defer release only for API-shape problems, broken Matplotlib reference behavior, misleading docs/support claims, or Datoviz differences that contradict the advertised capability matrix. Local Datoviz offscreen capture being unsupported is not itself a release blocker.

The latest committed release-facing capability baseline is S045. Review-pack artifacts from S031
remain the broad 2D visual matrix baseline, while `artifacts/example_review/07_view3d_cube/`,
`artifacts/example_review/08_view3d_terrain/`, and
`artifacts/example_review/09_view3d_ndc_depth/` record the current static View3D offscreen review
paths. S039-S042 live 3D material/navigation checks are documented in the corresponding `.agent`
closeout files and are capability-gated for Datoviz.

## Datoviz HiDPI Fix Acceptance

Use this gate after the upstream Datoviz live high-DPI/text-anchor fix lands and the local Datoviz checkout is rebuilt.

1. Confirm the review runner uses the fixed Datoviz checkout:

   ```bash
   GSP_DATOVIZ_SOURCE=/home/cyrille/GIT/Viz/datoviz tools/compare-review-examples --live-side-by-side examples/review/05_color_mapping_colorbar.py examples/review/06_text_labels.py
   ```

2. Run the focused offscreen review path:

   ```bash
   GSP_DATOVIZ_SOURCE=/home/cyrille/GIT/Viz/datoviz tools/compare-review-examples --offscreen examples/review/05_color_mapping_colorbar.py examples/review/06_text_labels.py
   ```

3. Accept the Datoviz fix only if all of these hold:

   | Check | Required result |
   |---|---|
   | Live canvas size | Datoviz and Matplotlib have comparable apparent physical canvas size for the same `reference_px` request. |
   | Datoviz metrics | A requested `1280x720` reference canvas reports resolved host, framebuffer, and framebuffer-per-canvas metrics. |
   | No GSP workaround | GSP does not pass `DVZ_WINDOW_SIZE_SCALE` or any Datoviz-only live-size multiplier. |
   | Example 05 | The Datoviz colorbar is readable and does not overlap the plotted visual. |
   | Example 06 | Datoviz text labels match Matplotlib anchor semantics closely enough for visual review. |
   | Offscreen path | Examples 05 and 06 render or produce explicit unsupported status artifacts; no silent parity claim is made. |

4. Run the full local validation after the focused review passes:

   ```bash
   uv run pytest tests/ -q
   uv run mypy src/ --strict --show-error-codes
   tools/compare-review-examples --offscreen
   ```

Keep Datoviz release claims adapted until this gate passes against the fixed Datoviz checkout.

## Offscreen Capture Note

Live mode is the default interactive review path. The Datoviz v0.4 adapter automatically prefers a sibling `../datoviz` source checkout when present; set `GSP_DATOVIZ_SOURCE=/path/to/datoviz` to override, or `GSP_DATOVIZ_SOURCE=none` to disable this.

For a personal multi-machine Viz workspace, install the direnv template once:

```bash
tools/install-viz-envrc
```

This creates `../.envrc` from `tools/viz-workspace.envrc.example` and keeps the installed file local.

Offscreen PNG capture is opt-in for both Matplotlib and Datoviz:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --offscreen
uv run python examples/review/01_scatter_basic.py --backend datoviz --offscreen
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Datoviz offscreen creation can abort in some local GPU/display configurations. If Datoviz capture is unsupported, the runner writes `datoviz.unsupported.json` rather than pretending parity.
