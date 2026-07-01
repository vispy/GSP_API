# 1. Executive decision

**Decision: yes. Datoviz should introduce a unified retained panel/view/guide architecture centered on an immutable resolved panel frame snapshot.** This is the right foundation for both requested fronts: `layout_strict` guide semantics and retained `View3D` live navigation. Treat this as a deliberate Datoviz v0.4-dev API break, not as a compatibility patch.

The uploaded consultation packet establishes that GSP requires render, query, readback, and all-rendered guide contributions to share the same `ResolvedLayoutSnapshot`, and that current Datoviz `View3D` rendering in GSP uses CPU-projected panel-NDC buffers, which cannot support strict retained orbit/pan/zoom without reuploading changed vertex positions.  Public Datoviz docs also show the architectural tension: current guidance says visuals require NDC, while interactivity is attached to panels and controls internal transformation matrices; interactivity is described as limited/evolving, with Python exposure not always matching C. ([datoviz.org][1]) ([datoviz.org][2]) Datoviz also already has camera APIs such as orthographic/perspective setup, position/lookat/up, and view/projection matrix readback, so the missing piece is not “a camera exists,” but “the camera/view state is a retained, revisioned, queryable panel contract used by DATA-space visuals.” ([datoviz.org][3])

The two fronts should be solved by **one Datoviz architecture stage** with a shared core, then implemented through two mostly independent mission stacks:

1. **Core:** retained `DvzPanelFrameSnapshot` + revisioned `DvzPanelView`.
2. **Guide stack:** first-class semantic guide objects, guide layout/query/readback/all-rendered contributions.
3. **View3D stack:** DATA-space visual attachment, retained camera/projection updates, synchronized controller/readback path.

Do not promote Datoviz guide rows from adapted to strict, and do not claim `view3d.navigation.orbit_pan_zoom.v1`, until the corresponding evidence exists in Datoviz-native tests and GSP review artifacts.

---

# 2. Datoviz architecture proposal

## 2.1 Core model: `DvzPanelFrameSnapshot`

Introduce a Datoviz-owned resolved frame snapshot, tentatively:

```c
typedef struct DvzPanelFrameSnapshot DvzPanelFrameSnapshot;
typedef uint64_t DvzSnapshotId;
typedef uint64_t DvzRevision;
```

The snapshot is the authoritative render-time contract for a panel. It is produced after layout, view resolution, guide layout, clipping, and z/layer ordering are known.

Minimal required fields:

```c
typedef struct DvzPanelFrameInfo
{
    DvzSnapshotId snapshot_id;
    DvzRevision panel_revision;
    DvzRevision layout_revision;
    DvzRevision view_revision;
    DvzRevision guide_revision;
    DvzRevision visual_revision;

    DvzRenderTargetId render_target_id;
    vec2 framebuffer_size_px;
    vec2 logical_size_px;
    float device_scale;

    DvzRect panel_rect_px;
    DvzRect plot_rect_px;
    DvzRect grid_clip_rect_px;

    DvzViewId view_id;
    DvzViewKind view_kind;

    DvzTransform data_to_screen;
    DvzTransform screen_to_data;

    mat4 model;
    mat4 view;
    mat4 projection;
    mat4 mvp;
    mat4 inv_mvp;

    DvzLayerTable layers;
    DvzDiagnostics diagnostics;
} DvzPanelFrameInfo;
```

The snapshot must also provide indexed access to:

```c
DvzGuideLayout[]        guide_boxes;
DvzGuideAnchor[]        guide_anchors;
DvzTextBox[]            tick_label_boxes;
DvzTextBox[]            axis_label_boxes;
DvzTextBox[]            title_boxes;
DvzLegendBox[]          legend_boxes;
DvzColorbarBox[]        colorbar_boxes;
DvzRenderedContribution[] rendered_contributions;
DvzVisualAttachment[]   visual_attachments;
```

## 2.2 Required invariants

For any Datoviz capability advertised as strict:

1. **One snapshot governs everything.** Render, guide query, visual query, ray/readback, screenshots, and all-rendered contribution APIs must either use the same `snapshot_id` or explicitly report that the requested snapshot is unavailable.

2. **Snapshots are immutable.** Once returned, a `DvzPanelFrameSnapshot` cannot change. A resize, domain change, camera update, guide edit, font metric change, visual attach/detach, or layout policy change produces a new snapshot id or revision.

