# Visual semantics

Visual records declare semantic geometry and appearance. They never contain shaders, pipelines,
native artists, device buffers, windows, or backend handles.

## Common rules

Visual identifiers must be valid. Numeric arrays must have the declared rank, cardinality, dtype, and finite-value policy. Colors use explicit RGBA representation. Coordinate space and transforms are never inferred from backend defaults.

Screen-space widths and sizes are logical pixels unless a specific contract states otherwise. Draw order is semantic only where the relevant visual and depth contract defines it.

### Common visual fields

| Field | Type | Required | Default | Meaning |
|---|---|---:|---|---|
| `id` | identifier | yes | — | Public visual identity. |
| `coordinate_space` | `data` or `ndc` | no | family-specific | Interpretation of positions. |
| `transform` | transform binding or null | no | null | Declarative transform applied before view mapping. |
| `visible` | boolean | no | true | Semantic contribution flag. |
| `order` | finite number | no | 0 | Family/attachment order where depth does not override. |

| Rule | Requirement |
|---|---|
| `GSP-VIS-001` | Numeric position, size, angle, width, UV, normal, and scalar arrays contain finite values unless a family explicitly defines a sentinel encoding. |
| `GSP-VIS-002` | Array cardinalities are exact. Broadcasting is limited to fields explicitly documented as scalar-or-per-item. |
| `GSP-VIS-003` | RGBA8 uses four `uint8` channels in red, green, blue, alpha order. Floating colors, where accepted, are finite and within `[0,1]`; implicit clipping is invalid. |
| `GSP-VIS-004` | Screen-space values are logical-pixel lengths or diameters, not backend area units or device pixels. Negative widths and sizes are invalid. |
| `GSP-VIS-005` | An unsupported field produces rejection or an advertised adaptation; silently dropping it is forbidden. |

## Points and markers

`PointVisual` represents circular point samples with per-item positions, sizes, and colors. `MarkerVisual` adds a semantic marker shape, angle, fill, and stroke. A backend must not substitute points for an unsupported marker shape without an adaptation declaration.

### PointVisual

| Field | Type | Cardinality | Default |
|---|---|---|---|
| `positions` | float32/float64 array | `(N,2)` or `(N,3)` | required |
| `colors` | RGBA array or null | `(N,4)` | null when scalar encoding is present |
| `sizes` | float scalar/array | scalar or `(N,)` logical-pixel diameter | `1` |
| `color_encoding` | scalar encoding or null | values `(N,)` | null |

`GSP-VIS-006`: exactly one direct color source or scalar color encoding controls the point color
slot. `(N,3)` positions require an accepted 3D view/coordinate combination.

### MarkerVisual

| Field | Type | Cardinality/default |
|---|---|---|
| `positions` | float array | `(N,2)` or accepted `(N,3)` |
| `shape` | marker enum or tuple | scalar or `N`; disc, square, triangle, diamond, cross |
| `fill_colors` | RGBA array or null | `(N,4)` or scalar encoding |
| `sizes` | non-negative float | scalar or `(N,)` diameter |
| `angle` | finite radians | scalar or `(N,)`; default `0` |
| `stroke_color` | RGBA | uniform or explicitly supported per-item form |
| `stroke_width` | non-negative logical pixels | default `0` |

`GSP-VIS-007`: marker angle is radians, measured according to the panel orientation contract.
Marker shape substitution is adapted support and reports the requested and realized shapes.

## Segments and paths

`SegmentVisual` represents independent line segments. `PathVisual` represents connected path topology and subpaths. Width, cap, and join semantics are explicit; connectivity must not be guessed from NaN separators unless the contract explicitly accepts that encoding.

### SegmentVisual

| Field | Type | Cardinality/default |
|---|---|---|
| `starts`, `ends` | float arrays | matching `(N,2)` or accepted `(N,3)` |
| `colors` | RGBA | `(N,4)` |
| `widths` | non-negative float | scalar or `(N,)` logical pixels |
| `cap` | `butt`, `round`, `square` | default `butt` |

### PathVisual

| Field | Type | Cardinality/default |
|---|---|---|
| `positions` | float array | `(N,2)` or accepted `(N,3)` |
| `path_lengths` | positive integer tuple | sum equals `N`; each accepted subpath has at least 2 vertices |
| `colors` | RGBA | family-defined uniform or per-subpath association |
| `width` | non-negative float | logical pixels |
| `cap` | cap enum | default `butt` |
| `join` | `miter`, `round`, `bevel` | default `miter` |
| `miter_limit` | positive finite float | required for miter behavior; default contract value |

`GSP-VIS-008`: segment independence and path connectivity are distinct semantics. Converting one to
the other is an adaptation unless topology and cap/join behavior remain exactly equivalent.

## Images

`ImageVisual` represents RGBA or scalar sampled fields with explicit origin, interpolation, coordinate placement, and optional color scale. Scalar values are normalized before canonical colormap application. Image rendering and image-texel query support are separate capabilities.

