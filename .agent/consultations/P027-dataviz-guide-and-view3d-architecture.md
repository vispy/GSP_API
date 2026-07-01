# P027 - Datoviz Guide Strictness And View3D Retained Architecture

## Purpose

This needs ChatGPT Pro consultation.

The project needs a long-term architecture decision spanning both GSP_API and Datoviz. The user is
willing to break Datoviz v0.4-dev API compatibility if that produces a cleaner durable
architecture.

The decision must cover two linked fronts:

1. Datoviz guide strictness: axes, titles, grid clipping, guide layout/query/readback, and
   all-rendered guide contributions.
2. Datoviz live/interactive View3D: retained DATA-space 3D visuals, canonical GSP camera/projection
   state, and live orbit/pan/zoom without reuploading unchanged visual buffers.

Implementation depending on this decision should pause until the consultation result is pasted or
committed.

## Project Context

GSP_API is a backend-independent visualization protocol with multiple renderers. Matplotlib is the
publication/reference backend. Datoviz v0.4-dev is intended to be the flagship high-performance GPU
backend. GSP keeps public semantics backend-independent; raw toolkit events, backend-native cameras,
Datoviz controllers, and draw-state names are private backend implementation details.

Authority order in this repository:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

If existing source code conflicts with specs, the spec wins and implementation must stop rather than
inventing a third behavior.

Local repositories:

- GSP_API: `/home/cyrille/GIT/Viz/GSP_API`
- Datoviz: `/home/cyrille/GIT/Viz/datoviz`

Do not assume Datoviz API compatibility is sacred. The user explicitly allows breaking Datoviz
v0.4-dev API compatibility for better long-term architecture.

## Current GSP Semantics

### Layout and guides

GSP separates guide meaning, resolved layout geometry, raster output, and query/readback behavior.

Conformance tiers:

- `semantic_strict`: scene semantics match. Views, domains, visual identities, guide identities,
  roles, labels, deterministic tick intent, grid intent, supported query payloads, and capability
  diagnostics are protocol-stable. Pixel-identical placement is not required.
- `layout_strict`: render, query, readback, and all-rendered contributions use the same
  `ResolvedLayoutSnapshot`. Panel rectangles, plot rectangles, guide boxes, title boxes, axis lanes,
  tick label boxes, legend/colorbar boxes, grid clipping, data-to-screen transforms, and
  `layout_snapshot_id` match within geometric tolerance.
- `raster_tolerant`: layout geometry and nominal logical sizes match, while glyph rasterization,
  antialiasing, hinting, and small subpixel differences remain tolerant.
- `pixel_parity`: optional opt-in raster-level parity.

Minimal `ResolvedLayoutSnapshot` fields:

- `snapshot_id`
- `render_target`
- `panel_rect_px`
- `plot_rect_px`
- `view_id`
- `data_to_screen_transform`
- `guide_boxes`
- `guide_anchors`
- `tick_label_boxes`
- `axis_label_boxes`
- `title_boxes`
- `legend_boxes`
- `colorbar_boxes`
- `grid_clip_rect_px`
- `z_layers`
- `diagnostics`

Grid lines are clipped to `plot_rect_px` in layout-strict mode unless a future spec defines an
explicit alternate policy. A white overlay band that hides grid lines is not a strict clipping
proof.

Guide query/readback requirements:

- Axis, title, legend, and colorbar guides remain guides even if realized by backend-native axes,
  text, ramps, or visuals.
- `PanelTextGuide(role=TITLE)` must not be silently lowered to an ordinary `TextVisual` in
  conformance mode. If lowered through screen text, this is an explicit adaptation.
- Render, query, readback, and all-rendered guide contributions must report or use the same
  `layout_snapshot_id` when layout-strict support is advertised.

### View and navigation

GSP public interaction uses canonical actions applied to canonical public state:

- `View2D` pan/zoom actions update GSP `View2D` domains.
- `View3D` orbit/pan/zoom/reset actions update GSP `View3D` camera/projection state.
- Raw mouse, wheel, keyboard, Matplotlib, Datoviz, GLFW, and toolkit events are private. Backends
  adapt them into canonical GSP actions.
- Backend-native controllers may be used internally only when their effects are synchronized with
  canonical GSP state and query/readback snapshots.

Retained navigation boundary:

- Live navigation must not rebuild or reupload unchanged visual buffers for every pointer event.
- Camera/view/projection updates are acceptable retained updates.
- Reprojecting CPU vertices and reuploading mesh positions on every pointer event is not acceptable
  as a strict retained View3D navigation implementation.

## Current Datoviz/GSP State

### Guide strictness and grid clipping

Datoviz guide rows currently render as adapted, not strict.

What is now proven:

- Datoviz native axes render ticks, labels, grids, reversed domains, and View2D domains for the
  current GSP slices.