3. **Strict render paths may not use hidden layout state.** If grid clipping, guide placement, view transforms, or z/layer ordering affect pixels, the resolved values must be inspectable from the snapshot.

4. **Logical and physical pixels are explicit.** Snapshot rects must define whether they are logical pixels, framebuffer pixels, or both. Device scale must be recorded.

5. **View transforms are bidirectional or diagnostically absent.** If a transform cannot be inverted, query/ray/readback must return a capability diagnostic instead of fabricating a result.

6. **Grid clipping is real clipping.** In layout-strict mode, grid lines are clipped to `plot_rect_px` unless a future GSP spec adds another policy. A foreground overlay band must never count as strict clipping evidence.

7. **DATA-space visuals remain retained under navigation.** For retained `View2D`/`View3D`, camera/domain changes update view/projection uniforms or equivalent retained state. They must not rebuild or reupload unchanged visual buffers during ordinary pointer navigation.

8. **Native controller state must be synchronizable.** Datoviz can keep native arcball/panzoom/fly controllers internally, but strict GSP claims require that their effects be expressible as canonical public view/camera/projection state at snapshot boundaries.

---

# 3. GSP public contract boundary

GSP should not expose Datoviz-native controller names, draw-state names, visual flags, or material/light identifiers as public semantics.

The boundary should be:

```text
GSP public semantics
    View2D domains
    View3D camera/projection state
    guide identity/role/label/ticks/ramp intent
    ResolvedLayoutSnapshot
    canonical input actions
    query/readback payloads
    capability diagnostics
        |
        v
GSP Datoviz adapter
    maps GSP public state to Datoviz descriptors
    maps Datoviz snapshots back to GSP snapshots
    validates snapshot ids and capability evidence
        |
        v
Datoviz private implementation
    panels
    views
    guide layout engine
    visual pipelines
    native controllers
    Vulkan/DRP details
```

GSP may depend on Datoviz providing neutral, inspectable facts:

```text
panel rect
plot rect
guide boxes
guide identities and roles
tick/label boxes
grid clip rect
data-to-screen transforms
view/camera/projection state
snapshot id
rendered contribution identities
retained update counters or proof hooks
diagnostics
```

GSP must not depend on implementation names such as “Datoviz arcball,” “Datoviz material,” “DVZ visual flag X,” or “DRP pipeline Y” as protocol semantics.

---

# 4. Required Datoviz C/Python API changes

## 4.1 New panel frame APIs

Suggested C shape:

```c
typedef enum DvzFrameResolveFlags
{
    DVZ_FRAME_RESOLVE_DEFAULT          = 0,
    DVZ_FRAME_RESOLVE_FORCE            = 1 << 0,
    DVZ_FRAME_RESOLVE_WITH_GUIDES      = 1 << 1,
    DVZ_FRAME_RESOLVE_WITH_CONTRIBS    = 1 << 2,
    DVZ_FRAME_RESOLVE_WITH_DIAGNOSTICS = 1 << 3,
} DvzFrameResolveFlags;

DvzPanelFrameSnapshot* dvz_panel_resolve_frame(
    DvzPanel* panel,
    DvzFrameResolveFlags flags);

DvzSnapshotId dvz_panel_frame_id(
    const DvzPanelFrameSnapshot* snapshot);

void dvz_panel_frame_info(
    const DvzPanelFrameSnapshot* snapshot,
    DvzPanelFrameInfo* out);

uint32_t dvz_panel_frame_guide_count(
    const DvzPanelFrameSnapshot* snapshot);

bool dvz_panel_frame_guide_layout(
    const DvzPanelFrameSnapshot* snapshot,
    DvzGuideId guide_id,
    DvzGuideLayout* out);

uint32_t dvz_panel_frame_contribution_count(
    const DvzPanelFrameSnapshot* snapshot);

bool dvz_panel_frame_contribution(
    const DvzPanelFrameSnapshot* snapshot,
    uint32_t index,
    DvzRenderedContribution* out);

void dvz_panel_frame_ref(DvzPanelFrameSnapshot* snapshot);
void dvz_panel_frame_unref(DvzPanelFrameSnapshot* snapshot);
```

Python shape:

