## 1. **Architecture Decision**

Adopt the four-policy model, but tighten the terminology and add one missing concept: a **resolved canvas scale contract**.

The proposed policies are the right abstraction boundary for GSP:

```python
CanvasSize.pixel_exact(...)
CanvasSize.logical_px(...)
CanvasSize.reference_px(...)
CanvasSize.physical_mm(...)
```

However, the implementation must distinguish four different spaces that are currently being conflated:

| Space                       | Meaning                                                                                                     |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **GSP canvas/reference px** | Semantic screen units used by protocol visuals: marker diameters, text sizes, stroke widths, guide offsets. |
| **Host/window logical px**  | Units accepted by the OS/window toolkit, for example GLFW window logical size.                              |
| **Framebuffer px**          | Actual device pixels used for rendering, screenshots, GPU framebuffers.                                     |
| **Physical units**          | mm/inches on the display, only approximately knowable for live windows.                                     |

The current `DVZ_WINDOW_SIZE_SCALE` bug happens because it scales only the **host/window logical extent**, not the **GSP canvas-to-framebuffer scale**. The window gets larger, but markers/text/strokes remain authored and rendered as though the canvas were still unscaled.

The long-term fix is:

```text
CanvasSize request
    ↓
Backend resolves host/window size, framebuffer size, monitor scale/DPI
    ↓
Backend returns ResolvedCanvas
    ↓
Renderer maps GSP canvas px → framebuffer px consistently
```

The most important architectural rule should be:

> Visual `_px` attributes are authored in GSP canvas/reference pixels, not raw framebuffer pixels and not backend-specific window logical pixels.

Then every renderer uses the resolved scale:

```text
framebuffer_px_per_canvas_px
```

to lower marker sizes, text sizes, line widths, antialiasing radii, guide offsets, and other screen-space quantities.

GSP should own the portable semantic API. Datoviz and Matplotlib should own backend-specific realization. The bridge between them should be a shared `ResolvedCanvas` contract.

---

## 2. **Size Semantics Table**

