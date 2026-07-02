# S046 Scoping - 3D Code Examples Pack

## Goal

Add a focused pack of public 3D examples that demonstrates accepted S036-S044 behavior without
changing protocol semantics.

## Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M195 | ready | Add mesh-pick, asset-like Lambert mesh, and camera-path View3D review examples. |

## Scope

- Use existing `examples/review` conventions and `tools/compare-review-examples`.
- Prefer protocol-level examples unless current VisPy2 helpers already expose the needed 3D surface.
- Demonstrate S044 mesh triangle picking through the Matplotlib CPU oracle only.
- Include docs that make Datoviz structured unsupported behavior explicit.

## Out Of Scope

- Public perspective projection.
- Textures, UVs, smooth/Phong lighting, public material objects, or normal maps.
- Strict opaque GPU depth claims.
- Datoviz `query.view3d.mesh_triangle_pick.v1` advertisement.
- Sibling Datoviz repository edits.
