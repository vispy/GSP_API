# S065 M278 SphereVisual completion

Date: 2026-07-23

Status: completed and independently accepted.

## Integrated commits

- GSP implementation: `cf5040c` (`feat: add SphereVisual end to end`)
- GSP Mission Control specification correction: `0ef885e`
  (`docs: register SphereVisual contract`)
- VisPy2: `6520cbe` (`feat: add 3D sphere producer and examples`)

The GSP specification update is a separate Mission Control commit because the external M278 worker
held `packages` and `conformance` locks, not a `specs` lock.

## Result

- `SphereVisual` defines finite `(N, 3)` DATA positions, positive scalar or per-item DATA radii,
  and uniform or per-item RGBA colors.
- Scene validation requires `View3D`.
- Datoviz uses public `dvz_sphere`, mandatory `DVZ_SPHERE_MODE_RAYCAST_IMPOSTOR`, dense
  position/color/radius uploads, and DATA attachment. Missing symbols, null allocation, and setter
  failures produce structured diagnostics; there is no enum fallback.
- Matplotlib renders deterministic projected circles in far-to-near center-depth order. Its
  perspective view-plane-radius projection is explicitly an adaptation and does not advertise
  analytic sphere-surface depth.
- VisPy2 exposes `Axes3D.spheres(...)`, radius-aware camera fitting, documentation, and perspective
  and orthographic examples.
- Capability registries and executable conformance cover the semantic and analytic-depth boundary.

## Validation

- GSP source and installed-wheel suites: 506 tests passed.
- VisPy2 source and installed-wheel suites: 30 tests passed.
- Strict mypy passed for 51 GSP and 13 VisPy2 source/test/example files.
- Ruff lint and `git diff --check` passed.
- Four Hatchling wheels built and installed together under Python 3.13.4.
- The installed-wheel Matplotlib example generated both projection PNGs; both were visually
  inspected.
- Independent supervisor review accepted the corrected implementation with no software blocker.

## Deferred checkpoint

The real Datoviz binding constructed and rendered the sphere scene, but `capture_png_bytes()`
aborted with exit code 134 in both the plain and prescribed `direnv` Vulkan environments. No native
Datoviz PNG was produced. Native analytic-depth visual qualification remains assigned to M284 and
must not be claimed by M278.

M279 VectorVisual is approved next.