| Policy                                               |                                                   Intended use |                                                                                  Physical-size guarantee |                                                            Framebuffer guarantee | Live behavior                                                                                                                                                                                          | Offscreen behavior                                                                                                                                                                           |
| ---------------------------------------------------- | -------------------------------------------------------------: | -------------------------------------------------------------------------------------------------------: | -------------------------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pixel_exact(width_px, height_px)`                   | Tests, screenshots, deterministic PNG export, CI visual review |                                                                                                     None |           Strong for offscreen; best-effort for live unless strict mode succeeds | Request a live surface whose framebuffer is as close as possible to the requested size. Exactness may fail because OS toolkits create windows in logical units. Should report actual framebuffer size. | Create framebuffer/output image exactly `width_px × height_px`. One GSP canvas px maps to one framebuffer px by default.                                                                     |
| `logical_px(width_px, height_px)`                    |    Explicit current behavior; low-level backend/window control |                                                                                                     None |                                     None, except indirectly through device scale | Request host/window logical content size directly. Framebuffer becomes `logical_size × device_scale`, subject to OS rounding.                                                                          | In headless/offscreen mode, there is no OS logical size, so treat as `device_scale = 1` unless an explicit offscreen scale is provided. Usually outputs `width_px × height_px`.              |
| `reference_px(width, height, reference_dpi=96)`      |        “Make this 1280×720 canvas have CSS-like physical size” | Approximate live physical size target: `width / reference_dpi` inches by `height / reference_dpi` inches | No fixed framebuffer guarantee; framebuffer depends on monitor DPI/content scale | Resolve target physical size, choose host logical size for active monitor/toolkit, then render all GSP `_px` visuals through the same canvas-to-framebuffer scale.                                     | Physical target is deterministic. Output pixels depend on chosen raster/export DPI. For example, `1280×720 @ 96 reference DPI` exported at `192 raster DPI` gives approximately `2560×1440`. |
| `physical_mm(width_mm, height_mm, reference_dpi=96)` |                       “Make the live canvas about 340 mm wide” |                                                                         Approximate live physical target |                                                   No fixed framebuffer guarantee | Convert physical target to monitor/toolkit logical size. Define GSP canvas/reference size as `width_mm / 25.4 × reference_dpi` unless an advanced override exists.                                     | Figure physical size is exact in mathematical terms. Raster pixels depend on export DPI.                                                                                                     |

One refinement I would make: internally, treat `reference_px` as shorthand for a physical target:

```text
target_width_mm  = width  / reference_dpi × 25.4
target_height_mm = height / reference_dpi × 25.4
```

and treat `physical_mm` as the inverse:

```text
canvas_width_ref_px  = width_mm  / 25.4 × reference_dpi
canvas_height_ref_px = height_mm / 25.4 × reference_dpi
```

That makes these two policies consistent and avoids a special-case implementation.

I would also consider renaming `logical_px` to something more explicit in public docs, for example:

```python
CanvasSize.window_logical_px(...)
```

or

```python
CanvasSize.host_logical_px(...)
```

because “logical pixels” can otherwise be confused with GSP reference pixels.

---

## 3. **Datoviz API Proposal**

### C API

Use an explicit request object and a resolved metrics object.

```c
typedef enum DvzViewSizePolicy
{
    DVZ_VIEW_SIZE_FRAMEBUFFER_PX,   // pixel_exact
    DVZ_VIEW_SIZE_HOST_LOGICAL_PX,  // logical_px / current behavior
    DVZ_VIEW_SIZE_REFERENCE_PX,     // CSS/reference px physical target
    DVZ_VIEW_SIZE_PHYSICAL_MM,      // direct physical target
} DvzViewSizePolicy;
```

```c
typedef enum DvzPhysicalMetricsSource
{
    DVZ_PHYSICAL_METRICS_NONE,
    DVZ_PHYSICAL_METRICS_MONITOR_EDID,
    DVZ_PHYSICAL_METRICS_GLFW_MONITOR_SIZE,
    DVZ_PHYSICAL_METRICS_PLATFORM_API,
    DVZ_PHYSICAL_METRICS_USER_OVERRIDE,
    DVZ_PHYSICAL_METRICS_ESTIMATED,
} DvzPhysicalMetricsSource;
```

```c
typedef enum DvzResolvedExactness
{
    DVZ_RESOLVED_EXACT,
    DVZ_RESOLVED_APPROXIMATE,
    DVZ_RESOLVED_UNKNOWN,
} DvzResolvedExactness;
```

```c
typedef struct DvzViewSizeDesc
{
    DvzViewSizePolicy policy;

    // Meaning depends on policy:
    // FRAMEBUFFER_PX: framebuffer pixels
    // HOST_LOGICAL_PX: OS/window logical content units
    // REFERENCE_PX: reference/CSS-like pixels
    // PHYSICAL_MM: millimeters
    double width;
    double height;

    // Used by REFERENCE_PX and PHYSICAL_MM.
    // Default should be 96.0 if <= 0.
    double reference_dpi;

    // Optional advanced override for tests/headless/debugging.
    // 0 = auto. This should not replace semantic policies.
    double requested_device_scale;

    // Optional user override when OS physical DPI is unavailable/untrusted.
    // 0 = auto.
    double monitor_dpi_x_override;
    double monitor_dpi_y_override;

    // Optional strictness.
    // Useful for FRAMEBUFFER_PX live windows.
    bool strict_framebuffer_size;
} DvzViewSizeDesc;
```

Then `DvzViewDesc` should contain this instead of raw width/height alone:

```c
typedef struct DvzViewDesc
{
    DvzViewSizeDesc size;

    // Existing fields...
    // title, flags, parent, offscreen/live mode, etc.
} DvzViewDesc;
```

### Resolved metrics

Datoviz should expose a first-class resolved object:

```c
typedef struct DvzResolvedViewSize
{
    DvzViewSizePolicy requested_policy;

    double requested_width;
    double requested_height;
    double reference_dpi;

    // Semantic GSP/Datoviz canvas px.
    // Visual _px attributes are expressed in this space.
    double canvas_width_px;
    double canvas_height_px;

    // GLFW/window content size in host logical units.
    // Null/0 for pure offscreen if not meaningful.
    uint32_t host_logical_width;
    uint32_t host_logical_height;

    // Actual framebuffer/device-pixel size.
    uint32_t framebuffer_width;
    uint32_t framebuffer_height;

    // OS/toolkit/device scale.
    // Usually framebuffer / host logical size for live windows.
    double device_scale_x;
    double device_scale_y;

    // Additional semantic scaling.
    // This is the missing piece relative to DVZ_WINDOW_SIZE_SCALE.
    double canvas_to_host_scale_x;
    double canvas_to_host_scale_y;

    // Total scale used by shaders/rendering.
    double framebuffer_per_canvas_px_x;
    double framebuffer_per_canvas_px_y;

    // Target physical size if requested or derivable.
    double target_width_mm;
    double target_height_mm;

    // Estimated actual physical size.
    double estimated_width_mm;
    double estimated_height_mm;

    // Monitor diagnostics.
    double monitor_dpi_x;
    double monitor_dpi_y;
    double monitor_physical_width_mm;
    double monitor_physical_height_mm;

    DvzPhysicalMetricsSource physical_metrics_source;
    DvzResolvedExactness physical_exactness;
    DvzResolvedExactness framebuffer_exactness;

    // Optional short diagnostic string or warning flags.
    uint32_t warning_flags;
} DvzResolvedViewSize;
```

Suggested API functions:

```c
DvzViewSizeDesc dvz_view_size_framebuffer_px(uint32_t width_px, uint32_t height_px);
DvzViewSizeDesc dvz_view_size_host_logical_px(uint32_t width_px, uint32_t height_px);
DvzViewSizeDesc dvz_view_size_reference_px(double width, double height, double reference_dpi);
DvzViewSizeDesc dvz_view_size_physical_mm(double width_mm, double height_mm, double reference_dpi);

DvzResolvedViewSize dvz_view_resolved_size(DvzView* view);
```

For Python bindings:

```python
canvas = dvz.Canvas(
    size=dvz.ViewSize.reference_px(1280, 720, reference_dpi=96),
)

