# S050 strict opaque depth fixture plan

## Mission

M209 - S050 strict opaque depth fixture plan.

## Goal

Define a minimal fixture that can prove `meshvisual.positions3d.opaque_depth.v1` without relying on
mesh-pick identity, culling, transparency, barycentric payloads, or private backend internals.

## Fixture

Use two fully opaque triangles with the same projected XY footprint and opposite depth gradients.
Both triangles cover the same screen-space sample region. Their average face depths are arranged so a
painter/average-face fallback draws blue last everywhere, while strict per-fragment depth draws red
at a left sample and blue at a right sample.

Canonical NDC3 fixture:

```text
positions:
  r0 = (-0.75, -0.70, -0.80)
  r1 = ( 0.75, -0.70,  0.80)
  r2 = (-0.75,  0.70,  0.80)
  b0 = (-0.75, -0.70,  0.20)
  b1 = ( 0.75, -0.70, -0.60)
  b2 = (-0.75,  0.70, -0.60)

faces:
  red  = (0, 1, 2)
  blue = (3, 4, 5)

colors:
  red  = (230, 57, 70, 255)
  blue = (69, 123, 157, 255)

sample expectations:
  left sample near (-0.55, -0.45)  -> red
  right sample near (0.20, -0.45)  -> blue
```

The same geometry should also be expressed as a DATA-space retained View3D fixture for Datoviz by
using an orthographic `View3D` whose camera maps DATA x/y/z to panel NDC3 without perspective. That
is the promotion fixture for Datoviz because the current strict candidate path is retained DATA-space
View3D mesh rendering.

## Required checks

Protocol-only checks:

- The fixture uses `MeshVisual.positions.shape == (N, 3)` with `CoordinateSpace.NDC` for the pure
  protocol/adapted-reference case and `CoordinateSpace.DATA` plus `View3D` for the Datoviz retained
  runtime case.
- Colors are per-face or duplicated uniform opaque RGBA with alpha exactly 255.
- `depth_test` and `depth_write` are `AUTO` or `ENABLED`; disabled depth is a separate negative
  fixture.
- The fixture does not use culling, non-opaque alpha, transforms, perspective, or picking.

Matplotlib adapted-reference checks:

- Keep Matplotlib classified as adapted for 3D mesh raster output.
- Verify the existing average-face ordering path still draws the painter result, not strict
  per-fragment depth. This can be a non-promotion regression check that proves the fixture actually
  distinguishes adapted behavior from strict behavior.

Datoviz fake-adapter checks:

- Confirm the retained DATA-space View3D path uploads unprojected 3D positions.
- Confirm native depth test/write state is enabled when `depth_test` and `depth_write` are not
  disabled.
- Confirm Datoviz capability advertisements still omit
  `meshvisual.positions3d.opaque_depth.v1` until runtime evidence passes.

Datoviz runtime checks:

- Run a bounded offscreen review case using the DATA-space retained View3D fixture.
- Sample the rendered image at the left and right expected locations.
- Require red at the left sample and blue at the right sample within a documented color tolerance.
- Run a declared-face-order variant, or otherwise show that the result is invariant to face order, so
  the evidence rejects painter-style ordering.

## Promotion criteria

Datoviz may advertise `meshvisual.positions3d.opaque_depth.v1` only after all of these are true:

- The retained View3D DATA-space path is active and uploads the fixture positions as 3D DATA
  coordinates.
- Native depth testing is enabled for the visual.
- Offscreen runtime output passes the two-sample strict-depth expectation.
- A face-order variant proves the result is not declared-order or average-face painter sorting.
- Non-opaque alpha remains rejected or unsupported for this capability.
- Mesh triangle picking remains separately blocked until Datoviz exposes public canonical face or
  triangle identity.

## Non-goals

- Do not define culling semantics.
- Do not define transparent 3D mesh semantics.
- Do not expand mesh-pick query payloads.
- Do not edit the sibling Datoviz repository.
- Do not promote any backend capability as part of this planning mission.
