# GSP updates for a future Matplotlib -> GSP frontend

Status: **repo-aligned planning note**. This supersedes the original draft assumptions in this file.

Target repo/branch: local `GSP_API`, branch `agentic-gsp-vispy2`.
Purpose: identify what GSP_API still needs before an external Matplotlib backend package can lower
Matplotlib renderer calls into GSP protocol visuals and render them through Datoviz v0.4,
Matplotlib-reference, or another GSP backend.

## 0. Current repo reality

The original draft assumed several things that are now outdated. Current state:

| Area | Current repo status | Integration consequence |
|---|---|---|
| Protocol visuals | Formal protocol dataclasses exist for Point, Marker, Segment, Path, Image; TextVisual is accepted by ADR/spec but implementation starts at M075. | Build on `gsp.protocol.*`, not legacy `gsp.visuals.*`. |
| Datoviz v0.4 | A retained-scene protocol adapter exists in `src/gsp_datoviz/protocol_renderer.py` with capability gates and visual QA coverage for S023. | Do **not** add a new `gsp_datoviz_v04` package unless a future refactor justifies it. |
| Legacy Datoviz v0.3 | Legacy modules remain under `src/gsp_datoviz/renderer/*`. | Treat as legacy/reference only; never use v0.3 APIs for new protocol work. |
| Matplotlib reference | `src/gsp_matplotlib/protocol_renderer.py` renders formal protocol visuals. | Keep `gsp_matplotlib` as **GSP -> Matplotlib**, not Matplotlib -> GSP. |
| Coordinates | `CoordinateSpace` currently has `NDC` and `DATA`; attachments also have semantic `DATA/VIEW/PANEL`. | Do not add display-pixel coordinate space without ADR/spec. Use frontend-local pixel lowering first. |
| Text | S024 accepted public `TextVisual`; public `GlyphVisual` is deferred. | Matplotlib frontend text support should wait for M075/M076 or fallback to Agg. |
| Mesh | Mesh is still deferred. | Irregular quad meshes/Gouraud triangles should fallback until a Mesh stage. |
| QA | Visual QA harness exists for protocol scenes. | Add frontend-specific smoke tests separately; do not force pixel-perfect Agg parity. |

## 1. Proper dependency direction

Keep package meanings unambiguous:

```text
gsp                  protocol contracts and core models
gsp_matplotlib       GSP protocol -> Matplotlib reference rendering
gsp_datoviz          GSP protocol -> Datoviz v0.4 retained adapter, plus legacy modules
gsp.qa.visual        protocol visual QA harness
vispy2               high-level Python producer of GSP scenes
mpl_gsp              proposed Matplotlib -> GSP frontend/backend package
```

Rules:

- Do not import Matplotlib from `gsp` core.
- Do not put the Matplotlib frontend in `gsp_matplotlib`; that name is already used for the reference
  renderer in the opposite direction.
- Keep `mpl_gsp` experimental until protocol coverage and fallback behavior are proven.
- Lower Matplotlib objects into formal protocol dataclasses, not legacy `VisualBase` classes.

## 2. Do not duplicate Datoviz v0.4 work

The plan should no longer create `src/gsp_datoviz_v04/` as the default path. Current repo already has:

- `gsp_datoviz.protocol_renderer` targeting top-level v0.4 facade symbols such as `dvz_scene`,
  `dvz_point`, `dvz_marker`, `dvz_segment`, `dvz_path`, `dvz_image`, and
  `dvz_visual_set_data`;
- capability helpers in `gsp_datoviz.capabilities`;
- query helpers in `gsp_datoviz.query`;
- S023 Datoviz visual QA evidence.

Future Datoviz work for `mpl_gsp` should be incremental:

1. finish S024 TextVisual protocol/Matplotlib support;
2. run a Datoviz text/glyph capability probe (M078);
3. add Datoviz TextVisual support or structured unsupported reports (M079);
4. only then consider package refactoring if the legacy/protocol split becomes unmaintainable.

## 3. Coordinate strategy for a Matplotlib frontend

Matplotlib renderer callbacks mostly operate in display pixels. GSP protocol currently accepts `NDC`
and `DATA`, not display pixels.

### Recommended near-term approach

Keep display-pixel coordinates **frontend-local** inside `mpl_gsp`:

```text
Matplotlib display pixels
  -> mpl_gsp.lowerings.transforms converts to panel-local NDC
  -> GSP Point/Marker/Segment/Path/Image/Text visuals with CoordinateSpace.NDC
```

This avoids adding protocol surface before the frontend proves its needs.

