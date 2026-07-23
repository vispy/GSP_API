# S065 technical baseline - camera, visuals, text, and minimal query

Date: 2026-07-23

Status: accepted implementation baseline for S065. This is deliberately detailed enough for a
medium-reasoning worker to implement without choosing new public semantics.

## 1. Cross-cutting rules

- GSP records are frozen semantic dataclasses with eager NumPy arrays and stable validation.
- Positions use finite `float32`/`float64`. Colors use the existing GSP RGBA conventions.
- Screen-sized values are finite logical canvas pixels. DATA-sized values are finite data units.
- New records accept `CoordinateSpace.DATA` or `NDC` only where explicitly stated.
- A `(N,3)` DATA visual requires `Scene.view3d`; 2D DATA visuals require `Scene.view2d`.
- Capability snapshots advertise only behavior implemented and tested by that backend.
- Unsupported behavior returns a stable diagnostic or `QueryResult`; it is never silently dropped.
- Datoviz mappings use only public v0.4 generated bindings at the pinned/read-only dependency.
- Matplotlib may be an explicit adaptation where exact GPU behavior is impossible, but it must be
  deterministic and documented.
- VisPy2 imports only `gsp-core`, never concrete adapters.

## 2. High-level View3D and camera

Keep existing `Axes` as the 2D class. Add `Axes3D` and overload:

```python
vp.subplots() -> tuple[Figure, Axes]
vp.subplots(projection="2d") -> tuple[Figure, Axes]
vp.subplots(projection="3d") -> tuple[Figure, Axes3D]
```

`Figure.axes` may contain `Axes | Axes3D`, but the first experimental scene still supports exactly
one axes. `Figure.to_scene()` emits exactly one of `view2d` or `view3d`; it rejects mixed/multiple
views. `Axes3D` owns one `Panel`, one `View3D`, attachments, visuals, and optional title text. It
does not generate 2D axis guides in this stage.

Initial default:

```python
Camera3D(eye=(3, 3, 3), target=(0, 0, 0), up=(0, 0, 1))
PerspectiveProjection3D(fov_y_degrees=45, near_far=(0.1, 1000))
```

Required `Axes3D` methods:

```python
set_camera(*, eye, target, up) -> Camera3D
get_camera() -> Camera3D
set_perspective(*, fov_y_degrees=45, near=0.1, far=1000,
                aspect_ratio=None) -> PerspectiveProjection3D
set_orthographic(*, xlim=(-1, 1), ylim=(-1, 1),
                 near=0, far=1000) -> OrthographicProjection3D
get_projection() -> Projection3D
orbit(*, yaw_radians, pitch_radians) -> View3D
pan(*, right, up) -> View3D
zoom(scale, *, anchor_ndc=None) -> View3D
reset_camera() -> View3D
fit_camera(*, margin=1.1) -> View3D
```

Use existing GSP reducers for orbit/pan/zoom. Each accepted operation increments `View3D.revision`.
`reset_camera()` restores the axes construction state.

`fit_camera()` uses finite DATA-space bounds from current 3D visuals. Empty scenes raise a clear
`ValueError`. The target is the bounds center. Perspective fit preserves the current view direction,
places the eye far enough to contain the bounding sphere at the current vertical FOV and aspect,
and resolves positive near/far planes with margin. Orthographic fit projects all bounding-box
corners onto camera right/true-up/forward axes and expands x/y and near/far ranges by `margin`.
Degenerate bounds receive a deterministic nonzero epsilon extent. Add numeric tests.

M275 must expose at least `Axes3D.mesh()` so a complete static 3D journey exists before new visual
families arrive. Existing mesh material/texture semantics remain unchanged.

M276 enables retained camera updates and live input. Datoviz must update camera/projection state
without re-uploading unchanged visual buffers. Matplotlib must re-render deterministically from the
new `View3D`. Datoviz live orbit/pan/zoom remains unadvertised until its automated lifecycle tests
pass and the human checkpoint accepts interaction.

Capability IDs reuse the existing registry:

- `view3d.static.orthographic.v1`
- `view3d.static.perspective.v1`
- `view3d.navigation.orbit_pan_zoom.v1`
- `view3d.retained_data_space_visuals.v1`

## 3. PixelVisual

Add:

```python
@dataclass(frozen=True, slots=True)
class PixelVisual:
    id: str
    positions: FloatArray                 # (N,2|3)
    colors: ColorArray                    # (4,) or (N,4)
    pixel_size_px: FloatArray | float = 1.0
    coordinate_space: CoordinateSpace = CoordinateSpace.DATA
    transform: VisualTransformBinding | None = None
```

Sizes are finite and strictly positive. A pixel is a screen-aligned square of the requested logical
pixel width. Per-item state/hover bitfields are not protocol fields.

Datoviz maps to public `dvz_pixel` dense position/color/pixel-size attributes. Matplotlib uses
deterministic square markers with diameter conversion for 2D and a documented projected-square
adaptation for 3D. Add capability IDs:

- `pixelvisual.v1`
- `pixelvisual.positions3d.data.view3d.v1`
- `pixelvisual.exact_logical_size.v1`

VisPy2 adds `Axes.pixels(...)`, `Axes3D.pixels(...)`, and module-level `pixels(...)`.

## 4. SphereVisual

Add:

```python
@dataclass(frozen=True, slots=True)
class SphereVisual:
    id: str
    positions: FloatArray                 # exactly (N,3)
    radii: FloatArray | float             # DATA units, strictly positive
    colors: ColorArray                    # (4,) or (N,4)
    coordinate_space: CoordinateSpace = CoordinateSpace.DATA
```

Only DATA-space 3D spheres are accepted. S065 does not expose a Datoviz fast/raycast selector,
materials, or raw lighting state. Datoviz uses the accurate public sphere impostor mode when
available and must preserve analytic surface depth. Matplotlib projects deterministic screen
circles from DATA radii and is explicitly adapted because it cannot prove analytic GPU depth.

Capability IDs:

- `spherevisual.v1`
- `spherevisual.analytic_surface_depth.v1`

VisPy2 adds `Axes3D.spheres(x, y, z, *, radius, color, id=None)`.

## 5. VectorVisual

S065 accepts straight vectors only:

```python
class VectorAnchor(str, Enum):
    TAIL = "tail"
    CENTER = "center"
    HEAD = "head"

class VectorCap(str, Enum):
    NONE = "none"
    BUTT = "butt"
    ROUND = "round"
    TRIANGLE_IN = "triangle_in"
    TRIANGLE_OUT = "triangle_out"
    SQUARE = "square"

@dataclass(frozen=True, slots=True)
class VectorVisual:
    id: str
    positions: FloatArray                 # anchors, (N,2|3)
    vectors: FloatArray                   # displacements, same shape
    colors: ColorArray                    # (4,) or (N,4)
    widths_px: FloatArray | float = 1.0
    scale: float = 1.0
    anchor: VectorAnchor = VectorAnchor.TAIL
    start_cap: VectorCap = VectorCap.BUTT
    end_cap: VectorCap = VectorCap.TRIANGLE_OUT
    coordinate_space: CoordinateSpace = CoordinateSpace.DATA
    transform: VisualTransformBinding | None = None
```

Vectors must be finite and nonzero per item; widths and scale are strictly positive. Curved vector
subpaths, per-item caps, dashes, and backend-native style objects are deferred.

Datoviz maps to `dvz_vector` plus `DvzVectorStyle`. Matplotlib maps to deterministic 2D/3D
line-and-head artists and declares adaptation where head rasterization differs.

Capability IDs:

- `vectorvisual.straight.v1`
- `vectorvisual.positions3d.data.view3d.v1`
- `vectorvisual.triangle_head.v1`

VisPy2 adds `Axes.vectors(...)`, `Axes3D.vectors(...)`, and `quiver(...)` as a thin alias over the
same semantic record. Do not implement Matplotlib's full `quiver` argument surface.