### ImageVisual

| Field | Type | Required/default |
|---|---|---|
| `image` | contiguous array | required; `(H,W,4)` RGBA or `(H,W)` scalar |
| `extent` | four finite values | required for DATA placement; panel-NDC default may be full panel |
| `origin` | `upper` or `lower` | required; no backend default |
| `interpolation` | `nearest` or `linear` | default `nearest` |
| `color_encoding` | scalar encoding | required for non-RGBA scalar mapping beyond the fixed gray shorthand |

`GSP-VIS-009`: image row orientation is defined before view transforms. Interpolation describes
sampling, not color normalization. Scalar normalization uses the color-scale contract; NaN/under/
over behavior must be explicit when supported.

## Text

`TextVisual` contains strings, positions, logical-pixel size, anchors, rotation, color, and generic font role. Guide labels and titles remain guides rather than ordinary text visuals. Unicode shaping, bidirectional text, exact font matching, and multiline behavior require explicit support.

### TextVisual

| Field | Type | Cardinality/default |
|---|---|---|
| `text` | tuple of Unicode strings | `N` |
| `positions` | float array | `(N,2)` or accepted `(N,3)` |
| `size` | positive logical pixels | scalar or `(N,)` |
| `anchor_x` | left/center/right | scalar or `N` |
| `anchor_y` | baseline/top/center/bottom | scalar or `N` |
| `rotation` | finite radians | scalar or `(N,)`; default `0` |
| `colors` | RGBA | `(N,4)` |
| `font_role` | default/sans/serif/monospace | generic role, not a font handle |

`GSP-VIS-010`: anchor semantics refer to the resolved text layout box. A backend that cannot shape
or measure the requested text may adapt only under an advertised font/text capability and reports
the deviation. Guide text retains guide identity.

## Meshes

`MeshVisual` uses triangle geometry with indexed or accepted unindexed topology. The bounded contract includes uniform or per-face RGBA, opaque depth, flat Lambert face-normal shading, projected face culling, and unlit Texture2D records. Vertex-normal shading, broad material graphs, arbitrary transparency, instancing, and volume rendering are outside this contract.

Mesh rendering does not imply mesh-triangle picking. Identity, geometry, barycentric, depth, and facing query payloads are separately capability-gated.

### MeshVisual geometry and color

| Field | Type | Required/default |
|---|---|---|
| `positions` | finite float `(N,2)` or `(N,3)` | required |
| `faces` | integer `(M,3)` | required for indexed topology; indices in `[0,N)` |
| `color` | RGBA `(4,)`, `(M,4)`, or accepted `(N,4)` | required unless material supplies the slot |
| `color_mode` | uniform/face/vertex | inferred only when cardinality is unambiguous |
| `depth_mode` | auto/disabled/enabled | bounded by view/material capability |
| `face_culling` | none/back/front | default none |
| `shading` | unlit_rgba/flat_lambert/texture2d_unlit | default unlit_rgba |

### Flat Lambert fields

| Field | Type | Rule |
|---|---|---|
| `normal_mode` | none/face/vertex | bounded strict contract accepts face normals only |
| `normals` | finite float `(M,3)` | normalized or normalized by the specified deterministic rule |
| `normal_generation` | none/face_flat | generated face normals use declared winding |
| directional light | direction, color, intensity | finite, typed View3D lighting state |

### Texture2D unlit fields

| Field | Type | Rule |
|---|---|---|
| `texture2d_id` | Texture2D resource ID | required |
| `uv_mode` | vertex | fixed bounded mode |
| `uvs` | finite float `(N,2)` | one UV per mesh vertex |
| `texture_filter` | nearest/linear | visual-owned; default nearest; one value controls min and mag |
| base color | uniform RGBA | multiplicative color under the accepted equation |

`GSP-VIS-011`: mesh topology is triangles. Degenerate triangles, projected clipping, depth,
culling, and transparency support are capability-scoped; successful rasterization is not proof of
strict semantics.

`GSP-VIS-012`: flat Lambert uses deterministic face normals and accepted light/color arithmetic.
Smooth/Phong shading is outside GSP 0.2. Texture protocol validation is independent from renderer
material support.

`GSP-VIS-013`: strict opaque 3D depth requires per-fragment ordering for the advertised view and
mesh combination. CPU average-face sorting is adapted reference behavior, not strict GPU depth.

`GSP-VIS-014`: face culling is evaluated from projected NDC winding under the accepted front-face
convention. Query picking excludes culled and projected-degenerate contributions under the same
snapshot.

## Color scales

A `ColorScale` identifies a canonical colormap and finite normalization domain. Linear normalization
maps `(value-vmin)/(vmax-vmin)` before clamping or explicit under/over policy. `vmin < vmax`.

`GSP-VIS-015`: named colormap identity is protocol vocabulary, not a backend registry lookup.
Displayed RGBA, normalized scalar, and source scalar query payloads remain separately requested and
capability-gated.