```python
snapshot = panel.resolve_frame(with_guides=True, with_contributions=True)
snapshot.id
snapshot.panel_rect_px
snapshot.plot_rect_px
snapshot.grid_clip_rect_px
snapshot.view.data_to_screen
snapshot.guides["x-axis"].box_px
snapshot.contributions
snapshot.diagnostics
```

## 4.2 New first-class guide APIs

C shape:

```c
typedef enum DvzGuideKind
{
    DVZ_GUIDE_AXIS,
    DVZ_GUIDE_TITLE,
    DVZ_GUIDE_LEGEND,
    DVZ_GUIDE_COLORBAR,
    DVZ_GUIDE_TEXT,
} DvzGuideKind;

typedef enum DvzGuideRole
{
    DVZ_GUIDE_ROLE_X_AXIS,
    DVZ_GUIDE_ROLE_Y_AXIS,
    DVZ_GUIDE_ROLE_Z_AXIS,
    DVZ_GUIDE_ROLE_TITLE,
    DVZ_GUIDE_ROLE_LEGEND,
    DVZ_GUIDE_ROLE_COLORBAR,
    DVZ_GUIDE_ROLE_TICK_LABEL,
    DVZ_GUIDE_ROLE_AXIS_LABEL,
    DVZ_GUIDE_ROLE_GRID,
} DvzGuideRole;

typedef struct DvzGuideDesc
{
    DvzGuideId id;
    DvzGuideKind kind;
    DvzGuideRole role;
    DvzViewId view_id;

    DvzSide side;
    DvzAnchor anchor;
    const char* label;

    DvzTextStyle text_style;
    DvzTickSpec tick_spec;
    DvzGridSpec grid_spec;
    DvzColorbarSpec colorbar_spec;
    DvzLegendSpec legend_spec;

    uint32_t flags;
    void* user_data;
} DvzGuideDesc;

DvzGuide* dvz_panel_guide(
    DvzPanel* panel,
    const DvzGuideDesc* desc);

void dvz_guide_set_label(DvzGuide* guide, const char* label);
void dvz_guide_set_ticks(DvzGuide* guide, const DvzTickSpec* ticks);
void dvz_guide_set_visible(DvzGuide* guide, bool visible);
DvzGuideId dvz_guide_id(const DvzGuide* guide);
```

Guide query shape:

```c
typedef enum DvzGuideHitPart
{
    DVZ_GUIDE_HIT_NONE,
    DVZ_GUIDE_HIT_TITLE,
    DVZ_GUIDE_HIT_AXIS_LABEL,
    DVZ_GUIDE_HIT_TICK_LABEL,
    DVZ_GUIDE_HIT_TICK_MARK,
    DVZ_GUIDE_HIT_GRID_LINE,
    DVZ_GUIDE_HIT_COLORBAR_RAMP,
    DVZ_GUIDE_HIT_LEGEND_ENTRY,
} DvzGuideHitPart;

typedef struct DvzGuideHit
{
    DvzSnapshotId snapshot_id;
    DvzGuideId guide_id;
    DvzGuideKind kind;
    DvzGuideRole role;
    DvzGuideHitPart part;

    DvzRect box_px;
    DvzAnchor anchor;

    int32_t tick_index;
    double data_value;
    const char* label;
} DvzGuideHit;

bool dvz_panel_query_guide(
    DvzPanel* panel,
    DvzSnapshotId snapshot_id,
    vec2 screen_px,
    DvzGuideHit* out);
```

Python shape:

```python
x = panel.guides.axis("x", label="Time", ticks=ticks, grid=True)
title = panel.guides.title("Experiment A")
colorbar = panel.guides.colorbar("temperature", cmap="viridis", range=(0, 1))

hit = panel.query_guide(x_px, y_px, snapshot=snapshot.id)
hit.guide_id
hit.role
hit.part
hit.box_px
hit.snapshot_id
```

## 4.3 New unified view APIs

Replace public mutable `DvzPanelView2D`-style structs with revisioned descriptors and state APIs.

