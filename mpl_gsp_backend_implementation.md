# `mpl_gsp` backend implementation plan, aligned to current GSP_API

Status: **future implementation brief**. This should not be launched before the active S024
TextVisual protocol missions unless the user explicitly chooses to pause S024.

Goal: create an experimental Matplotlib external backend that lowers regular Matplotlib renderer
calls into GSP protocol visuals, while preserving clean fallback to Agg.

```python
import matplotlib
matplotlib.use("module://mpl_gsp.backend")

import matplotlib.pyplot as plt
plt.scatter(x, y, c=c, s=2)
plt.imshow(img)
plt.plot(x, y)
plt.show()
```

## 1. Architecture

```text
Matplotlib user script
  -> module://mpl_gsp.backend
  -> FigureCanvasGSP / RendererGSP
  -> mpl_gsp frontend-local display list and lowering helpers
  -> formal GSP protocol visuals: Point/Marker/Segment/Path/Image/Text
  -> selected GSP renderer path or Agg fallback
```

Important distinction:

- `mpl_gsp.RendererGSP` extends Matplotlib's `RendererBase` and receives Matplotlib draw calls.
- `gsp_matplotlib.protocol_renderer` is the existing **GSP -> Matplotlib** reference renderer.
- `gsp_datoviz.protocol_renderer` is the existing **GSP -> Datoviz v0.4** protocol adapter.

Do not mix those contracts.

## 2. Package layout

Add a separate experimental package only when ready to implement:

```text
src/mpl_gsp/
  __init__.py
  backend.py
  canvas_gsp.py
  figure_manager_gsp.py
  renderer_gsp.py
  config.py
  display_list.py
  fallback/
    __init__.py
    agg_fallback.py
  lowerings/
    __init__.py
    colors.py
    transforms.py
    paths.py
    markers.py
    path_collection.py
    image.py
    text.py
```

Then add `{include = "mpl_gsp", from = "src"}` to `pyproject.toml`.

Do not add Matplotlib imports to `gsp` core. Do not put this package under `gsp_matplotlib`.

## 3. Configuration

Suggested environment variables:

```text
MPL_GSP_RENDERER=matplotlib|datoviz|auto
MPL_GSP_FALLBACK=figure|error
MPL_GSP_DEBUG=0|1
MPL_GSP_DUMP_DISPLAY_LIST=/path/to/file.json
```

Initial defaults:

- `MPL_GSP_RENDERER=matplotlib` or `auto` with Matplotlib reference first;
- `MPL_GSP_FALLBACK=figure`;
- Datoviz use only where the current protocol adapter can render the emitted visuals.

## 4. Milestone 1: backend import and Agg fallback

First goal: regular Matplotlib scripts do not crash.

Implement:

- `backend.py` with `FigureCanvas = FigureCanvasGSP`, `FigureManager = FigureManagerGSP`;
- `FigureCanvasGSP.draw()`, `buffer_rgba()`, `print_png()`;
- `RendererGSP` method stubs for common draw calls;
- debug counters and unsupported reason collection;
- whole-figure Agg fallback.

Use Agg fallback carefully without recursive backend selection:

```python
from matplotlib.backends.backend_agg import FigureCanvasAgg

old_canvas = fig.canvas
try:
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    rgba = np.asarray(canvas.buffer_rgba()).copy()
finally:
    fig.set_canvas(old_canvas)
```

Acceptance:

- `matplotlib.use("module://mpl_gsp.backend", force=True)` works;
- `fig.canvas.draw()` works;
- `np.asarray(fig.canvas.buffer_rgba())` returns `(H, W, 4)`;
- `fig.savefig("out.png")` writes a non-empty PNG;
- unsupported operations fallback instead of crashing;
- debug stats reveal whether native lowering was used.

## 5. Coordinate policy for native lowering

Do not require public GSP display-pixel coordinates initially.

Matplotlib draw calls should be transformed to display pixels, then converted centrally into
panel-local NDC before protocol visual creation:

```text
x_ndc = 2 * (x_px / width_px) - 1
y_ndc = 2 * (y_px / height_px) - 1
```

Keep origin handling explicit. Matplotlib rendering coordinates are bottom-left; image arrays are
row-major and often visually top-left. All conversions must live in `mpl_gsp.lowerings.transforms`,
not scattered through draw methods.

If this becomes too awkward, open a future ADR for a public display-pixel coordinate space.

## 6. Native lowering targets

### `draw_image()` -> `ImageVisual`

