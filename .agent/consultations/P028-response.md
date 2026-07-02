Decision:

* Accept with changes.
* Define S044 now, but make it backend-neutral. The public name and payload should describe **mesh-triangle picking in a View3D**, not “GPU picking.”
* Do not accept a visual-only strict v1. For the first strict MeshVisual picking protocol, a hit should identify both the public `visual_id` and the public triangle/primitive index.
* Keep `query.view3d.ray_readback.v1` separate. Ray readback remains a camera/layout query; S044 is a visual/primitive readback query.

Accepted minimal scope:

* Orthographic `View3D` only.
* `depth_mode=opaque_less` only for v1. Do not generalize to arbitrary future depth modes yet.
* Opaque, depth-writing, DATA-space `MeshVisual` triangle geometry only.
* Query is a single panel point and returns at most one result: the frontmost visible supported triangle, or miss, or structured unsupported/stale/invalid diagnostics.
* Eligible geometry is the public GSP MeshVisual triangle stream, not Datoviz-native primitives.
* `(N, 3)` DATA-space MeshVisual geometry participates through the public `View3D`.
* `(N, 3)` NDC MeshVisual picking is out of scope for S044 v1, even though NDC3 rendering exists.
* Transparent meshes, non-mesh visuals, instancing, perspective, culling, textures, multi-hit selection, and hit-position details are deferred.
* A backend may only return strict `hit` or `miss` when it can prove the result came from the current public GSP state for the reported snapshots.

Public query payload:

* request.kind: literal `"query.view3d.mesh_triangle_pick.v1"`, identifies the query protocol, required.

* request.view_id: string, public `View3D.id` to query, required.

* request.panel_id: string or null, optional guard against dispatching the query to the wrong panel; if supplied and inconsistent with the resolved `View3D.panel_id`, return `invalid`.

* request.panel_xy: tuple[float, float], query point in the same public panel coordinate convention used by `query.view3d.ray_readback.v1`, required.

* request.expected_layout_snapshot_id: string or null, optional freshness guard; mismatch returns `stale`.

* request.expected_view_revision: int/string or null, optional freshness guard; mismatch returns `stale`.

* request.expected_view_projection_snapshot_id: string or null, optional freshness guard; mismatch returns `stale`.

* request.expected_pick_scene_snapshot_id: string or null, optional freshness guard for the depth-affecting visual scene used by the pick pass; mismatch returns `stale`.

* response.kind: literal `"query.view3d.mesh_triangle_pick.v1"`, identifies the response protocol, required.

* response.status: enum `"hit" | "miss" | "unsupported" | "stale" | "invalid"`, overall result, required.

* response.hit: bool, true only when `status == "hit"`, required.

* response.view_id: string, public `View3D.id` actually used, required.

* response.panel_id: string, public panel id actually used, required when resolvable.

* response.panel_xy: tuple[float, float], echoed canonical query point, required.

* response.panel_ndc_xy: tuple[float, float], canonical panel NDC point used for the query, required for `hit` and `miss`.

* response.layout_snapshot_id: string, layout snapshot used to convert panel coordinates and viewport bounds, required for `hit` and `miss`.

* response.view_revision: int/string, public `View3D.revision` used, required for `hit` and `miss`.

* response.view_projection_snapshot_id: string, public `View3DProjectionSnapshot` id used, required for `hit` and `miss`.

* response.pick_scene_snapshot_id: string, opaque public snapshot id for the depth-affecting visual scene used by the pick query; must change when eligible visual geometry, indices, visibility, depth mode, opacity classification, layout, or View3D projection state affecting the pick result changes; required for `hit` and `miss`.

* response.depth_mode: literal `"opaque_less"`, public depth mode used, required for `hit` and `miss`.

* response.visual_id: string or null, public GSP visual id of the picked visual; required and non-null only for `hit`.

* response.visual_type: literal `"MeshVisual"` or null, public visual type; required and non-null only for `hit`.

* response.primitive_kind: literal `"triangle"` or null, public primitive kind; required and non-null only for `hit`.

* response.primitive_index: non-negative int or null, public triangle index; required and non-null only for `hit`.

* response.diagnostics: list[diagnostic], stable diagnostic codes plus optional human-readable details, required and may be empty.

* diagnostic.code: string, stable public diagnostic code, required.

* diagnostic.severity: enum `"info" | "warning" | "error"`, required.

* diagnostic.message: string, non-normative human-readable explanation, optional.

* diagnostic.data: object, backend-neutral structured details only, optional.

Capability names:

* Add `query.view3d.mesh_triangle_pick.v1` as the strict S044 capability.
* Require these existing capabilities as prerequisites for strict support:

  * `view3d.static.orthographic.v1`
  * `meshvisual.positions3d.data.view3d.v1`
  * `meshvisual.positions3d.opaque_depth.v1`
  * `query.view3d.ray_readback.v1` is not required to perform picking, but S044 should share its panel coordinate and snapshot conventions.