resolved = canvas.resolved_size
print(resolved.framebuffer_width, resolved.framebuffer_height)
print(resolved.device_scale_x)
print(resolved.framebuffer_per_canvas_px_x)
print(resolved.estimated_width_mm)
```

### Datoviz live GLFW behavior

For `DVZ_VIEW_SIZE_HOST_LOGICAL_PX`:

```text
canvas_width_px              = requested_width
host_logical_width           = requested_width
canvas_to_host_scale         = 1
device_scale                 = framebuffer / host_logical
framebuffer_per_canvas_px    = device_scale
```

For `DVZ_VIEW_SIZE_FRAMEBUFFER_PX`:

```text
canvas_width_px              = requested_framebuffer_width
target_framebuffer_width     = requested_framebuffer_width
host_logical_width           ≈ requested_framebuffer_width / device_scale
framebuffer_per_canvas_px    ≈ actual_framebuffer_width / canvas_width_px
```

In strict mode, if Datoviz cannot create the requested framebuffer size, it should either retry with adjusted logical size or fail loudly.

For `DVZ_VIEW_SIZE_REFERENCE_PX`:

```text
canvas_width_px              = requested_reference_width
target_physical_width_in     = requested_reference_width / reference_dpi
target_framebuffer_width     ≈ target_physical_width_in × monitor_dpi_x
host_logical_width           ≈ target_framebuffer_width / device_scale_x
canvas_to_host_scale         = host_logical_width / canvas_width_px
framebuffer_per_canvas_px    = framebuffer_width / canvas_width_px
```

For `DVZ_VIEW_SIZE_PHYSICAL_MM`:

```text
target_physical_width_in     = requested_width_mm / 25.4
canvas_width_px              = target_physical_width_in × reference_dpi
target_framebuffer_width     ≈ target_physical_width_in × monitor_dpi_x
host_logical_width           ≈ target_framebuffer_width / device_scale_x
framebuffer_per_canvas_px    = framebuffer_width / canvas_width_px
```

### Critical Datoviz rendering rule

Datoviz should not upload marker diameter directly as raw framebuffer pixels. It should interpret `_px` attributes as **canvas/reference px** and lower them through resolved scale.

For example:

```text
diameter_framebuffer_px =
    diameter_canvas_px × framebuffer_per_canvas_px
```

Likewise:

```text
stroke_framebuffer_px =
    stroke_canvas_px × framebuffer_per_canvas_px

font_framebuffer_px =
    font_canvas_px × framebuffer_per_canvas_px
```

For isotropic quantities such as marker diameters, use a single scalar scale. Usually:

```text
framebuffer_per_canvas_px =
    0.5 × (framebuffer_per_canvas_px_x + framebuffer_per_canvas_px_y)
```

or require the two scales to be effectively equal and warn if they differ beyond a small tolerance.

### Datoviz offscreen behavior

Offscreen should not depend on `DVZ_WINDOW_SIZE_SCALE`.

For offscreen:

```text
device_scale = 1 unless explicitly requested
host_logical size = none / same as canvas for diagnostics
physical size = unknown unless policy includes physical/reference target
```

For `FRAMEBUFFER_PX`, output must be exact.

For `REFERENCE_PX` and `PHYSICAL_MM`, Datoviz should accept a raster/export DPI or framebuffer scale. Without one, use:

```text
raster_dpi = reference_dpi
```

so that:

```text
reference_px(1280, 720, 96)
```

naturally exports as:

```text
1280 × 720
```

unless the user explicitly asks for a higher export DPI.

### Deprecations in Datoviz

Deprecate semantic use of:

```text
DVZ_WINDOW_SIZE_SCALE
```

It may remain temporarily as a debug-only compatibility escape hatch, but it should emit a warning such as:

```text
DVZ_WINDOW_SIZE_SCALE is deprecated for semantic canvas sizing.
Use DvzViewSizeDesc with DVZ_VIEW_SIZE_REFERENCE_PX or DVZ_VIEW_SIZE_PHYSICAL_MM.
```

Eventually remove it from documented workflows.

---

## 4. **GSP API Proposal**

### Public Python API

Use a single public `CanvasSize` family.

```python
from dataclasses import dataclass
from typing import Literal, Optional, Tuple


@dataclass(frozen=True)
class CanvasSize:
    policy: Literal[
        "pixel_exact",
        "logical_px",
        "reference_px",
        "physical_mm",
    ]

    width: float
    height: float

    reference_dpi: float = 96.0

    strict: bool = False

    @staticmethod
    def pixel_exact(width_px: int, height_px: int, *, strict: bool = True) -> "CanvasSize":
        return CanvasSize(
            policy="pixel_exact",
            width=float(width_px),
            height=float(height_px),
            reference_dpi=96.0,
            strict=strict,
        )

    @staticmethod
    def logical_px(width_px: int, height_px: int) -> "CanvasSize":
        return CanvasSize(
            policy="logical_px",
            width=float(width_px),
            height=float(height_px),
            reference_dpi=96.0,
            strict=False,
        )

    @staticmethod
    def reference_px(
        width: float,
        height: float,
        *,
        reference_dpi: float = 96.0,
    ) -> "CanvasSize":
        return CanvasSize(
            policy="reference_px",
            width=float(width),
            height=float(height),
            reference_dpi=float(reference_dpi),
            strict=False,
        )

    @staticmethod
    def physical_mm(
        width_mm: float,
        height_mm: float,
        *,
        reference_dpi: float = 96.0,
    ) -> "CanvasSize":
        return CanvasSize(
            policy="physical_mm",
            width=float(width_mm),
            height=float(height_mm),
            reference_dpi=float(reference_dpi),
            strict=False,
        )
