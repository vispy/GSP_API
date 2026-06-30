# ADR-0027 - Datoviz Flat Lambert CPU Resolve

## Status

Accepted

## Context

S039 accepted a narrow flat Lambert material model for opaque DATA-space 3D triangle meshes:
face normals only, scalar ambient light, one optional DATA-space directional light, exact scalar
Lambert RGB arithmetic, and alpha passthrough. Matplotlib already resolves the S039 material math on
the CPU as a reference/adapted rendering path.

Datoviz v0.4 currently rejects `MeshVisual.shading="flat_lambert"` with
`flat_lambert_unsupported` and does not advertise `meshvisual.material.flat_lambert.v1`.

P025 reviewed whether Datoviz should promote strict S039 support through CPU-resolved colors, native
Datoviz lighting, a hybrid route, or continued unsupported behavior.

## Decision

Datoviz S039 flat Lambert support, if promoted, must use CPU-resolved exact per-face colors.

The Datoviz adapter may claim strict S039 support only when it:

- validates the public payload with the accepted S039 protocol validation path;
- resolves explicit or generated face normals through protocol code before Datoviz upload;
- computes S039 Lambert RGBA values in backend-neutral adapter code;
- uploads an unlit Datoviz mesh payload that preserves one constant color per canonical face;
- preserves existing strict View3D DATA-space orthographic and opaque-depth prerequisites;
- keeps native Datoviz lighting and material controls disabled, unused, or proven inert;
- retains `mesh3d_alpha_not_strict` for non-opaque 3D mesh alpha;
- advertises capabilities only after fixture-backed positive and negative coverage.

The preferred upload shape is triangle expansion: each canonical triangle contributes three
uploaded vertices and each of those vertices receives the same resolved RGBA value. This prevents
Datoviz vertex-color interpolation from changing S039 face-level colors.

Native Datoviz lighting and material APIs are out of scope for S040 strict support. Their existence
is not semantic evidence for GSP S039 parity.

## Capability Boundary

Datoviz may advertise these S039 capabilities only after the CPU-resolved route and prerequisites are
fixture-backed:

```text
meshvisual.material.flat_lambert.v1
meshvisual.normals.face3d.v1
meshvisual.normal_generation.face_flat.v1
view3d.light.ambient.v1
view3d.light.directional.v1
```

Prerequisites remain:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
meshvisual.material.unlit_rgba.v1
```

Datoviz native lighting/material capability names are not public GSP capabilities in S040.

## Diagnostics

S040 accepts these Datoviz-specific diagnostic boundaries:

| Diagnostic | Trigger |
|---|---|
| `flat_lambert_cpu_resolved_strict` | Datoviz accepts S039 via CPU-resolved protocol face colors. |
| `flat_lambert_native_lighting_unsupported` | A native Datoviz lighting/material route is requested or probed as strict S039 evidence. |
| `flat_lambert_unsupported` | CPU-resolved support or required View3D/depth prerequisites are unavailable or not fixture-backed. |
| `mesh3d_alpha_not_strict` | A Datoviz 3D mesh uses non-opaque alpha. |
| `flat_lambert_upload_not_constant_face_color` | The adapter cannot guarantee constant resolved RGBA for every triangle face. |

Existing S039 protocol diagnostics still cover invalid normals, generated normals, lights,
positions, coordinate spaces, and missing `View3D`.

## Consequences

CPU-resolved material semantics may satisfy a material capability when the accepted protocol defines
deterministic output colors rather than requiring a live backend lighting engine.

The implementation may duplicate vertices for strict face-color preservation. This is acceptable for
S040 because the feature is narrow, deterministic, and capability-gated.

Native Datoviz lighting remains a possible future route only after API probes and fixtures prove
exact semantic parity with GSP S039.

## Source

`.agent/consultations/P025-response.md` converted into this ADR and
`.agent/decisions/S040_datoviz_flat_lambert_promotion.md`.