```c
typedef enum DvzViewKind
{
    DVZ_VIEW_2D,
    DVZ_VIEW_3D,
} DvzViewKind;

typedef struct DvzView2DDesc
{
    DvzViewId id;
    vec2 domain_x;       // ordered; reversed domains allowed
    vec2 domain_y;       // ordered; reversed domains allowed
    DvzAspectPolicy aspect;
    DvzPaddingPolicy padding;
    DvzFitPolicy fit;
    uint32_t flags;
} DvzView2DDesc;

typedef struct DvzView3DDesc
{
    DvzViewId id;
    DvzCameraState camera;
    DvzProjectionState projection;
    DvzNavigationPolicy navigation;
    uint32_t flags;
} DvzView3DDesc;

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

`dvz_panel_set_domain()` can remain temporarily as a compatibility wrapper, but it should delegate to the active `DvzView2D`.

## 4.4 Visual attachment APIs

Visuals need explicit, inspectable coordinate-space and view attachment.

```c
typedef enum DvzCoordSpace
{
    DVZ_COORD_DATA_2D,
    DVZ_COORD_DATA_3D,
    DVZ_COORD_NDC,
    DVZ_COORD_PANEL_PIXEL,
    DVZ_COORD_FRAMEBUFFER_PIXEL,
} DvzCoordSpace;

typedef enum DvzViewportMode
{
    DVZ_VIEWPORT_PANEL,
    DVZ_VIEWPORT_PLOT,
    DVZ_VIEWPORT_CUSTOM,
} DvzViewportMode;

typedef enum DvzClipMode
{
    DVZ_CLIP_NONE,
    DVZ_CLIP_PANEL,
    DVZ_CLIP_PLOT,
    DVZ_CLIP_CUSTOM,
} DvzClipMode;

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

void dvz_visual_attach(
    DvzVisual* visual,
    DvzPanel* panel,
    const DvzVisualAttachDesc* desc);
```

For strict retained `View3D`, mesh positions must stay in `DVZ_COORD_DATA_3D` or an equivalent DATA-space contract:

```c
void dvz_mesh_set_positions_data3f(
    DvzVisual* mesh,
    uint32_t count,
    const vec3* positions,
    DvzBufferUpdatePolicy policy);
```

---

# 5. Compatibility break and migration plan

Break compatibility in Datoviz v0.4-dev deliberately, but make the migration mechanical.

## Keep temporarily as wrappers

```c
dvz_panel_set_domain(panel, x0, x1, y0, y1)
```

becomes:

```c
DvzView* view = dvz_panel_active_view(panel);
dvz_view2d_set_domain(view, (vec2){x0, x1}, (vec2){y0, y1});
```

Current `DvzPanelView2D` policy fields such as `flags`, `mode`, `aspect`, and `padding` can be mapped into `DvzView2DDesc`, but should no longer be treated as a public mutable live-state struct.

## Deprecate

Deprecate these patterns:

```text
public mutable panel-view structs with unrevisioned fields
generated guide visuals with no semantic guide identity
guide text lowered silently to ordinary visuals in strict/conformance paths
implicit visual viewport/clip behavior not inspectable from panel state
CPU-projected View3D mesh buffers used for interactive retained navigation
native controller state with no canonical readback equivalent
```

## Remove or hard-gate

Remove or hard-gate any Datoviz/GSP path that claims strict retained `View3D` navigation while using CPU-reprojected panel-NDC mesh buffers.

Legacy NDC mesh paths may remain for low-level Datoviz users, but they must be identified as:

```text
coord_space = DVZ_COORD_NDC
retained_navigation_eligible = false
```

GSP must treat them as static/adapted rendering paths, not strict retained navigation paths.

---

# 6. Guide strictness path

## 6.1 Decision

Datoviz guide objects should become **first-class semantic/layout/query participants**, not merely generated visuals.

Axes, titles, tick labels, axis labels, grid lines, legends, and colorbars must have durable identities and roles. Their resolved boxes and anchors must be produced by the panel frame layout engine and be queryable from the same snapshot used to render.

## 6.2 Required guide model

Each guide needs:

```text
guide_id
kind
role
associated view_id
side/anchor/lane
label text
tick/ramp/legend specification
style
visibility
z/layer
resolved box
hit regions
rendered contribution identity
snapshot_id
diagnostics
```

## 6.3 Strict promotion requirements

A Datoviz guide row can move from adapted to strict only when all of the following are true:

1. The guide is represented as a `DvzGuide`, not only as incidental generated geometry.
2. The rendered guide contribution reports the same `snapshot_id` as the panel frame snapshot.
3. Query/readback can return guide identity, role, box, hit part, and snapshot id.
4. All-rendered contribution enumeration includes guide contributions.
5. Grid clipping is performed by plot viewport/scissor or equivalent true clipping and is reflected in the snapshot.
6. Title, axis label, tick label, colorbar, and legend layout boxes are inspectable.
7. Text rasterization remains raster-tolerant, but text layout boxes and anchors are strict.

## 6.4 Grid clipping status

The current native-verified grid clipping proof should remain a separate capability from full guide strictness. The packet states that the correct Datoviz model is full inverse source extent grid geometry plus plot viewport/clip, and that endpoint trimming caused double clipping.

Therefore GSP should allow a diagnostic such as:

```text
datoviz.grid_clip.native_verified.plot_clip.v1 = true
layout_strict.guides = false
reason = "guide layout/query/all-rendered snapshot evidence incomplete"
```

This avoids under-crediting the grid clipping fix while preventing premature strict guide promotion.

---

# 7. View3D retained live-navigation path

## 7.1 Decision

Datoviz should implement retained `View3D` by making 3D visuals attach to a panel view in DATA space, with camera/projection state stored in a revisioned `DvzView3D` object. Ordinary orbit/pan/zoom must update only camera/view/projection retained state, not mesh vertex buffers.

## 7.2 Required architecture

A strict retained `View3D` stack needs:

```text
DvzView3D
    camera state
    projection state
    navigation policy
    view/projection matrices
    inverse matrices
    revision

