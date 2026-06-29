# Canvas Size Policies

Status: accepted S035 baseline.

GSP distinguishes four size spaces:

- **Canvas/reference pixels**: semantic screen units used by visual `_px` fields.
- **Host logical pixels**: window-system units accepted by a toolkit or OS.
- **Framebuffer/output pixels**: actual raster pixels used by GPU surfaces and image exports.
- **Physical units**: approximate display millimetres or deterministic export inches.

## Public Policies

`CanvasSize.pixel_exact(width_px, height_px)` requests deterministic framebuffer/output dimensions.
Use this for tests, CI, screenshots, and offscreen image comparison.

`CanvasSize.host_logical_px(width, height)` requests backend/window-system logical dimensions
directly. Use this only when the caller deliberately wants platform-native window units.

`CanvasSize.reference_px(width_px, height_px, reference_dpi=96)` requests CSS-like reference pixels.
The physical target is `width_px / reference_dpi` by `height_px / reference_dpi` inches.

`CanvasSize.physical_mm(width_mm, height_mm, reference_dpi=96)` requests a direct physical target.
The canvas/reference extent is derived from the physical size and `reference_dpi`.

## Resolved Contract

Backends resolve a request to `ResolvedCanvas` with:

- `canvas_width_px`, `canvas_height_px`;
- `host_logical_width`, `host_logical_height`;
- `framebuffer_width`, `framebuffer_height`;
- `device_scale_x`, `device_scale_y`;
- `canvas_to_host_scale_x`, `canvas_to_host_scale_y`;
- `framebuffer_per_canvas_px_x`, `framebuffer_per_canvas_px_y`;
- target and estimated physical dimensions;
- `output_dpi`, metric source, exactness, strictness, and warnings.

## Screen-Space Visuals

Visual fields ending in `_px` are authored in canvas/reference pixels. They are not raw framebuffer
pixels and not host logical pixels. Backends must scale marker diameters, text sizes, stroke widths,
guide offsets, and similar screen-space attributes through the resolved
`framebuffer_per_canvas_px`.

For Matplotlib point/text units:

```text
points = canvas_px * framebuffer_per_canvas_px * 72 / output_dpi
```

For deterministic `pixel_exact` output, `framebuffer_per_canvas_px` is `1`. For
`reference_px(..., reference_dpi=96)` rendered at `output_dpi=144`, it is `1.5`.

## User Knobs

`reference_dpi` controls how physically large a reference pixel is. Lower values make a given
reference-pixel canvas physically larger; higher values make it physically smaller.

`user_scale` or style scale is a visual styling multiplier after canvas resolution. It scales
markers, text, strokes, and offsets, but it does not resize the window, framebuffer, or physical
canvas target.