- A recent Datoviz grid clipping defect was fixed in Datoviz commit `9ba820489`:
  `Avoid double clipping axis grid geometry`.
- The corrected Datoviz model is:
  - grid geometry is authored over the full inverse source extent;
  - generated axis grid visuals use `DVZ_VISUAL_VIEWPORT_PLOT`;
  - generated axis grid visuals use `DVZ_VISUAL_CLIP_PLOT`;
  - plot viewport/scissor handles plot-rect clipping;
  - geometry endpoint trimming to the plot interval was wrong because it double-applied the plot
    inset and shortened grids in `examples/c/features/user_scale.c`.
- Datoviz native tests passed after this correction: full scene test binary `661/661`.
- GSP commit `18a7c46` detects the native grid clipping proof.
- GSP commit `0b93aed` adds a title-boundary grid clipping review row.
- The S031 legacy S028 review pack regenerated against Datoviz `9ba820489` reports:
  - strict: 53
  - adapted: 7
  - unsupported: 0

What remains adapted:

- Datoviz guide rows remain adapted because title layout/query and guide-query/all-rendered-guide
  semantics are not strict.
- Current diagnostics can now say grid clipping is natively verified for Datoviz builds with the
  `DVZ_VISUAL_VIEWPORT_PLOT` plus `DVZ_VISUAL_CLIP_PLOT` proof, but strict guide promotion still
  requires guide layout/query/readback evidence.

Known Datoviz View2D API facts:

- Current public `DvzPanelView2D` C struct and generated Python wrapper expose policy-like fields:
  `flags`, `mode`, `aspect`, and `padding`.
- They do not expose writable `data_x` / `data_y` fields in the inspected binding.
- `dvz_panel_set_domain()` carries ordered domains.
- `dvz_panel_set_view2d()` applies fit/aspect/padding policy.
- GSP currently sets ordered domains before enabling/updating the View2D policy.
- GSP has future-compat code for descriptor-domain fields if Datoviz later exposes
  `DvzPanelView2D.data_x/data_y`.

### Live/interactive examples and View3D

S042/M180 is completed:

- Live review examples enable navigation by default for supported `View2D` and `View3D` scenes.
- Matplotlib `View2D` and `View3D` review paths use canonical GSP navigation reducers.
- Datoviz `View2D` review paths use retained S035 navigation when live input bindings are present.
- Datoviz `View3D` live navigation is explicitly unsupported.

The current Datoviz View3D boundary:

- The GSP Datoviz protocol renderer uploads 3D meshes as CPU-projected panel-NDC positions with
  fixed controller mode.
- Updating only the native Datoviz camera does not move those retained mesh buffers.
- Reprojecting and reuploading mesh positions for every pointer event violates the retained
  navigation boundary.
- Datoviz must not claim `view3d.navigation.orbit_pan_zoom.v1` until it has a native DATA-space mesh
  path or another proven retained update strategy.

Current Datoviz View3D support in GSP:

- Static public `(N, 3)` `MeshVisual` rendering is supported when local Datoviz bindings expose P022
  camera prerequisites.
- GSP lowers `View3D.camera` through `dvz_panel_set_camera()`.
- GSP lowers orthographic projection bounds through `dvz_camera_set_orthographic_bounds()`.
- `query.view3d.ray_readback.v1` returns canonical ray-context payloads from public GSP `View3D`
  state and snapshot ids.
- Opaque depth, GPU 3D picking, native materials/lights/textures, perspective, and culling remain
  separately gated or deferred depending on the slice.
- S040 Datoviz strict flat Lambert is implemented by CPU-resolving exact per-face colors and
  uploading unlit color payloads, not by exposing Datoviz native material/light names as public GSP
  semantics.

## Existing Deferred Work

M130 is deferred:

Title: optional Datoviz adapted-row strict promotion proof.

Deliverables:

- Focused proof for selected adapted text or guide rows.
- Additional fixtures or tests for any strict claim.
- Updated capability matrix only where strict behavior is proven by explicit contract evidence.
- ChatGPT Pro packet if new public semantics or ambiguous Datoviz behavior must be decided.

Stop condition:

- Stop before broad strict promotion if the proof depends on undocumented backend behavior,
  architecture decisions, or capability taxonomy changes.

Because the user now wants to invest directly in Datoviz and accepts API breaks, this is no longer a
small M130 proof. It should become a new architecture stage/missions after this consultation.

## Decision Needed

Recommend the right long-term architecture for Datoviz and GSP together.

The answer should decide whether Datoviz should grow a unified retained panel/view/guide scene model
that can support both:

1. layout-strict guides with query/readback/all-rendered contribution semantics; and
2. retained DATA-space View2D/View3D visuals with live navigation through camera/view/projection
   state updates rather than visual buffer reuploads.