### Future ADR option

If display pixels become essential as a durable protocol concept, open a separate ADR/spec stage for:

- `CoordinateSpace.DISPLAY_PIXEL` or `VIEWPORT_PIXEL` naming;
- origin convention;
- DPI/device-pixel/logical-pixel semantics;
- clipping and viewport transform behavior;
- Datoviz attach mapping and Matplotlib reference mapping;
- conformance fixtures.

Do **not** introduce a second enum such as `CoordSpace` in `gsp.types`; extend the existing protocol
coordinate model only through accepted specs.

## 4. Display-list/builder integration

A Matplotlib frontend needs a builder, but it should initially live in the new `mpl_gsp` package, not
GSP core. Suggested shape:

```text
src/mpl_gsp/display_list.py       frontend-local display list and z-order
after proving value: gsp_extra/protocol_builder.py or gsp.protocol.builder
```

Initial builder responsibilities:

- collect normalized Matplotlib draw calls;
- maintain draw order and unsupported reasons;
- convert display pixels to panel-local NDC at freeze time;
- emit formal protocol visuals and optional attachments;
- preserve source/debug ids in frontend-local side tables rather than changing protocol metadata.

Only promote a builder into `gsp`/`gsp_extra` after at least image/scatter/line lowering proves the
shape.

## 5. Lowering targets by current visual support

| Matplotlib concept | Current GSP target | Current status |
|---|---|---|
| simple scatter/path collection, filled circles | `PointVisual` | ready after frontend lowering helpers |
| common markers | `MarkerVisual` | ready for conservative shape subset |
| simple line collections | `SegmentVisual` | ready |
| simple polylines | `PathVisual` | ready for MOVETO/LINETO, open paths |
| `imshow` / regular raster fallback | `ImageVisual` | ready; use RGBA8 or scalar image rules |
| simple text | `TextVisual` | wait for M075/M076, otherwise fallback |
| irregular quad mesh, Gouraud triangles | future `MeshVisual` | fallback until Mesh stage |
| arbitrary paths, Beziers, hatches, path effects, TeX/MathText | fallback RGBA/Agg | not native v1 |

## 6. Fallback layer policy

Start with whole-figure Agg fallback in `mpl_gsp`. It is simpler and safer than trying to compose
partial fallback layers.

RGBA fallback layers can be a later phase using `ImageVisual`, but only after coordinate and clipping
semantics are clear. Do not add a Text/Matplotlib-specific image overlay protocol field.

## 7. Metadata/external ids

Do not change protocol visuals for Matplotlib retained identity yet. Use frontend-local maps:

```text
(matplotlib artist id / draw call key) -> protocol visual id / cache entry
```

If retained updates require protocol-level metadata later, propose a small cross-visual metadata ADR.
Backends must remain free to ignore frontend-specific metadata.

## 8. Serialization

No serialization work is required for the first `mpl_gsp` proof. Existing debug/replay fixture
machinery should remain protocol-owned. Add serialization only after a stable builder/display-list
shape exists.

## 9. Recommended integration order

Respect the active S024 sequence first:

| Order | Mission/theme | Notes |
|---:|---|---|
| 1 | M075 TextVisual protocol dataclass/validation | Needed before native text plans. |
| 2 | M076 Matplotlib TextVisual reference renderer | Gives frontend a native simple-text target. |
| 3 | M077 Text visual QA | Proves text semantics independently of Matplotlib frontend. |
| 4 | M078/M079 Datoviz text probe/support | Keeps Datoviz text capability-gated. |
| 5 | New `mpl_gsp` architecture note | Convert these planning notes into a stage/ADR before implementation. |
| 6 | `mpl_gsp` package + Agg fallback | Backend import, draw, buffer_rgba, savefig; no native lowering required. |
| 7 | Native `draw_image` + simple `draw_path` | Use ImageVisual/PathVisual via NDC conversion. |
| 8 | Native scatter/path_collection | Performance proof: path collection -> PointVisual/MarkerVisual. |
| 9 | Optional frontend-local display list promotion | Only after repeated lowering code proves stable. |

## 10. Stop conditions

Stop and return to ADR/spec planning if implementation requires any of these:

- adding display-pixel coordinate space to public protocol without ADR;
- adding protocol metadata/external ids just for Matplotlib frontend caching;
- relying on Datoviz v0.3/private APIs;
- exposing glyph atlas/font handles through GSP TextVisual;
- implementing Mesh semantics before a Mesh stage;
- claiming Matplotlib compatibility without Agg fallback and debug stats.