```

I would document these as follows:

```python
CanvasSize.pixel_exact(1280, 720)
```

means:

> Give me an output framebuffer of exactly 1280×720 pixels. This is the right policy for PNG review images, tests, and screenshots.

```python
CanvasSize.logical_px(1280, 720)
```

means:

> Pass 1280×720 to the OS/toolkit as logical window units. This is explicit current behavior and does not promise comparable physical size.

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

means:

> Treat the canvas as 1280×720 reference pixels, where 96 reference pixels equal one physical inch. Make the live window approximately that physical size when possible.

```python
CanvasSize.physical_mm(340, 191)
```

means:

> Make the live canvas approximately 340 mm × 191 mm. Use `reference_dpi` to define the GSP canvas/reference-pixel coordinate system for screen-space visual sizes.

### Resolved canvas object

GSP should define the portable resolved contract, even though each backend fills it.

```python
@dataclass(frozen=True)
class ResolvedCanvas:
    backend: str
    mode: Literal["live", "offscreen"]

    request: CanvasSize

    # Semantic canvas/reference space.
    canvas_width_px: float
    canvas_height_px: float

    # OS/window logical content size.
    window_logical_width_px: Optional[int]
    window_logical_height_px: Optional[int]

    # Actual framebuffer/output size.
    framebuffer_width_px: int
    framebuffer_height_px: int

    # OS/device scale.
    device_scale_x: float
    device_scale_y: float

    # Semantic scaling.
    canvas_to_window_scale_x: float
    canvas_to_window_scale_y: float

    # Total renderer lowering scale.
    framebuffer_per_canvas_px_x: float
    framebuffer_per_canvas_px_y: float

    # Reference DPI used for semantic px.
    reference_dpi: float

    # Physical target, if any.
    target_width_mm: Optional[float]
    target_height_mm: Optional[float]

    # Estimated actual physical size, if knowable.
    estimated_width_mm: Optional[float]
    estimated_height_mm: Optional[float]

    # Monitor diagnostics.
    monitor_dpi_x: Optional[float]
    monitor_dpi_y: Optional[float]
    monitor_name: Optional[str]
    monitor_metrics_source: Literal[
        "none",
        "os",
        "glfw",
        "edid",
        "user_override",
        "estimated",
    ]

    physical_size_confidence: Literal[
        "exact",
        "estimated",
        "unknown",
    ]

    framebuffer_exact: bool

    warnings: Tuple[str, ...] = ()
```

### Renderer contract

Every GSP renderer should accept:

```python
renderer.render(scene, canvas_size=CanvasSize.pixel_exact(1280, 720))
```

and expose:

```python
result.resolved_canvas
```

or:

```python
renderer.resolved_canvas
```

The renderer contract should state:

1. Bare `(width, height)` resolution is no longer a semantic API.
2. All visual `_px` fields are in **GSP canvas/reference px**.
3. Renderers must convert visual `_px` fields using `ResolvedCanvas.framebuffer_per_canvas_px_*`.
4. Renderers must not apply ad-hoc per-visual compensation for backend window hacks.
5. The same scene rendered with `reference_px(1280, 720)` should preserve marker/text/stroke proportions relative to the semantic canvas even when the live host window is larger than 1280×720 OS logical units.

### Example user-facing diagnostics

For live Datoviz on high-DPI Linux, GSP should be able to report something like:

```text
Requested: CanvasSize.reference_px(1280, 720, reference_dpi=96)
Canvas/reference size: 1280.0 × 720.0 px
Window logical content size: 1856 × 1044
Framebuffer size: 1856 × 1044
Device scale: 1.00 × 1.00
Canvas-to-window scale: 1.45 × 1.45
Framebuffer per canvas px: 1.45 × 1.45
Target physical size: 338.7 × 190.5 mm
Estimated actual physical size: 337.0 × 189.6 mm
Monitor DPI source: estimated / OS / EDID
Warnings: physical size is approximate
```

On macOS Retina, the same request might resolve more like:

```text
Requested: CanvasSize.reference_px(1280, 720, reference_dpi=96)
Canvas/reference size: 1280.0 × 720.0 px
Window logical content size: 1280 × 720
Framebuffer size: 2560 × 1440
Device scale: 2.00 × 2.00
Canvas-to-window scale: 1.00 × 1.00
Framebuffer per canvas px: 2.00 × 2.00
Target physical size: 338.7 × 190.5 mm
Estimated actual physical size: approximate / unknown
```

The exact numbers depend on monitor DPI and OS reporting, but the diagnostic shape is what matters.

---

## 5. **Matplotlib Implementation Notes**

Matplotlib is tricky because figure size, figure DPI, GUI scaling, font sizes, marker sizes, and raster output are all entangled. GSP should avoid treating `fig.dpi` as “the logical pixel DPI” globally.

Use a resolved scale model instead.

### Generic Matplotlib lowering formula

Let:

```text
canvas_width_px  = resolved.canvas_width_px
canvas_height_px = resolved.canvas_height_px

fb_width_px      = resolved.framebuffer_width_px
fb_height_px     = resolved.framebuffer_height_px

output_dpi       = Matplotlib figure dpi used for rasterization
```

Then:

```text
framebuffer_per_canvas_px_x = fb_width_px  / canvas_width_px
framebuffer_per_canvas_px_y = fb_height_px / canvas_height_px
```

For isotropic marker/text/stroke sizes:

```text
framebuffer_per_canvas_px =
    0.5 × (framebuffer_per_canvas_px_x + framebuffer_per_canvas_px_y)
```

Matplotlib wants most screen-space quantities in points, where:

```text
1 point = 1 / 72 inch
```

and:

```text
rendered_pixels = points / 72 × output_dpi
```

Therefore, to render a GSP size of `size_canvas_px`:

```text
size_points =
    size_canvas_px × framebuffer_per_canvas_px × 72 / output_dpi
