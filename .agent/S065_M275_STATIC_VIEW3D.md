# M275 static View3D closeout

Date: 2026-07-23

M275 added the first complete VisPy2 static 3D producer journey while reusing the accepted GSP
camera, projection, and navigation reducers.

| Evidence | Result |
|---|---|
| Worker run | `R20260723-105843-M275` with `codex-ucl` |
| GSP worker/integrated commits | `196a50d` / `c39b046` |
| VisPy2 worker/integrated commits | `f51eebf` / `60077e8` |
| GSP full suite | 455 passed |
| VisPy2 full suite | 23 passed |
| Typing and lint | strict mypy and Ruff passed |
| Packages | four wheels built and installed together |
| Installed-wheel Matplotlib | perspective and orthographic PNGs passed |
| Installed-wheel Datoviz | capability discovery and retained lowering passed for both projections |

VisPy2 now exposes typed 2D/3D subplot overloads, `Axes3D`, semantic camera and projection
getters/setters, reducer-backed orbit/pan/zoom/reset, deterministic perspective and orthographic
camera fitting, DATA-space mesh emission, titles, attachments, and immutable GSP scene emission.
Numeric tests cover revision changes, reset, limiting field of view, reversed and degenerate
orthographic bounds, invalid inputs, and direct containment of every bounds corner.

Mission Control corrected the worker's initial core scene invariant so valid viewless NDC scenes
remain accepted; only simultaneous `view2d` and `view3d` are rejected. `Figure.to_scene()` retains
the narrower exactly-one-axes producer boundary.

The final example uses distinct semantic face colors so projection and depth ordering are visible
in the reference images. An independent reviewer accepted the implementation after checking fit
math with additional asymmetric bounds and rotated cameras.

## Environment-limited Datoviz capture

Native Datoviz PNG capture hung in this macOS session. The same hang reproduced in Datoviz's own
raw offscreen point example, below GSP and VisPy2. Installed-wheel capability discovery and
retained scene lowering succeeded for both projections, so this is recorded as an environment
waiver rather than a code failure. M276 must keep live capability advertisement conservative and
M284 must include native capture on a working Datoviz runtime before owner acceptance.
