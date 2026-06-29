## 1. Architecture Verdict

**Verdict: the proposed contract is directionally correct and should become the Datoviz v0.4 RC contract, but it needs one explicit extra concept: native/surface size is not the same thing as Datoviz logical size or render-target framebuffer size.**

The current bug is exactly that Datoviz already has the right high-level fields, but the GLFW path collapses the model by creating the window with `resolved.logical_width` / `resolved.logical_height` and then letting the GLFW-reported framebuffer/window sizes overwrite the meaning of logical size. The uploaded P017 evidence shows Datoviz detects a device scale around `1.4549`, but still creates/presents a `900 x 650` live framebuffer/window for a requested logical `900 x 650`; Qt/Matplotlib instead produce a native high-DPI surface around `900 * 1.459` by `650 * 1.459`. 

The corrected contract should be:

```text
logical_size       = Datoviz scene/application size, in logical pixels.
native_size        = backend/window-system content size, in backend coordinates.
surface_size       = presentable framebuffer/swapchain size, in physical pixels.
render_size        = actual internal render target size, in physical pixels.
device_scale       = surface physical pixels per Datoviz logical pixel.
render_scale       = extra supersampling scale from surface_size to render_size.
user_scale         = accessibility/style scale, not a layout or device scale.
```

For most current paths with `render_scale == 1`, `surface_size == render_size`, so `framebuffer_width/height` can continue to work. But architecturally, **live GLFW swapchain size and internal supersampled render-target size should not be conflated**. A live GLFW window cannot generally make the OS swapchain larger than the native surface without also changing the native window; supersampling should render to an intermediate target and resolve/downsample into the presentable surface.

The authoritative formula should therefore be:

```text
surface_size = round(logical_size * device_scale)

render_size  = round(surface_size * render_scale)
             = round(logical_size * device_scale * render_scale)
```

For offscreen views, there is no native window or presentable surface, so `surface_size` can be treated as the offscreen output size and `render_size == surface_size` unless Datoviz exposes an explicit resolve output.

GLFW’s own model supports this separation: GLFW window sizes are in “screen coordinates” while framebuffer sizes are in pixels, and GLFW explicitly warns that screen coordinates do not always correspond to pixels. It also documents that `GLFW_SCALE_TO_MONITOR` matters on platforms such as Windows/X11 where screen coordinates and pixels map 1:1, while `GLFW_SCALE_FRAMEBUFFER` matters on macOS/Wayland-style platforms where framebuffer pixels can scale independently of window coordinates. ([GLFW][1]) ([GLFW][2])

So the proposed contract is correct after these refinements:

```text
1. DvzFigure dimensions are logical pixels.
2. DvzView logical size is logical pixels.
3. DvzView surface size is presentable physical pixels.
4. DvzView render size is render-target physical pixels.
5. device_scale = surface_size / logical_size, preferably per axis.
6. render_scale = render_size / surface_size.
7. user_scale affects screen-space style and UI affordance sizes, not the scene layout coordinate system.
8. input delivered to scene/controllers is logical-pixel input.
9. backend/native input is converted at the window backend boundary.
10. native window size is a backend implementation detail, but queryable for diagnostics.
```

One more important API decision: **make scale two-dimensional internally**. Public convenience APIs may expose a scalar for the common case, but the model should carry `device_scale_x`, `device_scale_y`, `native_to_logical_x`, and `native_to_logical_y`. Some platforms and compositor configurations can report non-identical x/y scale or fractional values.

---

## 2. API Break Recommendations

Pre-RC is the right time to break the ambiguous APIs. The goal should be to eliminate every generic `width` / `height` field whose unit is unclear.

### Core size/scale types

Add small explicit structs:

```c
typedef struct DvzExtent
{
    uint32_t width;
    uint32_t height;
} DvzExtent;

typedef struct DvzScale2
{
    float x;
    float y;
} DvzScale2;
```

Optional but useful:

```c
typedef enum DvzSizeSpace
{
    DVZ_SIZE_LOGICAL,   // Datoviz logical pixels.
    DVZ_SIZE_NATIVE,    // Backend/window-system content coordinates.
    DVZ_SIZE_SURFACE,   // Presentable physical pixels.
    DVZ_SIZE_RENDER,    // Internal render-target physical pixels.
} DvzSizeSpace;
```

### Figure API

Break or clarify `DvzFigure`:

```c
typedef struct DvzFigure
{
    uint32_t logical_width;
    uint32_t logical_height;
    // Existing fields...
} DvzFigure;
```

Recommended constructors:

```c
DvzFigure* dvz_figure(uint32_t logical_width, uint32_t logical_height);
void dvz_figure_resize(DvzFigure* figure, uint32_t logical_width, uint32_t logical_height);
DvzExtent dvz_figure_logical_size(const DvzFigure* figure);
```

If preserving source compatibility is desired for one RC cycle, keep `width` / `height` as aliases but document them as logical pixels only. Since you said aggressive pre-RC breakage is acceptable, I would rename them now.

### View description

Replace the current ambiguous scale/extent fields with explicit ones:

```c
typedef struct DvzViewDesc
{
    DvzViewType type;

    DvzExtent logical_size;     // Requested scene/layout size, logical px.

    // Optional overrides. Zero means "resolve automatically".
    DvzExtent surface_size;     // Presentable/output physical px.
    DvzExtent render_size;      // Internal render-target physical px.

    DvzScale2 device_scale;     // 0/0 means auto. Physical surface px per logical px.
    float render_scale;         // Default 1.0. Internal render supersampling.
    float user_scale;           // Default 1.0. Style/accessibility scale.

    DvzHiDpiPolicy hidpi_policy;
    DvzViewSizePolicy size_policy;

    const char* title;
    void* native_surface;       // For external-hosted views, if applicable.
} DvzViewDesc;
```

Recommended enums:

```c
typedef enum DvzHiDpiPolicy
{
    DVZ_HIDPI_AUTO = 0,

    // Force device_scale = 1 unless explicitly specified.
    DVZ_HIDPI_DISABLED,

    // Platform provides a logical window and independently scaled framebuffer.
    // Expected on macOS/Wayland-like paths.
    DVZ_HIDPI_FRAMEBUFFER,

    // Platform/native content area must be enlarged to achieve logical size.
    // Expected on X11/Windows paths where framebuffer == window pixels.
    DVZ_HIDPI_NATIVE_WINDOW,

    // Host provides all metrics; Datoviz must not guess.
    DVZ_HIDPI_EXTERNAL,
} DvzHiDpiPolicy;

typedef enum DvzViewSizePolicy
{
    // User-provided size is logical. This should be the default.
    DVZ_VIEW_SIZE_LOGICAL = 0,

    // User-provided size is physical surface size. Mostly for low-level/offscreen use.
    DVZ_VIEW_SIZE_SURFACE,

    // Host/native size is authoritative; derive logical size using supplied scale.
    DVZ_VIEW_SIZE_NATIVE,
} DvzViewSizePolicy;
```

### Window config

Break `DvzWindowConfig.width` / `height`. These names are the root of the ambiguity.

Replace:

```c
DvzWindowConfig wcfg;
wcfg.width = width;
wcfg.height = height;
```

with:

```c
typedef struct DvzWindowConfig
{
    DvzExtent logical_size;      // Requested Datoviz logical content size.
    DvzExtent native_size;       // Optional raw backend content size. 0 = resolve.
    DvzExtent surface_size;      // Optional requested surface size. 0 = resolve.

    DvzScale2 device_scale;      // 0 = auto.
    float render_scale;          // Default 1.0.
    float user_scale;            // Default 1.0.

    DvzHiDpiPolicy hidpi_policy;
    DvzViewSizePolicy size_policy;

    bool visible;
    bool resizable;
    const char* title;
} DvzWindowConfig;
```

Add a current-state struct emitted by the backend:

```c
typedef struct DvzWindowMetrics
{
    DvzExtent logical_size;      // Datoviz logical px.
    DvzExtent native_size;       // GLFW/window-system coordinates.
    DvzExtent surface_size;      // Presentable framebuffer/swapchain px.
    DvzExtent render_size;       // Internal render target px.

    DvzScale2 content_scale;     // Raw platform/GLFW content scale.
    DvzScale2 framebuffer_scale; // surface_size / native_size.
    DvzScale2 device_scale;      // surface_size / logical_size.
    DvzScale2 native_to_logical; // logical_size / native_size.

    DvzHiDpiPolicy active_hidpi_policy;
    uint64_t generation;
} DvzWindowMetrics;
```

### Query and resize APIs

Add explicit queries:

```c
DvzExtent dvz_view_size(const DvzView* view, DvzSizeSpace space);

DvzExtent dvz_view_logical_size(const DvzView* view);
DvzExtent dvz_view_native_size(const DvzView* view);
DvzExtent dvz_view_surface_size(const DvzView* view);
DvzExtent dvz_view_render_size(const DvzView* view);

DvzScale2 dvz_view_device_scale(const DvzView* view);
float dvz_view_render_scale(const DvzView* view);
float dvz_view_user_scale(const DvzView* view);
```

Make the default resize logical:

```c
void dvz_view_resize(DvzView* view, uint32_t logical_width, uint32_t logical_height);
```

Add explicit low-level variants:

```c
void dvz_view_resize_logical(DvzView* view, DvzExtent logical_size);
void dvz_view_resize_surface(DvzView* view, DvzExtent surface_size);
void dvz_view_set_render_scale(DvzView* view, float render_scale);
void dvz_view_set_user_scale(DvzView* view, float user_scale);
void dvz_view_set_device_scale(DvzView* view, DvzScale2 device_scale);
```

### Resize event

Replace resize events that only carry width/height with explicit metrics:

```c
typedef struct DvzResizeEvent
{
    DvzView* view;

    DvzExtent logical_size;
    DvzExtent native_size;
    DvzExtent surface_size;
    DvzExtent render_size;

    DvzScale2 device_scale;
    DvzScale2 native_to_logical;

    DvzResizeReason reason;
} DvzResizeEvent;
```

Where:

```c
typedef enum DvzResizeReason
{
    DVZ_RESIZE_USER,
    DVZ_RESIZE_PROGRAMMATIC,
    DVZ_RESIZE_CONTENT_SCALE,
    DVZ_RESIZE_FRAMEBUFFER,
    DVZ_RESIZE_EXTERNAL_HOST,
} DvzResizeReason;
```

---

## 3. GLFW Implementation Strategy

### Key rule

`dvz_view()` must never create a GLFW window from logical size and then treat GLFW-reported native size as logical size. The backend must return a `DvzWindowMetrics` object, and app/view code must preserve the distinction.

GLFW documents that `glfwGetWindowSize()` returns content area size in screen coordinates, while `glfwGetFramebufferSize()` returns framebuffer size in pixels. Pixel-based rendering should use framebuffer size, not window size. ([GLFW][3])

### Refactor creation into two phases

Current:

```c
resolved = _view_desc_resolve(...)
_view_create_glfw(..., resolved.logical_width, resolved.logical_height, ...)
```

Replace with:

```c
DvzViewDesc partial = _view_desc_resolve_logical(src, figure);
DvzWindow* window = _view_create_glfw(app, figure, &partial);
DvzWindowMetrics metrics = dvz_window_metrics(window);
_view_apply_metrics(view, &partial, &metrics);
```

`_view_desc_resolve()` should no longer pretend it can always resolve device scale before the platform window exists. Split it:

```c
_view_desc_resolve_logical()
_view_desc_resolve_from_metrics()
```

### GLFW backend modes

Implement three active modes under `DVZ_HIDPI_AUTO`.

#### A. Framebuffer-scaling mode: macOS/Wayland-style

Use when:

```text
glfw framebuffer size / glfw window size ~= content scale
```

Behavior:

```text
glfwCreateWindow(logical_width, logical_height, ...)
logical_size = glfw window size
surface_size = glfw framebuffer size
device_scale = surface_size / logical_size
native_to_logical = 1
```

Set hints where available:

```c
glfwWindowHint(GLFW_SCALE_FRAMEBUFFER, GLFW_TRUE);  // GLFW 3.4+
```

For older GLFW/macOS:

```c
glfwWindowHint(GLFW_COCOA_RETINA_FRAMEBUFFER, GLFW_TRUE);
```

Do not multiply the window size in this mode. The platform keeps logical/screen-coordinate window size stable while changing the framebuffer.

#### B. Native-window-scaling mode: X11/Windows-style

Use when:

```text
glfw framebuffer size / glfw window size ~= 1
content_scale > 1
```

On these platforms, the native content area must be enlarged to get the same logical visual size as a high-DPI toolkit window. GLFW documents that `GLFW_SCALE_TO_MONITOR` is specifically for platforms such as Windows and X11 where screen coordinates and pixels map 1:1; in that case the window content area needs to be resized when content scale changes. ([GLFW][2])

Creation strategy:

```c
logical = requested logical size
scale   = resolved effective content scale

native_width  = round(logical_width  * scale.x)
native_height = round(logical_height * scale.y)

glfwCreateWindow(native_width, native_height, ...)
```

But because scale may only be known reliably after a window exists, prefer this robust sequence:

```c
glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);

glfwCreateWindow(initial_width, initial_height, ...);

query content scale, framebuffer size, window size;
compute active policy;

if native-window-scaling mode:
    glfwSetWindowSize(window,
        round(logical_width  * device_scale.x),
        round(logical_height * device_scale.y));

query again;
show window;
```

This avoids visible flicker and avoids relying blindly on `GLFW_SCALE_TO_MONITOR`.

`GLFW_SCALE_TO_MONITOR` can still be used, but only if Datoviz preserves the requested logical size separately. If GLFW returns an enlarged `glfwGetWindowSize()`, Datoviz must derive:

```text
logical_size = native_size / device_scale
```

not:

```text
logical_size = native_size
```

That is the likely collapse described in your prompt.

#### C. Disabled/1x mode

Use when:

```text
device_scale == 1
or DVZ_HIDPI_DISABLED
```

Behavior:

```text
logical_size == native_size == surface_size
device_scale = 1
```

### Effective metrics computation

Move the existing `_glfw_effective_content_scale()` logic into a backend metrics resolver that returns all values together:

```c
static DvzWindowMetrics _glfw_query_metrics(DvzWindow* window)
{
    int win_w = 0, win_h = 0;
    int fb_w = 0, fb_h = 0;
    float cs_x = 1, cs_y = 1;

    glfwGetWindowSize(handle, &win_w, &win_h);
    glfwGetFramebufferSize(handle, &fb_w, &fb_h);
    glfwGetWindowContentScale(handle, &cs_x, &cs_y);

    // Existing monitor DPI / DVZ_DISPLAY_SCALE override logic can contribute here.
}
```

Then normalize:

```c
framebuffer_scale.x = fb_w / (float)win_w;
framebuffer_scale.y = fb_h / (float)win_h;

if (policy == DVZ_HIDPI_FRAMEBUFFER)
{
    logical = win;
    surface = fb;
    device_scale = surface / logical;
    native_to_logical = {1, 1};
}
else if (policy == DVZ_HIDPI_NATIVE_WINDOW)
{
    native = win;
    surface = fb; // Usually equal to native on X11/Windows.
    logical = requested_logical_or_round(native / effective_scale);
    device_scale = surface / logical;
    native_to_logical = logical / native;
}
```

