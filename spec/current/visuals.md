# Visual semantics

## Common rules

Visual identifiers must be valid. Numeric arrays must have the declared rank, cardinality, dtype, and finite-value policy. Colors use explicit RGBA representation. Coordinate space and transforms are never inferred from backend defaults.

Screen-space widths and sizes are logical pixels unless a specific contract states otherwise. Draw order is semantic only where the relevant visual and depth contract defines it.

## Points and markers

`PointVisual` represents circular point samples with per-item positions, sizes, and colors. `MarkerVisual` adds a semantic marker shape, angle, fill, and stroke. A backend must not substitute points for an unsupported marker shape without an adaptation declaration.

## Segments and paths

`SegmentVisual` represents independent line segments. `PathVisual` represents connected path topology and subpaths. Width, cap, and join semantics are explicit; connectivity must not be guessed from NaN separators unless the contract explicitly accepts that encoding.

## Images

`ImageVisual` represents RGBA or scalar sampled fields with explicit origin, interpolation, coordinate placement, and optional color scale. Scalar values are normalized before canonical colormap application. Image rendering and image-texel query support are separate capabilities.

## Text

`TextVisual` contains strings, positions, logical-pixel size, anchors, rotation, color, and generic font role. Guide labels and titles remain guides rather than ordinary text visuals. Unicode shaping, bidirectional text, exact font matching, and multiline behavior require explicit support.

## Meshes

`MeshVisual` uses triangle geometry with indexed or accepted unindexed topology. The bounded contract includes uniform or per-face RGBA, opaque depth, flat Lambert face-normal shading, projected face culling, and unlit Texture2D records. Vertex-normal shading, broad material graphs, arbitrary transparency, instancing, and volume rendering are outside this contract.

Mesh rendering does not imply mesh-triangle picking. Identity, geometry, barycentric, depth, and facing query payloads are separately capability-gated.
