# Normative registries

This chapter assigns stable public identifiers. Removing an identifier records it as reserved or
replaced; identifiers are never reused for different semantics.

## Core command kinds

| Identifier | Payload contract |
|---|---|
| `initialize` | initialization request; transport entry point rather than ordinary active-session mutation |
| `query-capabilities` | no target; returns current immutable snapshot |
| `create-resource`, `update-resource` | typed resource payload |
| `create-transform`, `update-transform` | typed transform payload |
| `set-panel-state` | panel/view/guide/attachment state payload |
| `create-visual`, `update-visual` | typed visual payload |
| `submit-frame` | frame submission payload |
| `panel-query` | `QueryRequest` |
| `shutdown` | shutdown policy payload |

## Core visual families

`point`, `marker`, `segment`, `path`, `image`, `text`, and `mesh`.

## Capability identifiers

The machine registry is `spec/requirements/registries.json`. Important accepted identifiers include:

| Identifier | Meaning |
|---|---|
| `interaction.view2d.navigation.v1` | canonical View2D navigation actions |
| `view3d.static.orthographic.v1` | static orthographic View3D |
| `view3d.static.perspective.v1` | static perspective View3D |
| `meshvisual.positions3d.data_view3d.v1` | DATA-space 3D mesh mapping |
| `meshvisual.positions3d.ndc.v1` | NDC 3D mesh placement |
| `meshvisual.positions3d.opaque_depth.v1` | strict bounded opaque depth |
| `meshvisual.material.unlit_rgba.v1` | unlit RGBA material |
| `meshvisual.material.flat_lambert.v1` | bounded flat Lambert material |
| `texture2d.rgba8.v1` | RGBA8 Texture2D protocol resource |
| `meshvisual.material.texture2d_unlit.v1` | bounded textured unlit mesh material |
| `meshvisual.texture_filter.linear.v1` | base-level bilinear mesh texture filtering |
| `gsp_vispy2.producer.mesh.texture_filter.linear.v1` | producer emission of linear mesh texture filtering |
| `query.view3d.ray_readback.v1` | canonical View3D ray context |
| `query.view3d.mesh_triangle_pick.v1` | identity-only mesh triangle pick |
| `query.view3d.mesh_triangle_pick.geometry.v1` | geometry payload sibling |
| `query.view3d.mesh_triangle_pick.facing.v1` | projected-facing payload sibling |

`GSP-CAP-011`: the registry entry defines only semantic identity. Backend support is declared by a
session snapshot and evidence profile; presence in this registry is not a support claim.

## Diagnostic code namespaces

| Prefix | Category |
|---|---|
| `protocol.*` | version, state, sequencing, and command validation |
| `id.*` | identifier/reference validation |
| `resource.*` | data/resource validation and lifetime |
| `visual.*` | visual schema and semantic validation |
| `view.*` / `layout.*` | view, navigation, transform, and layout |
| `capability.*` | unsupported or missing capability |
| `adaptation.*` | accepted semantic deviation |
| `query.*` / `pick.*` | query request, payload, and freshness |
| `security.*` | policy rejection and redaction |
| `backend.*` | adapter/backend execution failures |

Existing stable mesh-pick diagnostic values such as `pick.unsupported.backend`,
`pick.stale.layout_snapshot`, and `pick.ambiguous.depth_tie` remain reserved to their accepted
conditions. M238 aligns Python enums with the complete machine registry.

## Payload kind identifiers

| Identifier | Payload |
|---|---|
| `gsp.guide-query@0.1` | guide contribution |
| `gsp.text-query@0.1` | text item contribution |
| `gsp.mesh-query@0.1` | mesh face contribution |
| `gsp.scalar-color-query@0.1` | scalar/color mapping values |
| `gsp.transform-query@0.1` | transform/inverse status |
| `gsp.view3d-query@0.1` | View3D ray/snapshot context |

Payload versions are independent from the package version. GSP 0.2 may preserve an accepted 0.1
payload unchanged or register a replacement; it must not mutate an existing payload identifier.