The decision may break Datoviz v0.4-dev API compatibility.

## Candidate Direction To Evaluate

One possible long-term architecture is:

### Datoviz native panel frame model

Introduce a Datoviz-owned resolved panel frame snapshot, for example `DvzPanelFrameSnapshot`, with:

- stable snapshot id/revision;
- logical render target size and device scale;
- panel rect;
- plot rect;
- data-to-screen transforms for View2D and View3D;
- grid clip rect;
- guide boxes and anchors;
- title/tick/axis-label/colorbar/legend boxes;
- z/layer information;
- diagnostics;
- enough identity to tie render, query, readback, and all-rendered output together.

### Datoviz guide/layout API

Make axes, titles, colorbars, legends, grids, and guide text panel-owned layout participants rather
than incidental visuals:

- guides are semantic panel objects;
- guide render geometry is generated from the resolved frame snapshot;
- guide query can return guide identity, role, label/tick/ramp hit, logical pixel box, and snapshot
  id;
- all-rendered queries can include guide contributions with the same snapshot id;
- title/axis/tick/colorbar placement is inspectable even when exact font rasterization remains
  raster-tolerant.

### Datoviz retained View2D/View3D model

Make panel views and visuals use a consistent retained model:

- data visuals retain DATA/NDC coordinates instead of CPU-projected panel-NDC replacements when
  strict view navigation is advertised;
- View2D domain/panzoom state and View3D camera/projection/controller state are panel-owned and
  revisioned;
- visual buffers are not rebuilt or reuploaded for ordinary camera/domain navigation;
- query/ray/readback paths use the same view/frame snapshot as render;
- backend-native input/controller events are converted into canonical GSP action effects or
  synchronized into canonical equivalent state before GSP claims strict behavior.

### API break strategy

Potential Datoviz API changes to consider:

- replace or redesign `DvzPanelView2D` as an explicit descriptor carrying domain and policy, or keep
  `dvz_panel_set_domain()` as the domain carrier but formalize ordering and snapshot behavior;
- add explicit retained View3D mesh DATA-space attach descriptors;
- add panel frame/layout snapshot C APIs;
- add guide query and all-rendered contribution APIs;
- revise visual attachment descriptors so `coord_space`, viewport, clipping, z/layer, and panel
  view identity are explicit and inspectable;
- version or remove legacy CPU-projected mesh paths that cannot support retained View3D navigation.

## Questions For ChatGPT Pro

Please answer as an architecture reviewer. Assume you can break Datoviz v0.4-dev API compatibility
if justified.

1. Should Datoviz introduce a unified panel frame/layout snapshot model as the foundation for guide
   strictness and retained View2D/View3D navigation? If yes, what are the minimal required fields and
   invariants?
2. Should Datoviz guide objects become first-class semantic/layout/query participants rather than
   generated visuals only? What should the C and Python API shape look like?
3. Should Datoviz `View2D` domains live in `DvzPanelView2D`, `dvz_panel_set_domain()`, a new
   `DvzPanelView`, or somewhere else? What is the cleanest API even if it breaks compatibility?
4. What is the right retained View3D architecture for DATA-space mesh visuals, camera/projection
   state, native input controllers, and query/ray readback?
5. How should Datoviz expose enough state for GSP to claim `layout_strict` guides and
   `view3d.navigation.orbit_pan_zoom.v1` without exposing Datoviz-native implementation names as
   public GSP semantics?
6. Which Datoviz APIs should be introduced, deprecated, or removed? Include names or pseudocode
   signatures where helpful.
7. How should GSP capabilities distinguish the transition period: adapted guide rendering,
   native-verified grid clipping, partial layout snapshot, strict layout, static View3D, retained
   View3D live navigation?
8. What implementation phases should be used across the two repos, and where should each phase stop
   if evidence is insufficient?
9. What tests and visual review artifacts are mandatory before promoting Datoviz guide rows from
   adapted to strict and before enabling Datoviz View3D live navigation?
10. Are these two fronts best solved by one unified Datoviz architecture stage, or should they be
    split? If split, what interface boundary prevents duplicated or conflicting concepts?

## Expected Output Format

Return a concise but complete decision document with these sections:

1. Executive decision
2. Datoviz architecture proposal
3. GSP public contract boundary
4. Required Datoviz C/Python API changes
5. Compatibility break and migration plan
6. Guide strictness path
7. View3D retained live-navigation path
8. GSP capability/test/review updates
9. Implementation phases and mission stack
10. Risks, rejected alternatives, and open questions
11. Stop/go criteria

The output should be actionable enough to convert directly into:

- one GSP_API decision record;
- one Datoviz architecture/design note;
- a new GSP stage or mission stack after S042;
- a Datoviz implementation branch plan;
- explicit tests/review packs for promotion.
