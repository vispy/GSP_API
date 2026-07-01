# S043 Datoviz Panel Frame Architecture Decisions

Status: accepted by local-main-codex from P027 response.

## Accepted

- Datoviz should introduce one unified retained panel/view/guide architecture centered on an
  immutable resolved panel frame snapshot.
- This is a deliberate Datoviz `v0.4-dev` API break when the cleaner architecture requires it.
- The shared core is:
  - `DvzPanelFrameSnapshot`;
  - revisioned `DvzView2D` and `DvzView3D` state;
  - first-class semantic `DvzGuide` objects;
  - explicit visual and guide attachment descriptors.
- The same snapshot identity must govern strict render, query, readback, and all-rendered
  contributions.
- Datoviz native grid clipping remains a separate native-verified capability. It is necessary for
  guide strictness, but it is not sufficient for guide strictness.
- Datoviz guide rows must remain adapted until guide identity, layout boxes, query/readback payloads,
  all-rendered guide contributions, and snapshot-id equality are proven.
- Datoviz `View3D` live navigation must remain unsupported until DATA-space 3D visual attachments
  and retained camera/projection updates are proven without reuploading unchanged visual buffers.

## Public Boundary

GSP public semantics remain backend-independent:

- `View2D` domains;
- `View3D` camera/projection state;
- guide identity, role, labels, ticks, ramps, and layout intent;
- `ResolvedLayoutSnapshot`;
- canonical navigation actions;
- query/readback payloads;
- capability diagnostics.

GSP must not expose Datoviz-native controller names, material names, shader names, draw-state names,
or pipeline names as public semantics.

## Datoviz Architecture Direction

Datoviz should add an immutable resolved frame snapshot that records, at minimum:

- snapshot id and panel/layout/view/guide/visual revisions;
- logical render target size, framebuffer size, and device scale;
- panel rect, plot rect, and grid clip rect;
- active view id and kind;
- data-to-screen and screen-to-data transforms;
- View3D model/view/projection and inverse matrices where applicable;
- guide boxes, anchors, tick-label boxes, axis-label boxes, title boxes, legend boxes, and colorbar
  boxes;
- rendered contribution identities;
- visual attachments;
- diagnostics.

Snapshots are immutable. Resizes, domain changes, camera/projection changes, guide edits, font metric
changes, visual attachment changes, and layout policy changes produce a new snapshot id or revision.

## Guide Strictness Criteria

A Datoviz guide row can move from adapted to strict only when:

- the guide is represented by a durable semantic `DvzGuide`, not only generated geometry;
- render/query/readback/all-rendered contribution enumeration use the same snapshot id;
- query/readback returns guide identity, role, box, hit part, and snapshot id;
- all-rendered enumeration includes guide contributions;
- title, axis label, tick label, colorbar, and legend boxes are inspectable;
- grid clipping is true plot clipping/scissor/equivalent clipping, not overlay masking;
- text layout boxes and anchors are strict, while glyph rasterization may remain raster-tolerant.

## View3D Retained Navigation Criteria

Datoviz may claim retained `View3D` live navigation only when:

- mesh positions remain in DATA space;
- ordinary orbit/pan/zoom updates retained camera/view/projection state only;
- visual identity remains stable during navigation;
- vertex/index buffers are not rewritten for unchanged visuals during ordinary navigation;
- camera/projection/snapshot readback is exposed;
- ray readback uses the same snapshot id as render;
- GSP canonical action replay matches Datoviz state;
- live review examples pass behind capability gates.

## Capability Taxonomy

GSP should distinguish transition states explicitly:

- `guide.render.adapted.v1`;
- `guide.grid_clip.native_verified.v1`;
- `layout.snapshot.partial.v1`;
- `layout.snapshot.guides.v1`;
- `layout_strict.guides.v1`;
- `view3d.static.mesh.v1`;
- `view3d.ray_readback.canonical.v1`;
- `view3d.retained_data_space_visuals.v1`;
- `view3d.navigation.orbit_pan_zoom.v1`.

## Deferred

- Full guide strict promotion before Datoviz snapshot/guide/query evidence exists.
- Datoviz `View3D` live navigation over CPU-projected panel-NDC mesh buffers.
- Public GSP exposure of Datoviz-native controller/material/pipeline concepts.
- Perspective, GPU 3D picking, depth readback, native materials/lights/textures, culling, and
  transparency unless accepted by separate capability slices.

## Source

`.agent/consultations/P027-dataviz-guide-and-view3d-architecture.md` and
`.agent/consultations/P027-response.md`.