* Do not use `query.view3d.gpu_pick.v1`; “GPU” is an implementation strategy, not public protocol.
* Do not use `query.meshvisual.face_pick.v1` for v1 unless “face” is formally defined as the public triangle stream. Prefer `primitive_index`/`triangle` to avoid ambiguity with source polygons, tessellation, or backend primitive ids.
* Reserve `query.view3d.visual_pick.v1` for a future broader visual-level protocol covering more visual types. It should not be the strict S044 capability.

Suggested diagnostic codes:

* `pick.unsupported.backend`
* `pick.unsupported.projection`
* `pick.unsupported.depth_mode`
* `pick.unsupported.coordinate_space`
* `pick.unsupported.visual_type`
* `pick.unsupported.transparent`
* `pick.unsupported.instancing`
* `pick.unsupported.non_triangle_mesh`
* `pick.unsupported.no_public_primitive_map`
* `pick.unsupported.scene_occluder`
* `pick.unsupported.native_state_only`
* `pick.stale.layout_snapshot`
* `pick.stale.view_revision`
* `pick.stale.view_projection_snapshot`
* `pick.stale.pick_scene_snapshot`
* `pick.invalid.view_id`
* `pick.invalid.panel_id`
* `pick.invalid.panel_point`
* `pick.invalid.outside_panel`
* `pick.adapted.cpu_reference`
* `pick.adapted.rasterization_tolerance`
* `pick.ambiguous.edge_or_vertex`
* `pick.ambiguous.depth_tie`

Strict semantics:

* “Frontmost visible hit” means the supported MeshVisual triangle fragment at the query sample that would win the public opaque depth test for the reported `View3D`, layout, projection snapshot, and depth-affecting visual scene.
* For S044 v1, the only strict depth rule is `opaque_less`: among covered fragments that pass clipping, smaller projected depth wins.
* A miss means no supported opaque DATA-space MeshVisual triangle covers the query sample after applying the v1 clipping, viewport, and depth semantics.
* A result must be computed from public GSP state only. Native Datoviz object ids, shader names, framebuffer attachment names, Vulkan state, controller objects, Matplotlib artists, and backend primitive ids are not part of the protocol.
* `primitive_index` is the index in the public canonical MeshVisual triangle stream:

  * If the public MeshVisual has triangle faces, it is the row index in that public face/triangle array.
  * If the public MeshVisual is an unindexed triangle list, it is the emitted triangle ordinal.
  * If the backend cannot map its rendered primitive back to this public index, it must not claim strict support.
* Triangle boundary and exact depth-tie cases are not required to be cross-backend deterministic in v1. Tests should avoid edge/vertex and equal-depth ties. A backend may return `pick.ambiguous.edge_or_vertex` or `pick.ambiguous.depth_tie`.
* Near/far clipping, panel viewport clipping, and panel coordinate conversion must match the public `View3D` and layout snapshots.
* Backface culling is out of scope. Strict v1 should treat MeshVisual triangles as two-sided unless GSP has already accepted a public culling semantic. A backend with implicit native culling must disable it or return unsupported.
* Barycentric coordinates, interpolated DATA position, normalized depth value, world-space hit point, and ray-hit distance are deferred. They are not needed to identify the selected public visual/triangle and would prematurely freeze rasterization, interpolation, depth precision, and coordinate-space details.

Backend behavior:

* Matplotlib:

  * Should be a limited CPU reference oracle for strict-scope scenes, not a GPU picker.
  * May return `hit`/`miss` for eligible fixtures by projecting public DATA-space triangles through the public `View3D`, applying public viewport/near/far/depth rules, and selecting the frontmost covered triangle.
  * Should include `pick.adapted.cpu_reference` in diagnostics when the result is produced by the adapted CPU path.
  * Must return `unsupported` outside the strict S044 scope.
  * Should not advertise `query.view3d.mesh_triangle_pick.v1` as strict unless it passes the same conformance fixtures as Datoviz. Otherwise it can be used as a limited reference oracle in tests.

* Datoviz:

  * May implement with an offscreen integer-id/depth picking pass, shader storage, color-id readback, or another GPU strategy, but none of that is public API.
  * Must return public `visual_id` and public `primitive_index`, never Datoviz object ids or pipeline ids.
  * Must update/invalidate pick state when retained View3D camera/projection, layout, visible visual set, mesh buffers, indices, opacity classification, or depth mode changes.
  * Must support live navigation only when the retained DATA-space View3D symbols and live input bindings are present, consistent with the accepted View3D navigation state.
  * Must synchronize readback so a strict result cannot come from an older pick framebuffer or older camera/projection state.
  * Must not claim support for scenes where unsupported depth-writing visuals may affect the answer unless it can handle them through accepted public semantics.

* Older/unsupported builds:

  * Must return structured `unsupported`, `stale`, or `invalid`; they must not encode unsupported as `miss`.
  * Should include stable diagnostics explaining which prerequisite failed.
  * May omit snapshot fields only when they cannot resolve the view/layout at all; otherwise they should report the public state they inspected.

Deferred:

* Transparent mesh picking.
* Alpha-tested, blended, or order-independent transparency semantics.
* Point, marker, path, line, image, volume, text, and non-mesh visual picking.
* NDC3 MeshVisual picking.
* Perspective projection.
* Instancing and source-instance/item ids.
* Multi-hit, all-hits, lasso, rectangle, brush, or frustum selection.
* Vertex, edge, face-adjacency, and nearest-surface picking.
* Barycentric coordinates.
* Interpolated DATA/world hit position.
* Normalized depth or raw depth-buffer values.
* Ray distance.
* Public culling semantics.
* Textures and per-fragment material semantics.
* Native Datoviz lighting/material identifiers.
* Backend event/controller objects.
* Performance, latency, async scheduling, or persistent hover/selection state guarantees.

Stop conditions:

* Datoviz must not claim `query.view3d.mesh_triangle_pick.v1` if the queried projection is not the accepted orthographic `View3D` projection.
* Must not claim support if `depth_mode` is anything other than `opaque_less`.
* Must not claim support if any candidate hit would require NDC3, transparent, instanced, non-triangle, non-MeshVisual, or non-DATA-space semantics.
* Must not claim support if a rendered depth-writing visual outside S044 scope may occlude or alter the answer.
* Must not claim support if the backend cannot map its pick id to a public GSP `visual_id`.
* Must not claim support if the backend cannot map its primitive id to the public canonical MeshVisual triangle index.
* Must not claim support if pick ids can collide, overflow, be MSAA-resolved incorrectly, or be corrupted by color conversion/compositing.
* Must not claim support if the pick pass does not use the same public layout, viewport, near/far, camera, projection, and depth mode reported in the response.
* Must not claim support if retained View3D camera/projection updates during live navigation are not reflected in the pick pass.
* Must not claim support if pick buffers are not invalidated after mesh geometry, indices, visibility, layout, View3D revision, projection snapshot, or depth-affecting visual state changes.
* Must not claim support if GPU readback is not synchronized with the submitted pick pass.
* Must not claim support if native backface culling, clipping, or depth state differs from public S044 semantics.
* Must not claim support if implementation depends on exposing Datoviz-native ids, shader names, framebuffer attachment names, Vulkan draw state, or controller objects to callers.
* Must not claim support if HiDPI/panel coordinate conversion cannot be made identical to the public panel coordinate convention used by ray readback.

Tests/fixtures required:

* Single triangle center hit returns expected `visual_id` and `primitive_index`.
* Empty/background point returns `miss`, not `unsupported`.
* Query outside panel returns `invalid.outside_panel`.
* Two non-overlapping visuals return the correct visual/triangle for each point.
* Two overlapping triangles at different depths return the frontmost triangle under `opaque_less`.
* A front triangle occludes a rear triangle from the same visual.
* Near/far clipping causes clipped triangles to miss.
* Layout and panel NDC conversion fixture verifies `panel_xy` to `panel_ndc_xy`.
* View navigation/update fixture verifies pick result changes after orbit/pan/zoom without mesh reupload.
* Snapshot freshness fixture verifies mismatched expected layout/view/projection/pick-scene ids return `stale`.
* Primitive mapping fixture verifies indexed and unindexed triangle-list MeshVisuals return public triangle ordinals.
* Multi-panel fixture verifies the queried `View3D.panel_id` is respected.
* Unsupported projection fixture returns `pick.unsupported.projection`.
* Unsupported NDC3 MeshVisual fixture returns `pick.unsupported.coordinate_space`.
* Unsupported transparent MeshVisual fixture returns `pick.unsupported.transparent`.
* Unsupported non-mesh visual occluder fixture returns `pick.unsupported.scene_occluder`.
* Edge/vertex fixture documents ambiguity and allows `pick.ambiguous.edge_or_vertex`.
* Equal-depth overlap fixture documents ambiguity and allows `pick.ambiguous.depth_tie`.
* Matplotlib CPU oracle fixture should avoid pixel-edge and exact-tie cases.
* Datoviz conformance fixture should verify no backend-native ids appear in the payload.

ADR/spec changes:

* Add S044 as a new spec for `query.view3d.mesh_triangle_pick.v1`.
* Update `SPEC_INDEX.md` with the new capability and prerequisite capabilities.
* Add a diagnostics registry section for stable `pick.*` diagnostic codes.
* Add or update an ADR recording “Accept with changes: backend-neutral MeshVisual triangle picking, no public GPU/native ids.”
* Cross-reference `query.view3d.ray_readback.v1` and state explicitly that ray readback does not identify visuals or primitives.
* Define `pick_scene_snapshot_id` or an equivalent public render/pick-scene snapshot id. It must be backend-neutral and must change when any public depth-affecting state relevant to the pick answer changes.
* Define the public canonical MeshVisual triangle stream used by `primitive_index`.
* Add conformance fixtures before Datoviz advertises strict support.
* Mark visual-only picking, barycentric/hit-position payloads, transparent picking, perspective picking, and non-mesh picking as explicitly deferred rather than silently unsupported.
