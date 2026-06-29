# P017 - Datoviz v0.4 Live HiDPI Window and Text Anchoring Architecture

## Prompt for ChatGPT Pro

You are reviewing a pre-RC Datoviz v0.4 architecture decision. API compatibility may be broken aggressively if that produces the correct long-term design. The goal is to define the right fix for Datoviz live GLFW high-DPI window sizing and Datoviz text anchoring, not a downstream workaround in GSP_API.

Please provide an architecture review and implementation plan. Treat the facts below as the complete context.

### Project Context

Datoviz v0.4 has a scene/app architecture with:

- `DvzFigure` dimensions intended to be logical pixels.
- `DvzViewDesc` containing both logical dimensions and framebuffer dimensions:
  - `logical_width`, `logical_height`
  - `framebuffer_width`, `framebuffer_height`
  - `device_scale`, `user_scale`, `render_scale`
- Scene specs stating that:
  - scene layout and visual sizes are authored in logical pixels;
  - runtime render targets are physical pixels;
  - `framebuffer = logical_size * device_scale * render_scale` where applicable;
  - user-facing screen-space style values such as point size, line width, text size, text offsets, colorbar dimensions, and reserves are logical pixels;
  - device scale and user scale lower logical-pixel style quantities to physical pixels at render time;
  - pointer/input coordinates exposed to scene controllers should be logical coordinates.

GSP_API uses Datoviz v0.4 as a backend. During live side-by-side review with Matplotlib, the Datoviz live canvas is systematically smaller than the Matplotlib live canvas for the same requested logical size. This is visible on a high-DPI Linux/X11 setup with i3/window manager.

### Observed Evidence

For a requested live size of `900 x 650`:

- Datoviz actual X11 client window: `900 x 650`.
- Datoviz `dvz_view_logical_size`: `900 x 650`.
- Datoviz `dvz_view_framebuffer_size`: `900 x 650`.
- Datoviz `dvz_view_device_scale`: approximately `1.4549`.
- Setting `DVZ_DISPLAY_SCALE=1.5` affects reported scale but does not change Datoviz live framebuffer/window geometry.

For Matplotlib/Qt with the same logical size:

- Matplotlib figure canvas logical size: `900 x 650`.
- Qt `devicePixelRatioF`: approximately `1.4591`.
- Actual X11 client window: about `1313 x 1005`.
- This matches `900 * 1.459` and `650 * 1.459` plus toolkit/window decoration effects.

Conclusion: Datoviz detects high-DPI scale but does not allocate/create/present a scaled live framebuffer. Matplotlib treats requested size as logical size; Datoviz treats it effectively as physical native size.

### Relevant Datoviz Source Findings

In `include/datoviz/app.h`, `DvzViewDesc` already exposes logical/framebuffer/device-scale fields.

In `src/app/app.c`:

```c
static void _view_desc_resolve(
    const DvzViewDesc* src, const DvzFigure* figure, DvzViewDesc* out)
{
    desc.device_scale = _view_valid_scale(desc.device_scale);
    ...
    if (desc.framebuffer_width == 0)
        desc.framebuffer_width = _view_round_size((float)desc.logical_width * desc.device_scale);
    if (desc.framebuffer_height == 0)
        desc.framebuffer_height = _view_round_size((float)desc.logical_height * desc.device_scale);
}
```

But `dvz_view()` ignores the resolved framebuffer size for GLFW:

```c
case DVZ_VIEW_GLFW:
    win = _view_create_glfw(
        app, figure, resolved.logical_width, resolved.logical_height, resolved.title);
    break;
```

And `_view_create_glfw()` passes those values directly to the window config:

```c
DvzWindowConfig wcfg = dvz_window_config();
wcfg.width  = width;
wcfg.height = height;
DvzWindow* window = dvz_window_create(app->window_host, DVZ_BACKEND_GLFW, &wcfg);
```

In `src/window/backend_glfw.c`:

```c
GLFWwindow* handle = glfwCreateWindow(
    (int)config->width, (int)config->height, config->title ? config->title : "", NULL, NULL);
```

Datoviz then queries:

```c
glfwGetFramebufferSize(handle, &fb_width, &fb_height);
glfwGetWindowSize(handle, &win_width, &win_height);
glfwGetWindowContentScale(handle, &scale_x, &scale_y);
_glfw_effective_content_scale(handle, scale_x, scale_y, &scale_x, &scale_y);
dvz_window_backend_emit_resize(
    window, fb_width, fb_height, win_width, win_height, scale_x, scale_y);
```

`_glfw_effective_content_scale()` already combines:

- GLFW window content scale;
- framebuffer/window ratio;
- monitor content scale;
- raw monitor DPI;
- `DVZ_DISPLAY_SCALE` override.

This computes the observed `~1.4549` scale, but the framebuffer remains the native `900 x 650`.

The vendored GLFW has `GLFW_SCALE_TO_MONITOR`. On X11, GLFW can multiply the native window size by content scale when `scaleToMonitor` is enabled, but simply setting that hint may cause `glfwGetWindowSize()` to report the enlarged native size, which could collapse Datoviz logical and physical sizes again unless Datoviz preserves logical size explicitly.

### Current Text Anchoring Problem

In GSP_API example 06, Datoviz text labels render shifted compared with Matplotlib even after GSP passes intended label positions and anchors.

GSP sends:

- NDC positions converted to panel-centered screen placement;
- `anchor_x = CENTER` mapped to Datoviz `text_anchor[0] = 0.5`;
- `anchor_y = BOTTOM` mapped to Datoviz `text_anchor[1] = 1.0`.

Datoviz source shows retained text receives and forwards these anchors:

```c
if (text->placement.has_text_anchor)
{
    item.anchor[0] = text->placement.text_anchor[0];
    item.anchor[1] = text->placement.text_anchor[1];
}
```

And batched text glyph realization uses:

```c
float align_x = -text_anchor[0] * width;
float align_y = -text_anchor[1] * height;
```

Current tests assert that text visuals create glyph visuals and carry anchor attributes, but they do not assert concrete glyph quad offsets for centered/bottom anchors.

There is also a suspicious shader convention mismatch:

WGSL glyph shader:

```wgsl
return vec2f(
    select(0.0, 2.0 * rotated.x / viewport.rect.z, viewport.rect.z > 0.0),
    select(0.0, -2.0 * rotated.y / viewport.rect.w, viewport.rect.w > 0.0));
```

GLSL glyph shader:

```glsl
return vec2(
    viewport.rect.z > 0.0 ? 2.0 * rotated.x / viewport.rect.z : 0.0,
    viewport.rect.w > 0.0 ? 2.0 * rotated.y / viewport.rect.w : 0.0);
```

The y sign differs. This may explain text placement differences depending on shader backend, but must be verified with tests rather than guessed.

### Design Constraints

- This is pre-RC. Breaking Datoviz v0.4 API compatibility is acceptable if the new API is cleaner.
- Do not fix this in GSP_API with a live-size multiplier workaround.
- The correct fix should live in Datoviz.
- The long-term architecture should work for:
  - GLFW live windows;
  - offscreen views;
  - externally hosted/native-surface views;
  - Linux/X11 now, and ideally macOS/Windows/Wayland later;
  - render scale/supersampling separately from device scale;
  - user scale/accessibility separately from device scale;
  - pointer/controller input coordinates in logical pixels;
  - scene layout in logical pixels;
  - physical framebuffer/render target sizing.
- The fix should be testable in CI as much as possible, with live GLFW tests skipped or tolerant when no display/GPU is available.

### Proposed Direction To Review

Adopt a single explicit contract:

1. `DvzFigure.width/height` are always logical pixels.
2. `DvzView.logical_width/height` are always logical pixels.
3. `DvzView.framebuffer_width/height` are always physical render-target pixels.
4. `device_scale` is physical pixels per logical pixel from platform/display.
5. `render_scale` is additional render-target supersampling, not layout scale.
6. `user_scale` scales screen-space styles and UI affordances, not layout geometry.
7. `framebuffer = round(logical * device_scale * render_scale)`.
8. Screen-space style payloads lower from logical pixels to physical pixels using `device_scale * user_scale`, and possibly render target scale only where shader math requires it.
9. Pointer/window/input events exposed to scene/controller APIs use logical pixels.
10. Backend-native physical/window coordinates are converted before reaching scene/controller APIs.

Potential implementation:

- Replace or extend `DvzWindowConfig.width/height` with explicit logical and framebuffer/native extents, or introduce `DvzWindowSizePolicy`.
- For GLFW live windows, create native size from the requested logical size and resolved device scale when the platform does not otherwise create a scaled framebuffer.
- Preserve requested logical size in `DvzView` even if GLFW reports native window size.
- Use platform callbacks to update both logical and framebuffer sizes, but keep them distinct.
- Convert GLFW cursor/wheel/window coordinates to logical coordinates if backend-reported coordinates are physical/native pixels under the chosen policy.
- Add direct unit tests for `_view_desc_resolve()`, `dvz_view_resize_scaled()`, and window scale resolution.
- Add live GLFW smoke/probe tests that report/validate logical/framebuffer/device scale when display/GPU is available.
- Add text glyph realization tests that assert actual `bounds` offsets for anchors `(0,0)`, `(0.5,0.5)`, `(0.5,1.0)`, and `(1,1)` for both bitmap and MSDF text where possible.
- Reconcile WGSL/GLSL glyph y-axis convention with a single documented screen-space coordinate system.

### Requested Output

Please return:

1. **Architecture Verdict**: Is the proposed contract correct? If not, give the corrected contract.
2. **API Break Recommendations**: Exact structs/functions/enums that should change or be added before RC, including names and field meanings.
3. **GLFW Implementation Strategy**: How to create and resize live GLFW windows so logical, framebuffer, and native sizes stay correct across X11/macOS/Windows/Wayland as far as feasible.
4. **Input Coordinate Strategy**: How to convert pointer/wheel/resize events so scene/controllers always receive logical coordinates.
5. **Render/Style Scaling Strategy**: Which scale factors apply to framebuffer allocation, viewport/scissor, point sizes, line widths, text sizes, text offsets, colorbar sizes, and axis/guide reserves.
6. **Text Anchoring Strategy**: How to test and fix retained text anchor semantics, including the WGSL/GLSL y-axis mismatch.
7. **Migration Plan**: Ordered implementation phases with files/modules touched, expected risk, and acceptance criteria.
8. **Regression Test Plan**: Specific tests to add, including skip conditions for live GLFW/GPU/display tests.
9. **Failure Modes**: Things that could go wrong with the proposed fix and how to detect them early.

Keep the answer practical and implementation-oriented. Prefer a design that is internally consistent over compatibility with existing pre-RC behavior.

