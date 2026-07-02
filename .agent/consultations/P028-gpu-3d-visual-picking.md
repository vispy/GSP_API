# P028 - GPU 3D Visual Picking Semantics

## Purpose

This needs ChatGPT Pro consultation.

GSP_API needs a bounded public protocol design for GPU 3D visual picking/readback. The design must
be distinct from the existing `query.view3d.ray_readback.v1` ray-context payload and must be safe to
implement first in the Datoviz v0.4 backend without leaking Datoviz-native implementation details.

Implementation depending on this decision should pause until the consultation result is pasted or
committed.

## Prompt

You are reviewing an architecture/API decision for `GSP_API`, a Python visualization protocol/library
with Matplotlib and Datoviz v0.4 backends plus a VisPy2-style producer API.

The goal is to define the smallest correct public protocol slice for GPU 3D visual picking. Answer
as a protocol/API architect, not as code generation. The expected output format is at the end.

### Project Authority and Constraints

Authority order in this repo is:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

Existing code is implementation material, not automatically authoritative. If legacy code conflicts
with accepted specs, specs win.

The public protocol is backend-neutral. It must not expose backend-native Datoviz shader names,
Vulkan draw-state, framebuffer attachment names, controller objects, Matplotlib artists/axes, raw
GLFW events, Datoviz object ids, or pipeline internals as public API.

Local repositories:

- GSP_API: `/home/cyrille/GIT/Viz/GSP_API`
- Datoviz: `/home/cyrille/GIT/Viz/datoviz`

Do not assume Datoviz v0.4-dev API compatibility is sacred. The user allows breaking Datoviz
v0.4-dev API compatibility for better long-term architecture, but GSP public API must stay
backend-independent.

### Accepted Current State

GSP has a bounded public 3D baseline:

- `Camera3D(eye, target, up)`.
- `OrthographicProjection3D(xlim, ylim, near_far)`.
- `View3D(id, panel_id, camera, projection, depth_mode=opaque_less, revision=...)`.
- Orthographic projection only.
- `MeshVisual.positions` accepts `(N, 2)` and `(N, 3)`.
- `(N, 3)` plus `CoordinateSpace.DATA` projects through `View3D`.
- `(N, 3)` plus `CoordinateSpace.NDC` is interpreted as panel NDC3 directly.
- Existing 2D affine transforms do not apply to `(N, 3)` mesh geometry.
- `View3DProjectionSnapshot` provides deterministic projection snapshot ids.
- `View3DNavigationAction` provides canonical orbit/pan/zoom/set/reset actions.
- Datoviz live View3D navigation is supported only when retained DATA-space View3D symbols and live
  input bindings are present.

Current query/readback state:

- `query.view3d.ray_readback.v1` returns a canonical ray-context payload from public `View3D` state:
  panel xy, panel NDC xy, near/far DATA points, ray direction, view id, view revision,
  layout snapshot id, and view/projection snapshot id.
- This payload does not identify a visual, face, primitive, vertex, or depth hit.
- GPU 3D visual picking remains deferred.

Current rendering state:

- Matplotlib is the publication/reference backend. Its 3D mesh rendering is adapted: vertices are
  CPU-projected to 2D faces and sorted for bounded opaque cases. It is not a native GPU picker.
- Datoviz v0.4-dev is intended as the flagship high-performance GPU backend. It can render retained
  DATA-space 3D meshes with panel-owned camera/projection state on local builds with the accepted
  P022/S043 bindings.
- Datoviz can update retained View3D camera/projection state during live navigation without
  reuploading unchanged mesh buffers.
- Datoviz supports CPU-resolved flat Lambert face colors for strict S039/S040 lighting semantics;
  native Datoviz lighting/material names are not public GSP semantics.

Accepted capability names include:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
view3d.navigation.orbit_pan_zoom.v1
meshvisual.material.unlit_rgba.v1
meshvisual.material.flat_lambert.v1
```

Possible new capability names are open for review. Examples could include:

```text
query.view3d.visual_pick.v1
query.meshvisual.face_pick.v1
query.view3d.gpu_pick.v1
```

These examples are not accepted names.

### Candidate S044 Scope

Define the smallest useful picking slice. Candidate boundaries:

1. Only opaque DATA-space `MeshVisual` triangles in orthographic `View3D`.
2. Only frontmost visible hit under the current depth mode.
3. Return public `visual_id`, optional public item/face/primitive index, hit status, query point,
   snapshot/revision ids, and diagnostics.
4. Defer sub-triangle barycentric coordinates unless they are necessary for correctness.
5. Defer transparent mesh picking, point/marker/path picking, instancing, perspective projection,
   culling semantics, textures, native material ids, and multi-hit selection.
6. Older Matplotlib/Datoviz builds may return structured unsupported/adapted diagnostics.

### Questions To Answer

1. Should S044 accept a minimal GPU 3D visual picking protocol now, or defer it?
2. If accepted, what is the smallest public query payload?
3. Should the first strict payload identify only the visual, or also face/triangle/primitive index?
4. Should barycentric coordinates, interpolated DATA position, depth value, or world-space hit point
   be included now or deferred?
5. What snapshot/revision freshness evidence is required?
6. What are the required occlusion/depth semantics for "frontmost visible hit"?
7. How should Matplotlib behave: adapted CPU reference, unsupported, or limited reference oracle?
8. What capability names and diagnostics should GSP use?
9. What exact stop conditions should prevent Datoviz implementation from claiming support?
10. What should remain explicitly out of scope?

### Expected Output Format

Please answer in this exact structure:

```text
Decision:
- Accept / Defer / Accept with changes

Accepted minimal scope:
- ...

Public query payload:
- field: type, meaning, required/optional

Capability names:
- ...

Strict semantics:
- ...

Backend behavior:
- Matplotlib:
- Datoviz:
- Older/unsupported builds:

Deferred:
- ...

Stop conditions:
- ...

Tests/fixtures required:
- ...

ADR/spec changes:
- ...
```