DvzVisualAttachDesc
    view_id
    coord_space = DATA_3D
    viewport = PLOT or PANEL
    clip mode
    layer/z order

DvzPanelFrameSnapshot
    view_id
    camera/projection state
    data_to_screen transform
    screen_to_data/ray transform
    plot rect
    snapshot id
```

## 7.3 Mesh path

The strict path should look like:

```c
DvzView* view = dvz_panel_view3d(panel, &view3d_desc);

DvzVisual* mesh = dvz_mesh(panel_or_scene);
dvz_mesh_set_positions_data3f(mesh, n_vertices, positions, DVZ_BUFFER_STATIC);
dvz_mesh_set_indices(mesh, n_indices, indices, DVZ_BUFFER_STATIC);

dvz_visual_attach(mesh, panel, &(DvzVisualAttachDesc){
    .view_id = view_id,
    .coord_space = DVZ_COORD_DATA_3D,
    .viewport = DVZ_VIEWPORT_PLOT,
    .clip = DVZ_CLIP_PLOT,
    .layer = DVZ_LAYER_DATA,
});
```

During navigation:

```c
dvz_view3d_set_camera(view, &new_camera);
dvz_view3d_set_projection(view, &new_projection);
snapshot = dvz_panel_resolve_frame(panel, DVZ_FRAME_RESOLVE_DEFAULT);
```

Expected retained behavior:

```text
vertex buffer writes: 0
index buffer writes: 0
mesh rebuilds: 0
view/projection uniform updates: >= 1
snapshot id changes: yes
visual identity changes: no
```

## 7.4 Native controller policy

There are two acceptable controller strategies.

Preferred GSP strategy:

```text
raw toolkit event
    -> GSP canonical action
    -> GSP View3D reducer
    -> Datoviz dvz_view3d_set_camera/projection
    -> Datoviz snapshot
```

Acceptable Datoviz-native strategy:

```text
raw toolkit event
    -> Datoviz native controller
    -> Datoviz canonical camera/projection state
    -> GSP reads synchronized state
    -> GSP validates equivalent canonical View3D state
```

Unacceptable strategy:

```text
raw toolkit event
    -> Datoviz private controller mutates private matrices
    -> GSP cannot read canonical equivalent state
    -> query/readback uses different state from render
```

## 7.5 Ray/readback

Datoviz should expose a ray/readback API from the frame snapshot:

```c
typedef struct DvzRayContext
{
    DvzSnapshotId snapshot_id;
    DvzViewId view_id;

    vec2 screen_px;
    DvzRect plot_rect_px;

    vec3 ray_origin_data;
    vec3 ray_direction_data;

    mat4 view;
    mat4 projection;
    mat4 inv_view;
    mat4 inv_projection;
    mat4 inv_mvp;

    DvzCameraState camera;
    DvzProjectionState projection_state;

    DvzDiagnostics diagnostics;
} DvzRayContext;