Use the same rounding everywhere:

```c
static uint32_t _dvz_round_extent(float x)
{
    return (uint32_t)DVZ_MAX(1, floorf(x + 0.5f));
}
```

Acceptance should allow ±1 px because fractional scales such as `1.4549` cannot always round identically across toolkit/window-manager paths.

### Resizing

`dvz_view_resize_logical(view, logical)` should:

```text
1. Store requested logical size.
2. Compute target native size from active policy.
3. Resize GLFW content area using glfwSetWindowSize().
4. Requery window/framebuffer/content scale.
5. Recreate surface/swapchain/render targets as needed.
6. Emit one logical resize event.
```

For native-window-scaling mode:

```c
glfwSetWindowSize(
    handle,
    round(logical.width  * device_scale.x),
    round(logical.height * device_scale.y));
```

For framebuffer-scaling mode:

```c
glfwSetWindowSize(handle, logical.width, logical.height);
```

For user drag-resize:

```text
native-window mode:
    logical = round(native / device_scale)

framebuffer mode:
    logical = window_size
```

For content-scale changes while moving monitors:

```text
If preserve-logical-on-scale-change is enabled:
    keep logical_size fixed;
    resize native window or wait for framebuffer update;
    recreate surface/render targets.

If user is actively resizing:
    avoid fighting the window manager;
    derive logical from current native size until resize ends.
```

Default should be **preserve logical size on pure content-scale change**, because a 900×650 Datoviz figure should remain a 900×650 Datoviz figure when dragged between monitors.

---

## 4. Input Coordinate Strategy

Scene/controller APIs should receive logical coordinates, always.

GLFW cursor positions are measured in screen coordinates relative to the top-left of the window content area, and GLFW’s coordinate systems use x-right, y-down screen coordinates. ([GLFW][1]) ([GLFW][4]) Datoviz should convert these at the GLFW backend boundary.

### Store conversion factors in window metrics

```c
metrics.native_to_logical.x =
    metrics.logical_size.width / (float)metrics.native_size.width;

metrics.native_to_logical.y =
    metrics.logical_size.height / (float)metrics.native_size.height;
```

Then:

```c
logical_x = native_x * metrics.native_to_logical.x;
logical_y = native_y * metrics.native_to_logical.y;
```

Examples:

```text
macOS/Wayland framebuffer-scaling mode:
    native/window coords = logical coords
    native_to_logical = 1

X11/Windows native-window-scaling mode:
    native/window coords = physical-ish screen coords
    native_to_logical = 1 / device_scale
```

For the observed case:

```text
device_scale ≈ 1.4549
native cursor x = 654.7
logical cursor x ≈ 450.0
```

### Event handling rules

Pointer move:

```c
emit_pointer_move(logical_x, logical_y);
```

Pointer delta:

```c
logical_dx = native_dx * native_to_logical.x;
logical_dy = native_dy * native_to_logical.y;
```

Mouse buttons:

```text
No scaling.
Use last logical cursor position in the event payload.
```

Wheel/scroll:

```text
Do not blindly multiply GLFW scroll offsets by device_scale.
GLFW scroll offsets are abstract scroll units, not framebuffer pixels.
If Datoviz has pixel-scroll or pan deltas, convert only those deltas with native_to_logical.
```

Window resize:

```text
Do not emit raw GLFW window size as Datoviz logical size.
Requery full metrics, normalize, then emit DvzResizeEvent with logical/native/surface/render sizes.
```

Picking:

```text
Scene/controller coordinate: logical.
Picking buffer coordinate: physical render target.
Conversion: physical = logical * (render_size / logical_size).
```

Y-axis conversion must be explicit:

```text
Logical input origin: top-left, y down.
GPU NDC origin: center, y up.
Therefore positive screen-space y offsets become negative clip-space y offsets.
```

This same convention should drive the glyph shader fix.

---

## 5. Render / Style Scaling Strategy

Use this as the single rule:

```text
layout_px           = logical pixels
surface_px          = logical_px * device_scale
render_px           = logical_px * device_scale * render_scale
style_render_px     = logical_style_px * user_scale * device_scale * render_scale
```

But distinguish layout values from style values.

