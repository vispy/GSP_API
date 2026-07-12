# Protocol specification

The specifications are the normative GSP contracts. Generated API pages describe Python objects;
they do not replace protocol semantics, validation rules, or backend capability requirements.

## Core model

- [Protocol and session model](https://github.com/vispy/GSP_API/blob/main/spec/protocol.md)
- [Resources and buffers](https://github.com/vispy/GSP_API/blob/main/spec/resources.md)
- [Physical canvas sizing](https://github.com/vispy/GSP_API/blob/main/spec/canvas_size.md)
- [Transforms](https://github.com/vispy/GSP_API/blob/main/spec/transforms.md)
- [Resolved layout](https://github.com/vispy/GSP_API/blob/main/spec/layout.md)
- [Capabilities and adaptation](https://github.com/vispy/GSP_API/blob/main/spec/capabilities.md)

## Views and interaction

- [View2D navigation](https://github.com/vispy/GSP_API/blob/main/spec/navigation.md)
- [Static View3D](https://github.com/vispy/GSP_API/blob/main/spec/view3d.md)
- [View3D navigation](https://github.com/vispy/GSP_API/blob/main/spec/view3d_navigation.md)
- [Query and readback](https://github.com/vispy/GSP_API/blob/main/spec/query.md)
- [View3D mesh picking](https://github.com/vispy/GSP_API/blob/main/spec/view3d_mesh_triangle_picking.md)
- [Mesh-pick geometry payload](https://github.com/vispy/GSP_API/blob/main/spec/view3d_mesh_triangle_pick_geometry.md)

## Visuals

- [Visual families](https://github.com/vispy/GSP_API/blob/main/spec/visual_families_v1.md)
- [Cross-cutting visual rules](https://github.com/vispy/GSP_API/blob/main/spec/visual_cross_cutting_rules.md)
- [Point](https://github.com/vispy/GSP_API/blob/main/spec/visuals/point.md),
  [marker](https://github.com/vispy/GSP_API/blob/main/spec/visuals/marker.md),
  [segment](https://github.com/vispy/GSP_API/blob/main/spec/visuals/segment.md),
  [path](https://github.com/vispy/GSP_API/blob/main/spec/visuals/path.md),
  [image](https://github.com/vispy/GSP_API/blob/main/spec/visuals/image.md),
  [text](https://github.com/vispy/GSP_API/blob/main/spec/visuals/text.md), and
  [mesh](https://github.com/vispy/GSP_API/blob/main/spec/visuals/mesh.md)
- [Color mapping and colorbars](https://github.com/vispy/GSP_API/blob/main/spec/color_mapping.md)
- [Mesh materials](https://github.com/vispy/GSP_API/blob/main/spec/visuals/mesh_materials_s038.md)
- [Flat Lambert shading](https://github.com/vispy/GSP_API/blob/main/spec/visuals/mesh_flat_lambert_s039.md)
- [Texture2D unlit material](https://github.com/vispy/GSP_API/blob/main/spec/visuals/mesh_texture2d_unlit_s050.md)
- [Face culling and alpha boundary](https://github.com/vispy/GSP_API/blob/main/spec/visuals/mesh_face_culling_alpha_s050.md)

## Backend support

Matplotlib is the reference backend. Datoviz v0.4 support is capability-gated: an implementation
advertises a row only after the required runtime evidence exists. The legacy `datoviz-v03`
renderer is a separate optional path.

- [Backend capability matrix](https://github.com/vispy/GSP_API/blob/main/spec/backend_capabilities_visuals.md)
- [Matplotlib contract](https://github.com/vispy/GSP_API/blob/main/spec/backends/matplotlib.md)
- [Datoviz contract](https://github.com/vispy/GSP_API/blob/main/spec/backends/datoviz.md)
- [Datoviz v0.4 API boundary](https://github.com/vispy/GSP_API/blob/main/spec/datoviz_v04_api_boundary.md)
- [Complete specification index](https://github.com/vispy/GSP_API/blob/main/SPEC_INDEX.md)
