# ADR-0023 - Static View3D Orthographic Baseline

## Status

Accepted

## Context

GSP has accepted 2D transform, `View2D`, query inverse, mesh, and retained `View2D` navigation
semantics. `MeshVisual` already permits positions shaped `(N, 3)`, but public 3D camera,
projection, depth, and query semantics were deferred to avoid freezing a backend-specific graphics
engine object model.

P020 resolved the S036 scope: make `(N, 3)` mesh data useful through the smallest strict public 3D
surface, while preserving GSP's semantic protocol model, capability gating, and render/query
coherence.

## Decision

S036 accepts a static, orthographic-only `View3D` baseline:

- Public camera state is parameter-first: `Camera3D(eye, target, up)`.
- Public projection state is `OrthographicProjection3D(xlim, ylim, near_far)`.
- Public authoring does not accept arbitrary view/projection matrices in S036.
- `View3D` targets one panel and carries a retained semantic revision.
- `CoordinateSpace.DATA` and `CoordinateSpace.NDC` remain the only public visual coordinate spaces.
- `(N, 3)` DATA `MeshVisual` positions are interpreted in the panel's `View3D` data coordinate
  system and projected through the accepted camera/projection.
- `(N, 3)` NDC `MeshVisual` positions are interpreted as panel NDC x/y plus GSP NDC depth.
- The only strict S036 depth mode is opaque nearer-fragment-wins (`opaque_less`) where capability is
  advertised.
- S036 defines projection/ray query readback but keeps 3D visual hit/picking unsupported with
  structured diagnostics.

S036 explicitly defers:

- public `View3DNavigationController`;
- perspective projection;
- matrix-first authoring;
- public materials, lights, normals, scene graph, model transforms, instancing, external model
  loading, transparency sorting, strict clipping of partially clipped triangles, and 3D picking;
- non-mesh 3D visual families.

## Camera and Projection Convention

Camera basis:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

The canonical camera:

```text
eye    = (0, 0, 1)
target = (0, 0, 0)
up     = (0, 1, 0)
```

derives:

```text
forward = (0, 0, -1)
right   = (1, 0, 0)
true_up = (0, 1, 0)
```

Panel NDC convention:

```text
x: -1 left, +1 right
y: -1 bottom, +1 top
z: -1 near, +1 far
smaller z is closer
```

Projection for DATA point `p`:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)

ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])
ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

Reversed `xlim` and `ylim` are valid, matching `View2D` precedent. Reversed `near_far` is invalid.

## Consequences

Workers can implement a useful static 3D slice without importing Matplotlib, Datoviz, VisPy, Qt,
browser, OpenGL, WebGPU, or game-engine object models into public protocol semantics.

Matplotlib can remain strict for validation, projection math, and ray readback even if 3D raster
output is adapted. Datoviz can become the first meaningful runtime 3D backend, but only through
capability-gated retained state that does not expose Datoviz-native camera, material, slot, or
draw-state names.

Public 3D navigation should be considered later only after static `View3D` projection, mesh, depth,
query, and examples are proven.