| Quantity                            | Authored in |                Affects layout? |                               Apply device_scale? |                   Apply render_scale? |      Apply user_scale? |
| ----------------------------------- | ----------: | -----------------------------: | ------------------------------------------------: | ------------------------------------: | ---------------------: |
| Figure/view size                    |  logical px |                            yes |                       only for surface allocation |       only for internal render target |                     no |
| Scene/panel layout rects            |  logical px |                            yes |                 when lowering to viewport/scissor | when rendering to supersampled target |                     no |
| Viewport/scissor                    | physical px |                             no |                                               yes |        yes if targeting render target |                     no |
| Swapchain/surface size              | physical px |                             no |                                               yes |                                    no |                        |
| Internal render target size         | physical px |                             no |                                               yes |                                   yes |                        |
| Point size                          |  logical px |                   visual style |                                               yes |                 yes for render target |                    yes |
| Line width                          |  logical px |                   visual style |                                               yes |                 yes for render target |                    yes |
| Text size                           |  logical px |                   visual style |                                               yes |                 yes for render target |                    yes |
| Text offset                         |  logical px |                   visual style |                                               yes |                 yes for render target |                    yes |
| Tick length / padding               |  logical px |            style-driven layout |                                  yes when drawing |                    yes when rendering |                    yes |
| Explicit colorbar rect/width/height |  logical px |                            yes |                                  yes when drawing |                    yes when rendering |          no by default |
| Default/auto colorbar thickness     |  logical px |        yes, derived from style |                                  yes when drawing |                    yes when rendering | yes before auto-layout |
| Explicit axis/guide reserve         |  logical px |                            yes | no for layout; yes when drawing reserved geometry |                    yes when rendering |          no by default |
| Auto axis/guide reserve             |  logical px | yes, derived from labels/ticks |                                  yes when drawing |                    yes when rendering | yes before auto-layout |

The distinction matters:

```text
Explicit layout geometry should not silently change because user_scale changed.
Auto layout derived from style should change, otherwise larger text will clip.
```

So I would add field-level naming or flags:

```c
axis.reserve_logical_px              // explicit layout, not user-scaled
axis.auto_reserve_from_style = true   // derived, user-scaled
colorbar.logical_width               // explicit layout, not user-scaled
colorbar.style_thickness             // UI affordance, user-scaled
```

For shader uniforms, stop passing ambiguous `device_scale` and instead pass the exact lowering factor:

```c
typedef struct DvzViewTransform
{
    DvzExtent logical_size;
    DvzExtent surface_size;
    DvzExtent render_size;

    DvzScale2 logical_to_surface;
    DvzScale2 logical_to_render;
    float user_scale;
} DvzViewTransform;
```

Then visuals use:

```text
logical_to_render = render_size / logical_size
style_to_render   = logical_to_render * user_scale
```

This avoids backend-specific guessing.

---

## 6. Text Anchoring Strategy

The current text anchor pipeline is probably half-correct: retained text stores anchors, forwards them into glyph items, and glyph realization applies:

```c
align_x = -text_anchor[0] * width;
align_y = -text_anchor[1] * height;
```

That formula is correct **if and only if** Datoviz defines text layout coordinates as:

```text
origin at top-left of the text layout box
x positive right
y positive down
anchor = normalized point inside layout box
```

Under that convention:

```text
anchor (0, 0)     = top-left
anchor (0.5, 0.5) = center
anchor (0.5, 1.0) = bottom-center
anchor (1, 1)     = bottom-right
```

For a text layout box with width `w`, height `h`, and anchor position `P`, the realized glyph union should be:

```text
anchor (0, 0):
    min = P
    max = P + (w, h)

anchor (0.5, 0.5):
    min = P - (w/2, h/2)
    max = P + (w/2, h/2)

anchor (0.5, 1.0):
    min = P + (-w/2, -h)
    max = P + ( w/2,  0)

anchor (1, 1):
    min = P + (-w, -h)
    max = P
```

That should become the documented Datoviz retained-text semantics.

### Fix the y-axis convention

The WGSL and GLSL glyph shaders disagree:

```wgsl
-2.0 * rotated.y / viewport.rect.w
```

versus:

```glsl
+2.0 * rotated.y / viewport.rect.w
```

If Datoviz screen-space coordinates are x-right/y-down and clip-space is y-up, the WGSL sign is the coherent one. The GLSL path should likely become:

```glsl
return vec2(
    viewport.rect.z > 0.0 ?  2.0 * rotated.x / viewport.rect.z : 0.0,
    viewport.rect.w > 0.0 ? -2.0 * rotated.y / viewport.rect.w : 0.0);
```

But do not merge this as a guess. First add a backend-independent glyph placement test and, where CI allows, a backend render test. The test should make the GLSL/WGSL mismatch fail visibly.

### Text tests to add

Add CPU glyph-realization tests that do not require a GPU:

```c
test_text_anchor_bounds_bitmap_top_left()
test_text_anchor_bounds_bitmap_center()
test_text_anchor_bounds_bitmap_bottom_center()
test_text_anchor_bounds_bitmap_bottom_right()

test_text_anchor_bounds_msdf_top_left()
test_text_anchor_bounds_msdf_center()
test_text_anchor_bounds_msdf_bottom_center()
test_text_anchor_bounds_msdf_bottom_right()
```

Use a deterministic bundled font and a string with ascenders/descenders, for example:

```text
"Hg"
```

or use a synthetic/fake glyph atlas for exact metrics.

For each test:

```text
1. Create text item at logical position P = (100, 100).
2. Realize glyph quads without rotation.
3. Compute union of realized glyph quad bounds in screen/logical coordinates.
4. Assert the union has the expected min/max relative to P.
5. Tolerance: ≤ 0.5 px for CPU/fixed metrics, ≤ 1 px for real font rasterization.
```

Add rotation-specific tests later, but define now:

```text
Anchor is applied before rotation.
The anchor point is the rotation pivot.
```

Add shader-sign tests:

