# ADR-0021 - Physical Canvas Size Policies

## Status

Accepted

## Context

GSP previously used width/height values as if they meant the same thing for Matplotlib figures,
Datoviz windows, framebuffer images, and high-DPI desktop windows. That is false on common systems:
window toolkits may use host logical pixels, GPU surfaces use framebuffer pixels, Matplotlib derives
output pixels from inches and DPI, and users often want a stable apparent physical size.

The old Datoviz `DVZ_WINDOW_SIZE_SCALE` workaround scaled the window extent without defining how
screen-space visual sizes such as marker diameters, stroke widths, guide offsets, and text sizes
should scale.

## Decision

GSP exposes explicit canvas size policies:

- `pixel_exact(width_px, height_px)` for deterministic framebuffer/output pixels.
- `host_logical_px(width, height)` for direct backend/window-system logical units.
- `reference_px(width_px, height_px, reference_dpi=96)` for CSS-like physical sizing.
- `physical_mm(width_mm, height_mm, reference_dpi=96)` for direct physical target sizing.

Backends resolve a `CanvasSize` request into `ResolvedCanvas`, which reports canvas/reference pixels,
host logical size, framebuffer/output size, device scale, framebuffer-per-canvas-pixel scale,
physical target estimates, metric source, and exactness.

Visual protocol fields ending in `_px` are authored in canvas/reference pixels. Backends must lower
those values through `ResolvedCanvas.framebuffer_per_canvas_px` before using native framebuffer or
typographic units.

`reference_dpi` is the user-facing knob for the apparent physical size of a reference pixel.
`user_scale` or style scale remains a visual styling multiplier inside an already resolved canvas; it
must not resize the requested window or canvas.

## Consequences

Offscreen tests and screenshots should use `pixel_exact`. Live review windows should use
`reference_px(..., reference_dpi=96)` unless the caller explicitly wants raw host logical pixels.

Matplotlib figure size is derived from physical target inches and output DPI. Datoviz adapters map
the same request to the Datoviz view-size policy API when available and keep resolved metrics for
debugging/query results.