bool dvz_panel_query_ray(
    DvzPanel* panel,
    DvzSnapshotId snapshot_id,
    vec2 screen_px,
    DvzRayContext* out);
```

GPU picking, depth readback, materials, lighting, perspective, culling, and transparency should remain separately gated capabilities. They are not prerequisites for the first strict retained orbit/pan/zoom claim.

---

# 8. GSP capability/test/review updates

## 8.1 Capability taxonomy during transition

GSP should distinguish these states explicitly:

```text
guide.render.adapted.v1
    Datoviz renders guide-like output, but guide layout/query/readback/all-rendered semantics are incomplete.

guide.grid_clip.native_verified.v1
    Grid clipping is natively verified against plot clipping, but broader guide strictness is not implied.

layout.snapshot.partial.v1
    Datoviz exposes panel/plot rects and transforms, but not all guide boxes/contributions.

layout.snapshot.guides.v1
    Datoviz exposes guide boxes and guide identities, but all-rendered/query/readback may still be incomplete.

layout_strict.guides.v1
    Render, query, readback, and all-rendered guide contributions use the same snapshot id.

view3d.static.mesh.v1
    Static 3D mesh rendering works for supported projection/camera slice.

view3d.ray_readback.canonical.v1
    Ray readback returns canonical GSP payloads from public View3D state and snapshot ids.

view3d.retained_data_space_visuals.v1
    3D visuals retain DATA-space buffers and respond to view/projection updates.

view3d.navigation.orbit_pan_zoom.v1
    Live orbit/pan/zoom is retained, canonical, queryable, and proven not to reupload unchanged visual buffers.
```

## 8.2 GSP diagnostics

Examples:

```text
Datoviz guide row remains adapted:
  reason = "title guide has no queryable layout box"
  evidence = "grid clipping native-verified; guide snapshot incomplete"

Datoviz View3D live navigation disabled:
  reason = "mesh path is CPU-projected panel-NDC"
  retained_boundary = "ordinary camera navigation would require vertex buffer reupload"

Datoviz partial snapshot:
  reason = "panel_rect/plot_rect/data_to_screen available; colorbar/legend boxes unavailable"
```

## 8.3 Mandatory tests before guide strict promotion

Datoviz-native tests:

```text
snapshot id stability and invalidation
panel rect and plot rect under resize/high-DPI
grid clip equals plot rect for axes grids
no endpoint double-trimming of grid geometry
title box query
axis label box query
tick label box query
legend box query
colorbar box/query
guide hit testing
all-rendered guide contributions
same snapshot id across render/query/readback/contribution enumeration
reversed domains
dense ticks
multi-panel layout
device scale changes
```

GSP tests/reviews:

```text
S031/S028-style review pack regeneration
title-boundary grid clipping row
axis/tick/title query fixtures
legend/colorbar contribution fixtures
layout_snapshot_id equality assertions
capability matrix update only for rows with evidence
adapted rows remain adapted with precise diagnostics
```

## 8.4 Mandatory tests before View3D live navigation

Datoviz-native tests:

```text
DATA-space mesh visual renders correctly
camera update changes screen projection without vertex buffer writes
orbit event replay changes only view/projection retained state
pan event replay changes only view/projection retained state
zoom event replay changes only view/projection retained state
mesh visual identity remains stable across navigation
snapshot id changes across navigation
ray query uses same snapshot id as render
resize updates camera/projection and snapshot consistently
multi-panel View3D isolation
```

Instrumentation should expose proof counters:

```c
typedef struct DvzRetainedUpdateStats
{
    uint64_t vertex_buffer_uploads;
    uint64_t index_buffer_uploads;
    uint64_t visual_rebuilds;
    uint64_t view_uniform_updates;
    uint64_t projection_uniform_updates;
    uint64_t snapshot_resolves;
} DvzRetainedUpdateStats;

void dvz_panel_retained_stats(
    DvzPanel* panel,
    DvzRetainedUpdateStats* out);