```c
test_glyph_screen_offset_to_clip_y_down_cpu()
```

Expected:

```text
positive screen y offset lowers the glyph on screen
positive screen y offset maps to negative clip-space y
```

GPU smoke test when available:

```text
Draw a small glyph or rectangle at viewport center with +Y screen offset.
Read back or snapshot.
Assert it appears below the center for both GLSL and WGSL backends.
```

This is the most direct way to prevent the current WGSL/GLSL sign split from surviving.

---

## 7. Migration Plan

### Phase 0 — Add diagnostics before changing behavior

Files likely touched:

```text
src/app/app.c
src/window/backend_glfw.c
src/window/window.c
include/datoviz/app.h
include/datoviz/window.h
```

Add a debug/probe log:

```text
requested_logical
glfw_window_size
glfw_framebuffer_size
glfw_content_scale
effective_device_scale
active_hidpi_policy
computed_logical
computed_surface
computed_render
```

Acceptance:

```text
On the known X11 setup, the log clearly shows:
requested logical = 900 x 650
current native/fb = 900 x 650
device_scale ≈ 1.45
active policy wants native-window scaling
```

Risk: low.

### Phase 1 — Introduce explicit metrics structs and APIs

Files:

```text
include/datoviz/app.h
include/datoviz/window.h
src/app/app.c
src/window/window.c
```

Add `DvzExtent`, `DvzScale2`, `DvzWindowMetrics`, `DvzHiDpiPolicy`, `DvzViewSizePolicy`.

Rename or replace ambiguous `width` / `height` fields.

Acceptance:

```text
Code compiles.
Existing tests either migrated or intentionally fail only where old width/height names were removed.
No GLFW behavior change yet.
```

Risk: medium because it touches public API.

### Phase 2 — Split view-desc resolution

Files:

```text
src/app/app.c
include/datoviz/app.h
```

Change:

```c
_view_desc_resolve()
```

into:

```c
_view_desc_resolve_logical()
_view_desc_resolve_from_window_metrics()
```

Acceptance:

```text
Unit tests prove logical size is preserved even when native/window size differs.
Offscreen view creation still produces expected physical render size.
```

Risk: medium.

### Phase 3 — Implement GLFW high-DPI policies

Files:

```text
src/window/backend_glfw.c
src/window/window.c
include/datoviz/window.h
```

Implement:

```text
DVZ_HIDPI_AUTO
DVZ_HIDPI_FRAMEBUFFER
DVZ_HIDPI_NATIVE_WINDOW
DVZ_HIDPI_DISABLED
```

Use hidden creation or post-create resize to avoid flicker.

Acceptance for X11 high-DPI:

```text
Requested logical: 900 x 650
Datoviz logical:   900 x 650
Device scale:      ≈ 1.45
Surface/fb:        ≈ round(900*1.45) x round(650*1.45)
Native client:     ≈ surface/fb on X11
```

Acceptance for macOS/Wayland-like paths:

```text
Requested logical: 900 x 650
GLFW window size:  900 x 650
Framebuffer:       ≈ round(900*scale) x round(650*scale)
```

Risk: high. This touches platform behavior and resize event ordering.

### Phase 4 — Normalize resize and content-scale callbacks

Files:

```text
src/window/backend_glfw.c
src/window/window.c
src/app/app.c
```

Callbacks should requery full metrics rather than trusting one callback’s arguments.

Acceptance:

```text
Moving between monitors does not collapse logical size.
User resize emits logical size, native size, and surface size correctly.
No resize feedback loop.
No repeated resize events when metrics are unchanged.
```

Risk: high on multi-monitor fractional-DPI setups.

### Phase 5 — Convert input at backend boundary

Files:

```text
src/window/backend_glfw.c
src/app/app.c
src/scene/controller*.c
```

Add `native_to_logical` conversion before controller events.

Acceptance:

```text
On X11 scale 1.5, clicking visual center of a 900 x 650 Datoviz view reports approximately (450, 325), not (675, 487).
Brush/pan/zoom interactions align with rendered visuals.
Picking uses logical-to-render conversion and still hits marks correctly.
```

Risk: medium.

### Phase 6 — Audit render/style lowering

Files likely touched:

```text
src/scene/*
src/visuals/*
src/scene/axis*
src/scene/colorbar*
src/scene/panel*
src/render/*
shader/*.glsl
shader/*.wgsl
```

Introduce explicit uniforms:

```text
logical_size
surface_size
render_size
logical_to_surface
logical_to_render
style_to_render
```

Acceptance:

```text
Point size, line width, text size, text offsets, ticks, labels, and colorbars match expected physical size at scale 1.0 and 1.5.
render_scale changes quality/resolution but not perceived layout size.
user_scale changes style affordance size but does not change explicit figure/panel geometry.
```

Risk: high because this can expose existing implicit assumptions.

### Phase 7 — Text anchor and shader y-axis fix

Files:

```text
src/scene/text*.c
src/visuals/text*.c
src/visuals/glyph*.c
shader/glyph.glsl
shader/glyph.wgsl
tests/scene/test_text_anchor*.c
tests/visuals/test_glyph*.c
```

Acceptance:

```text
Anchor bounds tests pass for bitmap and MSDF text.
GLSL and WGSL agree on positive y-down screen offsets.
GSP_API example 06 text labels align with Matplotlib semantics without GSP-side scaling or anchoring workarounds.
```

Risk: medium.

### Phase 8 — Documentation and examples

Files:

```text
docs/scene.md
docs/app.md
docs/window.md
examples/*
```

Document the four-size model:

```text
logical
native
surface
render
```

Acceptance:

```text
No public doc says "width" without a unit.
Examples specify logical sizes.
Debug output makes high-DPI behavior obvious.
```

Risk: low.

---

## 8. Regression Test Plan

### Pure unit tests: always run in CI

#### `_view_round_size()`

```text
round_size(900 * 1.4549) == 1309 or 1310 depending chosen rule
round_size(650 * 1.4549) == 946
round_size(0.2) == 1
round_size(NaN/Inf/negative) falls back or rejects
```

#### View-desc resolution

```c
test_view_desc_logical_size_from_figure()
test_view_desc_device_scale_default_1_for_offscreen()
test_view_desc_surface_size_from_logical_device()
test_view_desc_render_size_from_surface_render_scale()
test_view_desc_explicit_surface_size_preserved()
test_view_desc_explicit_render_size_preserved_or_rejected_if_inconsistent()
```

#### Synthetic GLFW metric normalization

No display required. Feed synthetic metrics into a pure function:

```c
DvzWindowMetrics dvz_window_metrics_normalize(
    DvzRawWindowMetrics raw,
    DvzWindowConfig requested);
```

Cases:

```text
macOS/Wayland-like:
    requested logical = 900 x 650
    raw window        = 900 x 650
    raw framebuffer   = 1350 x 975
    content scale     = 1.5
    expect logical    = 900 x 650
    expect surface    = 1350 x 975
    expect native_to_logical = 1

X11/Windows corrected:
    requested logical = 900 x 650
    raw window        = 1350 x 975
    raw framebuffer   = 1350 x 975
    content scale     = 1.5
    expect logical    = 900 x 650
    expect surface    = 1350 x 975
    expect native_to_logical = 1 / 1.5

X11/Windows current broken:
    requested logical = 900 x 650
    raw window        = 900 x 650
    raw framebuffer   = 900 x 650
    content scale     = 1.5
    expect needs_native_resize = true
```

#### Input conversion

```text
native_to_logical = 1:
    cursor 450,325 -> logical 450,325

native_to_logical = 2/3:
    cursor 675,487.5 -> logical 450,325

resize native 1500x900 at scale 1.5:
    logical 1000x600
```

#### Render/style scale matrix

Test a helper:

```c
DvzScale2 dvz_view_logical_to_render(metrics);
DvzScale2 dvz_view_style_to_render(metrics);
```

Cases:

```text
device=1, render=1, user=1 => style factor 1
device=1.5, render=1, user=1 => style factor 1.5
device=1.5, render=2, user=1 => style factor 3
device=1.5, render=2, user=1.25 => style factor 3.75
```

#### Text anchor bounds

CPU tests:

```text
anchor (0,0)     => union min = P,              max = P + (w,h)
anchor (0.5,0.5) => union min = P - (w/2,h/2), max = P + (w/2,h/2)
anchor (0.5,1.0) => union min = P + (-w/2,-h), max = P + (w/2,0)
anchor (1,1)     => union min = P - (w,h),     max = P
```

Run for:

```text
bitmap glyph path
MSDF glyph path
retained text -> glyph visual forwarding
```

#### Shader convention tests

At minimum:

```text
positive screen y offset maps to negative clip y
GLSL and WGSL shader source both contain the same y-down convention
```

Better: move the math into a generated shared snippet or a CPU-tested helper so the two shader backends cannot diverge silently.

### Live GLFW tests: conditional

Skip when any of these are true:

```text
DVZ_TEST_LIVE_GLFW is not set
CI has no DISPLAY and no WAYLAND_DISPLAY on Linux
GLFW init fails
GPU/Vulkan/WebGPU device creation fails
software/headless backend cannot create a presentable surface
window manager clamps or refuses requested size
```

Live tests:

```c
test_glfw_live_hidpi_probe()
test_glfw_live_display_scale_override()
test_glfw_live_logical_resize()
test_glfw_live_input_coordinate_conversion()
```

For deterministic CI, use `DVZ_DISPLAY_SCALE=1.5`.

Expected with override:

```text
requested logical = 300 x 200

native-window mode:
    native/surface ≈ 450 x 300
    logical        = 300 x 200

framebuffer mode:
    window/native  = 300 x 200
    surface        ≈ 450 x 300
    logical        = 300 x 200
```

Use tolerance:

```text
logical size exact
scale tolerance ±0.02
physical size tolerance ±2 px
outer-window/decorated size ignored
```

### Manual/integration tests

Keep a small probe executable:

```text
datoviz_hidpi_probe --logical 900x650 --render-scale 1 --user-scale 1
```

It should print:

```text
logical_size
native_size
surface_size
render_size
device_scale
content_scale
native_to_logical
active_hidpi_policy
```