```

So:

```python
px_to_point = 72.0 * framebuffer_per_canvas_px / output_dpi
```

Marker scatter areas:

```python
diameter_points = diameter_canvas_px * px_to_point
area_points_squared = diameter_points ** 2
```

Line widths:

```python
linewidth_points = linewidth_canvas_px * px_to_point
```

Text:

```python
font_size_points = font_size_canvas_px * px_to_point
```

This formula handles both cases correctly:

For `pixel_exact(1280, 720)` offscreen:

```text
canvas_width_px = 1280
fb_width_px     = 1280
framebuffer_per_canvas_px = 1
```

Therefore:

```text
size_points = size_px × 72 / output_dpi
```

A 10 px marker renders as 10 framebuffer pixels regardless of whether `output_dpi` is 96, 100, 144, or 200, because the point conversion compensates for the raster DPI.

For `reference_px(1280, 720, reference_dpi=96)` exported at 192 DPI:

```text
canvas_width_px = 1280
physical_width_inches = 1280 / 96
fb_width_px = physical_width_inches × 192 = 2560
framebuffer_per_canvas_px = 2
```

Therefore:

```text
size_points = size_px × 2 × 72 / 192
            = size_px × 72 / 96
```

A 10 reference-px marker becomes 20 framebuffer pixels, which is correct for a 192 DPI raster intended to preserve physical size.

### `pixel_exact` offscreen

Use:

```python
output_dpi = requested_output_dpi  # arbitrary; 96 or 100 are both fine
figsize_inches = (
    width_px / output_dpi,
    height_px / output_dpi,
)
fig = Figure(figsize=figsize_inches, dpi=output_dpi)
```

Resolved values:

```text
canvas_width_px = width_px
canvas_height_px = height_px
framebuffer_width_px = width_px
framebuffer_height_px = height_px
framebuffer_per_canvas_px = 1
```

Do **not** use:

```python
px_to_point = 72 / logical_figure_dpi
```

unless `logical_figure_dpi` has been explicitly defined as:

```text
output_dpi / framebuffer_per_canvas_px
```

The safer formula is:

```python
px_to_point = 72 * framebuffer_per_canvas_px / output_dpi
```

### `logical_px` Matplotlib behavior

For offscreen, `logical_px` can reasonably resolve the same as `pixel_exact` with device scale 1:

```text
canvas size = requested logical size
framebuffer size = requested logical size
```

For live GUI, pass the requested dimensions as the intended logical content size, but inspect the actual canvas after creation. Matplotlib backends may allocate a framebuffer that differs from the nominal logical size.

### `reference_px` Matplotlib behavior

For offscreen:

```python
physical_width_inches = width_ref_px / reference_dpi
physical_height_inches = height_ref_px / reference_dpi

figsize_inches = (
    physical_width_inches,
    physical_height_inches,
)

output_dpi = raster_dpi
framebuffer_width_px = round(physical_width_inches * output_dpi)
framebuffer_height_px = round(physical_height_inches * output_dpi)
```

Then use the generic point conversion.

For live:

```python
figsize_inches = (
    width_ref_px / reference_dpi,
    height_ref_px / reference_dpi,
)
```

Then choose or let the backend choose a GUI/raster DPI. After the window exists, inspect the actual canvas framebuffer/logical size and update `ResolvedCanvas`.

### `physical_mm` Matplotlib behavior

For offscreen:

```python
physical_width_inches = width_mm / 25.4
physical_height_inches = height_mm / 25.4

canvas_width_px = physical_width_inches * reference_dpi
canvas_height_px = physical_height_inches * reference_dpi

figsize_inches = (
    physical_width_inches,
    physical_height_inches,
)