```

GSP tests/reviews:

```text
canonical View3D reducer event replay
Datoviz state readback equals GSP canonical state
initial/orbit/pan/zoom screenshot sequence
ray readback after each navigation step
assert unchanged visual buffers are not reuploaded
live review examples enable Datoviz View3D only behind capability gate
```

---

# 9. Implementation phases and mission stack

## Phase 0 — Decision and freeze

Repos:

```text
GSP_API
Datoviz
```

Actions:

```text
commit this decision as GSP ADR or .agent/decisions entry
create Datoviz architecture note
freeze broad strict guide promotion
keep Datoviz View3D live navigation unsupported
keep native grid clipping proof as separate diagnostic
```

Stop if:

```text
the decision cannot be accepted in both repos
the architecture would require GSP public semantics to expose Datoviz-private names
```

## Phase 1 — Datoviz panel frame snapshot core

Repo:

```text
Datoviz
```

Deliverables:

```text
DvzPanelFrameSnapshot
snapshot id/revision lifecycle
panel_rect_px
plot_rect_px
grid_clip_rect_px
view transform fields
diagnostics
basic C API
basic Python wrapper
snapshot tests
```

Stop if:

```text
render uses layout state not present in snapshot
snapshot ids are unstable or mutable
resize/device-scale behavior is ambiguous
```

## Phase 2 — Datoviz unified view descriptors

Repo:

```text
Datoviz
```

Deliverables:

```text
DvzView
DvzView2DDesc
DvzView3DDesc
ordered View2D domains
revisioned camera/projection state
compatibility wrapper for dvz_panel_set_domain()
view state readback
```

Stop if:

```text
View2D domain ordering/reversal cannot be represented
View3D camera/projection state cannot be read back canonically
native controllers mutate private state with no synchronized equivalent
```

## Phase 3 — Datoviz first-class guide objects

Repo:

```text
Datoviz
```

Deliverables:

```text
DvzGuide
axis/title/legend/colorbar descriptors
guide layout boxes
guide hit query
all-rendered guide contributions
guide contribution snapshot ids
Python guide API
guide tests
```

Stop if:

```text
title, tick label, axis label, legend, or colorbar boxes are not inspectable
query/readback cannot return the same snapshot id used by render
all-rendered output omits guide contributions
```

## Phase 4 — GSP partial snapshot adapter

Repo:

```text
GSP_API
```

Deliverables:

```text
map Datoviz snapshot to GSP ResolvedLayoutSnapshot
add partial snapshot capability
preserve adapted guide diagnostics
recognize native-verified grid clipping separately
add snapshot-id equality tests for available fields
```

Stop if:

```text
GSP has to synthesize strict fields Datoviz cannot report
Datoviz and GSP disagree on pixel units or device scale
```

## Phase 5 — GSP guide strict promotion

Repo:

```text
GSP_API
```

Deliverables:

```text
promote only proven guide rows
update capability matrix
regenerate review packs
assert render/query/readback/all-rendered snapshot equality
```

Stop if:

```text
any promoted row lacks guide identity, guide box, hit/readback, contribution, or snapshot id
grid clipping proof depends on overlay masking
```

## Phase 6 — Datoviz retained DATA-space View3D visuals

Repo:

```text
Datoviz
```

Deliverables:

```text
DATA_3D mesh attachment
view/projection uniform update path
retained update stats
static DATA-space View3D tests
camera/projection readback from snapshot
ray query from snapshot
```

Stop if:

```text
ordinary camera updates require vertex buffer rewrites
mesh visual identity changes during navigation
query/ray state diverges from render state
```

## Phase 7 — GSP Datoviz View3D live navigation

Repo:

```text
GSP_API
```

Deliverables:

```text
Datoviz View3D live examples enabled behind capability gate
canonical action replay tests
retained update counter assertions
ray readback after navigation
review artifacts for orbit/pan/zoom/reset
```

Stop if:

```text
Datoviz controller effects cannot be synchronized to canonical GSP state
visual buffers are reuploaded during ordinary navigation
GSP must expose Datoviz controller names publicly
```

---

# 10. Risks, rejected alternatives, and open questions

## Risks

```text
Scope risk
    A unified panel frame architecture is larger than M130 and should be treated as a new stage.

Text layout risk
    Exact glyph rasterization will vary. The strict claim should cover boxes, anchors, roles, and snapshot ids, while raster output remains raster-tolerant.

Python binding lag
    Datoviz C may support the new model before generated Python wrappers expose it. GSP Python paths must not claim strict capability until wrappers expose the required state.

