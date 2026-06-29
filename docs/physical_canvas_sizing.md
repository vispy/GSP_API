# Physical Canvas Sizing

GSP separates the size a user asks for from the size a backend must allocate.

## Policies

- `CanvasSize.pixel_exact(width_px, height_px)` is for deterministic PNGs, CI, and visual
  comparison. The framebuffer/output size is exact.
- `CanvasSize.reference_px(width_px, height_px, reference_dpi=96)` is for live review and physical
  comparability. A `1280x720` canvas targets `1280 / 96` by `720 / 96` inches.
- `CanvasSize.host_logical_px(width, height)` is the explicit low-level window-system unit.
- `CanvasSize.physical_mm(width_mm, height_mm, reference_dpi=96)` targets physical millimetres
  directly.

`reference_dpi` is the user knob for apparent physical size. Lower values make the same reference-px
canvas larger; higher values make it smaller.

## Visual Pixel Units

Protocol fields ending in `_px` are canvas/reference pixels. Backends convert them through
`ResolvedCanvas.framebuffer_per_canvas_px`.

For Matplotlib:

```text
points = canvas_px * framebuffer_per_canvas_px * 72 / output_dpi
```

For Datoviz, marker diameters, text sizes, and stroke widths are multiplied by the resolved
framebuffer-per-canvas scale before upload.

## Style Scale

`user_scale` or style scale is not a window-size control. It is applied after canvas size resolution
to make markers, labels, strokes, and offsets visually larger or smaller inside the same canvas.

## Migration

Do not use `DVZ_WINDOW_SIZE_SCALE`. It enlarged Datoviz windows without defining canvas/reference
pixels or scaling `_px` visual attributes coherently.

Use `CanvasSize.reference_px(..., reference_dpi=...)` for live windows with comparable apparent
physical size across platforms. Use `CanvasSize.pixel_exact(...)` for deterministic captures.
