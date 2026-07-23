# S065 M280 PrimitiveVisual completion

Date: 2026-07-23

Status: completed and independently accepted.

## Integrated commits

- GSP implementation: `030d4e1` (`feat: add bounded PrimitiveVisual end to end`)
- GSP Mission Control specification correction: `dafc463`
  (`docs: register PrimitiveVisual contract`)
- VisPy2: `8051542` (`feat: add bounded primitive producers and gallery`)

The GSP specification update is separate because the external worker did not hold a `specs` lock.

## Result

- `PrimitiveVisual` supports point list, line list, line strip, triangle list, and triangle strip,
  indexed or unindexed.
- Validation uses the effective index stream and enforces exact topology cardinality, finite integer
  non-negative indices strictly below the vertex count, finite 2D/3D positions, colors, and
  View2D/View3D requirements.
- Datoviz uses strict public primitive construction, exact topology enums, dense attribute upload,
  and optional public index upload. Base/topology and indexed capability readiness are independent.
- Matplotlib deterministically adapts points, lines, and triangles; documented per-vertex color,
  projected-3D, painter-depth, and rasterization limitations remain explicit.
- VisPy2 exposes bounded `primitives()` producers for 2D, 3D, and module-level use without shader,
  pipeline, material, texture, normal, culling, depth, instance, or native-handle escape hatches.

## Validation

- GSP source and installed-wheel suites: 644 tests passed.
- VisPy2 source and installed-wheel suites: 53 tests passed.
- Strict mypy passed for 51 GSP and 17 VisPy2 source/test/example files.
- Ruff and `git diff --check` passed.
- Four fresh Hatchling wheels built and installed together under CPython 3.13.4.
- Installed-wheel Matplotlib gallery rendered all five topologies and was visually inspected.
- Real Datoviz no-capture construction retained all five topologies successfully.
- Independent supervisor review accepted without blockers.

## Deferred checkpoint

Native Datoviz capture remains assigned to M284 and is not claimed by M280.

M281 text hardening and 3D billboards is approved next.