Support scale/translate image transforms first. Normalize input to RGBA8 or accepted scalar image
forms, compute NDC extent, and emit `ImageVisual`.

Fallback on complex image transforms.

### `draw_path()` -> `PathVisual` / `SegmentVisual`

Support simple open MOVETO/LINETO paths with no Beziers, hatches, path effects, or fill. Convert to
NDC and emit `PathVisual` or `SegmentVisual`.

Fallback for filled polygons unless/until MeshVisual exists.

### `draw_path_collection()` -> `PointVisual` / `MarkerVisual`

This is the main performance target for scatter.

- Detect one repeated marker path with many offsets.
- Convert offsets to NDC positions.
- Convert Matplotlib scatter size `s` from points² area to approximate screen-pixel diameter:
  `diameter_px = sqrt(s) * dpi / 72`.
- Convert face/edge colors to RGBA.
- Circle/dot with no meaningful stroke -> `PointVisual`.
- Conservative known markers -> `MarkerVisual`.
- Unknown custom marker paths -> fallback.

### `draw_markers()` -> `PointVisual` / `MarkerVisual`

Conservative marker classification only. False negatives should fallback; false positives risk wrong
rendering and should be avoided.

### `draw_quad_mesh()`

Regular or rectilinear image-like meshes may lower to `ImageVisual`. Irregular quads and Gouraud
triangles should fallback until MeshVisual is accepted.

### `draw_text()`

Native simple text should wait for S024 implementation:

- M075: protocol dataclass/enums/validation;
- M076: Matplotlib TextVisual reference renderer.

Then lower simple `ismath=False`, non-TeX text to `TextVisual`. Use Agg/Matplotlib metrics for
`get_text_width_height_descent()` regardless of native drawing, because Matplotlib layout depends on
accurate metrics. MathText/TeX/rich text fallback.

## 7. Frontend-local display list

Use a frontend-local display list first:

```python
@dataclass
class DisplayItem:
    kind: str
    visual: object
    z_order: int
    source: str

class MplGspDisplayList:
    def add_visual(...): ...
    def freeze(...): ...  # returns protocol visuals and side metadata
```

Responsibilities:

- preserve Matplotlib draw order;
- record unsupported reasons;
- batch compatible items where safe;
- emit formal GSP protocol visuals;
- keep source/debug ids out of public protocol unless a future ADR accepts metadata.

## 8. Rendering session

First version may choose one of two paths:

1. render through current Matplotlib reference functions for deterministic tests;
2. render through Datoviz only for visual families the current adapter supports.

Do not assume a generic mature renderer registry path for protocol scenes unless verified during the
implementation mission. Prefer a narrow session helper that is explicitly tested.

## 9. Clipping and fallback

Initial clipping support:

- axes/panel rectangle only;
- arbitrary clip paths fallback;
- hatches/path effects fallback;
- unsupported projections fallback.

Start with whole-figure fallback. Per-layer RGBA fallback is a later phase and should use
`ImageVisual` only after coordinate/clipping semantics are proven.

## 10. Tests

Initial tests:

- backend import;
- basic draw + `buffer_rgba`;
- PNG save;
- forced fallback path;
- native `draw_image` stats once implemented;
- native simple line stats once implemented;
- native scatter/path_collection stats once implemented.

Do not require pixel-perfect parity with Agg. Check shape, non-empty image, fallback/native counters,
and basic semantic invariants.

## 11. Suggested implementation sequence

Only start this sequence after the user approves a new mission/stage:

1. M075-M077 finish the S024 TextVisual protocol/Matplotlib/QA baseline.
2. Create an `mpl_gsp` architecture ADR/task pack from this document.
3. Implement backend import + whole-figure Agg fallback.
4. Add frontend-local transforms/display list.
5. Implement native `draw_image()`.
6. Implement simple `draw_path()`.
7. Implement native scatter via `draw_path_collection()`.
8. Add optional native simple text after TextVisual renderer exists.
9. Probe end-to-end Datoviz path for native scatter/image.

## 12. Stop conditions

Stop rather than improvise if:

- Matplotlib frontend work requires public display-pixel coordinates before an ADR;
- code would add Matplotlib dependencies to `gsp` core;
- implementation relies on legacy Datoviz v0.3/private APIs;
- text lowering needs public glyph/atlas/font-handle fields;
- mesh-like Matplotlib calls require MeshVisual before a Mesh stage;
- fallback is unavailable, hiding incompatibilities as crashes;
- debug stats cannot distinguish native lowering from Agg fallback.
