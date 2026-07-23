# S065 M276 safe camera completion

Date: 2026-07-23

Status: completed and independently accepted.

## Integrated commits

- GSP: `42ac325` (`fix: complete safe View3D camera lifecycle`)
- VisPy2: `0dce6d6` (`docs: add programmatic View3D camera example`)

## Result

- Datoviz View3D navigation callbacks are unsubscribed exactly once before app and scene
  destruction; repeated close is idempotent.
- Interactive View3D session plumbing is enabled exactly once only when the session capability
  snapshot already advertises `view3d.navigation.orbit_pan_zoom.v1`.
- Static and offscreen rendering never enables View3D navigation, including when that capability
  is present in a synthetic session snapshot.
- Twenty-five mesh-backed synthetic cycles exercise orbit, pan, zoom, reset, and close without
  vertex uploads, index uploads, or visual rebuilds after initial construction.
- Matplotlib deterministically rerenders successive canonical camera states.
- VisPy2 includes a programmatic camera example with explicit caller-owned session lifecycle.

## Validation

- GSP: 458 tests passed.
- VisPy2: 23 tests passed.
- Strict mypy passed for all GSP and VisPy2 source, tests, and examples.
- Ruff lint passed.
- All four wheels built and installed together under Python 3.13.
- The installed-wheel Matplotlib example generated five camera-state PNGs.
- Independent supervisor review accepted the final diff; its focused selection passed four tests.

## Deferred checkpoint

The earlier native probe aborted during macOS GLFW/Cocoa application registration before camera
or callback code ran. This does not prove a Datoviz defect. M284 owns genuine GUI-capable,
timeout-bounded native lifecycle and human interaction qualification. Until then, the live
Datoviz View3D navigation capability remains unadvertised.

M277 PixelVisual is approved next.
