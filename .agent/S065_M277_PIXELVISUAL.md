# S065 M277 PixelVisual completion

Date: 2026-07-23

Status: completed and independently accepted.

## Integrated commits

- GSP: `a3a5c79` (`feat: add PixelVisual end to end`)
- VisPy2: `cd14234` (`feat: add 2D and 3D pixel producers`)

## Result

- `PixelVisual` defines finite 2D/3D positions, uniform or per-item RGBA colors, and strictly
  positive uniform or per-item logical-pixel square widths.
- Scene validation requires View2D for 2D DATA positions and View3D for 3D DATA positions, and
  rejects 3D NDC positions.
- Matplotlib renders deterministic square pixels in 2D and a documented projected-square
  adaptation in 3D without claiming analytic depth.
- The Datoviz adapter uses public `dvz_pixel` position, color, and `pixel_size_px` attributes,
  scales logical sizes exactly once, preserves 3D DATA attachments, and explicitly rejects
  unsupported view and transform combinations.
- Datoviz PixelVisual capabilities are advertised only when a callable public `dvz_pixel` symbol
  is present. No raw item-state flag or backend handle entered the protocol.
- VisPy2 exposes module-level, `Axes`, and `Axes3D` pixel producers with camera fitting and a
  documented installed-wheel example.

## Validation

- GSP: 480 tests passed.
- VisPy2: 26 tests passed.
- Strict mypy passed for 51 GSP and 11 VisPy2 source/test/example files.
- Ruff lint and diff checks passed.
- All four wheels built and installed together under Python 3.13.
- The installed-wheel Agg example generated inspected 640x480 2D and 3D PNG artifacts.
- Independent supervisor review accepted the corrected final diff with no blockers.

## Deferred checkpoint

Native Datoviz capture was not claimed. Public-binding and lowering behavior are covered by
executable tests; genuine GUI-capable native runtime and depth qualification remain assigned to
M284.

M278 SphereVisual is approved next.
