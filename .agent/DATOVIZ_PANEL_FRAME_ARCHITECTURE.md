# Datoviz Panel Frame Architecture Note

This note records the Datoviz-side architecture target accepted for S043. It is intended to be
portable into the Datoviz repository as a design note before API-breaking implementation begins.

## Goal

Unify Datoviz guide strictness and retained `View3D` navigation around one panel-owned resolved frame
model:

```text
DvzPanelFrameSnapshot
    revisioned DvzView2D / DvzView3D
    first-class DvzGuide objects
    explicit visual and guide attachments
    render/query/readback/all-rendered snapshot identity
```

This is allowed to break Datoviz `v0.4-dev` compatibility.

## Core APIs

Suggested C API shape:

```c
typedef struct DvzPanelFrameSnapshot DvzPanelFrameSnapshot;
typedef uint64_t DvzSnapshotId;
typedef uint64_t DvzRevision;

DvzPanelFrameSnapshot* dvz_panel_resolve_frame(
    DvzPanel* panel,
    DvzFrameResolveFlags flags);

DvzSnapshotId dvz_panel_frame_id(const DvzPanelFrameSnapshot* snapshot);
void dvz_panel_frame_info(const DvzPanelFrameSnapshot* snapshot, DvzPanelFrameInfo* out);
void dvz_panel_frame_ref(DvzPanelFrameSnapshot* snapshot);
void dvz_panel_frame_unref(DvzPanelFrameSnapshot* snapshot);
```

`DvzPanelFrameInfo` should expose snapshot/revision ids, logical and framebuffer sizes, device scale,
panel/plot/grid-clip rectangles, active view identity, transforms, View3D matrices where applicable,
layering, visual attachment summaries, rendered contribution summaries, and diagnostics.

## View APIs

Replace public mutable panel-view structs with revisioned descriptors and state APIs:

```c
typedef enum DvzViewKind
{
    DVZ_VIEW_2D,
    DVZ_VIEW_3D,
} DvzViewKind;

DvzView* dvz_panel_view2d(DvzPanel* panel, const DvzView2DDesc* desc);
DvzView* dvz_panel_view3d(DvzPanel* panel, const DvzView3DDesc* desc);

void dvz_view2d_set_domain(DvzView* view, vec2 domain_x, vec2 domain_y);
void dvz_view2d_get_domain(const DvzView* view, vec2 out_x, vec2 out_y);

void dvz_view3d_set_camera(DvzView* view, const DvzCameraState* camera);
void dvz_view3d_get_camera(const DvzView* view, DvzCameraState* out);

void dvz_view3d_set_projection(DvzView* view, const DvzProjectionState* projection);
void dvz_view3d_get_projection(const DvzView* view, DvzProjectionState* out);

DvzRevision dvz_view_revision(const DvzView* view);
```

`dvz_panel_set_domain()` may remain temporarily as a compatibility wrapper over the active
`DvzView2D`.

## Guide APIs

Guides should become semantic panel objects:

```c
DvzGuide* dvz_panel_guide(DvzPanel* panel, const DvzGuideDesc* desc);
void dvz_guide_set_label(DvzGuide* guide, const char* label);
void dvz_guide_set_ticks(DvzGuide* guide, const DvzTickSpec* ticks);
void dvz_guide_set_visible(DvzGuide* guide, bool visible);
DvzGuideId dvz_guide_id(const DvzGuide* guide);
```

Guide query should return snapshot id, guide id, guide kind, role, hit part, box, anchor, tick index,
data value, and label when applicable.

## Visual Attachments

Visual attachments must explicitly state view id, coordinate space, viewport, clipping, and layer:

```c
typedef struct DvzVisualAttachDesc
{
    DvzViewId view_id;
    DvzCoordSpace coord_space;
    DvzViewportMode viewport;
    DvzClipMode clip;
    int32_t layer;
    int32_t z_order;
    uint32_t flags;
} DvzVisualAttachDesc;
```

Strict retained `View3D` requires mesh positions to remain in DATA space:

```c
void dvz_mesh_set_positions_data3f(
    DvzVisual* mesh,
    uint32_t count,
    const vec3* positions,
    DvzBufferUpdatePolicy policy);
```

## Required Proofs

Before guide strictness:

- snapshot id stability and invalidation;
- panel/plot/grid rects under resize and device scale;
- title, tick label, axis label, legend, and colorbar box query;
- guide hit testing;
- all-rendered guide contributions;
- same snapshot id across render, query, readback, and contribution enumeration.

Before retained `View3D` navigation:

- DATA-space mesh visual renders correctly;
- camera updates change projection without vertex/index buffer writes;
- orbit/pan/zoom update only retained view/projection state;
- visual identity remains stable;
- snapshot id changes during navigation;
- ray query uses the render snapshot id;
- multi-panel isolation.

## Rejected Paths

- Promoting guide strictness from visual appearance only.
- Overlay masking as grid clipping proof.
- Keeping guides as generated visuals only for strict mode.
- Reuploading CPU-projected panel-NDC mesh buffers on pointer events.
- Exposing Datoviz-native controllers, materials, or pipelines as GSP public semantics.
- Building a GSP-only layout shim over Datoviz for strict mode.
