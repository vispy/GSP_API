# P018 - Physical Canvas Size Contract for GSP and Datoviz

## Prompt for ChatGPT Pro

You are reviewing a breaking architecture proposal for a Python visualization protocol library named GSP_API and a Datoviz v0.4 GPU backend. The goal is to design clean long-term canvas sizing semantics across Matplotlib and Datoviz, including high-DPI displays on macOS and Linux, even if this requires aggressive API breaks.

Project context:

- GSP_API is a backend-agnostic scene/protocol layer for scientific visualization.
- It has a Matplotlib reference renderer and a Datoviz v0.4 renderer.
- Protocol visuals such as `PointVisual`, `MarkerVisual`, `TextVisual`, `SegmentVisual`, and guides are authored in semantic units.
- Point/marker `sizes`, text `font_size_px`, and stroke widths are currently documented as logical screen-pixel sizes, not data-space quantities.
- The current review examples accept a resolution such as `1280x720`.
- Matplotlib review rendering currently computes:
  - `figsize=(width / 100, height / 100)`
  - `dpi=100`
  - therefore offscreen raster output is `width x height` pixels.
- Matplotlib converts protocol marker pixel diameters to scatter area units with:
  - `pixel_to_point = 72 / logical_figure_dpi`
  - `area = (diameter_px * pixel_to_point) ** 2`
- Datoviz receives the same protocol marker diameter and uploads it as `diameter_px`.
- Datoviz documentation says `_px` attributes are logical pixels and should be converted to framebuffer pixels using view/device scale when drawing.

Observed issue:

- On a high-DPI Linux display, a requested live window size like `1280x720` appears much smaller than on macOS.
- The user currently sets `DVZ_WINDOW_SIZE_SCALE=1.45` in a parent `.envrc` to make Datoviz live windows appear physically comparable to Matplotlib/macOS windows.
- This env var is a workaround. In Datoviz source it applies only to live GLFW view creation and multiplies the view descriptor logical width/height:
  - `desc->logical_width = round(desc->logical_width * scale)`
  - `desc->logical_height = round(desc->logical_height * scale)`
  - framebuffer width/height are then derived from the scaled logical size and device scale.
- This creates a mismatch: the Datoviz live canvas becomes physically larger, but GSP still authored markers/text/strokes in the original logical px values. Markers therefore look too small relative to the canvas by approximately `1 / 1.45`.
- The offscreen path does not apply `DVZ_WINDOW_SIZE_SCALE`, and Matplotlib/Datoviz offscreen marker sizes match closely at the same `1280x720` PNG size.

Important clarification:

The user is not primarily asking for matching framebuffer pixel dimensions. The user wants the apparent physical size of a live window to be comparable across operating systems and display scaling systems. For example, on macOS `1280x720` often means logical points and produces a comfortable physical size. On Linux high-DPI, a raw `1280x720` window may be much smaller because toolkit/window logical units may correspond closely to physical framebuffer pixels, depending on Wayland/X11/toolkit scaling.

The key architectural problem:

`1280x720` alone is ambiguous. It could mean:

1. exact framebuffer pixels for deterministic image export,
2. OS/window logical units,
3. CSS/reference pixels at 96 DPI,
4. physical units such as mm or inches.

Desired long-term result:

- GSP and Datoviz should make the sizing contract explicit.
- A user should be able to request "make this canvas appear about the same physical size across macOS and Linux" without relying on backend-specific scale hacks.
- Users should also be able to request exact-pixel output for screenshots/tests.
- Datoviz should expose resolved size diagnostics so GSP can report what actually happened:
  - requested sizing policy,
  - logical window size,
  - framebuffer size,
  - device/content scale,
  - monitor DPI if available,
  - apparent physical size estimate when possible.

Candidate direction to review:

Introduce explicit canvas size policies in GSP:

```python
CanvasSize.pixel_exact(width_px=1280, height_px=720)
CanvasSize.logical_px(width_px=1280, height_px=720)
CanvasSize.reference_px(width=1280, height=720, reference_dpi=96.0)
CanvasSize.physical_mm(width_mm=340.0, height_mm=191.0)
```

Rough semantics:

- `pixel_exact`: primarily offscreen/export/tests. Output framebuffer exactly matches requested pixels. Live may use a window of equivalent logical size but exact physical size is not promised.
- `logical_px`: request backend/window logical units directly. This is current behavior, but should be explicit and not confused with physical size.
- `reference_px`: CSS-like reference pixels. Convert `width / reference_dpi` to a physical size target, then ask the backend/toolkit for a window that approximates that physical size on the active monitor.
- `physical_mm`: direct physical size target. Convert to OS/window logical units based on monitor DPI and OS/toolkit scale.

For Datoviz:

- Replace or deprecate `DVZ_WINDOW_SIZE_SCALE` for semantic use.
- Add an explicit view size policy in `DvzViewDesc`, for example:

```c
typedef enum DvzViewSizeUnit {
    DVZ_VIEW_SIZE_LOGICAL_PX,
    DVZ_VIEW_SIZE_FRAMEBUFFER_PX,
    DVZ_VIEW_SIZE_REFERENCE_PX,
    DVZ_VIEW_SIZE_MM,
} DvzViewSizeUnit;

typedef struct DvzViewSizeDesc {
    DvzViewSizeUnit unit;
    double width;
    double height;
    double reference_dpi;
    double requested_device_scale;  // optional override, 0 = auto
} DvzViewSizeDesc;
```

- Datoviz should resolve this to:
  - host/window logical size,
  - framebuffer size,
  - device/content scale,
  - physical DPI or physical size estimate if available.
- `_px` visual attributes must remain authored in logical/reference units and lower consistently through device scale. Do not compensate per visual in GSP for a window size scale.

For Matplotlib:

- For offscreen `pixel_exact`, use `figsize_inches * dpi = requested pixels`.
- For physical/reference live sizing, compute `figsize_inches` from target physical size. DPI should then be considered separately for raster output and GUI backend scaling.
- Marker/text/stroke logical sizing should use a logical/reference DPI, not accidentally double-scale with a physical export DPI.

Questions to answer:

1. Is the proposed four-policy size model (`pixel_exact`, `logical_px`, `reference_px`, `physical_mm`) the right abstraction boundary for GSP? If not, propose a cleaner one.
2. Where should physical-size resolution live: GSP, Datoviz, both, or a shared `ResolvedCanvas` contract?
3. What is the clean Datoviz v0.4 API design for live GLFW and offscreen views?
4. How should Matplotlib implement these policies without conflating figure DPI, logical marker units, and physical window size?
5. What should be deprecated or removed from current APIs?
6. What exact tests and visual review cases should be added to prove the fix?
7. What migration sequence should be used if aggressive API breaking is acceptable?

Expected output format:

Please return:

1. **Architecture Decision** - concise recommendation and rationale.
2. **Size Semantics Table** - each public sizing policy, intended use, physical-size guarantee, framebuffer guarantee, live/offscreen behavior.
3. **Datoviz API Proposal** - concrete C/Python API shape, required resolved metrics, and deprecations.
4. **GSP API Proposal** - concrete Python dataclass/API shape, renderer contract, and resolved-canvas object.
5. **Matplotlib Implementation Notes** - exact formulas and pitfalls.
6. **Test Plan** - unit tests, offscreen tests, live diagnostic tests, and manual review cases.
7. **Migration Plan** - ordered breaking-change steps.
8. **Risks/Open Questions** - especially OS APIs for monitor physical dimensions, Wayland/X11/macOS behavior, and fallback behavior when physical DPI is unavailable.

Do not assume attached files are available. Use only the context above.
