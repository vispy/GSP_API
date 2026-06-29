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

Capture and compare offscreen outputs:

```bash
uv run python examples/review/01_scatter_basic.py --backend both --offscreen
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Offscreen artifacts are written under `artifacts/example_review/<example>/`.

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
   | Live canvas size | Datoviz and Matplotlib have the same apparent logical canvas size for the same `--resolution`. |
   | Datoviz metrics | A requested `1280x720` live view keeps logical size `1280x720` and reports a physical framebuffer close to `1280 * device_scale` by `720 * device_scale`. |
   | No GSP workaround | GSP does not pass a Datoviz-only live-size multiplier or alter requested resolution for Datoviz. |
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