framebuffer_width_px = round(physical_width_inches * output_dpi)
framebuffer_height_px = round(physical_height_inches * output_dpi)
```

Then:

```python
framebuffer_per_canvas_px = output_dpi / reference_dpi
```

subject to rounding.

For live, set `figsize_inches` from the physical target, but treat the actual physical result as approximate. GUI backends and OS scaling can override or reinterpret the requested figure size.

### Matplotlib pitfalls

Avoid these mistakes:

1. **Do not assume `fig.dpi == logical DPI`.**
   `fig.dpi` is part of rasterization and GUI backend behavior.

2. **Do not use physical/export DPI directly for marker sizes unless mediated through `framebuffer_per_canvas_px`.**
   Otherwise high-DPI exports will double-scale or under-scale visual sizes.

3. **Do not assume offscreen and live have the same DPI semantics.**
   Offscreen is deterministic. Live is OS/backend mediated.

4. **Do not assume `figsize=(width / 100, height / 100), dpi=100` is semantically neutral.**
   That is fine for legacy `pixel_exact`, but it silently bakes in `100 DPI` as both raster DPI and logical unit conversion.

5. **Do not convert text with one DPI rule and markers with another.**
   Text, markers, strokes, guide widths, tick lengths, and padding should share the same resolved screen-unit conversion.

---

## 6. **Test Plan**

### A. Pure unit tests for size resolution

Use a fake monitor/platform resolver so tests are deterministic.

#### 1. `pixel_exact` offscreen

Input:

```python
CanvasSize.pixel_exact(1280, 720)
```

Expected:

```text
canvas_width_px = 1280
canvas_height_px = 720
framebuffer_width_px = 1280
framebuffer_height_px = 720
framebuffer_per_canvas_px = 1
framebuffer_exact = True
physical target = None
```

#### 2. `logical_px` live on 1× display

Fake monitor:

```text
device_scale = 1
monitor_dpi = 96
```

Input:

```python
CanvasSize.logical_px(1280, 720)
```

Expected:

```text
window_logical = 1280 × 720
framebuffer = 1280 × 720
canvas_to_window_scale = 1
framebuffer_per_canvas_px = 1
physical guarantee = none
```

#### 3. `logical_px` live on 2× display

Fake monitor:

```text
device_scale = 2
```

Input:

```python
CanvasSize.logical_px(1280, 720)
```

Expected:

```text
window_logical = 1280 × 720
framebuffer = 2560 × 1440
canvas_to_window_scale = 1
framebuffer_per_canvas_px = 2
physical guarantee = none
```

#### 4. `reference_px` on 96 DPI monitor

Fake monitor:

```text
monitor_dpi = 96
device_scale = 1
```

Input:

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Expected:

```text
target physical size = 338.666... mm × 190.5 mm
window_logical ≈ 1280 × 720
framebuffer ≈ 1280 × 720
framebuffer_per_canvas_px ≈ 1
```

#### 5. `reference_px` on 144 DPI Linux 1× monitor

Fake monitor:

```text
monitor_dpi = 144
device_scale = 1
```

Input:

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Expected:

```text
target physical size = 338.666... mm × 190.5 mm
window_logical ≈ 1920 × 1080
framebuffer ≈ 1920 × 1080
canvas_width_px = 1280
canvas_height_px = 720
canvas_to_window_scale ≈ 1.5
framebuffer_per_canvas_px ≈ 1.5
```

A 10 px marker should resolve to approximately 15 framebuffer pixels.

#### 6. `reference_px` on macOS-like 2× display

Fake monitor:

```text
host logical size already behaves like reference-like points
device_scale = 2
canvas_to_window_scale = 1
```

Input:

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Expected:

```text
window_logical ≈ 1280 × 720
framebuffer ≈ 2560 × 1440
framebuffer_per_canvas_px ≈ 2
```

A 10 px marker should resolve to approximately 20 framebuffer pixels.

#### 7. `physical_mm` equivalence

Inputs:

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

and:

```python
CanvasSize.physical_mm(
    width_mm=1280 / 96 * 25.4,
    height_mm=720 / 96 * 25.4,
    reference_dpi=96,
)
```

Expected:

```text
same target physical size
same derived canvas size
same framebuffer_per_canvas scale on same fake monitor
```

#### 8. Rounding behavior

Test fractional scales:

```text
monitor_dpi = 110
reference_dpi = 96
device_scale = 1.25
```

Verify:

```text
actual framebuffer_per_canvas_px =
    actual_framebuffer_width / canvas_width_px
```

not merely the theoretical scale.

The renderer should use actual resolved scale after rounding.

---

### B. Datoviz offscreen visual tests

Use image-based tests with tolerances.

#### 1. Pixel exact PNG dimensions

Render:

```python
CanvasSize.pixel_exact(1280, 720)
```

Assert:

```text
PNG size == 1280 × 720
```

#### 2. Marker size parity with Matplotlib

Scene:

```text
single point at center
marker diameter = 20 GSP px
```

Render with:

```python
CanvasSize.pixel_exact(512, 512)
```

Assert both Datoviz and Matplotlib produce approximately the same measured marker diameter in framebuffer pixels.

Use a tolerance that accounts for antialiasing.

#### 3. Stroke width parity

Scene:

```text
horizontal and vertical segments
stroke_width_px = 1, 2, 4, 8
```

Render with:

```python
CanvasSize.pixel_exact(512, 512)
```

Assert measured stroke widths match across backends.

#### 4. Text size parity

Scene:

```text
TextVisual(font_size_px=12, 24, 48)
```

Render with:

```python
CanvasSize.pixel_exact(1024, 512)
```

Compare approximate bounding boxes, not exact glyph rasters.

#### 5. Reference export DPI scaling

Render:

```python
CanvasSize.reference_px(512, 512, reference_dpi=96)
```

with export DPI:

```text
96
192
```

Expected:

```text
96 DPI output: 512 × 512
192 DPI output: 1024 × 1024
```

A 20 reference-px marker should measure approximately:

```text
20 framebuffer px at 96 DPI
40 framebuffer px at 192 DPI
```

The marker should occupy the same physical fraction of the intended output.

#### 6. Physical-mm export

Render:

```python
CanvasSize.physical_mm(100, 100, reference_dpi=100)
```

with export DPI:

```text
100
200
```

Expected approximate framebuffer sizes:

```text
100 mm / 25.4 × 100 ≈ 394 px
100 mm / 25.4 × 200 ≈ 787 px
```

A 10 reference-px marker should become:

```text
10 px at 100 DPI
20 px at 200 DPI
```

---

### C. Matplotlib-specific tests

#### 1. DPI independence for `pixel_exact`

Render the same scene with:

```text
output_dpi = 80
output_dpi = 100
output_dpi = 200
```

using:

```python
CanvasSize.pixel_exact(800, 600)
```

Expected:

```text
PNG size always 800 × 600
marker measured diameter remains 20 framebuffer px
line width remains 4 framebuffer px
```

This catches accidental use of:

```python
px_to_point = 72 / reference_dpi
```

in the `pixel_exact` path.

#### 2. Reference DPI behavior

Render:

```python
CanvasSize.reference_px(960, 540, reference_dpi=96)
```

with:

```text
output_dpi = 96
output_dpi = 192
```

Expected:

```text
framebuffer doubles
visual framebuffer sizes double
visual physical sizes remain stable
```

#### 3. Text/marker/stroke common conversion

Create a scene with:

```text
marker diameter = 24 px
stroke width = 24 px
font size = 24 px
```

The three should scale consistently when output DPI changes.

---

### D. Live diagnostic tests

These should not require exact visual assertions on CI.

#### 1. Datoviz live resolved metrics smoke test

Create a live window with:

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Assert that Datoviz reports:

```text
requested_policy
canvas_width_px
canvas_height_px
window_logical_width_px
window_logical_height_px
framebuffer_width_px
framebuffer_height_px
device_scale
framebuffer_per_canvas_px
monitor metrics source
warnings
```

#### 2. Live `logical_px` preserves current behavior

Create:

```python
CanvasSize.logical_px(1280, 720)
```

Assert:

```text
canvas_to_window_scale ≈ 1
```

This proves the new API can explicitly request the old behavior.

#### 3. Live physical/reference scaling on high-DPI Linux

On a high-DPI Linux machine where old `1280×720` appeared too small:

Compare:

```python
CanvasSize.logical_px(1280, 720)
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Expected:

```text
reference_px window has larger host logical/framebuffer size
markers/text/strokes are also scaled by the same framebuffer_per_canvas_px
relative visual proportions remain correct
```

#### 4. Window moved between monitors

If Datoviz supports live callbacks:

1. Create a `reference_px` window.
2. Move it between monitors with different scale/DPI.
3. Verify resolved metrics update.
4. Verify rendering scale updates.

At minimum, Datoviz should report stale/changed metrics clearly.

---

### E. Manual review cases

Add side-by-side review examples:

#### 1. Legacy explicit logical behavior

```python
CanvasSize.logical_px(1280, 720)
```

Purpose:

```text
Shows raw OS/window logical behavior.
Expected to differ physically across OSes.
```

#### 2. Physical comparable live canvas

```python
CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

Purpose:

```text
Should appear approximately the same physical size on macOS and Linux.
```

#### 3. Direct physical size

```python
CanvasSize.physical_mm(340, 191)
```

Purpose:

```text
Should measure about 340 mm × 191 mm with a ruler when monitor DPI is known.
```

#### 4. Exact screenshot/test output

```python
CanvasSize.pixel_exact(1280, 720)
```

Purpose:

```text
PNG/screenshot should be exactly 1280 × 720.
```

#### 5. Visual scale grid

Render a diagnostic scene containing:

```text
10 px, 20 px, 40 px markers
1 px, 2 px, 4 px, 8 px lines
12 px, 24 px, 48 px text
100 px reference ruler
```

Use the same scene across:

```text
Matplotlib offscreen
Datoviz offscreen
Datoviz live logical_px
Datoviz live reference_px
Datoviz live physical_mm
```

The review image should print the `ResolvedCanvas` diagnostics directly into the scene or beside it.

---

## 7. **Migration Plan**

Because aggressive API breaking is acceptable, I would do this in ordered stages.

### Step 1 — Introduce explicit canvas-size objects

Add:

```python
CanvasSize.pixel_exact
CanvasSize.logical_px
CanvasSize.reference_px
CanvasSize.physical_mm
```

to GSP.

Keep old `resolution=(w, h)` temporarily, but emit a deprecation warning.

For compatibility, map old behavior contextually:

```text
offscreen resolution=(w, h) → CanvasSize.pixel_exact(w, h)
live resolution=(w, h)      → CanvasSize.logical_px(w, h)
```

This preserves the current observed behavior while forcing users to confront the ambiguity.

### Step 2 — Define GSP `_px` semantics

Update protocol docs:

```text
PointVisual.sizes
MarkerVisual.sizes
TextVisual.font_size_px
SegmentVisual.stroke_width_px
guide widths/offsets
```

are in:

```text
GSP canvas/reference px
```

not raw framebuffer pixels.

If the name `_px` is considered too ambiguous, introduce clearer names such as:

```python
font_size_screen_px
stroke_width_screen_px
```

or:

```python
font_size_canvas_px
stroke_width_canvas_px
```

For a breaking release, I would prefer the clearer `*_screen_px` or `*_canvas_px` names, while keeping aliases for one cycle if desired.

### Step 3 — Add `ResolvedCanvas`

Every renderer should return or expose:

```python
ResolvedCanvas
```

Tests and review tools should print it.

This is essential. Without resolved diagnostics, users cannot know whether the backend honored the requested policy.

### Step 4 — Refactor Matplotlib renderer

Replace hard-coded logic like:

```python
figsize = (width / 100, height / 100)
dpi = 100
pixel_to_point = 72 / logical_figure_dpi
```

with the resolved-canvas formula:

```python
px_to_point = 72 * framebuffer_per_canvas_px / output_dpi
```

Then implement each policy explicitly.

### Step 5 — Add Datoviz size request/resolution API

Add:

```c
DvzViewSizeDesc
DvzResolvedViewSize
```

and Python bindings.

Datoviz live GLFW creation should resolve:

```text
requested policy
host logical size
framebuffer size
device/content scale
monitor DPI/physical estimate
canvas-to-host scale
framebuffer-per-canvas scale
```

### Step 6 — Change Datoviz visual lowering

Modify Datoviz shaders/render paths so `_px` attributes are interpreted as canvas/reference px and multiplied by:

```text
framebuffer_per_canvas_px
```

Do not let GSP compensate marker sizes one visual at a time.

### Step 7 — Deprecate `DVZ_WINDOW_SIZE_SCALE`

Emit warnings when it is present.

The warning should explain the replacement:

```text
Use CanvasSize.reference_px(...) or CanvasSize.physical_mm(...).
```

After one transition period, remove it from documented behavior or restrict it to internal debugging.

### Step 8 — Update examples and review cases

Replace examples like:

```python
resolution=(1280, 720)
```

with explicit intent:

```python
canvas_size=CanvasSize.pixel_exact(1280, 720)
```

for PNG review/tests, and:

```python
canvas_size=CanvasSize.reference_px(1280, 720, reference_dpi=96)
```

for physically comparable live windows.

### Step 9 — Make ambiguity an error

In the breaking release, reject bare resolution arguments:

```python
render(scene, resolution=(1280, 720))
```

with an error message such as:

```text
Canvas size is ambiguous. Use one of:
  CanvasSize.pixel_exact(...)
  CanvasSize.logical_px(...)
  CanvasSize.reference_px(...)
  CanvasSize.physical_mm(...)
