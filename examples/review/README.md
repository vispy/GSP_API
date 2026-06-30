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

Open a live example with S035 View2D drag-to-pan and wheel-to-zoom:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --interactive-navigation
uv run python examples/review/01_scatter_basic.py --backend datoviz --interactive-navigation
```

Open all six review examples with 2D interactivity, one example after another:

```bash
tools/compare-review-examples --interactive-navigation
```

Open Matplotlib and Datoviz interactive windows side by side for one example:

```bash
tools/compare-review-examples --live-side-by-side --interactive-navigation examples/review/01_scatter_basic.py
```

If the local Datoviz v0.4 build does not expose the live pointer-input binding, the Datoviz window
still opens as a normal live review window and prints a message that GSP navigation is unavailable.
Matplotlib remains the strict interactive review path for the six examples.

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