Performance risk
    Snapshot resolution must be cheap enough for interaction. Use revisions and dirty bits so camera-only updates do not recompute guide layout unnecessarily.

Coordinate convention risk
    Logical pixels, framebuffer pixels, NDC, panel pixels, plot pixels, and DATA coordinates must be explicitly named in APIs.

Controller risk
    Datoviz-native controllers are useful, but dangerous if they mutate state that cannot be read back canonically.

API churn risk
    v0.4-dev compatibility breaks are acceptable, but the migration must be mechanical and documented.
```

## Rejected alternatives

```text
Promote adapted guide rows based on visual appearance only
    Rejected. It would violate GSP layout_strict semantics.

Use white overlay bands as grid clipping proof
    Rejected. Strict clipping must be real plot clipping/scissor/equivalent clipping.

Keep guides as generated visuals only
    Rejected. It cannot provide durable guide identity, role, query, layout box, and all-rendered contribution semantics.

Keep View3D mesh buffers as CPU-projected panel-NDC and reupload on pointer events
    Rejected. It violates retained navigation.

Expose Datoviz controller/material/pipeline names as GSP semantics
    Rejected. GSP must remain backend-independent.

Build a GSP-only layout shim over Datoviz
    Rejected for strict mode. It would create two sources of truth and likely diverge from Datoviz render output.

Treat grid clipping proof as full guide strictness
    Rejected. Native grid clipping is necessary but not sufficient.
```

## Open questions

```text
Should perspective projection be part of the first retained View3D strict slice, or remain deferred behind an additional capability?

What exact text metric engine should Datoviz use for layout boxes, and how are font changes/version changes reflected in diagnostics?

Should Datoviz snapshots be serializable for offline GSP conformance artifacts?

What is the first supported legend/colorbar layout subset?

Should native Datoviz controllers emit canonical action deltas, final state snapshots, or both?

What is the lifetime policy for snapshots during continuous interaction?
```

---

# 11. Stop/go criteria

## Go for unified Datoviz architecture stage

Proceed if the accepted design includes:

```text
DvzPanelFrameSnapshot as authoritative render/query/readback contract
revisioned DvzView2D/DvzView3D state
first-class DvzGuide identities
explicit visual coordinate-space attachments
capability diagnostics for incomplete states
```

## Stop guide strict promotion if

```text
render/query/readback/all-rendered do not share one snapshot id
guide boxes are not inspectable
guide identities or roles are missing
title is silently lowered to ordinary TextVisual in conformance mode
legend/colorbar/tick labels are omitted from all-rendered contributions
grid clipping depends on hidden overlay masking
```

## Go for guide strict promotion when

```text
Datoviz native tests pass for guide layout/query/contribution snapshot equality
GSP maps Datoviz snapshot fields into ResolvedLayoutSnapshot without synthesis
review pack rows pass
diagnostics identify remaining adapted rows precisely
```

## Stop View3D live navigation if

```text
ordinary orbit/pan/zoom reprojects CPU vertices
ordinary orbit/pan/zoom reuploads unchanged mesh buffers
native controller state cannot be read back as canonical camera/projection state
ray/readback uses different state from render
visual identity changes during navigation
```

## Go for `view3d.navigation.orbit_pan_zoom.v1` when

```text
View3D mesh positions remain in DATA space
navigation updates only retained camera/view/projection state
Datoviz exposes camera/projection/snapshot readback
GSP canonical action replay matches Datoviz state
retained update counters prove no unchanged visual buffer reupload
ray readback returns the same snapshot id as render
live review examples pass under capability gating
```

Final recommendation: **create one new Datoviz/GSP architecture stage after S042, with a shared panel-frame/view foundation and two implementation branches: guide strictness and retained View3D navigation.** The shared interface boundary is `DvzPanelFrameSnapshot` + `DvzView` + explicit visual/guide attachment descriptors. That boundary prevents duplicated layout, duplicated transforms, and conflicting render/query state.

[1]: https://datoviz.org/guide/common/ "Main Concepts - Datoviz Documentation"
[2]: https://datoviz.org/guide/interactivity/ "Interactivity - Datoviz Documentation"
[3]: https://datoviz.org/reference/api_c/ "C API Reference - Datoviz Documentation"