```

---

## 8. **Risks / Open Questions**

### 1. Physical DPI is often unreliable

The largest risk is that monitor physical dimensions and DPI are not always trustworthy.

Potential problems:

```text
EDID reports wrong physical size.
External monitors report generic dimensions.
X11 may expose inaccurate millimeter dimensions.
Wayland may hide or abstract monitor details.
macOS exposes logical points/backing scale more reliably than physical DPI.
Users may use display scaling, accessibility scaling, or non-native modes.
```

Therefore `reference_px` and `physical_mm` should promise:

```text
best-effort approximate physical size
```

not exact physical size.

The resolved canvas must include:

```text
monitor_metrics_source
physical_size_confidence
warnings
```

### 2. “Same physical size” is not always the same as “same perceived size”

Even if two windows are both 340 mm wide, they may not feel identical because of:

```text
viewing distance
OS font smoothing
window decorations
desktop scaling preferences
monitor pixel density
user accessibility settings
```

The API should be honest: it targets approximate physical content size, not identical perception.

### 3. Content area versus outer window size

The contract should always refer to the drawable **content area**, not the outer decorated window.

Docs should say:

```text
Canvas size means drawable content size, excluding title bars and window borders.
```

Datoviz diagnostics should use framebuffer/content size, not outer window size.

### 4. Live exact framebuffer sizing may be impossible

Some platforms do not allow reliable creation of a live window with an exact framebuffer size because apps request logical content size and the OS chooses backing pixels.

Therefore:

```python
CanvasSize.pixel_exact(..., strict=True)
```

should be primarily for offscreen.

For live, strict mode may fail with a clear diagnostic.

### 5. Multi-monitor behavior

Physical/reference size resolution depends on which monitor owns the window.

Datoviz should eventually support:

```text
monitor selection
monitor change callbacks
resolved metrics refresh when the window moves
```

Initial behavior can use the primary monitor or the monitor selected before window creation, but this must be reported.

### 6. Fractional scaling and rounding

Fractional Wayland/Linux scaling can produce awkward values:

```text
1.25
1.333
1.5
1.75
```

Never rely only on theoretical scale. Always compute final rendering scale from actual resolved dimensions:

```text
framebuffer_per_canvas_px =
    actual_framebuffer_width / canvas_width_px
```

and similarly for height.

### 7. Non-square or anisotropic scaling

Most displays have effectively square pixels, but APIs may report slightly different X/Y DPI or rounding may produce slightly different scales.

Visual diameters and font sizes need a scalar scale. Recommended behavior:

```text
Use average scale if X/Y differ only slightly.
Warn if anisotropy exceeds tolerance.
```

### 8. Matplotlib GUI backend differences

Different Matplotlib GUI backends may interpret `figsize` and `dpi` differently in live mode. Therefore the Matplotlib renderer should inspect actual canvas dimensions after creation and return a resolved canvas, instead of assuming requested values were honored.

### 9. Backward compatibility of visual sizes

Changing `_px` semantics from “whatever the backend currently did” to “GSP canvas/reference px” may subtly change live Datoviz output on high-DPI systems. That is the correct break, but examples and screenshots will need updating.

### 10. Default reference DPI

`96 DPI` is the right default for CSS-like reference pixels and cross-platform intuition.

However, current Matplotlib review code implicitly uses `100 DPI`. Moving to `96` may cause small visual changes in physical/reference modes. For `pixel_exact`, this should not matter if the generic conversion formula is used correctly.

My recommendation:

```text
Use 96 DPI for reference_px and physical_mm.
Allow explicit reference_dpi.
Do not rely on 96 DPI for pixel_exact marker conversion; use resolved scale.
```

---

The core recommendation is to make canvas sizing a two-step contract: first request a semantic policy, then report a resolved canvas. `DVZ_WINDOW_SIZE_SCALE` should disappear from semantic use because it scales only the window, not the canvas unit system. The durable fix is for Datoviz, Matplotlib, and GSP to agree that visual `_px` fields live in GSP canvas/reference pixels and are lowered through `framebuffer_per_canvas_px` from the resolved canvas.
