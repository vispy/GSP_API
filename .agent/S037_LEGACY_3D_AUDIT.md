# S037 Legacy 3D Audit

Status: non-public implementation audit, pending P021 decision.

## Executive Summary

Legacy 3D code is useful as implementation material, especially for Matplotlib adapted rendering.
It should not be treated as public protocol authority.

Recommended split:

| Area | Reuse now? | Reason |
|---|---:|---|
| Projection/depth/culling helpers | yes, internal only | Matches current S036 adapted mesh rendering needs. |
| Face normal computation | yes, internal only | Pure geometry helper; useful for future shaded examples. |
| Flat Phong math | maybe, after P021 | Small and testable, but depends on unaccepted light/material schema. |
| Textured triangle warp | maybe, after separate texture spec | Matplotlib-specific and expensive; implies UV/texture resource semantics. |
| Legacy `Camera` class | no | Matrix-first public model conflicts with S036 camera-parameter-first authority. |
| Legacy material/light classes | no public reuse | They encode old object model and ownership conventions. |

## Current S036 Landing Points

Current protocol renderer locations:

- `src/gsp_matplotlib/protocol_renderer.py::_render_mesh3d_positions`
  projects `(N, 3)` `MeshVisual` vertices through `View3D` or interprets NDC3 directly.
- `src/gsp_matplotlib/protocol_renderer.py::_mesh3d_face_depth_order`
  sorts faces by average panel-NDC z with stable far-to-near ordering.
- `src/gsp_matplotlib/protocol_renderer.py::_validate_mesh3d_opaque_colors`
  rejects translucent colors from the adapted 3D depth path.

The safest first extraction, if P021 accepts it, is an internal helper module for:

- panel-NDC face depth;
- projected 2D winding/culling;
- per-face normal calculation;
- per-face attribute broadcasting.

That extraction can be tested without changing public protocol objects.

## Reusable Legacy Techniques

### MVP Projection

`src/gsp_matplotlib/renderer/matplotlib_renderer_mesh.py` resolves legacy geometry buffers,
model/view/projection matrices, computes an MVP matrix, applies homogeneous projection, and derives:

- `faces_vertices_ndc`;
- `faces_vertices_2d`;
- `vertices_view_numpy`;
- `vertices_world_numpy`;
- `camera_position_world`.

This is useful as a reference pattern, but S036 already provides canonical projection through
`View3D` helpers, not through public matrices.

### Face Depth Sorting

`src/gsp_matplotlib/utils/renderer_utils.py::compute_face_depths_ndc` computes average NDC z per
face. Legacy renderers sort with `np.argsort(-faces_depth)`, consistent with S036's smaller-z-is-
closer convention and the current `_mesh3d_face_depth_order` adapted path.

This can become a shared internal helper if we want to remove duplication between current protocol
rendering and any future material-specific path.

### Screen-Space Face Culling

`RendererUtils.compute_faces_visible()` computes 2D triangle winding after projection:

- positive cross product: front side;
- negative cross product: back side;
- near-zero area: degenerate.

This is a reasonable adapted-renderer technique. It should be represented as backend behavior, not
as strict 3D raster semantics, because clipping and perspective edge cases are not yet specified.

### Normals

`RendererUtils._compute_face_normals()` computes per-face unit normals using a triangle cross
product. The current code exposes view-space and world-space wrappers.

This is safe internal geometry math. Public normal attributes and normal-space semantics remain
deferred by `spec/view3d.md`.

### Depth Material

`matplotlib_renderer_mesh_depth.py` maps view-space depth to grayscale by recovering near/far from a
legacy OpenGL-style projection matrix. This exact recovery is not compatible with S036 public
orthographic `View3D` as-is, because S036 does not expose projection matrices as authoring input.

Reusable part: the idea of deterministic depth-color fixtures.

Do not reuse directly: near/far recovery from matrix entries.

### Normal Material

`matplotlib_renderer_mesh_normal.py` maps view-space normals to RGB by `n * 0.5 + 0.5`.

Reusable part: a future debug/example material can use this exact mapping if P021 or a later spec
accepts normal visualization.

Do not claim it as a public `MeshVisual` feature until normal semantics are specified.

### Flat Phong

`matplotlib_renderer_mesh_phong.py` computes flat per-face Lambert plus Phong-style specular terms:

- diffuse/specular colors are broadcast per face;
- ambient lights add a diffuse base;
- directional and point lights create face-to-light directions;
- view direction uses camera position and face centroid;
- all output is clipped to `[0, 1]`.

Reusable part: pure `shade_faces_flat()` math can be ported into a private helper after a light
schema decision.

Risk: legacy lights live on materials, light positions are model-space, and unknown light types are
silently skipped. Those are public semantics decisions and should not be inherited accidentally.

### Textured Triangles

`matplotlib_renderer_mesh_textured.py` creates one `AxesImage` per triangle, crops a UV texture
region, multiplies it by per-face lighting, maps UV triangle coordinates to projected screen-space
triangle coordinates with an affine transform, and clips the image to the UV triangle path.

Reusable part: the Matplotlib affine-warp technique is useful for adapted textured examples.

Risks:

- one artist per triangle will not scale;
- UV wrapping/filtering/mip behavior is unspecified;
- texture resources and image orientation are public API decisions;
- clipping is adapted, not strict GPU rasterization.

## Non-Reusable Public Models

### Legacy Camera

`src/gsp/core/camera.py` stores arbitrary `view_matrix` and `projection_matrix`. S036 explicitly
uses camera-parameter-first public state: `eye`, `target`, `up`, and orthographic bounds.

Do not expose legacy `Camera` in the protocol. Derived matrices may remain diagnostics/snapshots
only if accepted.

### Legacy Material And Light Classes

Legacy material and light classes encode:

- material subclasses as public object types;
- lights attached to materials;
- model-space light positions;
- texture objects with raw RGBA buffers;
- face sorting/culling flags per material.

These are not current protocol authority. They may inform a later minimal schema, but only after
P021 or a separate material/light/texture consultation accepts that scope.

## Recommended M163 Implementation Shape

If P021 accepts internal helper extraction before public material/light work:

1. Add a private Matplotlib helper module, for example
   `src/gsp_matplotlib/_mesh3d_adapted.py`.
2. Move current adapted math into small functions:
   `face_depth_order_ndc()`, `face_normals()`, `projected_faces_visible()`.
3. Keep inputs as numpy arrays and current protocol enums only.
4. Add focused tests using current S036 fixtures.
5. Do not import legacy `gsp.core.camera`, `gsp.materials`, `gsp.lights`, or `gsp.visuals.mesh`.

## Recommended Deferrals

Keep these deferred unless P021 explicitly accepts them:

- public material or light protocol objects;
- textured mesh protocol;
- perspective projection;
- strict 3D clipping;
- strict 3D picking;
- backend-native camera/controller exposure;
- scene graph or model loader API.