## 6. PrimitiveVisual

This is a bounded geometry escape hatch, not a raw draw-call API:

```python
class PrimitiveTopology(str, Enum):
    POINT_LIST = "point_list"
    LINE_LIST = "line_list"
    LINE_STRIP = "line_strip"
    TRIANGLE_LIST = "triangle_list"
    TRIANGLE_STRIP = "triangle_strip"

@dataclass(frozen=True, slots=True)
class PrimitiveVisual:
    id: str
    topology: PrimitiveTopology
    positions: FloatArray                 # (N,2|3)
    colors: ColorArray                    # (4,) or (N,4)
    indices: IndexArray | None = None      # flat public vertex indices
    coordinate_space: CoordinateSpace = CoordinateSpace.DATA
    transform: VisualTransformBinding | None = None
```

Validate topology cardinality after applying indices: pairs for line lists, at least two for line
strips, triples for triangle lists, and at least three for triangle strips. Reject out-of-range,
negative, non-integer, and non-finite input. Normals, materials, textures, instancing, restart
indices, adjacency, culling knobs, depth knobs, shader selection, and backend handles are deferred.

Datoviz maps to public `dvz_primitive` and optional index binding. Matplotlib deterministically maps
points, lines, and triangles, with explicit adaptation for raster/depth differences.

Capability IDs:

- `primitivevisual.v1`
- `primitivevisual.indexed.v1`
- topology-specific `.point_list`, `.line_list`, `.line_strip`, `.triangle_list`, and
  `.triangle_strip` capability IDs.

VisPy2 adds `Axes.primitives(...)`, `Axes3D.primitives(...)`, and module-level `primitives(...)`.

## 7. Text hardening

Retain `TextVisual`; do not add a glyph visual. Make these semantics executable:

- 2D DATA/NDC text keeps logical-pixel font size, anchors, rotation, color, and generic font role.
- A `(N,3)` DATA `TextVisual` with `Scene.view3d` is a screen-facing billboard anchored at the
  projected 3D point.
- Billboard size is logical pixels and does not shrink with depth.
- S065 billboard text is ordered overlay text; strict depth occlusion is deferred.
- Multiline layout, rich text, exact font files, shaping guarantees, glyph identity, atlas access,
  and per-glyph query are deferred.

Capability IDs:

- existing `text` family for 2D;
- `textvisual.billboard3d.v1`;
- `textvisual.billboard3d.depth_occlusion.v1` remains unadvertised.

VisPy2 exposes billboard behavior through `Axes3D.text(...)`; no backend-specific keyword is added.

## 8. Minimal public query

Extend `BackendSession` with:

```python
def query(
    self,
    request: QueryRequest,
    *,
    scene_id: str | None = None,
) -> QueryResult: ...
```

Sessions retain a map from `Scene.id` to the most recent live renderer/result. `scene_id=None`
targets the latest rendered scene. Query before render, after close, or for an unknown scene ID is a
clear session-state error. A backend that rendered the target but lacks a requested capability
returns a structured unsupported `QueryResult`, not `NotImplementedError`.

VisPy2 adds:

```python
Figure.query(session, request) -> QueryResult
```

It targets the figure's stable scene ID and does not retain the session or backend result.

M282 wires already-proven Matplotlib queries and Datoviz point/ray queries. New S065 visual
families may return structured unsupported payloads. Comprehensive multi-hit picking, sphere/vector
item picking, mesh geometry payload parity, glyph picking, volume query, and scientific readback are
deferred.

## 9. Required gallery

Installed-wheel examples must cover:

1. 2D priority families in one scene.
2. Perspective 3D mesh + spheres + vectors + billboard labels.
3. Orthographic 3D primitive/pixel scene.
4. Programmatic camera fit/orbit/pan/zoom with deterministic before/after captures.
5. Live Datoviz camera navigation.
6. Backend discovery and explicit capability selection.
7. Minimal point query plus structured unsupported query.

Each example must state supported backends and expected strict/adapted/unsupported behavior.