This is essential because high-DPI regressions are often platform/window-manager-specific.

---

## 9. Failure Modes

### Double scaling

Symptom:

```text
requested logical 900 x 650
device scale 1.5
native/surface becomes ~2025 x 1463
```

Cause:

```text
Both GLFW_SCALE_TO_MONITOR and manual native-size multiplication are applied.
```

Detection:

```text
Assert surface/logical ≈ device_scale, not device_scale².
```

### Logical size overwritten by native size

Symptom:

```text
requested logical 900 x 650
native window 1310 x 946
Datoviz logical becomes 1310 x 946
Scene layout appears too large or input is offset.
```

Detection:

```text
Unit test synthetic X11 corrected metrics.
Live test: requested logical must remain exact after create.
```

### Render scale changes window size

Symptom:

```text
render_scale=2 makes the OS window twice as large.
```

Correct behavior:

```text
render_scale changes internal render target only.
surface/native window remains logical * device_scale.
```

Detection:

```text
Create view with render_scale=1 and 2; native/surface should match, render_size should differ.
```

### Input is off by high-DPI scale

Symptom:

```text
Clicking the visual center reports a coordinate near physical center, not logical center.
```

Detection:

```text
Synthetic cursor tests and live center-click/picking tests.
```

### Resize feedback loop

Symptom:

```text
Moving to another monitor or user-resizing causes repeated resize events or oscillating sizes.
```

Cause:

```text
Callback A sets native size; callback B derives logical size differently; rounding differs.
```

Detection:

```text
Generation counter, idempotent metrics comparison, ±1 px tolerance, callback coalescing.
```

### Content-scale callback ordering bugs

Symptom:

```text
During monitor move, Datoviz briefly reallocates wrong framebuffer or emits inconsistent events.
```

Cause:

```text
Using callback arguments directly instead of requerying all metrics.
```

Fix:

```text
Every resize/content-scale callback should requery window size, framebuffer size, and content scale together.
```

### User scale accidentally changes layout

Symptom:

```text
Changing accessibility/user scale moves panels or changes explicit figure size.
```

Correct behavior:

```text
Explicit layout values stay logical.
Auto reserves derived from style may grow.
```

Detection:

```text
Tests for explicit reserves versus auto reserves.
```

### Text anchor uses ink bounds in one path and layout bounds in another

Symptom:

```text
Bitmap and MSDF text with same anchor land differently.
Strings with descenders shift unexpectedly.
```

Fix:

```text
Define one layout box convention.
Use it in both bitmap and MSDF realization.
```

Detection:

```text
Anchor bounds tests for "Hg" or synthetic glyph metrics across both text paths.
```

### GLSL/WGSL y-axis divergence

Symptom:

```text
Text appears shifted up in one backend and down in another.
```

Fix:

```text
Adopt y-down screen-space offsets and negative y conversion to clip space in both shader languages.
```

Detection:

```text
Shader-sign unit test and GPU smoke test.
```

### External host supplies incomplete metrics

Symptom:

```text
Embedded/native-surface view has correct framebuffer but wrong logical layout or input mapping.
```

Fix:

```text
External-hosted views must provide logical_size, surface_size, and device_scale, or choose an explicit derivation policy.
```

Detection:

```text
Reject ambiguous external descriptors at creation time.
```

### X11 raw DPI fallback is wrong

Symptom:

```text
Scale computed from monitor millimeters is unrealistic.
```

Fix:

```text
Prefer explicit platform content scale and DVZ_DISPLAY_SCALE override.
Treat raw DPI as fallback only.
Clamp suspicious values or log warnings.
```

Detection:

```text
Scale resolver tests for raw DPI edge cases.
```

---

## Bottom-line recommendation

Do **not** fix this in GSP_API. Fix Datoviz by making the window/view contract explicit and enforcing it at the backend boundary.

The most important concrete change is this:

```c
// Wrong for high-DPI GLFW:
_view_create_glfw(app, figure,
                  resolved.logical_width,
                  resolved.logical_height,
                  resolved.title);

// Correct shape:
_view_create_glfw(app, figure, &resolved_desc);
metrics = dvz_window_metrics(window);
_view_apply_metrics(view, &resolved_desc, &metrics);
```

And inside the GLFW backend:

```text
requested logical size is preserved;
native size is platform-dependent;
surface/framebuffer size is physical;
render size is surface * render_scale;
input is converted native -> logical before scene/controller delivery.
```

For the observed `900 x 650` at scale `~1.4549`, the acceptance target should be:

```text
Datoviz logical size:      900 x 650
Datoviz device scale:      ~1.4549
Datoviz surface/fb size:   ~1309 x 946, subject to rounding/platform tolerance
Datoviz input center:      ~450 x 325 logical
No GSP_API live-size multiplier workaround.
```

[1]: https://www.glfw.org/docs/latest/intro_guide.html "GLFW: Introduction to the API"
[2]: https://www.glfw.org/docs/latest/window_guide.html "GLFW: Window guide"
[3]: https://www.glfw.org/docs/latest/group__window.html "GLFW: Window reference"
[4]: https://www.glfw.org/docs/latest/input_guide.html "GLFW: Input guide"
